"""
TabQA Generator — FastAPI backend
Wraps the Gradino generation library and serves the React frontend.
"""

import asyncio
import csv
import io
import json
import os
import re
import sys
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="TabQA Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory task store ────────────────────────────────────────────────────
# { task_id: { status, progress, current, total, instances, ... } }
tasks: dict = {}


# ── Pydantic models ─────────────────────────────────────────────────────────

class GenerationParams(BaseModel):
    domain: str = "environmental"
    question_type: str = "sum"
    num_tables: int = 3
    num_samples: int = 10
    col_cardinality: int = 20
    num_columns: int = 21
    sequential: bool = False
    api_key: str = ""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _extract_tables(raw) -> list:
    """Normalize the 'Table' field from Gradino output into a list of HTML strings."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(t) for t in raw if t]
    s = str(raw)
    # Find all <table>…</table> blocks
    found = re.findall(r'<table[\s\S]*?</table>', s, re.IGNORECASE)
    return found if found else ([s] if s.strip() else [])


def _flatten_instances(data: dict) -> list:
    """Convert Gradino's nested {nt: {method: {pert: [records]}}} into a flat list."""
    instances = []
    idx = 0
    for nt_key in sorted(data.keys(), key=lambda k: int(k) if k.lstrip("-").isdigit() else k):
        for method_key, pert_dict in data[nt_key].items():
            for pert_key, records in pert_dict.items():
                for rec in records:
                    instances.append({
                        "id": idx,
                        "num_tables": nt_key,
                        "method": method_key,
                        "perturbation": pert_key,
                        "question": str(rec.get("Question") or ""),
                        "tables": _extract_tables(rec.get("Table")),
                        "answer": str(rec.get("Label") or ""),
                        "sql_queries": rec.get("SQL Query") or [],
                        "constraints": rec.get("Constraints") or {},
                    })
                    idx += 1
    return instances


# ── Background generation task ───────────────────────────────────────────────

async def _run_generation(task_id: str, params: dict):
    task = tasks[task_id]
    env = os.environ.copy()
    api_key = params.get("api_key", "")
    if api_key:
        env["OPENAI_API_KEY"] = api_key
    elif not env.get("OPENAI_API_KEY"):
        # Try loading from gradino/.env as a convenience for local runs
        here = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(here, "..", "gradino", ".env")
        if os.path.isfile(dotenv_path):
            with open(dotenv_path) as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line.startswith("OPENAI_API_KEY=") and not _line.startswith("#"):
                        env["OPENAI_API_KEY"] = _line.split("=", 1)[1].strip().strip('"').strip("'")
                        break

    params_json = json.dumps(params)
    script_path = os.path.join(os.path.dirname(__file__), "generate_script.py")

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, script_path, params_json,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            limit=16 * 1024 * 1024,  # 16 MB stdout buffer
        )
        task["process"] = proc

        # Drain stderr concurrently so it never blocks the subprocess
        stderr_chunks: list = []
        async def _read_stderr():
            async for chunk in proc.stderr:
                stderr_chunks.append(chunk)
        stderr_task = asyncio.create_task(_read_stderr())

        async for raw_line in proc.stdout:
            if task.get("stop_requested"):
                proc.terminate()
                await proc.wait()
                await stderr_task
                task["status"] = "stopped"
                return

            line = raw_line.decode().strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                mtype = msg.get("type")
                if mtype == "progress":
                    task["progress"] = msg["progress"]
                    task["current"] = msg["current"]
                    task["total"] = msg["total"]
                    task["status_message"] = msg.get("desc", "Generating…")
                elif mtype == "status":
                    task["status_message"] = msg.get("message", "")
                elif mtype == "result":
                    task["progress"] = 1.0
                    task["instances"] = _flatten_instances(msg.get("data", {}))
                    task["generation_errors"] = msg.get("errors", [])
                elif mtype == "error":
                    task["status"] = "error"
                    task["error"] = msg.get("message", "Unknown error")
                    task["traceback"] = msg.get("traceback", "")
                    await stderr_task
                    return
            except json.JSONDecodeError:
                pass

        await proc.wait()
        await stderr_task
        stderr_output = b"".join(stderr_chunks).decode(errors="replace").strip()
        if stderr_output:
            print(f"[generate_script stderr]\n{stderr_output[:4000]}", file=sys.stderr, flush=True)

        if task["status"] == "running":
            if proc.returncode == 0:
                task["status"] = "completed"
                task["progress"] = 1.0
            else:
                task["status"] = "error"
                task["error"] = (stderr_output or "subprocess exited with non-zero code")[-2000:]

    except Exception as exc:
        import traceback as _tb
        task["status"] = "error"
        task["error"] = str(exc)
        task["traceback"] = _tb.format_exc()


# ── API routes ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/generate")
async def start_generation(params: GenerationParams):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "running",
        "progress": 0.0,
        "current": 0,
        "total": params.num_samples,
        "instances": [],
        "status_message": "Initializing…",
        "error": None,
        "traceback": None,
        "generation_errors": [],
        "process": None,
        "stop_requested": False,
        "created_at": datetime.utcnow().isoformat(),
        "params": params.model_dump(exclude={"api_key"}),
    }
    asyncio.create_task(_run_generation(task_id, params.model_dump()))
    return {"task_id": task_id}


@app.get("/api/generate/{task_id}/stream")
async def stream_progress(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")

    async def _events():
        last_payload = None
        while True:
            task = tasks.get(task_id)
            if not task:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break

            payload = json.dumps({
                "status": task["status"],
                "progress": task["progress"],
                "current": task["current"],
                "total": task["total"],
                "instance_count": len(task.get("instances", [])),
                "status_message": task.get("status_message", ""),
                "error": task.get("error"),
            })
            if payload != last_payload:
                yield f"data: {payload}\n\n"
                last_payload = payload

            if task["status"] in ("completed", "stopped", "error"):
                break
            await asyncio.sleep(0.4)

    return StreamingResponse(
        _events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.delete("/api/generate/{task_id}")
async def stop_generation(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    tasks[task_id]["stop_requested"] = True
    tasks[task_id]["status"] = "stopped"
    return {"status": "stop_requested"}


@app.get("/api/tasks")
async def list_tasks():
    result = []
    for tid, task in tasks.items():
        result.append({
            "task_id": tid,
            "status": task["status"],
            "progress": task["progress"],
            "instance_count": len(task.get("instances", [])),
            "created_at": task.get("created_at"),
            "params": task.get("params"),
        })
    return {"tasks": result}


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "current": task["current"],
        "total": task["total"],
        "instance_count": len(task.get("instances", [])),
        "status_message": task.get("status_message", ""),
        "error": task.get("error"),
        "params": task.get("params"),
        "created_at": task.get("created_at"),
    }


@app.get("/api/tasks/{task_id}/instances")
async def get_instances(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    return {
        "instances": tasks[task_id].get("instances", []),
        "generation_errors": tasks[task_id].get("generation_errors", []),
    }


@app.put("/api/tasks/{task_id}/instances/{instance_id}")
async def update_instance(task_id: str, instance_id: int, data: dict):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    instances = tasks[task_id].get("instances", [])
    for inst in instances:
        if inst["id"] == instance_id:
            for field in ("question", "answer", "tables"):
                if field in data:
                    inst[field] = data[field]
            return {"status": "ok"}
    raise HTTPException(404, "Instance not found")


@app.get("/api/tasks/{task_id}/download")
async def download_dataset(task_id: str, fmt: str = "csv"):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    instances = tasks[task_id].get("instances", [])

    if fmt == "json":
        content = json.dumps(instances, indent=2, ensure_ascii=False)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=tabqa_{task_id[:8]}.json"},
        )

    # Default: CSV
    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=["id", "question", "answer", "tables", "method", "perturbation", "num_tables"],
        extrasaction="ignore",
    )
    writer.writeheader()
    for inst in instances:
        writer.writerow({
            "id": inst["id"],
            "question": inst["question"],
            "answer": inst["answer"],
            "tables": json.dumps(inst["tables"], ensure_ascii=False),
            "method": inst["method"],
            "perturbation": inst["perturbation"],
            "num_tables": inst["num_tables"],
        })
    return StreamingResponse(
        io.BytesIO(out.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=tabqa_{task_id[:8]}.csv"},
    )


# ── Static frontend ──────────────────────────────────────────────────────────
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True), name="static")
