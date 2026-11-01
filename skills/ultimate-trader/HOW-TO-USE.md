# Ultimate Trader: how to use it

Not financial advice. Paper trading first. Nothing here places an order without your yes.

## What you have

| piece | where | what it is |
| --- | --- | --- |
| `ultimate-trader` | `~/.claude/skills/ultimate-trader` | the master skill; routes to the three engines |
| 11 `trader-*` skills | `~/.claude/skills/trader-*` | day-trading pipeline (scan, news, entry, exit, Time Machine, budget, risk, broker, alerts, analyst, pelosi) |
| TradingAgents | `~/.claude/trading-venv-ta` | multi-agent LLM debate -> rated decision |
| Vibe-Trading | `~/.claude/trading-venv-vt` + 90 method skills in `references/vibe-skills` | backtests, factors, options, journal analysis |

## One-time setup

1. Restart Claude Code so it sees the new skills.
2. Set ONE LLM key as an environment variable for TradingAgents (never paste it in chat), e.g. in PowerShell:
   `setx ANTHROPIC_API_KEY "sk-..."` (then reopen the terminal).
3. Optional, for SEC tools: `setx SEC_USER_AGENT "Your Name you@email.com"`.
4. Optional, Vibe-Trading as direct Claude tools: add `vibe-trading-mcp` (in `~/.claude/trading-venv-vt/Scripts`) to your MCP config.
5. Optional, for paper orders: connect Alpaca's MCP server (paper account) as described in `/trader-broker`.

## Prompts to try

- `/ultimate-trader analyze NVDA` -> TradingAgents debate, bull vs bear, rating.
- `/ultimate-trader find me a day trade today, $5,000 account, $50 max loss, paper` -> full pipeline.
- `/ultimate-trader backtest a 20/50 SMA crossover on AAPL 2022-2025 with costs` -> Vibe-Trading.
- `/ultimate-trader review my trades` (give a broker CSV) -> journal analysis and habit report.
- Single steps: `/trader-scanner`, `/trader-news`, `/trader-timemachine`, `/trader-risk` ...

## The pipeline

scan -> news -> deep research (TradingAgents) -> backtest / Time Machine -> entry -> exit -> budget -> risk check -> your yes -> broker (paper) -> alerts -> monthly journal review.

If risk says BLOCK, or the odds are a coin flip, the right answer is "pass".
