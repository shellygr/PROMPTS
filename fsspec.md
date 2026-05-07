<!-- feature-loop: 85ca9291 -->

=== /plan #1 ===
A colleague proposed we use fsspec for dual lcoal filesystem/s3 update.
What do you think if we used fsspec for some of the files we write in preaudit instead of syncing them via s3_sync.py? I thought about all the cache/state related writes in autosetup and preaudit. 
The certora/ folder would still have to be synced manually by s3_sync.py, since it's read by the jar and thus won't be available for the jar running.

But it would be particularly useful to get rid of specific files since those may change be preaudit/autosetup and thus we'll be chasing changes in both these repos and s3_sync.py. It would make renaming folders easier.
For example this part of s3_sync.py is very sensitive to changes and I believe already broke since we wrote it:
```

# Individual files (not directories) to preserve across runs.
CACHE_FILES = [
    ".certora_internal/autosetup_result.json", # TODO We would need to update this. also, brittle.
]
```


  Caches (reusable across runs)                                                                                                                                                                       
                                                                                                                                                                                                      
  ┌─────────────────┬──────────────────┬────────────────────┬────────────────────────────────────────────────────────────────────────────────┐                                                        
  │    Directory    │      Owner       │    Written when    │                                    Purpose                                     │                                                        
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ build_cache/    │ AutoSetup        │ Compilation        │ Cached Solidity compilation results (hash-keyed)                               │                                                        
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ checker_cache/  │ PreAudit         │ Checker generation │ Per-checker content hashes (e.g. cei_SimpleVault/) — tracks if sources changed │                                                        
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ preaudit_cache/ │ PreAudit         │ Reporting          │ Hash-keyed JSON files with intermediate analysis results                       │                                                        
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ preaudit_state/ │ PreAudit         │ Initial analysis   │ signature_database.json — extracted method signatures                          │                                                        
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ llm_cache/      │ AutoSetup        │ AI analysis        │ Cached LLM API responses (avoids redundant calls)                              │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ api_cache/      │ AutoSetup/Prover │ Result retrieval   │ Cached prover tree view/status data                                            │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ content_cache/  │ AutoSetup        │ Setup              │ Content hashing for autosetup                                                  │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ analysis_cache/ │ PreAudit         │ Reporting          │ AI analysis results per rule                                                   │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ tarball_cache/  │ Prover utils     │ Result retrieval   │ Downloaded .tar.gz prover job results                                          │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ extracted_tars/ │ Prover utils     │ Result retrieval   │ Extracted prover debug output (SVG, logs)                                      │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ autocvl_cache/  │ AutoCVL          │ Spec generation    │ AutoCVL spec generation cache                                                  │
  ├─────────────────┼──────────────────┼────────────────────┼────────────────────────────────────────────────────────────────────────────────┤                                                        
  │ bulk_cache/     │ PreAudit         │ Reporting          │ Bulk analysis cache                                                            │
  └─────────────────┴──────────────────┴────────────────────┴────────────────────────────────────────────────────────────────────────────────┘                                                        
                                                        
  Per-run artifacts (one set per prover invocation)                                                                                                                                                   
                                                        
  ┌──────────────────────────┬──────────────────┬──────────────────────────────────────────────────────────────────────────┐                                                                          
  │        Directory         │      Owner       │                                 Purpose                                  │
  ├──────────────────────────┼──────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ [timestamp_hash]/ (150+) │ AutoSetup/Prover │ Metadata, build config, sources snapshot, debug logs for each prover job │
  └──────────────────────────┴──────────────────┴──────────────────────────────────────────────────────────────────────────┘
                                                                                                                                                                                                      
  State/metadata files
                                                                                                                                                                                                      
  ┌───────────────────────────┬──────────────┬────────────────────────────────────────────┐
  │           File            │    Owner     │                  Purpose                   │
  ├───────────────────────────┼──────────────┼────────────────────────────────────────────┤
  │ .certora_recent_jobs.json │ Prover utils │ Index of recent jobs submitted             │
  ├───────────────────────────┼──────────────┼────────────────────────────────────────────┤
  │ .generator_cache_*.json   │ PreAudit     │ Generator config checksums per contract    │                                                                                                           
  ├───────────────────────────┼──────────────┼────────────────────────────────────────────┤                                                                                                           
  │ autosetup_result.json     │ AutoSetup    │ Setup compilation result (the brittle one) │                                                                                                           
  └───────────────────────────┴──────────────┴────────────────────────────────────────────┘                                                                                                           
                                                        
  Debug                                                                                                                                                                                               
                                                        
  ┌──────────────────┬───────────┬──────────────────────────────────────────────────────────────────┐
  │    Directory     │   Owner   │                             Purpose                              │
  ├──────────────────┼───────────┼──────────────────────────────────────────────────────────────────┤
  │ llm_input_dumps/ │ AutoSetup │ Debug dumps of LLM inputs/outputs                                │
  ├──────────────────┼───────────┼──────────────────────────────────────────────────────────────────┤
  │ rule_analyses/   │ PreAudit  │ Per-rule analysis directories (200+ dirs with analysis metadata) │                                                                                                 
  └──────────────────┴───────────┴──────────────────────────────────────────────────────────────────┘                                                                                                 
                                                                                                                                                                                                      
  Notable gaps in s3_sync.py's CACHE_DIRS                                                                                                                                                             
                                                        
  These exist in dummyproject but are not listed in CACHE_DIRS:                                                                                                                                       
  - build_cache/ — compilation cache                    
  - checker_cache/ — listed under content_cache in s3_sync but this is a separate dir                                                                                                                 
  - api_cache/ — prover API response cache                                           
  - tarball_cache/ + extracted_tars/ — downloaded prover results                                                                                                                                      
  - bulk_cache/ — bulk analysis cache                                                                                                                                                                 
  - autocvl_cache/ — AutoCVL cache                                                                                                                                                                    
  - rule_analyses/ — per-rule analysis state                                                                                                                                                          
  - .generator_cache_*.json files                       
  - .certora_recent_jobs.json                                                                                                                                                                         
  - All the timestamped run directories                                                                                                                                                               
                                       
  This confirms the maintenance problem is worse than the code suggests — many cache directories are silently not persisted across SaaS runs.      


   Plan: Centralize cache/state path constants + fsspec integration

 Context

 .certora_internal/ subdirectory paths are scattered as inline strings across PreAudit (~11 declarations in 9 files) and AutoSetup (~80 inline Path(".certora_internal/...") references). s3_sync.py
 maintains hardcoded CACHE_DIRS/CACHE_FILES lists that must stay in sync with both repos — already broken for several directories that exist but aren't listed.

 Goals:
 1. Centralize path constants for all cache/state dirs we control
 2. Evaluate names and rename where unclear
 3. Introduce fsspec so cache I/O transparently targets local FS or S3 (direct writes, no buffering)
 4. Shrink s3_sync.py as dirs move to fsspec

 Directory inventory and proposed names

 PreAudit-owned (constants go in src/certora_preaudit/paths.py)

 ┌──────────────────────────────┬───────────────────┬────────────────────────────────────────────┬──────────────────────────────┐
 │         Current name         │   Proposed name   │                 Rationale                  │          Defined in          │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ preaudit_debug/              │ crash_dumps/      │ Contains only crash dump JSONs             │ debug_recorder.py:173        │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ multi_analysis_aggregate/    │ aggregate_output/ │ Shorter, clearer                           │ reporting/__main__.py:1600   │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ analysis_cache/              │ (keep)            │ Unambiguous once preaudit_cache is renamed │ reporting/cache.py:49        │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ checker_cache/               │ (keep)            │ Clear                                      │ rule_generator.py:300,316    │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ autocvl_cache/               │ (keep)            │ Clear                                      │ autocvl/runner.py:67         │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ rule_analyses/               │ (keep)            │ Clear                                      │ (telemetry.py exclusion set) │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ .generator_cache_{name}.json │ (keep pattern)    │ Add constant for the pattern               │ rule_generator.py:100        │
 ├──────────────────────────────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────────┤
 │ telemetry_metadata.json      │ (keep)            │ Clear                                      │ telemetry.py:96              │
 └──────────────────────────────┴───────────────────┴────────────────────────────────────────────┴──────────────────────────────┘

 AutoSetup-owned (constants go in utils/constants.py)

 ┌───────────────────────┬───────────────────┬───────────────────────────────────────────────────────┬───────────────────────────────────────────┐
 │     Current name      │   Proposed name   │                       Rationale                       │                Defined in                 │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ preaudit_cache/       │ job_result_cache/ │ Stores prover job results (ProverRunner/CacheManager) │ prover_runner.py:103, cache_manager.py:32 │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ preaudit_state/       │ signature_state/  │ Contains only signature_database.json                 │ signature_manager.py:259                  │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ content_cache/        │ (keep)            │ Clear                                                 │ content_cache.py:19                       │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ llm_cache/            │ (keep)            │ Clear                                                 │ setup_summaries.py:1224                   │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ llm_input_dumps/      │ (keep)            │ Clear (debug replay files)                            │ llm_debug.py:18 (has DEBUG_DIR)           │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ sanity_analysis/      │ (keep)            │ Clear                                                 │ sanity.py:262                             │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ autosetup_result.json │ (keep)            │ Clear                                                 │ autosetup/cli.py:172                      │
 ├───────────────────────┼───────────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ worktree_logs/        │ (keep)            │ Clear                                                 │ parallel_autosetup.py:547                 │
 └───────────────────────┴───────────────────┴───────────────────────────────────────────────────────┴───────────────────────────────────────────┘

 We do NOT control (certora-cli/prover) — no constants, no fsspec

 - build_cache/, tarball_cache/, extracted_tars/, api_cache/, .certora_recent_jobs.json, timestamped run dirs

 Special cases — no fsspec

 - findings.db — SQLite, handled via PREAUDIT_DB_URL
 - certora/ — prover jar needs local files, stays in s3_sync.py

 Implementation phases

 Phase 1: Constants (both repos, no fsspec yet)

 AutoSetup PR — expand utils/constants.py:
 # Already exists:
 DIR_CERTORA_INTERNAL = ".certora_internal"

 # Add cache/state subdirectory constants:
 DIR_JOB_RESULT_CACHE = "job_result_cache"       # renamed from preaudit_cache
 DIR_SIGNATURE_STATE = "signature_state"          # renamed from preaudit_state
 DIR_CONTENT_CACHE = "content_cache"
 DIR_LLM_CACHE = "llm_cache"
 DIR_LLM_INPUT_DUMPS = "llm_input_dumps"
 DIR_SANITY_ANALYSIS = "sanity_analysis"
 DIR_WORKTREE_LOGS = "worktree_logs"
 FILE_AUTOSETUP_RESULT = "autosetup_result.json"

 Replace all inline string references in AutoSetup with these constants.

 PreAudit PR (after AutoSetup lands) — create src/certora_preaudit/paths.py:
 DIR_ANALYSIS_CACHE = "analysis_cache"
 DIR_CHECKER_CACHE = "checker_cache"
 DIR_AUTOCVL_CACHE = "autocvl_cache"
 DIR_CRASH_DUMPS = "crash_dumps"                  # renamed from preaudit_debug
 DIR_AGGREGATE_OUTPUT = "aggregate_output"        # renamed from multi_analysis_aggregate
 DIR_RULE_ANALYSES = "rule_analyses"
 FILE_TELEMETRY_METADATA = "telemetry_metadata.json"
 GENERATOR_CACHE_TEMPLATE = ".generator_cache_{contract_name}.json"

 Replace all inline string references. Update s3_sync.py CACHE_DIRS to use constants.

 For renames: s3_sync.py temporarily lists both old and new names in download (read from either), writes only new names. Remove old names after one cache cycle.

 Phase 2: fsspec infrastructure (AutoSetup)

 Add fsspec to AutoSetup dependencies. Create utils/cache_fs.py:
 - init_cache_fs(s3_bucket, s3_prefix) — called once at startup
 - get_cache_fs() → fsspec.AbstractFileSystem (defaults to local)
 - cache_path(relative) → full path for the configured backend

 Phase 3: Migrate call sites (incremental, both repos)

 Migrate one directory at a time, removing it from s3_sync.py as it moves:

 1. llm_input_dumps/ — simple writes, already has a constant
 2. llm_cache/ — straightforward get/put
 3. content_cache/ — ContentCache class, update __init__/get/put
 4. analysis_cache/ — AnalysisCache class, same pattern
 5. checker_cache/ — uses ContentCache, already done after step 3
 6. job_result_cache/ — ProverRunner + CacheManager
 7. crash_dumps/ — write-only
 8. autocvl_cache/, signature_state/, sanity_analysis/
 9. Single files: autosetup_result.json, telemetry_metadata.json
 10. aggregate_output/, rule_analyses/, worktree_logs/

 End state: s3_sync.py CACHE_DIRS contains only "certora".

 Key files to modify

 AutoSetup:
 - src/certora_autosetup/utils/constants.py — add constants
 - src/certora_autosetup/utils/prover_runner.py — 3 refs to preaudit_cache
 - src/certora_autosetup/utils/cache_manager.py — 1 ref to preaudit_cache
 - src/certora_autosetup/cache/content_cache.py — 1 ref to content_cache
 - src/certora_autosetup/setup/setup_summaries.py — 2 refs to llm_cache
 - src/certora_autosetup/utils/llm_debug.py — DEBUG_DIR (replace with constant)
 - src/certora_autosetup/setup/signature_manager.py — 1 ref to preaudit_state
 - src/certora_autosetup/autosetup/cli.py + autosetup.py — refs to autosetup_result.json
 - src/certora_autosetup/setup/sanity.py — 33 refs to sanity_analysis
 - src/certora_autosetup/parallel_autosetup.py — 1 ref to worktree_logs

 PreAudit:
 - src/certora_preaudit/paths.py — new file with constants
 - src/certora_preaudit/saas/s3_sync.py — use constants, shrink lists
 - src/certora_preaudit/generic_checkers/reporting/cache.py — use constant
 - src/certora_preaudit/rule_generator.py — use constants (2 paths)
 - src/certora_preaudit/generic_checkers/reporting/debug_recorder.py — use constant + rename
 - src/certora_preaudit/generic_checkers/reporting/__main__.py — use constant + rename
 - src/certora_preaudit/autocvl/runner.py — use constant
 - src/certora_preaudit/telemetry.py — use constant

 Verification

 - Phase 1: All existing tests pass (mechanical refactoring). Run pytest tests/unit/ tests/integration/test_orchestrator_integration.py -v in both repos.
 - Phase 2-3: fsspec local mode is a thin wrapper — tests pass unchanged. For S3 mode, use fsspec.filesystem("memory") in unit tests.
 - Rename migration: Run PreAudit on dummyproject, verify caches are created under new names.

=== /plan cachemanager siblings:autosetup ===
 we discussed initially if we need the CacheManager class and we saw it is only used in tests.
 Examine those tests. I want a report from you on whether those are actually testing things that occur in production code or not. Propose changes and extensions. In particular, you should answer the question of whether we can throw away the CacheManager class.  use a worktree in autosetup if you need to make changes    


=== /plan fsspec-docs siblings:autosetup ===
please update CLAUDE.md of both autosetup and preaudit with the files using fsspec, in particular what files managed by these tools should use fsspec, and which should not. explain what ContentCache is.