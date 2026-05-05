<!-- feature-loop: 6b0f0632 -->

=== /plan #1 ===

We are going back to the containerization feature.
We need to be able to generate the images from CI and upload them to ghcr.
Then, we need to have a test workflow that checks that a simple dummy run (e.g. a-la dummyproject-integration) fully works, but instead of invoking the script directly, it should test two kinds of workflows:
1. run only preaudit docker image in a sterile environment with only docker
2. run first autobuild image, then 'upload' results like s3_sync does, then invoke the preaudit image on this output.
Let's focus on #1 for now.

In this plan, we focus only on setting up the ci workflows that build both images and publish them. In general, we want to release only when tags on main are created. For testing, we also want to be able to manually dispatch the task so that we could operate on the test images.

Explore the image definitions.
Plan the CI workflow for building them.

  ⎿  · The `Dockerfile.build` references `FROM cvt-base AS solc-source` which is a placeholder. How should we handle this for the CI build? → so cvt-base is actually 
     called cvt-image, and you can see how it gets built here ~/certora/containers/.circleci/config.yml, the image is defined in ~/certora/containers/cvt-image.      
     you'll need to authenticate the AWS ECR to pull it. put placeholders for the secrets, and remind me later what to add to make pulling work.    

went with cvt-executables-linux at the end.


Plan: CI Workflow for Building & Publishing Docker Images to GHCR                                                                                                    

 Context

 PreAudit has a two-container SaaS architecture (Dockerfile.build and Dockerfile.preaudit) that needs CI-automated builds published to GHCR. Release images are
 published on version tags on main; test images can be built via manual dispatch.

 Files to Create/Modify

 ┌──────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────┐
 │                 File                 │                                          Action                                           │
 ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ .github/workflows/docker-publish.yml │ Create — new workflow                                                                     │
 ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ Dockerfile.build                     │ Modify — add BuildKit SSH mount, replace cvt-base with git clone of cvt-executables-linux │
 ├──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ Dockerfile.preaudit                  │ Modify — add BuildKit SSH mount, add solc binaries via git clone                          │
 └──────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────┘

 1. Solc Binaries Strategy

 Instead of pulling from AWS ECR's cvt-image, clone Certora/cvt-executables-linux (private repo) during Docker build using SSH mount and copy solcX.YY binaries from
 there. This approach:
 - Needs only one extra deploy key (DEPLOY_KEY_CVT_EXECUTABLES)
 - No AWS ECR authentication needed
 - Both images get solc binaries the same way

 2. Dockerfile Modifications

 Both Dockerfiles need # syntax=docker/dockerfile:1 at the top and --mount=type=ssh on RUN commands that need private repo access.

 Dockerfile.build

 - Add # syntax=docker/dockerfile:1 header
 - Remove the FROM cvt-base AS solc-source stage and COPY --from=solc-source line
 - Add a RUN --mount=type=ssh step that clones cvt-executables-linux and copies solc binaries:
 RUN --mount=type=ssh \
     mkdir -p /root/.ssh && ssh-keyscan github.com >> /root/.ssh/known_hosts && \
     git clone --depth 1 git@github.com:Certora/cvt-executables-linux.git /tmp/cvt-exec && \
     cp /tmp/cvt-exec/solc* /usr/local/bin/ && \
     rm -rf /tmp/cvt-exec
 - Change pip install to use --mount=type=ssh:
 RUN --mount=type=ssh \
     pip install --no-cache-dir -e . && pip install --no-cache-dir boto3
 - (ssh-keyscan + known_hosts already set up in the solc step above)

 Dockerfile.preaudit

 - Add # syntax=docker/dockerfile:1 header
 - Add same solc clone step (both images need solc)
 - Change pip install to use --mount=type=ssh

 3. Workflow: .github/workflows/docker-publish.yml

 Triggers

 - push.tags: ["v*"] — release builds on version tags
 - workflow_dispatch with optional push boolean input (default true)

 Permissions

 - contents: read, packages: write

 Job: docker (matrix strategy)

 Matrix entries:

 ┌────────────────┬─────────────────────┐
 │   image name   │     dockerfile      │
 ├────────────────┼─────────────────────┤
 │ preaudit-build │ Dockerfile.build    │
 ├────────────────┼─────────────────────┤
 │ preaudit       │ Dockerfile.preaudit │
 └────────────────┴─────────────────────┘

 Steps

 1. Checkout with submodules: recursive (for vendor/wala-solidity)
 2. SSH setup — write all deploy keys, configure ssh hosts + agent. Keys needed:
   - Existing: DEPLOY_KEY_AUTOSETUP, DEPLOY_KEY_AUTOCVL, DEPLOY_KEY_PROVER_OUTPUT_UTILITY, DEPLOY_KEY_CERTORA_CLOUD_CLI, DEPLOY_KEY_AICOMPOSER, DEPLOY_KEY_TIMEOUTER,
  DEPLOY_KEY_GRAPHCORE
   - New: DEPLOY_KEY_CVT_EXECUTABLES — for cloning Certora/cvt-executables-linux
 3. Set up Docker Buildx (docker/setup-buildx-action@v3)
 4. GHCR login (docker/login-action@v3 with secrets.GITHUB_TOKEN)
 5. Docker metadata (docker/metadata-action@v5):
   - Image: ghcr.io/certora/${{ matrix.image }}
   - Tags: latest (on tag push only), sha-<short>, semver {{version}}, semver {{major}}.{{minor}}
 6. Build and push (docker/build-push-action@v6):
   - ssh: default=${{ env.SSH_AUTH_SOCK }}
   - push: true on tag push; controlled by input on dispatch

 Tagging strategy

 ┌───────────────────┬─────────────────────────────────┐
 │      Trigger      │              Tags               │
 ├───────────────────┼─────────────────────────────────┤
 │ push tag v1.2.3   │ 1.2.3, 1.2, latest, sha-abc1234 │
 ├───────────────────┼─────────────────────────────────┤
 │ workflow_dispatch │ sha-abc1234 only                │
 └───────────────────┴─────────────────────────────────┘

 4. Secrets to Add (reminder for user)

 - Already exist (used by test.yml): all DEPLOY_KEY_* secrets, GITHUB_TOKEN (automatic)
 - New: DEPLOY_KEY_CVT_EXECUTABLES — deploy key for Certora/cvt-executables-linux

 5. Verification

 1. Push the branch, trigger workflow_dispatch with push: false to verify the build succeeds
 2. Trigger with push: true to verify GHCR upload
 3. Verify images are accessible: docker pull ghcr.io/certora/preaudit:sha-<xxx>
 4. Tag a version to verify the full release flow


=== /question ===
 1. Push the branch, trigger workflow_dispatch with push: false to verify the build succeeds
 2. Trigger with push: true to verify GHCR upload
 3. Verify images are accessible: docker pull ghcr.io/certora/preaudit:sha-<xxx>
 4. Tag a version to verify the full release flow

=== /plan #2 ===
we need to integrate a local version of chromadb for the analyzer from AIComposer.
Look at the process here https://github.com/Certora/AIComposerRAGDBPublish
locally in ~/certora/AIComposerRAGDBPublish
you would need to first run it within the ci in that repo, then in the build process integrate it.

=== /plan #2.1 ===
I am not sure the github_token will successfully read the package for rag db.

Part 1 (AIComposerRAGDBPublish CI)

 1. Push workflow, trigger workflow_dispatch
 2. Verify GitHub Release is created with both tarballs
 3. Verify tarballs contain valid ChromaDB files (chroma.sqlite3, fts_index.db, VERSION.json)

 Part 2 (PreAudit Docker)

 1. Rebuild preaudit image with RAG DB bundled
 2. Verify CERTORA_RAG_DB is set and points to valid ChromaDB
 3. Run a test analysis to confirm RAG search works

=== /plan #2.2 ===
let's test rag db access works from docker. we need a dummy query to the analyzer and invoke it via the docker, and see we get a decent answer. show me the outputs.

=== /plan #3 ===
Now, let's focus on planning the testing for bullet 1 out of plan #1. 
It should be runnable both locally and in CI. it should run the SimpleVault contract of the dummy project.


=== /plan #3.1 ===
let's add a test of AIComposer chromadb access like we did in #2.2.

=== /plan #3 ===
After we completed plan #1 and #2 and just the first bullet out of #1, we need to plan the testing of the scenario described in the second bullet on the same contract as in plan #2. 