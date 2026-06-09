=== /plan re-do-spec-output-report-pr13-on-top-of-aic ===

Consider the extensive reviews by @johspaeth and others on PR#13. Our conclusion was that this PR belongs in AIComposer and not in AIAutoProver repo. 
We further decided to build it _on top of_ PR#121 of AIComposer, which is `johannes/json-dump-prover-links`. So you should create a branch `shelly/autoprove-summary` on top of the `johannes/json-dump-prover-links` branch.

Focus on introducing proper datatypes and re-using existing AIComposer constants, methods, and conventions.
We will add to AIComposer a dependency on ProverOutputUtility.
Consider how to decouple the LLM calling taken from Autosetup and use the one existing in AIComposer. Note that it's a one-shot query right now and I'm not sure if we have it in AIComposer - this is a research task for you to solve properly.

We won't need to do special capturing for --memory-ns and --cache-ns since we'll be part of the AIComposer console workflow for autoprover.

Following all discussion on where to put outputs, we agreed it's not in the project root dir. 