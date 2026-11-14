---
name: apply-insights
description: Turn the latest Claude Code /insights report into a short, plain-English summary and apply the suggestions the user picks to CLAUDE.md, the right skill or memory — checked against the rules they already have, never duplicated. Use when the user types /apply-insights, asks to apply / act on / explain an /insights report, or wants its suggestions moved into CLAUDE.md.
---

# apply-insights

`/insights` writes an HTML report (`~/.claude/usage-data/report-*.html`) with friction points, CLAUDE.md
additions, features to try and prompts. This skill turns it into something the user can read in a minute and act
on with a few clicks. The report is a model's guess from session logs: check each suggestion against what the
user already decided before offering it.

Write everything for the user in English (summary, labels, questions), whatever language the conversation is in.
Text added to a file follows that file's existing language and style.

## 1. Read the report

```bash
python3 -I <this skill's base directory>/parse_report.py   # newest report; or pass a path
```

It prints JSON: `date`, `subtitle` (sessions / messages / date range), `glance` (4 summary paragraphs),
`friction` (S1…), `claude_md` (K1…, each a block of rules + `why`), `features` (F1…, with example code),
`patterns` (H1…, habits with a copyable prompt), `horizon` (I1…).

- `no_report`: tell the user to type `/insights` (only they can run it), then `/apply-insights` again. Stop.
- Report older than 7 days: say so in one line and continue; offer a fresh `/insights` at the end.

## 2. Check every suggestion against what already exists

Read only what you need, cheaply (grep before opening whole files):

- `~/.claude/CLAUDE.md`, the project's `CLAUDE.md` / `AGENTS.md` (if in a repo)
- the auto-memory index (`MEMORY.md`) and the memory files it points to that match a suggestion's topic
- skills the suggestion is really about (`~/.claude/skills/*/SKILL.md`: grep for the topic), and hooks in
  `~/.claude/settings.json` when a hook is suggested

Split each K block into its single rules (bullets) and give each a status:

| Status | Meaning | Offer it? |
|---|---|---|
| new | not written anywhere | yes |
| partly there | the idea exists but this detail is missing | only the missing part |
| already there | already a rule; name the file (and line) | no |
| conflicts | contradicts a rule the user set (quote both) | only if the user picks it explicitly; default is to keep theirs |
| unsupported | the report's inference is wrong or can't be confirmed (cheap check: memory, git log, the file) | no; mention it |

Pick the best home for each rule and say why in a few words:

- **Global `~/.claude/CLAUDE.md`**: applies to every session and project (ways of working, environment facts).
- **Project `CLAUDE.md`**: true only in this repo.
- **A skill's `SKILL.md`**: rules for one workflow (video, puzzles, publishing). Prefer this for
  workflow-specific rules: CLAUDE.md loads into every session, so keep it lean. If the skill is a symlink into a
  git repo, edit the repo copy.
- **A memory file**: a preference or lesson the user stated, per the memory instructions in the system prompt.

F items: check whether that skill / hook already exists. H items: a habit becomes either a one-line rule or a
small skill — say which fits. I items are ideas, not rules: list them, apply nothing.

## 3. Show it: one list of changes, grouped by file

The user must see exactly what will be written where. Don't show the report's codes (K1, F2, H3 …) and don't
group by report section: turn everything offerable into numbered **changes**, one per target file (a new skill
or hook is its own change). No raw dumps, no marketing tone, no headings for empty groups.

```
Report: <date> · <n> sessions analyzed (<total> total) · <first day> – <last day>
In short: <what works, one line>. <what gets in the way, one line>.

Changes I can make (nothing is written until you pick)

1. ~/.claude/CLAUDE.md: add 5 lines under a new "## Environment & ways of working" section
   + Everything runs locally on my Mac: run commands, or give ready-to-run ones.
   + …
   Why: <the friction it fixes, one line with the report's example>

2. promo-video skill (<real path>/SKILL.md): add 3 lines to "<existing heading>"
   + …
   Why: …

3. New skill /linkedin (~/.claude/skills/linkedin/SKILL.md): <what it does, one line>
   Why: …

Not added
- Already written: <rule, short> (<file>), …
- Conflicts with your rule: "<report's rule>" vs "<their rule>" (<file>). Pick it only to replace yours.
- Not confirmed: <rule> (<why>)
- Ideas only: <title>, <title>
```

- `+` lines are the exact text that will be written, in the target file's language and style.
- A change to a file that is not CLAUDE.md says why it goes there ("only used when making videos").
- A conflicting rule is never a numbered change unless the user asks for it after reading "Not added".

## 4. Let the user pick

AskUserQuestion with `multiSelect: true`, question "Which changes should I write?", header "Changes". One option
per numbered change, same number and file in the label ("1. CLAUDE.md +5 lines", "2. promo-video skill +3
lines", "3. New /linkedin skill"); the description repeats in a few words what those lines say. At most 4 options
per question; with more changes, split into a second question ("Which of changes 5–8 …"). Nothing offerable: say
so and stop.

## 5. Apply what was picked

- Before the first change to a file, back it up once: `cp <file> <file>.bak-insights-<YYYYMMDD>` (skip if it
  exists).
- Add rules under a matching existing heading; otherwise append one `## <heading>` section. Short imperative
  bullets, same language and tone as the file. Never duplicate a line that is already there.
- Skills (F): write `SKILL.md` only after showing its text. Hooks: load the `update-config` skill and follow it.
  Cron / headless jobs: show the exact command; install only on an explicit yes.
- Memory: follow the memory instructions (one fact per file + index line).
- Never touch files the user did not pick; never commit or push unless asked.

## 6. Report back

A short list by change number: what went where (path:line), what was skipped and why, backup paths. Close with
one line: run `/insights` again in a couple of weeks to see whether those frictions went down.
