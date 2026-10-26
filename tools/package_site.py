"""Package only explicit deliverable directories; exclude local env, secrets and DBs."""
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
destination = ROOT.parent / f"{ROOT.name}.zip"
files = list(ROOT.glob("*.html")) + list(ROOT.glob("*.md")) + list(ROOT.glob("requirements*.txt"))
for directory, extensions in {
    "assets": {".css", ".js", ".json"}, "content": {".json"},
    "examples": {".py"}, "project": {".py"}, "tools": {".py"},
    "validation": {".json", ".png"},
}.items():
    files.extend(p for p in (ROOT / directory).iterdir() if p.is_file() and p.suffix in extensions)
files = sorted(set(files))
with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, (Path(ROOT.name) / path.relative_to(ROOT)).as_posix())
with ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(files)
    assert all(".venv/" not in name and ".tmp/" not in name for name in archive.namelist())
print(f"Packaged {len(files)} files: {destination} ({destination.stat().st_size:,} bytes)")
print("SHA256:", hashlib.sha256(destination.read_bytes()).hexdigest())
