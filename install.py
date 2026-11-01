#!/usr/bin/env python3
"""Ultimate Trader installer.

Copies the skills into ~/.claude/skills, builds the two Python environments
(TradingAgents and Vibe-Trading pin conflicting dependencies, so they cannot
share one) and registers the Vibe-Trading MCP server in ~/.claude.json.

    python install.py              # everything
    python install.py --skills     # only copy the skills
    python install.py --no-mcp     # skip the MCP registration
    python install.py --no-venvs   # skip the Python packages
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import venv

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
IS_WIN = os.name == "nt"


def venv_python(name):
    sub, exe = ("Scripts", "python.exe") if IS_WIN else ("bin", "python")
    return os.path.join(CLAUDE, name, sub, exe)


def venv_script(name, script):
    sub = "Scripts" if IS_WIN else "bin"
    return os.path.join(CLAUDE, name, sub, script + (".exe" if IS_WIN else ""))


def install_skills():
    src = os.path.join(ROOT, "skills")
    dst = os.path.join(CLAUDE, "skills")
    os.makedirs(dst, exist_ok=True)
    names = sorted(d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d)))
    for name in names:
        target = os.path.join(dst, name)
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.copytree(src_dir := os.path.join(src, name), target,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"skills: {len(names)} installed to {dst}")


def make_venv(name, package):
    py = venv_python(name)
    if not os.path.exists(py):
        print(f"creating {name} ...")
        venv.create(os.path.join(CLAUDE, name), with_pip=True)
    print(f"installing {package} into {name} (a few minutes the first time) ...")
    subprocess.check_call([py, "-m", "pip", "install", "--quiet", "--upgrade", "pip", package])


def register_mcp():
    exe = venv_script("trading-venv-vt", "vibe-trading-mcp")
    if not os.path.exists(exe):
        print("mcp: vibe-trading-mcp not found, skipped")
        return
    path = os.path.join(HOME, ".claude.json")
    data = {}
    if os.path.exists(path):
        shutil.copy(path, path + ".bak-ultimate-trader")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    data.setdefault("mcpServers", {})["vibe-trading"] = {
        "type": "stdio", "command": exe, "args": [], "env": {}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"mcp: vibe-trading registered in {path} (backup: .claude.json.bak-ultimate-trader)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills", action="store_true", help="only copy the skills")
    ap.add_argument("--no-venvs", action="store_true")
    ap.add_argument("--no-mcp", action="store_true")
    a = ap.parse_args()

    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or newer is required (TradingAgents and Vibe-Trading need it).")

    install_skills()
    if not a.skills and not a.no_venvs:
        make_venv("trading-venv-ta", "tradingagents")
        make_venv("trading-venv-vt", "vibe-trading-ai")
        if not a.no_mcp:
            register_mcp()
    print("\nDone. Restart Claude Code, then run: python scripts/doctor.py")
    print("Next: set your keys as environment variables (see README, 'Keys').")


if __name__ == "__main__":
    main()
