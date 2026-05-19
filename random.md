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

 
 .........