=== /plan random-stuff ===

.....

check fssync changes are valid. no files that should be under fssync are missed.

......


preaudit-dev tgp_v1_8IXhdLQcYNbjDnQknhVcaKvB-CTIWnc8CfLyPVVmaao
preaudit-ci tgp_v1_-7wYDfvp5nYhYr8Cv74__SXMAtFgqOgX5fkBTVVOQD0


 Pre-work the user needs to handle outside this worktree

 - Generate a Bedrock long-term API key in the AWS console for the AWS account
 that prod uses, scoped to qwen.qwen3-coder-480b-a35b-instruct in us-west-2.
 - Request model access for Qwen3-Coder-480B in the Bedrock console if the
 account hasn't already (one-click in us-west-2).
 - Store the key in the GitHub secret currently named
 PREAUDIT_CUSTOM_ON_CLOUD_API_KEY (replacing the Together key) — or, to keep
 both available, add PREAUDIT_BEDROCK_API_KEY and update the workflow to
 reference it. (Recommend the latter: easier rollback.)
 - Confirm with whoever owns the prod AWS account that the IAM principal the
 containers run under can call Bedrock in us-west-2 (separate from the API
 key — if the key was minted by that principal, it's already authorized).

   Not done (your pre-work, per the plan):
  1. Generate a long-term Bedrock API key in the AWS console for the prod account.
  2. Request Qwen3-Coder-480B model access in us-west-2 (Bedrock console).
  3. Update the GitHub secret PREAUDIT_CUSTOM_ON_CLOUD_API_KEY value to the Bedrock key (or add a new PREAUDIT_BEDROCK_API_KEY secret and update the workflow ref — I went with reusing the existing
  secret name to avoid extra setup; let me know if you'd rather split).
  4. Run the E2E smoke + the batch-mode verification (requires the key). If batch mode 404s on Bedrock-Mantle, add the fail-fast guard in cli.py as the plan describes.
  5. Push + open PR (not done since you didn't ask, and CLAUDE.md says don't commit/push unprompted).
 .........