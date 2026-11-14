#!/usr/bin/env python3
"""Parse a Claude Code /insights HTML report into structured JSON.

Usage: parse_report.py [report.html]   (default: newest ~/.claude/usage-data/report-*.html)
"""
import glob, html, json, os, re, sys

DATA = os.path.expanduser("~/.claude/usage-data")


def newest_report():
    files = sorted(glob.glob(os.path.join(DATA, "report-*.html")))
    if files:
        return files[-1]
    plain = os.path.join(DATA, "report.html")
    return plain if os.path.exists(plain) else None


def text(fragment):
    fragment = re.sub(r"<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"</(li|p)>", "\n", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(fragment).strip()


def field(chunk, cls):
    m = re.search(r'class="%s"[^>]*>(.*?)</(div|code|p|ul|span|pre)>' % re.escape(cls), chunk, re.S)
    return text(m.group(1)) if m else ""


def fields(chunk, cls):
    return [text(m.group(1)) for m in re.finditer(r'class="%s"[^>]*>(.*?)</(div|code|p|ul|span|pre)>' % re.escape(cls), chunk, re.S)]


def prompt(chunk):
    m = re.search(r'class="(?:copyable-prompt|pattern-prompt)"[^>]*>.*?<code[^>]*>(.*?)</code>', chunk, re.S)
    return text(m.group(1)) if m else field(chunk, "copyable-prompt")


def cards(doc, cls):
    starts = [m.start() for m in re.finditer(r'class="%s"' % re.escape(cls), doc)]
    out = []
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else doc.find("<h2", s)
        out.append(doc[s:end if end > 0 else len(doc)])
    return out


def section(doc, sid):
    s = doc.find('id="%s"' % sid)
    if s < 0:
        return ""
    e = doc.find("<h2", s + 10)
    return doc[s:e if e > 0 else len(doc)]


def parse(path):
    doc = open(path, encoding="utf-8").read()
    m = re.search(r"report-(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    out = {
        "report": path,
        "date": m.group(1) if m else None,
        "subtitle": field(doc, "subtitle"),
        "glance": [text(g) for g in re.findall(r'class="glance-section"[^>]*>(.*?)</div>', doc, re.S)],
        "friction": [],
        "claude_md": [],
        "features": [],
        "patterns": [],
        "horizon": [],
    }
    for i, c in enumerate(cards(doc, "friction-category"), 1):
        out["friction"].append({"id": "S%d" % i, "title": field(c, "friction-title"),
                                "desc": field(c, "friction-desc"), "examples": field(c, "friction-examples")})
    for i, c in enumerate(cards(doc, "claude-md-item"), 1):
        dt = re.search(r'data-text="(.*?)"\s*>', c, re.S)
        body = html.unescape(dt.group(1)) if dt else field(c, "cmd-code")
        body = re.sub(r"^Add to CLAUDE\.md(\\n|\n)+", "", body).strip()
        out["claude_md"].append({"id": "K%d" % i, "text": body, "why": field(c, "cmd-why")})
    for i, c in enumerate(cards(doc, "feature-card"), 1):
        out["features"].append({"id": "F%d" % i, "title": field(c, "feature-title"), "oneliner": field(c, "feature-oneliner"),
                                "why": re.sub(r"^Why for you:\s*", "", field(c, "feature-why")), "examples": fields(c, "example-code")})
    for i, c in enumerate(cards(doc, "pattern-card"), 1):
        out["patterns"].append({"id": "H%d" % i, "title": field(c, "pattern-title"), "summary": field(c, "pattern-summary"),
                                "detail": field(c, "pattern-detail"), "prompt": prompt(c)})
    for i, c in enumerate(cards(doc, "horizon-card"), 1):
        out["horizon"].append({"id": "I%d" % i, "title": field(c, "horizon-title"), "possible": field(c, "horizon-possible"),
                               "tip": re.sub(r"^Getting started:\s*", "", field(c, "horizon-tip")), "prompt": prompt(c)})
    return out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else newest_report()
    if not path or not os.path.exists(path):
        print(json.dumps({"error": "no_report", "hint": "Run /insights first; it writes ~/.claude/usage-data/report-*.html"}))
        sys.exit(1)
    print(json.dumps(parse(path), ensure_ascii=False, indent=1))
