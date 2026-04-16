# Codex Workflow

Before pushing, always run:

```bash
npx prettier . --check
```

This repository also has a `pre-push` git hook that runs the same command and blocks the push if the check fails.
