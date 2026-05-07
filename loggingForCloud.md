<!-- feature-loop: c9f95a1e -->

=== /plan #1 siblings:autosetup ===

For runs in the cloud we want to dump all our logs to stdout and not mute them. We also don't need the file logging really. but for now, control the muted flag with an env var, so that in cloud we set `ALL_LOGS_IN_STDOUT=true` in env, and basically get that desired result (umuting! setting muted=False in all cases). work in a workrtee. handle the logger class in autosetup which iirc is the single class for logging both in preaudit and autosetup.