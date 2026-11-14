# apply-insights

A Claude Code skill for the `/insights` report.

`/insights` reads your Claude Code sessions and writes an HTML report: where you get stuck, lines to add to
CLAUDE.md, features to try. `/apply-insights` turns that report into a short plain-English summary, checks every
suggestion against the CLAUDE.md, memory and skills you already have (new / partly there / already there /
conflicts / unsupported), lets you pick with a few clicks, and writes only what you picked — after backing the
file up, without duplicating lines.

## Install

```bash
git clone https://github.com/falconsw/apply-insights.git
ln -sfn "$PWD/apply-insights/skill" ~/.claude/skills/apply-insights
```

Restart Claude Code if the skill doesn't show up.

## Use

1. In Claude Code, type `/insights` and wait for the report.
2. Type `/apply-insights`.

Needs Python 3 (standard library only) to parse the report.
