<!-- feature-loop: 0ab26dab -->

=== /plan qwenOnCloud ===

I had a long conversation with you Claude Chat on the usage of Qwen in the cloud and how best to facilitate it.
I want you to support one more LLM_BACKEND which would be called `CUSTOM_ON_CLOUD`. The idea is that we'll use some serverless hosting and some model of choice (e.g. largest supported Qwen) together with batch/regular mode in `LLM_PROCESSING` env var.

Read the below. Your tasks are:
1. Help me get started with Together in a secure way.
2. Design/plan the changes in order to support the new LLM BACKEND. 
3. Build a test pipeline for it including a CI workflow that will be run weekly or manually
4. Document new env vars options and CLAUDE.md


# Project Brief: Batched LLM Pipeline on Together AI

## Goal
Build a Python pipeline for sending batches of 100–1000 one-shot prompts to Qwen models hosted on Together AI, optimized for low cost and privacy, with a clean path to serving fine-tuned LoRA adapters later.

## Provider choice: Together AI
- **Why Together over alternatives:** matches Fireworks on price (~$0.88/1M tokens for Qwen 2.5 72B), but has a cleaner "bring-your-own-LoRA" workflow — upload an adapter from HuggingFace, serve at base-model rates. Qwen 2.5 is a first-class supported base for their multi-LoRA serving.
- **Why not DashScope (Alibaba):** privacy posture is weaker; routes through Alibaba Cloud.
- **Why not DeepInfra/Fireworks:** Fireworks is roughly equivalent (slightly faster inference via FireAttention), DeepInfra has less polished LoRA-upload UX. Together wins on workflow flexibility.
- **Why not self-host on Modal/RunPod yet:** unnecessary complexity for batch sizes of 100–1000; revisit if (a) regulated data requires no-third-party-sees-prompts, or (b) sustained volume exceeds ~10M tokens/day.

## API surface
- OpenAI-compatible chat completions endpoint: `https://api.together.xyz/v1/chat/completions`
- Auth: `Authorization: Bearer $TOGETHER_API_KEY`
- Base model today: `Qwen/Qwen2.5-72B-Instruct`
- Fine-tuned model later: `<username>/<adapter-name>` (same endpoint, same per-token cost, one string change)
- Batch endpoint available at 50% discount with up to 30B tokens per job, async — use when wall-clock doesn't matter.

## Pipeline requirements
1. **Async parallel calls** via `httpx` + `asyncio.Semaphore` for concurrency control. Start at concurrency=32, tunable up to ~128 depending on rate limits.
2. **Resume on crash** — append results to JSONL line-by-line with flush, skip already-completed IDs on restart.
3. **Retries with exponential backoff** on 429s and 5xx (1s, 2s, 4s, 8s).
4. **Per-prompt error isolation** — a failed prompt gets an `"error"` field in output; the rest of the batch keeps running.
5. **Input format:** `prompts.jsonl`, one JSON per line with required `"prompt"` field and optional `"id"`, `"temperature"`, `"max_tokens"`.
6. **Output format:** `results.jsonl`, one JSON per line with `"id"`, `"prompt"`, `"answer"`, `"usage"` (or `"error"`).

## Privacy posture
- Together AI: US-jurisdiction, doesn't train on API traffic, short retention. Acceptable for "private-ish but not regulated" data.
- If data becomes regulated (PII/medical/legal): escalate to self-hosted vLLM on Modal/RunPod (script logic identical — only `API_URL` and `MODEL` change because vLLM speaks the same OpenAI protocol).

## Future-proofing for LoRA fine-tuning
- Fine-tune anywhere (axolotl, unsloth, LlamaFactory, or hosted) producing a standard PEFT adapter.
- **Critical constraint:** the LoRA must be trained on a base that Together already hosts (Qwen 2.5 72B Instruct is fine), otherwise you fall off the cheap multi-LoRA path.
- Upload adapter to Together → assign a name → change the `MODEL` string in the batch script. Same cost as base model.

## What's already decided / not in scope
- **Not using E2B.dev** — it's a sandbox for AI-generated code execution, not an inference provider. Wrong layer for this problem.
- **Not using DashScope** for any sensitive data.
- **Not self-hosting yet** — only revisit when LoRA workflow or scale demands it.
- **Not using the batch endpoint initially** — real-time async parallel is fast enough for 100–1000 prompts and simpler.

## First task for Claude Code
Implement `qwen_batch.py` per the requirements above, targeting Together AI. Include a `prompts.jsonl` example file and a README with the run commands. Set up so swapping to a fine-tuned LoRA later is a one-line change.

ANSWER FROM CLAUDE:
# Plan: Add `custom_on_cloud` LLM backend

## Context

We want to run Qwen (or other OSS models) on a serverless provider like **Together AI** for PreAudit's LLM analysis stage. Together is the chosen first provider because (a) it matches Fireworks on price for Qwen 2.5 72B at ~$0.88/1M tokens, (b) it has a clean bring-your-own-LoRA workflow on top of Qwen 2.5 base models (so we can later swap in a fine-tuned adapter with a one-string model change), and (c) its privacy posture (US jurisdiction, no training on traffic, short retention) is acceptable for our data class.

The current `local` backend already speaks the OpenAI-compatible protocol via the `openai` SDK, just pointed at `http://localhost:11434/v1` with `api_key="not-needed"`. **`custom_on_cloud` is essentially the `local` backend with a real API key, a cloud base URL, and a hosted model name.** We add it as a distinct backend value (rather than overloading `local`) so that:

1. CI/tests can switch on it without colliding with local-dev Ollama usage.
2. Boot-time validation can require its three env vars when selected.
3. Token-usage tracking can attribute cost to a "custom_on_cloud" source.

Batch mode (`LLM_PROCESSING=batch`) is intentionally out of scope for this first cut — it would require implementing the OpenAI-compatible batch flow (file upload + create batch + poll), which differs from Anthropic's Batch API path in `batch_orchestrator.py`. See the follow-up prompt at the end of this plan.

## Task 1 — Together AI onboarding (secure setup)

Steps the **user** runs manually (no code changes here):

1. **Create the account**: sign up at `https://api.together.ai/` with the Certora work email. Enable 2FA on the account.
2. **Provision an API key**: `Settings → API Keys → Create key`. Name it `preaudit-dev` (or `preaudit-ci` for the CI key). Note that Together does **not** support per-key scoping — treat each key as full account access; rotate by deleting and recreating.
3. **Store locally for development**:
   - Add to `~/.zshrc` or to a project-local `.env` file (the project already auto-loads `.env` via `python-dotenv` in `certora_autosetup/utils/llm_util.py:30`). The repo's `.gitignore` already excludes `.env`.
   - Variables:
     ```bash
     export LLM_BACKEND=custom_on_cloud
     export CUSTOM_ON_CLOUD_API_KEY=tgp_v1_...
     export CUSTOM_ON_CLOUD_BASE_URL=https://api.together.xyz/v1
     export CUSTOM_ON_CLOUD_MODEL=Qwen/Qwen2.5-72B-Instruct
     ```
4. **Verify connectivity** without committing the key — one-liner:
   ```bash
   curl -sS https://api.together.xyz/v1/chat/completions \
     -H "Authorization: Bearer $CUSTOM_ON_CLOUD_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"Qwen/Qwen2.5-72B-Instruct","messages":[{"role":"user","content":"reply with the word OK"}],"max_tokens":4}' | jq -r '.choices[0].message.content'
   ```
   Expected: `OK`.
5. **Store for CI**: in GitHub → Repository Settings → Secrets and variables → Actions:
   - Add `CUSTOM_ON_CLOUD_API_KEY` (the CI-specific key).
   - Optionally `CUSTOM_ON_CLOUD_BASE_URL` and `CUSTOM_ON_CLOUD_MODEL` as repo variables (not secrets — they're not sensitive) so they can be overridden per workflow run without redeploying secrets.
6. **Set a spending alert**: in Together's billing dashboard, set a monthly budget cap (e.g. $50 for dev, separate budget for CI). Together supports alert thresholds at 50/75/100%.
7. **Do NOT** bake the key into any Docker image. CI passes it as `env:` at the step level; the existing `test-dummyproject-weekly.yml` pattern shows the right shape.

Security checklist before merging:
- [ ] `.env` not staged (`git status` clean)
- [ ] No occurrence of `tgp_v1_` literal anywhere in tracked files (`grep -r tgp_v1_ . --exclude-dir=.git` returns nothing)
- [ ] CI key is distinct from local-dev key
- [ ] Budget alert is set

## Task 2 — Backend implementation

### Surface area

Two repos. AutoSetup gets all the dispatch logic; PreAudit gets validation, batch-mode rejection, and the CI/test wiring.

### A. AutoSetup repo changes (`/Users/shelly/Certora/AutoSetup`)

**Branch:** `shelly/custom-on-cloud-backend`

**`certora_autosetup/utils/constants.py`** — add three constants alongside the existing `LOCAL_LLM_*` block (around lines 17–21):
```python
CUSTOM_ON_CLOUD_API_KEY_ENV = "CUSTOM_ON_CLOUD_API_KEY"
CUSTOM_ON_CLOUD_BASE_URL_ENV = "CUSTOM_ON_CLOUD_BASE_URL"
CUSTOM_ON_CLOUD_MODEL_ENV = "CUSTOM_ON_CLOUD_MODEL"
```
**No defaults** — when this backend is selected, all three are required (boot-time validation in PreAudit, see Task 2.B).

**`certora_autosetup/utils/llm_util.py`** — the key insight is that `custom_on_cloud` reuses the OpenAI-compatible path. To avoid duplicating ~200 lines of `_local_*` functions:

1. Widen `_get_backend()` return type to `Literal["anthropic", "local", "mock", "custom_on_cloud"]` (line 108) and add a branch:
   ```python
   if backend == "custom_on_cloud":
       if not OPENAI_SDK_AVAILABLE:
           raise RuntimeError("LLM_BACKEND=custom_on_cloud requires the openai package.")
       return "custom_on_cloud"
   ```
2. Add helper `is_openai_compatible_backend()` returning `_get_backend() in ("local", "custom_on_cloud")`. Update existing `is_local_backend()` to keep its single-backend meaning so callers that specifically check for *local* (e.g. retry policy) stay correct.
3. Add `_get_custom_on_cloud_api_key()`, `_get_custom_on_cloud_base_url()`, `_get_custom_on_cloud_model()` reading the new constants. **Fatal** if any is missing (per project style: prefer fatal errors).
4. Refactor `_init_local_client()` / `_init_async_local_client()` into a generic `_init_openai_compatible_client(base_url, api_key, *, async_client)` with the existing local cache. Have the local path pass `api_key="not-needed"` and the new path pass the real key.
5. Update every dispatch site in `call_llm`, `call_llm_structured`, `call_llm_async_structured_cached`, `call_llm_messages`, `call_llm_messages_structured` (lines 668, 719, 795, 869, 968) so that the existing `_local_*` branches fire for both backends. The simplest implementation: rename the `_local_*` functions to `_openai_compat_*` and route both backends through them; pick the right client and model by backend inside the function.
6. **Retry/backoff**: reuse the existing local path's `_local_retry_transient` (simple exponential `2**attempt`). Do **not** add `CERTORA_MAX_RETRIES`/`CERTORA_INITIAL_BACKOFF`/`CERTORA_MAX_BACKOFF` plumbing in this PR — those env vars are documented but not currently wired anywhere; that's a separate cleanup.
7. **Token tracking**: in `token_usage.py` (PreAudit), widen the `source` Literal in `record_api_usage` from `Literal["api", "aicomposer", "claude_agent_sdk", "batch_api"]` to also include `"custom_on_cloud_api"`. Pricing entries can be added later — for now they fall back to zero estimated cost, which is fine for an externally-hosted Qwen.

**Tests in AutoSetup** — add a unit test in `tests/` that monkeypatches `os.environ` with `LLM_BACKEND=custom_on_cloud` plus stubbed URL/key/model, mocks the `openai.OpenAI` constructor, and asserts the dispatch picks up the right client + model. Mirror the structure of any existing local-backend test if present.

### B. PreAudit repo changes (`/Users/shelly/Certora/PreAudit`)

**Branch:** `shelly/custom-on-cloud-backend`

1. **`src/certora_preaudit/preaudit/cli.py:57`** — extend boot validation:
   ```python
   backend = os.environ.get("LLM_BACKEND", "anthropic").lower()
   if backend == "custom_on_cloud":
       required = ("CERTORAKEY", "CUSTOM_ON_CLOUD_API_KEY",
                   "CUSTOM_ON_CLOUD_BASE_URL", "CUSTOM_ON_CLOUD_MODEL")
   else:
       required = ("CERTORAKEY", "ANTHROPIC_API_KEY")
   missing = [v for v in required if not os.environ.get(v)]
   if missing:
       sys.exit(f"Error: required environment variable(s) not set: {', '.join(missing)}")
   ```
   Note: for `custom_on_cloud` we drop the `ANTHROPIC_API_KEY` requirement (it's not used). Mock/local backends already bypass the Anthropic key path via existing code in `llm_util`.

2. **`src/certora_preaudit/generic_checkers/reporting/batch_orchestrator.py:42`** — reject the unsupported combination with a clear pointer to the follow-up prompt:
   ```python
   def is_batch_mode() -> bool:
       batch = os.environ.get("LLM_PROCESSING", "regular").lower() == "batch"
       if batch and os.environ.get("LLM_BACKEND", "").lower() == "custom_on_cloud":
           raise RuntimeError(
               "LLM_PROCESSING=batch is not yet supported with LLM_BACKEND=custom_on_cloud. "
               "Use LLM_PROCESSING=regular, or run with LLM_BACKEND=anthropic for batch."
           )
       return batch
   ```

3. **`tests/integration/test_dummyproject_e2e.py`** — no test code changes needed. The existing `test_preaudit_single_contract` already reads `LLM_BACKEND` from the environment (set by the workflow). It will run unchanged against the new backend when the new CI workflow sets the env vars.

   *Optional polish*: add a `pytestmark = pytest.mark.custom_on_cloud` marker class to allow `-m custom_on_cloud` filtering. Skip if scope grows.

4. **`.github/workflows/test-custom-on-cloud-weekly.yml`** — new workflow file. Copy the structure of `test-dummyproject-weekly.yml`, change:
   - Schedule: `cron: '0 3 * * 1'` (Mon 3am UTC, offset from Sun-2am and Wed-4am)
   - Add `workflow_dispatch` with optional `model` input (default `Qwen/Qwen2.5-72B-Instruct`) so a manual run can A/B different models.
   - Job env:
     ```yaml
     env:
       CERTORAKEY: ${{ secrets.CERTORAKEY }}
       LLM_BACKEND: custom_on_cloud
       CUSTOM_ON_CLOUD_API_KEY: ${{ secrets.CUSTOM_ON_CLOUD_API_KEY }}
       CUSTOM_ON_CLOUD_BASE_URL: ${{ vars.CUSTOM_ON_CLOUD_BASE_URL || 'https://api.together.xyz/v1' }}
       CUSTOM_ON_CLOUD_MODEL: ${{ inputs.model || vars.CUSTOM_ON_CLOUD_MODEL || 'Qwen/Qwen2.5-72B-Instruct' }}
     ```
   - Run only the single-contract variant (`test_preaudit_single_contract`, ~60min on SimpleVault). The all-contracts variant stays Anthropic-only for now to avoid blowing the Together budget on every weekly run.
   - Timeout: 90 minutes (slightly more than the Anthropic equivalent to absorb Qwen latency variance).

5. **`CLAUDE.md`** — add a new sub-table under "LLM Configuration":

   | Variable | Purpose | Default |
   |---|---|---|
   | `CUSTOM_ON_CLOUD_API_KEY` | Bearer token for an OpenAI-compatible hosted backend (e.g. Together AI). Required when `LLM_BACKEND=custom_on_cloud`. | None (fatal if missing) |
   | `CUSTOM_ON_CLOUD_BASE_URL` | Base URL for the hosted backend (e.g. `https://api.together.xyz/v1`). | None (fatal if missing) |
   | `CUSTOM_ON_CLOUD_MODEL` | Model identifier passed to the backend (e.g. `Qwen/Qwen2.5-72B-Instruct` or a fine-tuned adapter path). | None (fatal if missing) |

   Also update the `LLM_BACKEND` row to add `"custom_on_cloud"` as a valid value.

### Critical files to modify

- `~/Certora/AutoSetup/certora_autosetup/utils/constants.py` (+3 lines)
- `~/Certora/AutoSetup/certora_autosetup/utils/llm_util.py` (Literal type widening, new branch in `_get_backend`, refactor `_local_*` → `_openai_compat_*`, dispatch sites at lines 668, 719, 795, 869, 968)
- `~/Certora/AutoSetup/tests/` (new unit test for the dispatch)
- `~/Certora/PreAudit/src/certora_preaudit/preaudit/cli.py` (boot validation at line 57)
- `~/Certora/PreAudit/src/certora_preaudit/generic_checkers/reporting/batch_orchestrator.py:42` (batch+custom_on_cloud rejection)
- `~/Certora/PreAudit/src/certora_preaudit/generic_checkers/reporting/token_usage.py` (widen `source` Literal)
- `~/Certora/PreAudit/.github/workflows/test-custom-on-cloud-weekly.yml` (new)
- `~/Certora/PreAudit/CLAUDE.md` (env var docs)

### Existing utilities to reuse

- `_init_local_client` / `_init_async_local_client` in `llm_util.py:140-156` — refactor to the generic OpenAI-compatible initializer
- `_local_retry_transient` / `_local_retry_transient_async` in `llm_util.py:193-223` — reuse as-is for the new backend
- `_anthropic_messages_to_openai` in `llm_util.py:158-190` — already converts messages correctly for any OpenAI-compatible backend
- `load_dotenv()` call in `llm_util.py:30-36` — already auto-loads `.env` for local dev

## Task 3 — Test pipeline

**Already covered above** (workflow file `.github/workflows/test-custom-on-cloud-weekly.yml`). To summarize the test pipeline shape:

- **Trigger**: weekly cron (Mon 3am UTC) + `workflow_dispatch` (with optional `model` input).
- **Body**: runs `test_dummyproject_e2e.py::test_preaudit_single_contract` against SimpleVault, with `LLM_BACKEND=custom_on_cloud` and the three required env vars set from secrets/vars.
- **Pass criteria** (existing test): preaudit completes, HTML report is generated, report contains findings sections, no crashes in the LLM analysis stage.
- **No mocking**: this is a real-API test. We accept the Together cost per run (~$1–$3 estimated for SimpleVault on Qwen 72B).
- **Failure mode**: if Together is down or the key is exhausted, the test fails loud — that's correct; it tells us the integration is broken.

### Local manual run

To run the new workflow's logic locally before merging:
```bash
cd /Users/shelly/Certora/PreAudit
export LLM_BACKEND=custom_on_cloud
export CUSTOM_ON_CLOUD_API_KEY=...
export CUSTOM_ON_CLOUD_BASE_URL=https://api.together.xyz/v1
export CUSTOM_ON_CLOUD_MODEL=Qwen/Qwen2.5-72B-Instruct
python -m pytest tests/integration/test_dummyproject_e2e.py::TestDummyProjectE2E::test_preaudit_single_contract -v -s
```

## Task 4 — Documentation

Two files:

1. **`CLAUDE.md`** — add the three new env vars and update the `LLM_BACKEND` row (see Task 2.B step 5 above).
2. **`docs/followups/custom_on_cloud_batch_mode.md`** — new file holding the verbatim prompt for the future batch-mode follow-up (see "Follow-up prompt" section below).

## Verification

End-to-end verification once both PRs are open:

1. **AutoSetup unit test** runs in its CI and passes (`pytest tests/test_custom_on_cloud_backend.py`).
2. **PreAudit unit tests** still pass: `python -m pytest tests/unit/ -v` — no regression.
3. **PreAudit type check**: `pyright src/` — clean (the widened `Literal` may surface assignment errors; fix at the touched sites only).
4. **Local smoke test**: from PreAudit repo with Together env vars set,
   ```bash
   python -m certora_preaudit.preaudit src/Token.sol
   ```
   completes and writes a report under `.certora_internal/`.
5. **CI smoke test**: trigger `test-custom-on-cloud-weekly.yml` manually via `gh workflow run test-custom-on-cloud-weekly.yml`. Confirm green within ~90min.
6. **Batch rejection works**: run with `LLM_BACKEND=custom_on_cloud LLM_PROCESSING=batch python -m certora_preaudit.preaudit src/Token.sol` and assert it exits with the helpful error message.
7. **Validation works**: run `LLM_BACKEND=custom_on_cloud python -m certora_preaudit.preaudit src/Token.sol` without the three new env vars set; assert the CLI exits with the missing-vars message.

## PR sequencing

Two PRs (AutoSetup first, PreAudit follows):

1. **AutoSetup**: `shelly/custom-on-cloud-backend` → tag a new pre-release version (e.g. `0.2.0`).
2. **PreAudit**: `shelly/custom-on-cloud-backend` — bump the autosetup dependency pin to the new version, add CLI validation + batch rejection + workflow + docs.

Do **not** merge PreAudit until AutoSetup is tagged and the dependency pin is resolvable.

---

## Follow-up prompt — add batch mode for `custom_on_cloud`

> Save this as `docs/followups/custom_on_cloud_batch_mode.md` in PreAudit. To execute later, paste it as a new Claude conversation.

```
Context: PreAudit supports LLM_BACKEND=custom_on_cloud for OpenAI-compatible cloud
backends (e.g. Together AI, Fireworks, vLLM on Modal). Currently only
LLM_PROCESSING=regular works for this backend; LLM_PROCESSING=batch is rejected at
boot in src/certora_preaudit/generic_checkers/reporting/batch_orchestrator.py.

Goal: Add OpenAI-compatible batch processing so LLM_PROCESSING=batch works with
LLM_BACKEND=custom_on_cloud. Together AI offers a 50% discount on its batch
endpoint; the protocol is: (1) upload a JSONL file of request objects via
POST /v1/files, (2) create a batch via POST /v1/batches referencing the file id,
(3) poll GET /v1/batches/{id} until status is "completed" or "failed", (4) GET
/v1/files/{output_file_id}/content for results.

Tasks:
1. In src/certora_preaudit/generic_checkers/reporting/batch_orchestrator.py,
   refactor _submit_and_poll and _track_batch_usage so the Anthropic-specific
   client.messages.batches.* calls live behind a small interface
   (BatchClient with submit/poll/results methods). Add an OpenAI-compatible
   implementation (TogetherBatchClient or OpenAICompatibleBatchClient) that uses
   the openai SDK's files.create + batches.create + batches.retrieve. Pick the
   right implementation in is_batch_mode/run_batch_analysis based on
   _get_backend().
2. The request format for OpenAI batches is different from Anthropic's.
   build_batch_request_params in autosetup/utils/llm_util.py needs an
   OpenAI-compatible sibling — build_openai_batch_request_params — that emits
   {"custom_id": "...", "method": "POST", "url": "/v1/chat/completions",
   "body": {...}} per line in the upload JSONL.
3. Token tracking: parse usage from each result row's body.usage field; record
   via get_global_tracker().record_api_usage(... source="custom_on_cloud_batch").
   Add the new source to the Literal in token_usage.py.
4. Remove the rejection in batch_orchestrator.is_batch_mode (the function we
   added in the previous PR).
5. Update CLAUDE.md to note that LLM_PROCESSING=batch now works with both
   anthropic and custom_on_cloud backends, with the caveat that the
   custom_on_cloud backend must point to a provider supporting OpenAI-batch
   protocol (Together does; raw Ollama does not).
6. Extend the weekly workflow .github/workflows/test-custom-on-cloud-weekly.yml
   with a matrix step that runs once with LLM_PROCESSING=regular and once with
   LLM_PROCESSING=batch.

Constraints:
- Keep the BatchClient interface tight — submit/poll/results — so future
  providers (Anthropic-style, OpenAI-style, self-hosted) can be added without
  changing run_batch_analysis.
- Reuse _compute_content_hash + the existing cache layer for batch results.
- Don't break the existing Anthropic batch path; add tests that both paths
  produce equivalent per-finding outputs on a fixture.
```


------------------