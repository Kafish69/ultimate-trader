# Changelog

## 1.0.0

First public release.

- One router skill, `ultimate-trader`, that combines TradingAgents, Vibe-Trading and the Day Trader pack into a gated workflow: research, test, size, risk check, your yes, paper order.
- 11 Day Trader skills bundled, plus Vibe-Trading's 90 method skills as references.
- `trader-graduate`: a trade journal and a graduation check (50 paper trades over 10 days, positive after fees, profit factor of 1.2 or more, drawdown of 20% or less) before any real money.
- `install.py` installs the skills, builds two virtual environments and registers the Vibe-Trading MCP server with a config backup. `scripts/doctor.py` reports readiness without printing keys.
- 330 offline tests, including contract tests for the router's safety rules and a scan for key-shaped strings. CI runs on Linux, macOS and Windows.
- Project website with a signal demo, the route, a trade-size lab and a paper trade race against the skills.
