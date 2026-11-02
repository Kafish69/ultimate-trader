# Contributing

Thanks for looking. This project is small, so the rules are short.

## Ground rules

1. **Safety first.** A change must never weaken the gates: risk PASS, your typed yes, your click on Claude's permission card, and the graduation check before real money. Tests in `tests/test_router.py` guard these on purpose. Changing them needs a clear reason in the pull request.
2. **Paper by default.** Never ship a config or example that turns on live trading.
3. **No secrets.** No keys, tokens or account numbers anywhere, including tests and screenshots.
4. **Not financial advice.** Do not add copy that promises returns.

## Set up

```bash
git clone https://github.com/Kafish69/ultimate-trader.git
cd ultimate-trader
python scripts/check_skills.py
python -m unittest discover -s tests
```

You need Python 3.11 or newer. The tests are offline and use saved fixtures, so they need no keys and no network.

## Before you open a pull request

- `python scripts/check_skills.py` passes (every `SKILL.md` has a name that matches its folder and a description).
- `python -m unittest discover -s tests` passes.
- New behaviour has a test.
- The site in `docs/` still works if you touched it: open `docs/index.html` and `docs/paper.html` through a local server (`python -m http.server -d docs`).

## Skills

Each skill is a folder under `skills/` with a `SKILL.md` (frontmatter `name` and `description`) and optional standard-library Python tools. Keep tools free of third-party dependencies.

## Upstream code

`skills/trader-*` (except `trader-graduate`) and `skills/ultimate-trader/references/vibe-skills` come from the Day Trader skill and Vibe-Trading under MIT. Fixes that belong upstream are better sent upstream too. See `NOTICE`.
