#!/usr/bin/env python3
"""data/inbox.jsonl (written by Brain Home: done, keep, drop, still on, a new task) -> commitments.md. Then empties the file."""
import json, os, re, sys, subprocess, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "data", "inbox.jsonl")
if not os.path.exists(P): raise SystemExit("no inbox")
lines = [l for l in open(P).read().splitlines() if l.strip()]
if not lines: raise SystemExit("inbox empty")
today = datetime.date.today().isoformat()
cm = open(os.path.join(R, "commitments.md")).read()
raw_path = os.path.join(R, "raw", f"{today}.md")
done = reopened = thoughts = kept = dropped = moved = fortunes = added = deleted = 0
cell = lambda v: re.sub(r"\s+", " ", (v or "").replace("|", "/")).strip()
PAGE = re.compile(r"(wiki/[a-z0-9-]+\.md|projects/[a-z0-9-]+/README\.md)")
def page_title(rel):
    try: m = re.search(r"^# (.+)$", open(os.path.join(R, rel), errors="replace").read(), re.M)
    except OSError: return None
    return cell(m.group(1)).replace("[", "(").replace("]", ")") if m else rel.split("/")[-2 if rel.endswith("README.md") else -1].removesuffix(".md")
for l in lines:
    try: e = json.loads(l)
    except Exception: continue
    t = e.get("t"); ts = (e.get("at") or "")[11:16] or datetime.datetime.now().strftime("%H:%M")
    # a row deleted from Brain Home (right click): the line and its ## Details note go, git keeps them
    if t == "delete" and re.fullmatch(r"c[0-9a-f]{7}", e.get("id", "")):
        n = len(cm)
        cm = re.sub(rf"^\| {e['id']} \|.*\n?", "", cm, flags=re.M)
        cm = re.sub(rf"^### {e['id']}\b.*?(?=^### |^## |\Z)", "", cm, flags=re.M | re.S)
        if len(cm) != n: deleted += 1
        continue
    if t in ("done", "reopen", "keep", "drop", "due") and re.fullmatch(r"c[0-9a-f]{7}", e.get("id", "")):
        m = re.search(rf"^\| {e['id']} \|.*$", cm, re.M)
        if not m: continue
        c = [x.strip() for x in m.group(0).strip().strip("|").split("|")]
        via = e.get('via') or 'Brain Home'
        if t == "done":
            c[6] = "done"; c[7] = c[7] + f", done {today} via {via}"; done += 1
        # Brain Home's review: a row Brain filed, checked by you. Kept stays as it is, marked so the
        # queue lets it go; dropped was never a promise, it leaves the open list
        elif t == "keep":
            if "kept " not in c[7]: c[7] = c[7] + f", kept {today}"
            kept += 1
        # Brain Home's sweep, "still on": the promise stands, with a new date
        elif t == "due" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", e.get("date", "")):
            c[5] = e["date"]; c[6] = "open"; c[7] = c[7] + f", moved to {e['date']} on {today} via {via}"; moved += 1
        elif t == "drop":
            c[6] = "dropped"; c[7] = c[7] + f", dropped {today} via {via}"; dropped += 1
        else:
            c[6] = "open"; reopened += 1
        cm = cm.replace(m.group(0), "| " + " | ".join(c) + " |")
    # a new task from Brain Home's form: one row at the end of the table, its links in Source,
    # its description under ## Details at the bottom, keyed by the id
    elif t == "add" and re.fullmatch(r"c[0-9a-f]{7}", e.get("id", "")) and cell(e.get("what")):
        # the page made the id: the same row twice is skipped, a clash with another row gets a new id
        if re.search(rf"^\| {e['id']} \|[^|]*\|[^|]*\|[^|]*\| {re.escape(cell(e['what']))} \|", cm, re.M): continue
        while re.search(rf"^\| {e['id']} \|", cm, re.M): e["id"] = "c" + os.urandom(4).hex()[:7]
        due = e.get("due", "") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", e.get("due", "")) else ""
        links = []
        for rel in dict.fromkeys(x.strip() for x in e.get("links", "").split(",")):
            title = page_title(rel) if PAGE.fullmatch(rel) else None
            if title: links.append(f"[{title}]({rel})")
        src = f"added {today} via {e.get('via') or 'Brain Home'}" + (", re: " + ", ".join(links) if links else "")
        row = f"| {e['id']} | {today} | {cell(e.get('owes')) or 'Me'} | {cell(e.get('to')) or '-'} | {cell(e['what'])} | {due} | open | {src} |"
        last = list(re.finditer(r"^\| c[0-9a-f]{7} \|.*$", cm, re.M))
        cm = cm[:last[-1].end()] + "\n" + row + cm[last[-1].end():] if last else cm.rstrip("\n") + "\n" + row + "\n"
        desc = "\n".join(l.rstrip() for l in (e.get("desc") or "").strip().replace("|", "/").splitlines())
        if desc:
            if not re.search(r"^## Details$", cm, re.M):
                cm = cm.rstrip("\n") + "\n\n## Details\n\nLonger notes on a row, under its ID. Brain Home writes these when a task is made.\n"
            cm = cm.rstrip("\n") + f"\n\n### {e['id']}: {cell(e['what'])}\n\n{desc}\n"
        added += 1
    # fortune verdicts from Brain Home: good, noise, seen, open on an f-id
    elif t in ("good", "noise", "seen", "open") and re.fullmatch(r"f[0-9a-f]{7}", e.get("id", "")):
        r = subprocess.run([sys.executable, os.path.join(R, "tools", "fortune.py"), "feedback", t, e["id"], e.get("note", "")],
                           capture_output=True, text=True)
        if r.returncode == 0: fortunes += 1
    elif t == "watch" and e.get("text", "").strip():
        subprocess.run([sys.executable, os.path.join(R, "tools", "fortune.py"), "watch", e.get("op", "add"), e["text"].strip()], capture_output=True)
        fortunes += 1
    elif t in ("brain", "answer"):
        text = e.get("text", "").strip()
        if t == "answer": text = f"answer to the brief question: {e.get('q','').strip()}\n{text}"
        if not text: continue
        new = not os.path.exists(raw_path)
        with open(raw_path, "a") as f:
            if new: f.write(f"# {today}\n\n")
            f.write(f"## {ts}\n\n{text}\n\n")
        thoughts += 1
open(os.path.join(R, "commitments.md"), "w").write(cm)
open(P, "w").write("")
print(f"inbox: {added} added, {done} done, {reopened} reopened, {kept} kept, {dropped} dropped, {moved} moved, {thoughts} thoughts, {fortunes} fortune, {deleted} deleted")
