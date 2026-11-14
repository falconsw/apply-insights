---
name: apply
description: Apply your /insights report to CLAUDE.md, rule by rule.
when_to_use: The user wants to apply, act on or explain a Claude Code /insights report, or move its suggestions into CLAUDE.md, a skill or memory.
---

# /insights:apply

`/insights` writes an HTML report (`~/.claude/usage-data/report-*.html`) with friction points, CLAUDE.md
additions, features to try and prompts. This skill turns it into something the user can read in a minute and act
on by typing a few numbers. The report is a model's guess from session logs: check each suggestion against what the
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

- `no_report`: tell the user to type `/insights` (only they can run it), then `/insights:apply` again. Stop.
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

## 3. Show it: one flat numbered list, one rule per line

No bundles. Every single thing that can be written gets its own number and its own line, with its target in
brackets in front. Don't show the report's codes (K1, F2 …), don't group by report section, don't merge two
suggestions into one line. No raw dumps, no marketing tone.

```
Report: <date> · <n> sessions analyzed (<total> total) · <first day> – <last day>
In short: <what works, one line>. <what gets in the way, one line>.

Can be added (nothing is written until you pick)
 1. [CLAUDE.md]         Everything runs locally on my Mac: run commands, or give ready-to-run ones.
 2. [CLAUDE.md]         Local databases are MySQL containers in OrbStack, not Cloud SQL.
 3. [promo-video skill] Offer 3 angles before a full script.
 4. [linkedin memory]   Check eval is on in the extension before starting.
 5. [new skill]         /linkedin: one command with the eval check, pacing and save check.
 6. [hook]              Run the tests after every edit (can slow down big repos).

Not offered
 – already written: <rule, short> (<file>)
 – conflicts with your rule: "<report's rule>" vs "<their rule>" (<file>)
 – not confirmed: <rule> (<why>)
 – ideas only: <title>, <title>

Type the numbers to add: e.g. `1 3 5`, `all`, `all except 4`, or `none`.
```

- The text after the bracket is the exact line that will be written (in the target file's language and style);
  for a new skill or hook it is one line saying what it does.
- Order: CLAUDE.md lines first, then skills, memory, new skills, hooks. Keep each line to one row where possible.
- Targets in brackets are short names; give the full paths once under the list if they are not obvious.
- "Not offered" lines have no number and cannot be picked. A conflicting rule is applied only if the user asks
  for it in words.

## 4. Let the user pick

End the message with the "Type the numbers" line and stop. Do not use AskUserQuestion. Read the reply as a
selection: numbers in any form (`1 3 5`, `1,3,5`, `1-4`), `all`, `all except …`, `none`. If the reply is unclear,
ask once in one line. Nothing offerable: say so and stop.

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

A short list by number: what went where (path:line), what was skipped and why, backup paths. Close with
one line: run `/insights` again in a couple of weeks to see whether those frictions went down.
