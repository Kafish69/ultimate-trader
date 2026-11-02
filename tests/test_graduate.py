import contextlib
import io
import json
import os
import tempfile
import unittest

from _load import load

G = load("trader-graduate", "graduate")


def trades(n, win, loss, days=None, mode="paper"):
    out = []
    for k in range(n):
        d = "2026-10-%02d" % (1 + (k % (days or 20)))
        out.append({"date": d, "symbol": "TSLA", "pnl": win if k % 2 == 0 else -loss, "mode": mode})
    return out


class Math(unittest.TestCase):
    def test_pnl_includes_fees(self):
        t = G.make_trade("2026-10-19", "tsla", 2, 100, 105, 0.5, "x", "paper")
        self.assertEqual(t["pnl"], 9.5)
        self.assertEqual(t["symbol"], "TSLA")

    def test_bad_inputs_refused(self):
        for args in [("2026-10-19", "A", 0, 1, 1, 0, "", "paper"), ("2026-10-19", "A", 1, 1, 1, -1, "", "paper"),
                     ("19/10/2026", "A", 1, 1, 1, 0, "", "paper"), ("2026-10-19", "A", 1, 1, 1, 0, "", "demo")]:
            with self.assertRaises(G.GateError):
                G.make_trade(*args)

    def test_drawdown_and_streak(self):
        s = G.stats([{"date": "d", "pnl": p} for p in (5, -3, -4, 2)], 100)
        self.assertAlmostEqual(s["max_drawdown"], 7)
        self.assertEqual(s["longest_losing_streak"], 2)
        self.assertAlmostEqual(s["total"], 0)

    def test_profit_factor(self):
        s = G.stats([{"date": "d", "pnl": p} for p in (6, -2, -1)], 60)
        self.assertAlmostEqual(s["profit_factor"], 2.0)


class Gate(unittest.TestCase):
    def evalu(self, t, start=60):
        return G.evaluate(t, start, dict(G.DEFAULTS))

    def test_empty_is_not_yet(self):
        _, _, ok = self.evalu([])
        self.assertFalse(ok)

    def test_too_few_trades_fails_even_if_all_wins(self):
        _, checks, ok = self.evalu([{"date": "2026-10-%02d" % d, "pnl": 1} for d in range(1, 11)])
        self.assertFalse(ok)
        self.assertFalse(dict((n, p) for n, p, _ in checks)["Enough trades"])

    def test_good_record_graduates(self):
        _, _, ok = self.evalu(trades(60, 2.0, 1.0))
        self.assertTrue(ok)

    def test_losing_record_never_graduates(self):
        _, _, ok = self.evalu(trades(80, 1.0, 1.5))
        self.assertFalse(ok)

    def test_one_day_is_not_enough(self):
        _, checks, ok = self.evalu(trades(60, 2.0, 1.0, days=1))
        self.assertFalse(ok)
        self.assertFalse(dict((n, p) for n, p, _ in checks)["Enough different days"])

    def test_deep_drawdown_blocks(self):
        t = [{"date": "2026-10-%02d" % (1 + k % 15), "pnl": -1.0} for k in range(20)]
        t += [{"date": "2026-10-%02d" % (1 + k % 15), "pnl": 2.0} for k in range(40)]
        _, checks, ok = self.evalu(t, start=60)
        self.assertFalse(dict((n, p) for n, p, _ in checks)["Drawdown under control"])
        self.assertFalse(ok)


class Cli(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = G.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_log_then_check_writes_file_and_says_not_yet(self):
        with tempfile.TemporaryDirectory() as d:
            j, c, o = (os.path.join(d, x) for x in ("journal.jsonl", "config.json", "graduation.json"))
            with open(c, "w") as f:
                json.dump({"budget": 60}, f)
            code, _, _ = self.run_cli("log", "--symbol", "TSLA", "--qty", "1", "--entry", "10", "--exit", "11",
                                      "--date", "2026-10-19", "--journal", j)
            self.assertEqual(code, 0)
            code, out, _ = self.run_cli("check", "--journal", j, "--config", c, "--out", o)
            self.assertEqual(code, 1)
            self.assertIn("NOT YET", out)
            self.assertFalse(json.load(open(o))["graduated"])

    def test_live_trades_do_not_count(self):
        with tempfile.TemporaryDirectory() as d:
            j, c, o = (os.path.join(d, x) for x in ("journal.jsonl", "config.json", "graduation.json"))
            with open(c, "w") as f:
                json.dump({"budget": 60, "graduation": {"min_trades": 1, "min_days": 1}}, f)
            self.run_cli("log", "--symbol", "A", "--qty", "1", "--entry", "10", "--exit", "12",
                         "--date", "2026-10-19", "--mode", "live", "--journal", j)
            code, out, _ = self.run_cli("check", "--journal", j, "--config", c, "--out", o)
            self.assertEqual(code, 1)
            self.assertIn("0 closed paper trades", out)

    def test_missing_budget_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as d:
            code, _, err = self.run_cli("check", "--journal", os.path.join(d, "j"), "--config", os.path.join(d, "nope"),
                                        "--out", os.path.join(d, "o"))
            self.assertEqual(code, 2)
            self.assertIn("budget", err)

    def test_broken_journal_line_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            j = os.path.join(d, "j")
            with open(j, "w") as f:
                f.write("not json\n")
            code, _, err = self.run_cli("check", "--journal", j, "--budget", "60", "--out", os.path.join(d, "o"))
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
