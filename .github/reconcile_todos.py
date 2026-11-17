import os, re, sys

ROOT = os.environ["GITHUB_WORKSPACE"]
os.chdir(ROOT)

CHANGED = [
    "luffy/deepscaler/utils.py",
    "luffy/verl/verl/protocol.py",
]
ITEM_RE = re.compile(r"^- \[ \] \*\*(.+?):(\d+)\*\* - (.*)$")

def transform(raw):
    s = raw.strip()
    m = re.match(r"^#\s*TODO\s*(.*)$", s, flags=re.I)
    if not m:
        return s
    rest = m.group(1).strip()
    if rest.startswith("("):
        return rest.strip()
    rest = re.sub(r"^:\s*", "", rest)
    return rest.strip()

def scan(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh.read().splitlines(), 1):
            if "TODO" in line:
                out.append((i, transform(line)))
    return out

with open("README.md", encoding="utf-8") as fh:
    readme = fh.read()
lines = readme.split("\n")

records = []
for idx, line in enumerate(lines):
    m = ITEM_RE.match(line)
    if m:
        records.append((idx, m.group(1), int(m.group(2)), m.group(3), line))

first_gi = records[0][0]
last_gi = records[-1][0]

baseline = {}
for idx, path, line, desc, raw in records:
    baseline.setdefault(path, []).append((line, desc))

new_groups = []
summary_removed = []
summary_moved = []
summary_added = []
for path in CHANGED:
    current = scan(path)
    cur_desc = [d for _, d in current]
    base = baseline.get(path, [])
    base_map = {}
    for ln, d in base:
        base_map[d] = ln
    cur_set = set(cur_desc)
    for ln, d in base:
        if d not in cur_set:
            summary_removed.append((path, ln, d))
    for newline, d in current:
        if d in base_map:
            oldline = base_map[d]
            summary_moved.append((path, oldline, newline, d))
        else:
            summary_added.append((path, newline, d))
        new_groups.append((path, newline, d))

kept = [(p, ln, d) for _, p, ln, d, _ in records if p not in CHANGED]
final = sorted(kept + new_groups, key=lambda t: (t[0], t[1]))
new_block = ["- [ ] **%s:%d** - %s" % rec for rec in final]
new_lines = lines[:first_gi] + new_block + lines[last_gi + 1:]
new_readme = "\n".join(new_lines)

print("REMOVED", len(summary_removed))
for p, ln, d in summary_removed:
    print("R|%s|%d|%s" % (p, ln, d))
print("MOVED", len(summary_moved))
for p, old, new, d in summary_moved:
    print("M|%s|%d->%d|%s" % (p, old, new, d))
print("ADDED", len(summary_added))
for p, ln, d in summary_added:
    print("A|%s|%d|%s" % (p, ln, d))
print("FINAL_TOTAL", len(final))

if new_readme != readme:
    with open("README.md", "w", encoding="utf-8") as fh:
        fh.write(new_readme)
    print("README_CHANGED yes")
else:
    print("README_CHANGED no")
