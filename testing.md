=== /plan #1 ===
plan.  
This is a long running task. Run experiment.py in full in the background, as follows: `LLM_BACKEND=local CERTORAKEY=904bac08e5f5ada45a2ac7f8c228d96f5b262704 python3 ~/Certora/PreAudit/experiment.py /Volumes/PREAUDIT/sales.csv /Volumes/PREAUDIT/WD_SALES --run-mode preaudit`  It will run on multiple projects. As it runs, monitor the error logs you built in the previous step. For each fatal error that made a project not produce a final html report, you should come up with a plan on how to fix it. Dump it to a unique file under the plans/ directory which is a git repo too, and commit it. Make sure to not override files. Go one by one. Continue as long as experiment.py runs and there are new logs that you haven’t analyzed yet

I attach here a list of repos and commits to test preaudit on. Run `experiment.py` on those.

Needs to run `LLM_BACKEND=local` which hopefully gets inherited from experiment.py to preaudit.