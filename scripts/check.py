#!/usr/bin/env python3
"""Run Python and Node syntax checks plus the unit test suite."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PY_FILES = sorted(SCRIPTS.glob("*.py")) + sorted((SCRIPTS / "tests").glob("*.py"))


def run(args):
    print("$", " ".join(args), flush=True)
    subprocess.run(args, check=True)


def main():
    for path in PY_FILES:
        run([sys.executable, "-m", "py_compile", str(path)])
    run([sys.executable, "-m", "unittest", "discover", "-s", str(SCRIPTS / "tests"), "-v"])
    run(["node", "--check", str(SCRIPTS / "record_video.js")])


if __name__ == "__main__":
    main()
