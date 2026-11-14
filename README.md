# apply-insights

A Claude Code plugin for the `/insights` report.

`/insights` reads your Claude Code sessions and writes an HTML report: where you get stuck, lines to add to
CLAUDE.md, features to try. The report is long, in one place, and some of its suggestions don't fit you or are
already in your setup.

`/insights:apply` reads the latest report and:

1. Sums it up in a few plain lines: what works, where you get stuck.
2. Checks every suggested rule against the CLAUDE.md, memory and skills you already have, and labels it
   **new**, **partly there**, **already there** (with the file), **conflicts** (with your own rule, quoted) or
   **unsupported**.
3. Suggests the right home for each rule: global `~/.claude/CLAUDE.md`, the project's `CLAUDE.md`, the skill
   it belongs to, or memory.
4. Shows one flat numbered list, one rule per line with its target file; you type the numbers you want
   (`1 3 5`, `all`, `all except 4`).
5. Backs the file up and writes only what you picked, without duplicate lines. Conflicting rules are never
   applied unless you choose them.

## Install

In Claude Code:

```
/plugin install insights --marketplace falconsw/apply-insights
```

On Claude Code older than 2.1.275, add the marketplace first:

```
/plugin marketplace add falconsw/apply-insights
/plugin install insights@apply-insights
```

## Use

1. Type `/insights` and wait for the report (only you can run it).
2. Type `/insights:apply`.

Run `/insights` again after a couple of weeks to see whether the same frictions show up.

## Requirements

Python 3 (standard library only), used to read the report.

## License

MIT
