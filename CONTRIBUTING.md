# Contribution workflow

1. Read the product master and your role prompt.
2. Join through the membership Issue. A public comment proves control of an account, not the student's real identity; Yu verifies that separately and records the numeric GitHub ID. Unknown accounts remain PENDING.
3. Fork the repository into your own account, create a branch and fill `team/<role>/PLAN.md`. Open a plan-only PR, linking your role Issue.
4. Yu reviews the plan and merges it. In a separate owner-controlled change, Yu records its current Git blob SHA and approved implementation paths in `.github/team-policy.json`. A workflow or plan's self-declared approval is not trusted.
5. Synchronize your Fork. Implement only approved files. A plan revision is a new plan-only PR followed by fresh approval.
6. Include actual test results and limitations in your PR. Do not submit an unredacted user record or restricted source.
7. The trusted scope status must pass. Yu reviews and manually merges; members never merge into the main repository.

## Shared-file changes

Use the interface request template. Yu coordinates shared contracts and integration. Request a narrowly scoped owner-recorded exception only when necessary; never edit ownership policy from a member PR.

## Fork CI

Contributor code is built only in a separate unprivileged `pull_request` workflow with read-only token, no secrets, no environment credentials and no self-hosted runner. First-time contributor workflows may wait for owner approval. The trusted scope workflow uses only default-branch code and inspects PR metadata/data; it never imports or executes PR code.

## No self-review deadlock

Native protection requires a PR and successful checks, but does not require an approving review from the author. Only Yu has repository write/admin rights and therefore only Yu can merge. CODEOWNERS routes review to Yu; it is not a filesystem ACL. Product PRs remain for Yu's final decision.
