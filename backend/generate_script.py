#!/usr/bin/env python3
"""
Worker script that runs Gradino generation in a subprocess.
Patches tqdm before importing Gradino to capture progress.
Outputs JSON lines to stdout for the parent process to read.
"""

import sys
import json
import os
import traceback


def emit(msg: dict):
    print(json.dumps(msg), flush=True)


# ── Patch tqdm BEFORE any Gradino imports ──────────────────────────────────
try:
    import tqdm as _tqdm_module
    from tqdm import tqdm as _orig_tqdm

    class _ProgressTqdm(_orig_tqdm):
        def update(self, n=1):
            result = super().update(n)
            try:
                if self.total and self.total > 0:
                    emit({
                        "type": "progress",
                        "current": int(self.n),
                        "total": int(self.total),
                        "progress": float(min(self.n / self.total, 1.0)),
                        "desc": self.desc or "",
                    })
            except Exception:
                pass
            return result

    _tqdm_module.tqdm = _ProgressTqdm
    try:
        import tqdm.auto as _tqdm_auto
        _tqdm_auto.tqdm = _ProgressTqdm
    except Exception:
        pass
    try:
        import tqdm.std as _tqdm_std
        _tqdm_std.tqdm = _ProgressTqdm
    except Exception:
        pass
except ImportError:
    pass  # tqdm not installed — no progress bars


# ── Main generation logic ──────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        emit({"type": "error", "message": "No parameters provided"})
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        emit({"type": "error", "message": f"Invalid JSON params: {exc}"})
        sys.exit(1)

    # Set OpenAI API key
    api_key = params.get("api_key", "")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    gradino_path = os.environ.get("GRADINO_PATH", "/app/gradino")
    if gradino_path not in sys.path:
        sys.path.insert(0, gradino_path)

    emit({"type": "status", "message": "Importing Gradino modules…"})

    try:
        from models import MTAutoGen  # noqa: E402
    except ImportError as exc:
        emit({"type": "error", "message": f"Failed to import Gradino: {exc}\n{traceback.format_exc()}"})
        sys.exit(1)

    emit({"type": "status", "message": "Starting generation…"})

    # Build args dict (Gradino expects a plain dict, not argparse.Namespace)
    args = {
        "domain": params.get("domain", "environmental"),
        "question_type": params.get("question_type", "sum"),
        "num_tables": int(params.get("num_tables", 3)),
        "num_samples": int(params.get("num_samples", 10)),
        "col_cardinality": int(params.get("col_cardinality", 20)),
        "num_columns": int(params.get("num_columns", 21)),
        "sequential": bool(params.get("sequential", False)),
    }

    try:
        generator = MTAutoGen(args)

        num_tables = args["num_tables"]
        sequential = args["sequential"]
        domain = args["domain"]
        method = args["question_type"]
        num_samples = args["num_samples"]
        col_cardinality = args["col_cardinality"]
        num_columns = args["num_columns"]

        emit({"type": "status", "message": f"Calling run_generation(num_tables={num_tables}, method={method}, num_samples={num_samples}, domain={domain})"})

        if num_tables == -1:
            samples, error_logs = generator.run_generation(
                num_tables=-1,
                num_samples=num_samples,
                domain=domain,
                sequential=sequential,
            )
        else:
            samples, error_logs = generator.run_generation(
                num_tables=num_tables,
                method=method,
                num_samples=num_samples,
                domain=domain,
                col_cardinality=col_cardinality,
                num_columns=num_columns,
                sequential=sequential,
            )

        # Diagnostic: log structure of returned samples
        print(f"[DEBUG] samples keys: {list(samples.keys()) if samples else 'empty'}", file=sys.stderr, flush=True)
        for sk in (samples or {}):
            for mk in samples[sk]:
                for pk in samples[sk][mk]:
                    v = samples[sk][mk][pk]
                    print(f"[DEBUG] samples[{sk!r}][{mk!r}][{pk!r}] = {type(v).__name__} shape={getattr(v, 'shape', '?')}", file=sys.stderr, flush=True)
        if error_logs:
            print(f"[DEBUG] error_logs ({len(error_logs)}): {[str(e)[:200] for e in error_logs[:5]]}", file=sys.stderr, flush=True)

        # Serialize DataFrames to JSON-serialisable dicts
        import pandas as pd

        output: dict = {}
        for nt_key in samples:
            output[str(nt_key)] = {}
            for k1 in samples[nt_key]:
                output[str(nt_key)][k1] = {}
                for k2 in samples[nt_key][k1]:
                    df = samples[nt_key][k1][k2]
                    if not isinstance(df, pd.DataFrame):
                        print(f"[DEBUG] skipping non-DataFrame at [{nt_key}][{k1}][{k2}]: {type(df)}", file=sys.stderr, flush=True)
                        continue
                    records = []
                    for _, row in df.iterrows():
                        record: dict = {}
                        for col in df.columns:
                            val = row[col]
                            # Normalize value
                            if isinstance(val, float) and val != val:  # NaN
                                record[col] = None
                            elif isinstance(val, (int, float, bool)):
                                record[col] = val
                            else:
                                s = str(val)
                                # Try to decode JSON-encoded lists/dicts
                                if s and s[0] in ('[', '{'):
                                    try:
                                        record[col] = json.loads(s)
                                        continue
                                    except Exception:
                                        pass
                                record[col] = s
                        records.append(record)
                    output[str(nt_key)][k1][k2] = records

        total_records = sum(
            len(output[a][b][c]) for a in output for b in output[a] for c in output[a][b]
        )
        print(f"[DEBUG] output keys: {list(output.keys())}, total_records={total_records}", file=sys.stderr, flush=True)

        emit({
            "type": "result",
            "data": output,
            "errors": [str(e) for e in (error_logs or [])],
        })

    except Exception as exc:
        emit({
            "type": "error",
            "message": str(exc),
            "traceback": traceback.format_exc(),
        })
        sys.exit(1)


if __name__ == "__main__":
    main()
