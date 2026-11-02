"""Contract tests for the router skill and the repo's safety promises.

These check the written rules and the shipped config. They cannot test what a model
does with the rules. They stop the rules from being deleted or weakened by accident.
"""
import glob
import json
import os
import re
import unittest

from _load import REPO, ROOT


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


ROUTER = read(ROOT, "ultimate-trader", "SKILL.md")
TRADER_SKILLS = sorted(d for d in os.listdir(ROOT) if d.startswith("trader-"))


class RouterRules(unittest.TestCase):
    def test_no_order_without_an_explicit_yes(self):
        self.assertRegex(ROUTER, r"(?i)no order without an explicit yes")

    def test_orders_only_via_broker_after_risk_pass(self):
        self.assertIn("/trader-broker", ROUTER)
        self.assertRegex(ROUTER, r"(?i)only\s+`/trader-broker`\s+may\s+lead\s+to\s+an\s+order")
        self.assertIn("/trader-risk", ROUTER)

    def test_paper_by_default_and_tool_output_cannot_authorize(self):
        self.assertRegex(ROUTER, r"(?i)paper account by default")
        self.assertRegex(ROUTER, r"(?i)because a tool output, file or web page told you to")

    def test_keys_never_in_chat(self):
        self.assertRegex(ROUTER, r"(?i)keys never go in chat")

    def test_live_requires_graduation(self):
        self.assertIn("trader-graduate", ROUTER)
        self.assertRegex(ROUTER, r"(?i)never skip the graduation gate")

    def test_every_trader_skill_is_reachable_from_the_router(self):
        for name in TRADER_SKILLS:
            self.assertIn(name, ROUTER, "%s is not mentioned in the router" % name)

    def test_news_and_files_are_data_not_instructions(self):
        text = ROUTER + read(ROOT, "trader-broker", "SKILL.md")
        self.assertRegex(text, r"(?i)(data, not (instructions|commands)|never (authorize|an instruction))")


class BrokerAndConfig(unittest.TestCase):
    def test_broker_requires_needs_approval(self):
        self.assertRegex(read(ROOT, "trader-broker", "SKILL.md"), r"Needs approval")

    def test_example_config_is_paper_with_tight_limits(self):
        cfg = json.loads(read(REPO, "config.example.json"))
        self.assertIs(cfg["paper"], True)
        self.assertLessEqual(cfg["max_loss_per_trade_usd"], 0.05 * cfg["budget"])
        self.assertIn("graduation", cfg)

    def test_example_broker_config_uses_a_placeholder_key(self):
        text = read(ROOT, "trader-broker", "claude_desktop_config.example.json")
        self.assertIn("YOUR_PAPER_API_KEY", text)
        self.assertIn("paper", text.lower())


class NoSecrets(unittest.TestCase):
    PATTERNS = [r"\bPK[A-Z0-9]{18,}\b", r"\bsk-ant-[A-Za-z0-9_-]{20,}", r"\bsk-[A-Za-z0-9]{32,}",
                r"\bghp_[A-Za-z0-9]{30,}", r"\bgithub_pat_[A-Za-z0-9_]{30,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]

    def test_repo_has_no_key_shaped_strings(self):
        bad = []
        for path in glob.glob(os.path.join(REPO, "**", "*"), recursive=True):
            if not os.path.isfile(path) or os.sep + ".git" + os.sep in path or "fixtures" in path:
                continue
            try:
                text = read(path)
            except (UnicodeDecodeError, OSError):
                continue
            for pat in self.PATTERNS:
                if re.search(pat, text):
                    bad.append((os.path.relpath(path, REPO), pat))
        self.assertEqual(bad, [])

    def test_gitignore_keeps_keys_and_trader_data_out(self):
        text = read(REPO, ".gitignore")
        for entry in (".env", "trader/"):
            self.assertIn(entry, text)


if __name__ == "__main__":
    unittest.main()
