# Team Workflow Documentation

## Branching Strategy
- **Main branch**: Holds releasable code only.
- **Feature branches**: Follow the `feature/[description]` naming pattern (e.g., `feature/data-ingestion`).
- **Deletion**: Branches are deleted after merge.

## Commit Message Convention
- **Types used**: `feat`, `fix`, `docs`, `refactor`, `chore`.
- **Format**: `[type]: [description]`
- **Why**: Enables automated changelog generation and clear history.

## PR Review Process
- PRs require at least one approval before merge.
- Code review focuses on: correctness, clarity, data integrity, and test coverage.
- Commit messages are reviewed as part of code review.

## GitHub Issue Tracking
- Every feature or fix starts with an issue.
- Issues have labels, assignees, and descriptions.
- Issues are closed when the corresponding PR is merged.