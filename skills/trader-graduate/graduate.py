#!/usr/bin/env python3
"""Graduation gate: decide, from your own closed paper trades, whether going live is justified.

Two commands:
  log    append one closed trade to trader/journal.jsonl
  check  read the journal, test it against fixed criteria, print GRADUATED or NOT YET
         and write trader/graduation.json

The criteria are fixed before you look at results. Standard library only.
Education and tooling, not financial advice.
"""
import argparse
import datetime
import json
import math
import os
import sys

DEFAULTS = {"min_trades": 50, "min_days": 10, "min_profit_factor": 1.2, "max_drawdown_pct": 20.0}


class GateError(Exception):
    pass


def read_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, doc):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")


def read_journal(path):
    trades = []
    if not os.path.isfile(path):
        return trades
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                t = json.loads(line)
            except ValueError:
                raise GateError("%s line %d is not valid JSON" % (path, n))
            if not isinstance(t, dict) or not isinstance(t.get("pnl"), (int, float)) or not t.get("date"):
                raise GateError("%s line %d needs a date and a numeric pnl" % (path, n))
            trades.append(t)
    return trades


def make_trade(date, symbol, qty, entry, exit_, fees, why, mode):
    if qty <= 0 or entry <= 0 or exit_ <= 0:
        raise GateError("qty, entry and exit must all be above zero")
    if fees < 0:
        raise GateError("fees cannot be negative")
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise GateError("--date wants a date like 2026-10-19")
    if mode not in ("paper", "live"):
        raise GateError("--mode is paper or live")
    pnl = round(qty * (exit_ - entry) - fees, 4)
    return {"date": date, "symbol": symbol.upper(), "qty": qty, "entry": entry, "exit": exit_,
            "fees": fees, "pnl": pnl, "mode": mode, "why": why}


def stats(trades, start):
    pnls = [float(t["pnl"]) for t in trades]
    n = len(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    gross_win, gross_loss = sum(wins), -sum(losses)
    equity, peak, dd, dd_pct, streak, worst = start, start, 0.0, 0.0, 0, 0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        if peak - equity > dd:
            dd = peak - equity
            dd_pct = dd / peak * 100 if peak > 0 else 100.0
        streak = streak + 1 if p < 0 else 0
        worst = max(worst, streak)
    if gross_loss > 0:
        pf = gross_win / gross_loss
    else:
        pf = math.inf if gross_win > 0 else 0.0
    return {"trades": n, "days": len({t["date"] for t in trades}), "wins": len(wins), "losses": len(losses),
            "win_rate": (len(wins) / n * 100) if n else 0.0, "total": sum(pnls),
            "expectancy": (sum(pnls) / n) if n else 0.0,
            "avg_win": (gross_win / len(wins)) if wins else 0.0,
            "avg_loss": (-gross_loss / len(losses)) if losses else 0.0,
            "profit_factor": pf, "max_drawdown": dd, "max_drawdown_pct": dd_pct,
            "longest_losing_streak": worst, "end_equity": equity}


def evaluate(trades, start, rules):
    s = stats(trades, start)
    pf_text = "no losing trades yet" if math.isinf(s["profit_factor"]) else "%.2f" % s["profit_factor"]
    checks = [
        ("Enough trades", s["trades"] >= rules["min_trades"],
         "%d closed paper trades, need %d. Fewer than that is an anecdote, not a result." % (s["trades"], rules["min_trades"])),
        ("Enough different days", s["days"] >= rules["min_days"],
         "%d trading days, need %d. One lucky week proves nothing." % (s["days"], rules["min_days"])),
        ("Positive after fees", s["total"] > 0 and s["expectancy"] > 0,
         "total %+.2f, average per trade %+.4f, all after fees." % (s["total"], s["expectancy"])),
        ("Wins beat losses", s["profit_factor"] >= rules["min_profit_factor"],
         "profit factor %s, need at least %.2f." % (pf_text, rules["min_profit_factor"])),
        ("Drawdown under control", s["max_drawdown_pct"] <= rules["max_drawdown_pct"],
         "worst fall from a peak was %.1f%% (%.2f), limit %.1f%%." % (s["max_drawdown_pct"], s["max_drawdown"], rules["max_drawdown_pct"])),
    ]
    return s, checks, all(ok for _, ok, _ in checks)


def money(v):
    return "%s$%.2f" % ("-" if v < 0 else "", abs(v))


def cmd_log(a):
    t = make_trade(a.date or datetime.date.today().isoformat(), a.symbol, a.qty, a.entry, a.exit,
                   a.fees, a.why or "", a.mode)
    folder = os.path.dirname(a.journal)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(a.journal, "a", encoding="utf-8") as f:
        f.write(json.dumps(t) + "\n")
    print("Logged %s %s: %s %s" % (t["symbol"], t["mode"], "profit" if t["pnl"] > 0 else "loss", money(abs(t["pnl"]))))
    return 0


def cmd_check(a):
    cfg = read_json(a.config) or {}
    start = a.budget if a.budget else cfg.get("budget")
    if not start or float(start) <= 0:
        raise GateError("no starting budget: set \"budget\" in %s or pass --budget" % a.config)
    rules = dict(DEFAULTS)
    rules.update(cfg.get("graduation", {}) or {})
    trades = [t for t in read_journal(a.journal) if t.get("mode", "paper") == "paper"]
    s, checks, ok = evaluate(trades, float(start), rules)
    out = {"graduated": ok, "checked_on": datetime.date.today().isoformat(), "rules": rules,
           "stats": {k: (None if isinstance(v, float) and math.isinf(v) else v) for k, v in s.items()},
           "checks": [{"name": n, "pass": p, "detail": d} for n, p, d in checks]}
    write_json(a.out, out)
    if a.json:
        print(json.dumps(out, indent=2))
        return 0 if ok else 1
    print("Graduation check on %d closed paper trades (start %s):" % (s["trades"], money(float(start))))
    for n, p, d in checks:
        print("  %-24s %s  %s" % (n, "PASS" if p else "FAIL", d))
    print("  Win rate %.0f%%, average win %s, average loss %s, longest losing streak %d."
          % (s["win_rate"], money(s["avg_win"]), money(s["avg_loss"]), s["longest_losing_streak"]))
    if ok:
        print("\nGRADUATED. Going live is now a reasonable choice, never a certainty. Start with an amount you can lose.")
    else:
        print("\nNOT YET. Keep paper trading. Do not set paper to false, and do not move an order to a live account.")
    print("Written to %s. Education and tooling, not financial advice." % a.out)
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log", help="append one closed trade")
    lg.add_argument("--symbol", required=True)
    lg.add_argument("--qty", type=float, required=True)
    lg.add_argument("--entry", type=float, required=True)
    lg.add_argument("--exit", type=float, required=True)
    lg.add_argument("--fees", type=float, default=0.0)
    lg.add_argument("--date")
    lg.add_argument("--why", help="why you took it, in a few words")
    lg.add_argument("--mode", default="paper")
    lg.add_argument("--journal", default="trader/journal.jsonl")
    ck = sub.add_parser("check", help="test the journal against the graduation criteria")
    ck.add_argument("--journal", default="trader/journal.jsonl")
    ck.add_argument("--config", default="trader/config.json")
    ck.add_argument("--budget", type=float)
    ck.add_argument("--out", default="trader/graduation.json")
    ck.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        return cmd_log(a) if a.cmd == "log" else cmd_check(a)
    except GateError as e:
        print("graduate: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
