#!/usr/bin/env python3
"""Fail if any skills/*/SKILL.md lacks name + description frontmatter or its name differs from its folder."""
import os
import re
import sys

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")
bad = 0
for d in sorted(os.listdir(root)):
    p = os.path.join(root, d, "SKILL.md")
    if not os.path.isfile(p):
        continue
    text = open(p, encoding="utf-8").read()
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        print("no frontmatter:", d); bad += 1; continue
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    if not name or name.group(1).strip() != d:
        print("name mismatch:", d); bad += 1
    if not re.search(r"^description:", fm, re.M):
        print("no description:", d); bad += 1
print("skills checked, problems:", bad)
sys.exit(1 if bad else 0)
