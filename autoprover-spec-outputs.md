=== /plan re-do-spec-output-report-pr13-on-top-of-aic ===

Consider the extensive reviews by @johspaeth and others on PR#13. Our conclusion was that this PR belongs in AIComposer and not in AIAutoProver repo. 
Some PRs got merged just now for AIComposer that should make this actually much better streamlined and well-programmed.

Focus on introducing proper datatypes and re-using existing AIComposer constants, methods, and conventions.
We will add to AIComposer a dependency on ProverOutputUtility.
Consider how to decouple the LLM calling taken from Autosetup and use the one existing in AIComposer. Note that it's a one-shot query right now and I'm not sure if we have it in AIComposer - this is a research task for you to solve properly.

We won't need to do special capturing for --memory-ns and --cache-ns since we'll be part of the AIComposer console workflow for autoprover.

Following all discussion on where to put outputs, we agreed it's not in the project root dir. It will be under `certora/` in a separate subdir.

For you it menas you'll have to re-generate from scratch large parts of this PR. You should do that while taking into account the feedback on the PR and also making sure you don't break the logic that we already saw was working quite well.
Pay special attention to programming style comments you got. You could probably take many parts verbatim. But you have to be careful with design. 
Work on top of AIComposer's current master. /effort max