import os, base64

root = os.environ.get("GITHUB_WORKSPACE", ".")
py_files = []
for dp, dn, fns in os.walk(root):
    if ".git" in dn:
        dn.remove(".git")
    rel_dir = os.path.relpath(dp, root)
    if rel_dir != "." and rel_dir.split(os.sep)[0] == ".github":
        continue
    for f in fns:
        if f.endswith(".py"):
            p = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")
            if p.startswith(".github/"):
                continue
            py_files.append(p)
py_files.sort()

print("@@COUNTS")
total = 0
all_hits = []
for p in py_files:
    with open(os.path.join(root, p), encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    hits = [(i + 1, line) for i, line in enumerate(lines) if "TODO" in line]
    if hits:
        print("C|%s|%d" % (p, len(hits)))
        total += len(hits)
        for lineno, line in hits:
            all_hits.append((p, lineno, line))
print("CTOTAL|%d" % total)

print("@@ITEMS")
for p, lineno, line in all_hits:
    enc = base64.b64encode(line.encode("utf-8")).decode("ascii")
    print("I|%s|%d|%s" % (p, lineno, enc))

print("@@README")
with open(os.path.join(root, "README.md"), "rb") as fh:
    data = fh.read()
b = base64.b64encode(data).decode("ascii")
for i in range(0, len(b), 700):
    print("R|" + b[i:i + 700])
print("@@END")
