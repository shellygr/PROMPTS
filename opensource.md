=== /plan open-source-everything ===

 I am considering to open-source this repo. What do I need to be aware of? What could be 'embarassing'? What could be risky? /effort max     


 ANSWER FROM CLAUDE:

 Synthesis below. I verified the most critical findings directly — one agent's report was inaccurate, corrected below.

  Open-Sourcing PreAudit — Risk Assessment

  TL;DR

  The code itself is professional and clean (no embarrassing comments, no profanity, no AI-slop). But the repo has four hard blockers and one strategic-IP question you need to resolve before
  any public release. The biggest issue is not what's in the code — it's that the prompts and CVL specs ARE the audit methodology, and you'd be giving them away.

  ---
  🔴 HARD BLOCKERS (must fix before any release)

  1. Secrets in git history — REAL

  Two API keys are still reachable via git log, even though they were removed from current source in commits 042ab83 / 3c088d1:
  - Anthropic key sk-ant-api03-vR6P1hfoIMl9… (was in src/preaudit/__init__.py)
  - CERTORAKEY 3890c7685ca36c2dee89ba547c5e5f486332bf4e

  Earlier commits to look at: ab31ce0, 79a1a01, 32f7b7a. These need to be rotated (treat them as compromised — they have been on Certora-internal GitHub since 2025, but public exposure is a
  different category of risk) and the history needs git filter-repo before publishing.

  ▎ Correction to the secrets-hunting agent: the local .env file is NOT tracked by git (verified git ls-files .env is empty). The agent confused "exists on disk" with "committed". Only the 
  ▎ historical hardcoded values are in git history.

  2. No LICENSE file

  pyproject.toml declares MIT, but there is no LICENSE file at the repo root. You cannot legally open-source code without shipping the license text. Also missing: NOTICE.md (would need one to
   credit vendor/wala-solidity, which is EPL-2.0).

  3. Private dependency surface is huge

  The repo cannot be pip install-ed by an outside contributor as-is:

  ┌──────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────┐
  │           Private dep            │                                              Coupling                                               │         Import count          │
  ├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ certora-autosetup                │ architectural — RuleGenerator extends SanityRuleGenerator, fsspec cache abstraction comes from here │ 2,659 imports across 57 files │
  ├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ prover-output-utility            │ API/auth/data models                                                                                │ 52 imports across 12 files    │
  ├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ certora-login                    │ auth + identity                                                                                     │ 11 imports across 6 files     │
  ├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ autocvl                          │ subprocess (looser)                                                                                 │ 1 file                        │
  ├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ ai-composer                      │ mostly mentioned in docs, occasional import                                                         │ low                           │
  ├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ vendor/wala-solidity (submodule) │ optional roundabout checker                                                                         │ submodule                     │
  └──────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────┘

  You either (a) open-source AutoSetup first (it's the lynchpin), (b) extract a public AutoSetup-API package, or (c) ship PreAudit as "source-available, requires Certora's other internal
  packages" — which is not really open source.

  4. Internal infrastructure references

  - data-api-dev.certora.com, vaas-dev, staging server mappings (runner.py:127-131, scripts/test-cloud-saas-workflow.py)
  - Direct file-path link to private Certora/data-processors repo in persistence/schema.py:8 and mockups/api_endpoints.md
  - Private repo references: Certora/proverlite-release, Certora/DummyProject, Certora/mirror-cork-depeg-swap, Certora/aave-v4-pub (in tests/unit/test_saas_builder_io.py:177,211 and
  CLAUDE.md:196 as an example value)

  None of these are catastrophic alone; collectively they sketch out Certora's internal architecture for anyone who reads carefully.

  ---
  🟠 STRATEGIC RISK — the real question

  The prompts/ directory (64 Jinja2 templates) and generic_checkers/*/specs/ (41 CVL specs) encode the audit methodology. This is not a "could be embarrassing" issue — it's a "do you actually
   want to give this away?" issue.

  What's in there:
  - defect_analysis/erc4626.j2, cei_violation.j2, input_validation.j2 — explicit decision trees for distinguishing true positives from false positives, calibrated against named real-world
  hacks (DAO $60M, Rari $80M, Curve $70M)
  - impact_likelihood/default.j2 — Certora's risk matrix calibrated to 2024 loss data
  - generic_checkers/RULES_STUDY.md (~160KB) — the playbook in prose form: which patterns to flag, which false positives to suppress, why
  - 41 CVL spec templates — executable formalizations of vulnerability classes (vault inflation, write-after-call, ERC-1967 slot collision, etc.)

  The CVL specs themselves are arguably already implied by tool output. But the prompts + RULES_STUDY combined are years of audit experience codified, and they would shorten a competitor's
  time-to-market for an AI audit tool from ~12 months to ~3.

  This is a business decision, not a hygiene one. Options:
  - Full open source — give it all away (good for community trust, bad for moat)
  - Open-source infrastructure, keep prompts/specs proprietary — ship empty templates, real ones load from Certora's backend
  - Source-available with a non-commercial clause (e.g., BSL/PolyForm Noncommercial)

  ---
  🟡 MEDIUM — cleanup
  
  - mockups/ directory contains AISS API specs, frontend prototypes, the rules catalog. Decide whether this is documentation you want public or internal-only planning.
  - Dockerfile.preaudit silently swallows submodule clone failures (2>/dev/null || true) — currently masks a real failure mode and will look sketchy in a public repo.
  - Test fixtures reference private Certora/DummyProject and Certora/mirror-cork-depeg-swap — without these, integration tests don't run for outsiders. Either make them public or provide
  replay fixtures (a PREAUDIT_REPLAY_FIXTURE_DIR mode already exists).
  - persistence/schema.py:8 cites the exact file path inside a private repo as the source-of-truth schema reference.

  ---
  🟢 SURPRISINGLY CLEAN — not problems

  - Zero profanity, zero venting, zero snark. No "wtf", no "I hate this", no commented-out dumping grounds.
  - No half-finished refactors. BIG_REFACTOR.md reads as completed work, not aspirational.
  - One employee initial in a TODO (rule_generator.py:49 "TODO SG"). That's it for personal exposure.
  - No customer names in source. (aave-v4-pub appears only as an env-var example, not as embedded audit findings.)
  - No GPL/AGPL/BUSL deps that would conflict with MIT.
  - CI workflows handle secrets correctly (${{ secrets.* }}, no hardcoded tokens in .github/workflows/).
  - Vendored OpenZeppelin / forge-std in tests/test_projects/ is properly isolated and gitignored from your distribution.
  - Largest file is 2,994 lines (html_shared.py) and is well-organized, not a junk drawer.

  ---
  Recommended sequence

  1. Decide the strategic question first: open-source the whole methodology, or just the engine?
  2. Rotate the two leaked keys. Then git filter-repo to scrub history.
  3. Open-source AutoSetup first (or extract the public surface as a separate package). PreAudit can't ship before its biggest dependency does.
  4. Add LICENSE + NOTICE.md. Add per-file headers if you want belt-and-suspenders.
  5. Scrub internal references: data-api-dev.certora.com, vaas-dev/staging mappings if those endpoints aren't public, the data-processors repo path in schema.py.
  6. Make DummyProject (or a replacement) public, or ship the repo in replay-fixture-only mode.
  7. Fix the silent submodule failure in Dockerfile.preaudit.
  8. Audit mockups/ as a deliberate publish-or-strip decision.

  The code itself won't embarrass you. The question is whether open-sourcing PreAudit means open-sourcing Certora's audit methodology — and that's a call only you and leadership can make.


--- 
we can deal with 2 already - use license from github.com/Certora/CertoraProver. Add the NOTICE.md.
proverlite-release is no longer relevant. we can scrub it.
Our strategy would be to create a mirror repository at github.com/Certora/StaticAnalyzer. So we would be able to get rid of the problems of internal docs etc.
I suggest, beyond what I mentioned above, that you make a markdown OPENSOURCE_STRATEGY.md listing all steps needed to open source, what should be omitted, and what not.
I am not concerned about the strategic risk. The prompts are so far very basic. The value will come from fine-tuned models on a large set of examples.


--------------------

=== /plan open-source certora-cloud-cli ===
Look into this repo. It contains information about our AWS infrastructure which I prefer to keep confidential. 
Show me how you plan to split the AWS parts into a separate repo certora-cloud-cli-internal, including code and documentation and anything else that should not be open source.
Then, create a new folder ~/Certora/certora-cloud-cli-internal that is basically the confidential parts + dependency on current certora-cloud-cli. 
Now, because we're still doing work on top of certora-cloud-cli and may do it for a while before the final go, we need to mirror current certora-cloud-cli into a new repo certora-cloud-cli-pub,
which you'll put locally in ~/Certora/certora-cloud-cli-pub. In that new repo, REMOVE all the confidential parts. This will eventually become the new certora-cloud-cli once we're ready.
Write a document that describes the split and how to append new commits from certora-cloud-cli to either certora-cloud-cli-internal or certora-cloud-cli-pub.


=== /plan os-followup-pou ===
Look at opensource_assessment.md. We now have certora-cloud-cli-pub repo and internal folder ~/certora/certora-cloud-cli-pub. Let's change pyproject.toml to use it instead. This repo will also become public.
Would you recommend keeping readthedocs for the open source or remove it?
email in pyproject toml-  is it standard practice to use a generic email such as info@certora.com?


- License files
- license headers in each file?
- mirror from public to private
- code hygiene process in the private branch
- secret docs in the private branch
- test splitting

Ondrej:
- Pypi supply chain attacks - if we do not upload to pypi
- Graphcore from github, should be Certora prefix for pypi package, same for all others.

separate code from tests/ci for ProverOutputUtility, which will have a public repo named ProverCLI, package name certora-prover-cli.

separate code from tests/ci for Autosetup, which will have a public repo named SolidityProverAutosetup, package name certora-solidity-autosetup