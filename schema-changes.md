=== /plan followup-schema-changes ===
  PR mechanics

  A1. PR #351 (shelly/aiss-schema-round2) — just merged main in (57c7c8c). CI re-running in background. If green, it's ready for your review/approve-to-merge.

  A2. PR #355 (shelly/aiss-payload-to-fsspec) — stacked on #351, so GitHub Actions skips CI (workflows only target main/develop). Two options to get CI: wait for #351 to merge then rebase
  #355 onto main, or retarget #355 to main now.

  Round 4 follow-ups (documented in spec, not yet implemented)

  B1. BehaviorSummary + IterationResult URLs in payload_urls (Appendix C.14). You explicitly asked for these earlier. The current PR #355 only writes the 4 post-synthesis types. Adding the
  cache-side types requires the analyzer to surface URLs at write time (e.g., a new entry.cache_urls transient field, or a glob-and-classify pass at save time). Not in #355's MVP; documented
  as planned.
  A2. PR #355 (shelly/aiss-payload-to-fsspec) — stacked on #351, so GitHub Actions skips CI (workflows only target main/develop). Two options to get CI: wait for #351 to merge then rebase
  #355 onto main, or retarget #355 to main now.

  Round 4 follow-ups (documented in spec, not yet implemented)

  B1. BehaviorSummary + IterationResult URLs in payload_urls (Appendix C.14). You explicitly asked for these earlier. The current PR #355 only writes the 4 post-synthesis types. Adding the
  cache-side types requires the analyzer to surface URLs at write time (e.g., a new entry.cache_urls transient field, or a glob-and-classify pass at save time). Not in #355's MVP; documented

  B3. fsspec URL portability for the dashboard (Appendix C.15). When the dashboard fetches payload_urls, how does it resolve s3://bucket/... (SaaS) vs absolute local paths (dev)? Pick one:
  (a) backend rewrites to a GET /workflows/{wid}/files?key=... redirect; (b) cloud serves s3:// URLs directly and dashboard uses an S3 client; (c) presigned URLs at write time.

  Spec open questions (need backend team confirmation; nothing for me to code)

  C1. Appendix C.1 — workflow visibility / authz scope across /workflows, /logs, /results, /results/file.
  C2. C.2 — single-workflow GET path style (/workflows/{id} vs /workflow?id=...).
  C3. C.3 — PUT /start-prebuild upload contract (where does the artifact go).
  C4. C.4 — gh_token lifecycle.
  C5. C.5 — design_md_path semantics.
  C6. C.6 — empty securitySchemes in live OpenAPI.
  C7. C.7 — findings ingestion idempotency (append vs replace).
  C8. C.8 — cursor vs offset pagination on /results (acknowledged intentional).
  C9. C.9 — POST /start idempotency on (repo_id, contract_id, git_ref).
  C10. C.10 — AissRepo.active flag semantics.
  C11. C.11 — extra_prover_args wire format (string vs list).
  C12. C.12 — cloud-side findings table shape confirmation (data-processors team).
  C13. C.13 — heavy SaveFindingsResponse — ?return=ids flag.

  Cross-cutting

  D1. Dashboard code (currently in mutation_svelte or wherever) that reads payload.synthesis / payload.formatted_markdown will need updating once #355 ships.

  D2. mockups/DEVELOPMENT_PLAN.md lists MSW frontend handlers using legacy /api/*/aissk/... URLs. Out of date relative to the current spec; not yet updated.
  

  ========================

  We need to sort out cached files vs results files.
  Current situation:
  1. PREAUDIT_S3_PREFIX is used for fsspec and all cache is written there. WRONG.  It is keyed by workflow_id and thus not suitable for cache which is shared across tuples <user,repo,contract>, but not the commit. workflow is unique per commit too.
  2. PREAUDIT_REPO_CACHE_PREFIX is used to upload the certora/ folder via zip. WRONG. The cloud didn't set it yet, and certora/ is not the only thing we cache. We also do not want to use zip here but just copy with fsspec.