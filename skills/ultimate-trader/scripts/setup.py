"""Create two venvs (the packages pin conflicting dependencies):
~/.claude/trading-venv-ta  -> TradingAgents
~/.claude/trading-venv-vt  -> Vibe-Trading
"""
import os
import subprocess
import venv

home = os.path.expanduser("~")


def make(name, package):
    env_dir = os.path.join(home, ".claude", name)
    exe = "python.exe" if os.name == "nt" else "python"
    py = os.path.join(env_dir, "Scripts" if os.name == "nt" else "bin", exe)
    if not os.path.exists(py):
        venv.create(env_dir, with_pip=True)
    subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "pip", package])
    print("ready:", py)


make("trading-venv-ta", "tradingagents")
make("trading-venv-vt", "vibe-trading-ai")
