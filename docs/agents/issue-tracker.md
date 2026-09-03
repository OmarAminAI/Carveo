# Issue tracker: GitHub

Issues and specifications live in GitHub Issues for `OmarAminAI/Carveo`.
Use the `gh` CLI from this repository for all operations.

## Conventions

- Create: `gh issue create --title "..." --body "..."`
- Read: `gh issue view <number> --comments`
- List: `gh issue list --state open`
- Comment: `gh issue comment <number> --body "..."`
- Label: `gh issue edit <number> --add-label "..."`
- Close: `gh issue close <number> --comment "..."`
- Infer the repository from the configured Git remote.
- Pull requests are not a triage request surface.

When a skill says to publish something to the issue tracker, create a GitHub issue.
When a skill requests the relevant ticket, retrieve the issue and its comments.
