=== /plan megaclouddev ===
You are a leading software architect with deep understanding of cloud, deployments, devops, ci, java, python, rust. 
Due to unfortunate circumstances, soon we'll have fewer people to help build the overall cloud infrastructure of Certora and the Certora Prover. It consists of the Prover which we developed for about 7-8 years now, and the newly,
  not yet launched AISS which is now simply AutoProver.

I want to show you all the relevant repos and explain everything I know and remember about them. 
Your task is to build here in this folder either a a mega folder with all cloned repos from which you'll work and correlate all tasks. Each repo may have one or more worktrees, working on several tasks at once in parallel via different claude sessions.
In each task, I expect to be able to fully plan, implement, test, and get a visual manual validation by myself that the change works, create a CI test (or at least the option to make such a test), and deploy it to either dev, stg, or prod (after sufficient gating and tests, that are likely not done locally in the stg/prod case at least).

Some of these repos are soon to be open source, and some will never be.
All of the repos are hosted in Github under Certora organization.

*Core repos - logic, but no cloud*
- EVMVerifier - the core Certora Prover + certora-cli python package.
- AIComposer - the core of AutoProver - an agentic system for writing specs for solidity code. It is currently Open-source
- graphcore - a dependency of AutoProver. It is currently open source, and AIComposer imports it as a submodule.
- AutoSetup - it will be folded into AIComposer as a separate module in the coming future. It helps prepare the Prover runs by finding working configurations and specs with appropriate summaries and links.
- Preaudit - a wrapper around the Certora Prover that runs AutoSetup, injects a bunch of builtin-rules and auto-generated rules, and analyzes results with LLMs. Has its own API for invoking from the cloud, thus contains several modules for running it properly from the cloud. Later on, it will be also open-sourced (non-cloud parts).
- AIAutoProver a wrapper around Autosetup + AIComposer since they are currently co-depended. In the future it will only contain the cloud-related dockerfiles.
- wala-solidity - a Solidity static analyzer, frontend for WALA, with a rounding error analysis we use as part of Preaudit.
- ProverOutputUtility - a dependency of Autosetup. Helps facilitate extraction of information from the certora cloud.
- zeus-llm-orchestrator - an AI Auditor backend

*Cloud related repos*
- data-processors - the entire db management and some API backend logics
- Containers - dockerfiles for the certora prover images running on AWS Batch
- cloud-infrastructure - CDKs and specs of the overall AWS services used to run the Prover and Autoprover
- httpHandlerContainer - legacy APIs running on AWS Beanstalk
- certora-cloud-cli - a collection of utilities to interact with the certora cloud. not open source.
- certora-cloud-cli-pub - a lean version of certora-cloud-cli containing only the part allowing to authenticate with the APIs (e.g. data-api.certora.com)
- backendless-api - AWS Lambdas and API Gateway configurations to handle Prover, AutoProver related requests
- zeus-saas - the webapp, frontend for zeus-llm-orchestrator historically, hosts also Autoprover and effectively becomes autoprover webapp. hosted on railway.
- mutation_svelte - the frontend the Prover. legacy code.

*Deployments*
Every week there is an update from stg to prod of a prover container I believe it happens via Containers repo.
Prover (EVMVerifier) that are tagged have their jar uploaded to our artifacts account in AWS.
A certora-cli release (also in EVMVerifier) happens when we tag, and on the cloud the right jar is invoked based on the certora-cli version that invoked it.
The Prover container knows how to fetch the matching jar from the artifacts account. It is not baked into the container if I remember correctly.
I do not know what is the deployment process for the cloud infrastructure itself: job definitions, machine types, queue definitions etc.

With AutoProver (AISS historical name) I only know the deployment is similar to Prover in the sense that we upload containers to ECR and they already contain the relevant part when built. Thus if we trigger a new container build and push to ECR on the right tag it is likely the API will invoke it. As far as I know it was only deployed on dev.

[enacted on fable with max]

----------------

  1. Who runs the manual deploys for cloud-infrastructure / data-processors / aws-templates today, and is there a runbook beyond the repo docs? (Process knowledge — important given the team shrinkage.)
  2. Is AISS deployed beyond dev? CDK defines stg/prod stacks; checking needs aws cloudformation describe-stacks per account. You believe dev only — easy to confirm once you want me to run read-only AWS calls.
  3. httpHandlerContainer prod — no prod path in the repo; how its Beanstalk env gets updated and what still depends on it.
  4. Railway topology for zeus-saas/orchestrator — projects, environments, access. Lives in Railway, not git.
  5. Prover promotion cadence — confirmed manual (no scheduler); the who/when/checks is team process.
  6. Secrets ownership — org-level CI secrets (CIRCLE_TOKEN, OIDC roles, DEPLOY_KEY_*, opscertora PyPI) need an owner/rotation inventory; a resilience task worth scheduling.
