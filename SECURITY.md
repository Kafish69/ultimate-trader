# Security

Ultimate Trader can lead to orders at a real broker, so security reports are taken seriously.

## Report a problem

Please **do not open a public issue** for anything that could expose keys or cause an unwanted order. Use GitHub's private reporting instead:
**Security tab > Report a vulnerability** on this repository.

Include what you did, what you expected, what happened, and your OS and Python version. Never include a real API key or secret in a report.

## What counts

- A way for text in a headline, filing, web page or journal note to trigger an order, a setting change or a key request.
- A way to place an order without the risk PASS, the typed yes and the click on Claude's permission card.
- Anything that prints, logs or commits an API key or secret.
- A way around the graduation check before real money.

## What does not

- Trading losses. This is education and tooling, not financial advice.
- Problems in the upstream projects (TradingAgents, Vibe-Trading, Day Trader skill). Report those to their own repositories.

## How keys are handled

Keys live only in environment variables. `scripts/doctor.py` reports whether they are set and never prints a value. The test suite scans the repo for key-shaped strings on every run.

Expect a first reply within a few days. This is a small project maintained by one person.
