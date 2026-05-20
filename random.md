=== /plan random-stuff ===

.....

check fssync changes are valid. no files that should be under fssync are missed.

.......

We need to design a test for the finding dismissal workflow.

The github.com/certora/dummyproject which is cloned here in ~/certora/tmp/dummyproject contains various 
'mistakes' in the contract injected for the purpose of detecting the preaudit detection rules.
in particular, some of them are true positives, and some are perhaps false positives.
we want to pick the highest 'false positive', i.e. that has the highest score, 
and come up with a dismissal reason, that's not overly long, 1-2 lines.
then, we want to rerun preaudit, and see that the score for that finding is reduced.

the second test, for the same finding, is first to modify the code slightly, in the area of the bug, 
but still in a way that does not change the verdict. it is still a false positive, and we will still
use dismissal info to score it lower than in the first run.

the third test is to introduce some code change that makes the bug real. now, the re-run
should ignore the dismissal, understand that the context changed, and give it a high score anyway.

your tasks:
1. find out which finding from the dummy project and which preaudit check could be suitable for our test. 
use existing docs here and the reports in the local copy of the repo and its code.
2. plan how the testing script will work. I suggest once you know the relevant checker, to run _only_ that checker.
in particular you need to simulate an api call that 'dismisses' the finding. 
you also need to plan the code patches for the second and third scenarios described above.
3. check, and plan if needed, whether we should adapt the prompts to account for dismissals. we will not 
always have dismissal information. but if we have it, it should be integrated within step 2 and the judge as
additional specific evidence to this example. 
it could be the case that we do not want to change the templates, perhaps just add a jinja section that will 
usually be empty unless there are dismissals info that are dynamically loaded from the db based on matching
rule fingerprints. it may be wise to aggregate all dismissals for the same rule, and specify the
fingerprint next to the dismissal text as a header when including in the prompt, so that we could apply
even if the finding happens in slightly different contexts.
4. success criteria are a bit tricky. real findings should get a score above 40. false findings should get a 
score below 40. so if we had a false positive finding with score higher than 40 then dismissal should take
bring it to below 40, and introducing a bug should make it go above 40. even if the diff is 41-39 that's ok
and passes our test. 

================

......

we need to be more serious about the way we count tokens.
Since we understand pricing changes, the _cost_usd field could be computed incorrectly.
the _tokens fields are not helpful because they conflate input, output, cache read and cache write tokens
all together. we should store FULL information. One option is to add fields for each token type.
Another option is to add dictionary entries with equal format for each type. it seems the better solution to me.
in the meantime to avoid backward compatibility issues, name the new suffix _tokens_breakdown and 
keep reporting total tokens.


......

land installations for all things. uv? pip? get it sorted out already

1. jobdiff
2. fixconf
3. proverswissarmyknife
4. [later] local dashboard


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


  
  ┌──────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────┐
  │                              │                                 Bedrock qwen.qwen3-coder-480b-a35b-instruct                                 │                    Together                     │
  │                              │                                                                                                             │     Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8     │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Base weights                 │ Qwen3-Coder-480B-A35B-Instruct (480B total / 35B active MoE, 62 layers, 160 experts × 8 active)             │ Same                                            │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Precision                    │ Unspecified by AWS (most likely FP8 since that's the standard 480B deployment, but the model card doesn't   │ Explicitly FP8 — fine-grained block-128 quant   │
  │                              │ say)                                                                                                        │                                                 │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Context window               │ 128K tokens                                                                                                 │ 256K native, up to 1M with YaRN                 │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Max output tokens            │ 16K                                                                                                         │ 65,536 recommended                              │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Price (input / output per    │ $0.22 / $1.80                                                                                               │ $2.00 / $2.00                                   │
  │ 1M)                          │                                                                                                             │                                                 │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Prompt caching               │ No                                                                                                          │ No                                              │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ API surface                  │ OpenAI-compat (bedrock-mantle) + native Invoke/Converse                                                     │ OpenAI-compat only                              │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Auth                         │ AWS Bedrock long-term API key (Bearer) or IAM/SigV4                                                         │ Together API key (Bearer)                       │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Regions                      │ 11 regions (US/EU/APAC/SA, in-region only)                                                                  │ Together's global infra                         │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ Function-calling / tool use  │ Yes                                                                                                         │ Yes                                             │
  ├──────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ No "thinking" mode           │ Yes (Instruct variant)                                                                                      │ Yes (Instruct variant)                          │
  └──────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────┘


  .........
 