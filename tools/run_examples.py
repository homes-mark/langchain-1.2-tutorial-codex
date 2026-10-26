"""Run all deterministic examples plus project regression, never live API branches.

Run with the tutorial venv: python tools/run_examples.py
Writes validation/report.json. Each child uses the same interpreter with a 45s limit.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def run_examples(root: Path = ROOT) -> dict:
    root = root.resolve()
    temporary = root / ".tmp"
    temporary.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update({"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1",
                "LANGSMITH_TRACING": "false", "LANGCHAIN_TRACING_V2": "false",
                "LANGCHAIN_TRACING": "false", "TMP": str(temporary), "TEMP": str(temporary),
                "TMPDIR": str(temporary)})
    # No key is needed by the selected paths. Remove inherited provider/tracing keys
    # so an accidental missing --live guard cannot bill a configured account.
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
                 "LANGSMITH_API_KEY", "LANGCHAIN_API_KEY"):
        env.pop(name, None)
    scripts = sorted((root / "examples").glob("[0-9][0-9]_*.py"))
    scripts.append(root / "project" / "check_project.py")
    results = []
    for script in scripts:
        relative = script.relative_to(root).as_posix()
        started = time.monotonic()
        command = [sys.executable, str(script)]
        try:
            completed = subprocess.run(command, cwd=root, env=env, capture_output=True,
                                       text=True, encoding="utf-8", errors="replace", timeout=45)
            record = {"script": relative, "command": [sys.executable, relative],
                      "returncode": completed.returncode, "timed_out": False,
                      "stdout": completed.stdout, "stderr": completed.stderr}
        except subprocess.TimeoutExpired as error:
            def text(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
            record = {"script": relative, "command": [sys.executable, relative],
                      "returncode": None, "timed_out": True,
                      "stdout": text(error.stdout), "stderr": text(error.stderr)}
        except OSError as error:
            record = {"script": relative, "command": [sys.executable, relative],
                      "returncode": None, "timed_out": False,
                      "stdout": "", "stderr": f"Could not start process: {error}"}
        record["seconds"] = round(time.monotonic() - started, 3)
        record["passed"] = record["returncode"] == 0 and not record["timed_out"]
        results.append(record)
        print(f"{'PASS' if record['passed'] else 'FAIL'} {relative} ({record['seconds']:.3f}s)", flush=True)
    failed = [record["script"] for record in results if not record["passed"]]
    if len(scripts) < 2:
        failed.append("No numbered tutorial example scripts were discovered")
    report = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "interpreter": sys.executable, "mode": "offline deterministic regression",
              "status": "passed" if not failed else "failed",
              "executed_count": len(results), "passed_count": sum(r["passed"] for r in results),
              "failed": failed, "results": results,
              "limitations": ["No --live branch or provider network request is executed.",
                              "Scripted models check framework control flow, not language understanding.",
                              "This runner disables tracing and removes common API keys; it is not a network sandbox."]}
    validation = root / "validation"
    validation.mkdir(exist_ok=True)
    (validation / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{report['status'].upper()}: {report['passed_count']}/{len(results)}; validation/report.json")
    return report


if __name__ == "__main__":
    outcome = run_examples()
    sys.exit(0 if outcome["status"] == "passed" else 1)
