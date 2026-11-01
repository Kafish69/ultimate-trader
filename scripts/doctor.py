#!/usr/bin/env python3
"""Check that Ultimate Trader is installed and ready. Prints OK / WARN / FAIL per item.
Exit code is 1 if any FAIL. Never prints key values, only whether they are set."""
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
IS_WIN = os.name == "nt"
SKILLS = ["ultimate-trader", "trader-scanner", "trader-news", "trader-entry", "trader-exit",
          "trader-timemachine", "trader-budget", "trader-risk", "trader-broker",
          "trader-alerts", "trader-analyst", "trader-pelosi"]
LLM_KEYS = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "DEEPSEEK_API_KEY",
            "OPENROUTER_API_KEY", "GROQ_API_KEY", "XAI_API_KEY", "MISTRAL_API_KEY"]
fails = 0


def show(level, msg):
    global fails
    fails += level == "FAIL"
    print(f"[{level:>4}] {msg}")


def py(name):
    return os.path.join(CLAUDE, name, "Scripts" if IS_WIN else "bin", "python" + (".exe" if IS_WIN else ""))


for s in SKILLS:
    ok = os.path.exists(os.path.join(CLAUDE, "skills", s, "SKILL.md"))
    show("OK" if ok else "FAIL", f"skill {s}")

checks = [("trading-venv-ta", "from tradingagents.graph.trading_graph import TradingAgentsGraph", "TradingAgents"),
          ("trading-venv-vt", "import importlib.metadata as m; m.version('vibe-trading-ai')", "Vibe-Trading")]
for venv_name, code, label in checks:
    if not os.path.exists(py(venv_name)):
        show("FAIL", f"{label}: {venv_name} missing (run install.py)")
        continue
    r = subprocess.run([py(venv_name), "-c", code], capture_output=True, text=True)
    show("OK" if r.returncode == 0 else "FAIL", f"{label} imports")

try:
    with open(os.path.join(HOME, ".claude.json"), encoding="utf-8") as f:
        mcp = json.load(f).get("mcpServers", {})
    show("OK" if "vibe-trading" in mcp else "WARN", "Vibe-Trading MCP server registered" if "vibe-trading" in mcp
         else "Vibe-Trading MCP server not registered (optional)")
except Exception:
    show("WARN", "could not read ~/.claude.json")

have = [k for k in LLM_KEYS if os.environ.get(k)]
show("OK" if have else "WARN", f"LLM key set for TradingAgents: {', '.join(have)}" if have
     else "no LLM key set; TradingAgents needs one (e.g. ANTHROPIC_API_KEY)")
alp = bool(os.environ.get("ALPACA_API_KEY") and os.environ.get("ALPACA_SECRET_KEY"))
show("OK" if alp else "WARN", "Alpaca paper keys set" if alp else "Alpaca keys not set; the broker step needs them")
show("OK" if sys.version_info >= (3, 11) else "FAIL", f"Python {sys.version.split()[0]}")
sys.exit(1 if fails else 0)
