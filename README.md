# apply-insights

A Claude Code skill that turns the `/insights` usage report into a short plain-English summary, checks each
suggestion against your existing CLAUDE.md, memory and skills, and applies the ones you pick.

```bash
ln -sfn "$PWD/skill" ~/.claude/skills/apply-insights
```

Then in Claude Code: `/insights`, followed by `/apply-insights`.
