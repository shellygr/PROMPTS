=== /plan #1 ===

For runs in the cloud we want to dump all our logs to stdout and not mute them. We also don't need the file logging really. but for now, control the muted flag with an env var, so that in cloud we set `ALL_LOGS_IN_STDOUT=true` in env, and basically get that desired result (umuting! setting muted=False in all cases).