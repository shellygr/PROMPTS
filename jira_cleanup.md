# Jira cleanup

Your goal is to review the sub-issues opened under https://certora.atlassian.net/browse/CERT-5350 that are not yet in closed status.
Many of them may be duplicates of each other, or no longer reproducible in the latest version of certora-cli.
So your first task would be to attempt to reproduce (don't forget to put `--server vaas-stg`).
If the issue does not reproduce, report back here that it is likely non-reporducible. Take note if the issue is reported in the comments as flaky.
If the issue does reproduce, start an agent for exploring the issue in greater depth. It should take into account other knowledge from Jira if found to be relevant, it should try to minimize the example, and explore the EVMVerifier repo to consider possible fixes, that would be tested locally. 
I ask you not to run more than one instance of `emv.jar` locally (it is invoked locally by certoraRun if you do not provide the `--server` flag).
If you manage to fix the issue, open a draft PR with the fix to EVMVerifier repo.

At the end, you should produce a csv with the outcomes for each ticket: the table consists of columns with the ticket id, its title, your summary of the issues, the mitigation with a draft PR, or the justification for closing it, and the new status to be set.
In any case, do not update jira yourself.

Use jira_cleanup_aug20_2026/ as your working directory. each subagent should record their progress in suitable subdir within the working directory.