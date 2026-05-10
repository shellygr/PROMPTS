# cloud knowledge

---                                                                                                            
  Research Summary: Certora Cloud Infrastructure & AISS API Effort Analysis
                                                                                                                 
  1. Cloud Infrastructure Overview
                                                                                                                 
  Environments:   
  - Production: prover.certora.com — production AWS account
  - Staging: vaas-stg.certora.com — staging AWS account                                                          
  - Integration: dev account (separate AWS account per Option 3 deployment model)
                                                                                                                 
  Core Architecture (Prover flow):                                                                               
  1. Python CLI (certora-cli) POSTs to /v2/cli/verify with job params
  2. Lambda handler (cli_verify_v2 in backendless-api repo) validates + stores in DynamoDB                       
  3. Returns a pre-signed S3 URL; CLI uploads zip to S3 (certora-dev for staging, certora-prod for production)
  4. EventBridge fires on S3 upload → SQS queue (submit_job_event_queue.fifo)                                    
  5. submit_job Lambda consumes SQS, submits AWS Batch job, updates DynamoDB                                     
  6. Two DBs maintained in sync: DynamoDB (NoSQL) + RDS PostgreSQL (streamed)                                    
  7. Batch runs container from ECR (dev-prover image, built via CircleCI from ProverContainer repo)              
  8. Frontend is deployed to S3 + CloudFront per environment (separate AWS accounts)                             
                                                                                                                 
  2. Authentication (Cognito)                                                                                    
                                                                                                                 
  User Login (PKCE flow):                                                                                        
  1. FE calls /dashboard/whoAmI → if 403, redirects to Cognito login
  2. FE generates codeVerifier + codeChallenge (SHA256), stores verifier in session storage                      
  3. Redirects to Cognito hosted UI with response_type=code, code_challenge_method=S256    
  4. After login, Cognito redirects back with code query param                                                   
  5. FE sends code + code_verifier to /auth/callback/login → BE exchanges for tokens
  6. Three cookies: user, certoraToken (short-lived), refreshToken                                               
  7. certoraToken expired → 401 → FE calls /refresh; both expired → 403 → re-login                               
                                                                                                                 
  Machine-to-Machine (service-to-service):                                                                       
  - Separate Cognito App Client (machine-to-machine)                                                             
  - client_credentials grant type                                                                                
  - Basic auth with base64(client_id:client_secret) from Parameter Store
  - Scopes: backend/* (full) or backend/read                                                                     
  - Endpoint: auth-stg-certora.auth.us-west-2.amazoncognito.com/oauth2/token                                     
                                                                                                                 
  Staging access: Controlled by custom:stgUserId attribute in Cognito — users without it can log into production 
  but not staging.                                                                                               
                                                                                                                 
  3. GitHub App (certora-run-action)                                                                             
                                                                                                               
  - Used for CI/CD integration (triggering Prover runs from GitHub Actions)                                      
  - Requires CERTORAKEY (Certora API key)                                                                      
  - Blog post in progress, "waiting for 2 more successful client integrations beyond EigenLayer"                 
  - For AISSK Milestone 1: the plan is to integrate a GitHub App to let users trigger the starter kit through a  
  GitHub Action, with build happening in the action and outputs uploaded to S3                                   
                                                                                                                 
  4. AISSK Technical Design (Milestone 1)                                                                        
                                                                                                               
  The design doc describes a simplified architecture:                                                            
  - Trigger: GitHub Action (build) → uploads zip to S3                                                         
  - Execution: S3 upload triggers Batch job containing Python app + local SQLite + local ChromaDB                
  - Output: Static HTML uploaded to S3, served via API                                           
  - DB tables: preaudit_job, build_job, repositories (in existing PostgreSQL)                                    
  - Auth (open question): M2M auth with Cognito being researched; question of whether to reuse existing user pool
   or create new client app                                                                                      
  - Infrastructure TODO: S3 bucket, EventBridge rules, SQS queues + DLQs, multiple Lambdas (builder trigger,     
  executor trigger, status reporting), Batch job definitions, new DB tables                                      
                                                                                                                 
  ---                                                                                                          
  Effort Assessment: AISS API Endpoints                                                                          
                                                                                                                 
  The API spec at ~/Certora/PreAudit/mockups/api_endpoints.md defines ~35 endpoints across 10 sections. Here's my
   breakdown:                                                                                                    
                                                                                                               
  What Can Be Reused from Existing Infrastructure                                                                
                                                                                                               
  ┌────────────────────────────┬───────────┬────────────────────────────────────────────────────────────────┐    
  │         Component          │  Reuse    │                             Notes                              │  
  │                            │   Level   │                                                                │    
  ├────────────────────────────┼───────────┼────────────────────────────────────────────────────────────────┤  
  │ Cognito JWT auth (PKCE     │ High      │ Same user pool, same cookie flow. Just need AISS subscription  │ 
  │ flow)                      │           │ gate middleware                                                │    
  ├────────────────────────────┼───────────┼────────────────────────────────────────────────────────────────┤ 
  │ API Gateway + Lambda       │ High      │ Same backendless-api CDK pattern                               │    
  │ pattern                    │           │                                                                │    
  ├────────────────────────────┼───────────┼────────────────────────────────────────────────────────────────┤ 
  │ S3 for inputs/outputs      │ High      │ New bucket but same pattern                                    │    
  ├────────────────────────────┼───────────┼────────────────────────────────────────────────────────────────┤    
  │ AWS Batch for job          │ High      │ Same pattern, new job definition + container                   │ 
  │ execution                  │           │                                                                │    
  ├────────────────────────────┼───────────┼────────────────────────────────────────────────────────────────┤  
  │ DynamoDB/RDS dual-store    │ Medium    │ New tables, but existing streaming infra                       │    
  ├────────────────────────────┼───────────┼────────────────────────────────────────────────────────────────┤    
  │ Frontend auth              │ Full      │ Already exists, just reused                                    │
  │ (whoAmI/refresh)           │           │                                                                │    
  └────────────────────────────┴───────────┴────────────────────────────────────────────────────────────────┘  
                                                                                                                 
  What's New / Significant Work                                                                                  
  
  Work Area: Subscription & Billing (Stripe)                                                                     
  Endpoints: 5 endpoints + webhook                                                                             
  Effort: Large                                                                                                  
  Commentary: Stripe integration is entirely new. Need Stripe SDK, webhook validation, subscription state    
  machine,                                                                                                       
    credit tracking, overage billing. This is the single largest new component.                                  
  ────────────────────────────────────────                                                                   
  Work Area: Repository CRUD + GitHub integration                                                                
  Endpoints: 7 endpoints + webhook                                                                             
  Effort: Large                                                                                                  
  Commentary: GitHub App installation validation, repo connection flow, webhook handler for push/installation
    events, auto-run triggering. Much of this is new domain logic — the existing GH App (certora-run-action) does
                                                                                                               
    simpler things.                                                                                              
  ────────────────────────────────────────
  Work Area: Runs & Verification                                                                                 
  Endpoints: 8 endpoints                                                                                       
  Effort: Large
  Commentary: POST /runs is the core orchestration: credit validation, S3 upload, Batch job submission, status
    tracking. The SSE progress stream is architecturally challenging — API Gateway has a 29s timeout, so  you'll
    need either WebSocket API, ALB→ECS, or short-polling fallback.
  ────────────────────────────────────────
  Work Area: Findings & Feedback                                                                                 
  Endpoints: 5 endpoints
  Effort: Medium                                                                                                 
  Commentary: New DB schema (fingerprinting system), but CRUD is straightforward. The diff endpoint (comparing 
    findings across runs) is non-trivial.
  ────────────────────────────────────────
  Work Area: Branch/Contract Config                                                                              
  Endpoints: 6 endpoints
  Effort: Small-Medium                                                                                           
  Commentary: Standard CRUD, but URL-encoding branch names with / adds edge cases. Contract auto-detection     
    (/contract-suggestions) requires parsing build artifacts.
  ────────────────────────────────────────
  Work Area: Usage & Config                                                                                      
  Endpoints: 3 endpoints
  Effort: Small                                                                                                  
  Commentary: Aggregation queries over run/credit data                                                         
  ────────────────────────────────────────
  Work Area: Report serving                                                                                      
  Endpoints: 3 endpoints (/report, /sources, /roundabout)
  Effort: Medium                                                                                                 
  Commentary: Need S3 pre-signed URL generation, XSS sanitization for HTML output, source file access control  
  ────────────────────────────────────────
  Work Area: Infrastructure (IaC)                                                                                
  Endpoints: N/A
  Effort: Large                                                                                                  
  Commentary: S3 bucket + prefixes, 2 EventBridge rules, 2 SQS + DLQ pairs, 3+ Lambdas (builder trigger, executor

    trigger, status), 2 Batch job definitions, DB migrations, CDK stack

  Effort Summary                                                                                                 
  
  ┌──────────────────┬────────────────┬────────────────────────┐                                                 
  │     Priority     │ Endpoint Count │    Estimated Effort    │                                               
  ├──────────────────┼────────────────┼────────────────────────┤                                                 
  │ P0 — MVP         │ ~12 endpoints  │ 8-12 weeks (2-3 devs)  │
  ├──────────────────┼────────────────┼────────────────────────┤                                                 
  │ P1 — Core        │ ~10 endpoints  │ 4-6 weeks additional   │                                                 
  ├──────────────────┼────────────────┼────────────────────────┤                                                 
  │ P2 — Enhancement │ ~7 endpoints   │ 3-4 weeks additional   │                                                 
  ├──────────────────┼────────────────┼────────────────────────┤                                                 
  │ Total            │ ~29+ endpoints │ 15-22 weeks (2-3 devs) │                                               
  └──────────────────┴────────────────┴────────────────────────┘                                                 
  
  Key Risk Areas & Blockers                                                                                      
                                                                                                               
  1. Stripe integration — No existing payment infrastructure. This is greenfield: customer portal, webhook       
  handling, subscription state transitions, credit ledger. Budget ~3-4 weeks alone for this.
  2. SSE / real-time progress — API Gateway's 29s HTTP timeout makes Server-Sent Events impractical without      
  architectural changes. Most pragmatic approach for MVP: short-polling fallback (GET /runs/{id} with status     
  field), deferring SSE to P1.
  3. M2M Authentication — Still in research per the design doc. The AISSK flow (GH Action → S3 → Batch) needs a  
  non-interactive auth path. The existing client_credentials M2M flow exists for service-to-service, but         
  extending it to per-user context (which user triggered this run?) needs design work.
  4. Multi-tenant isolation — The design doc explicitly raises the question of managing users across products.   
  Currently each product has somewhat independent user management. The API spec assumes a unified user with      
  subscription gating, which requires backend changes to how user scoping works.
  5. GitHub App scope expansion — The existing certora-run-action app is built for Prover CI. AISS needs richer  
  repo access (reading contract files, branch listing, push event monitoring, auto-run). Either expand the       
  existing app's permissions or create a new one — both have implications.
  6. Builder container — The spec assumes a two-stage flow (Builder + Executor). Building user code in the cloud 
  has security implications (arbitrary code execution during forge build). The design doc flagged this. Needs    
  strict container isolation.
                                                                                                                 
  Bottom Line                                                                                                  

  The API surface is well-designed and maps cleanly onto the existing Certora cloud patterns (API Gateway →      
  Lambda → S3/Batch). About 40-50% of the infrastructure is reusable. The three big new domains are:
  - Payments (Stripe) — entirely new                                                                             
  - GitHub App integration (repos/branches/webhooks) — partially new                                             
  - Job orchestration (two-stage builder/executor) — extends existing Batch pattern
                                                                                                                 
  For a team of 2-3 backend engineers familiar with the existing backendless-api codebase, I'd estimate P0 MVP in
   ~10 weeks, full API in ~18-20 weeks, assuming the infrastructure (CDK, Batch definitions, DB migrations) is   
  done in parallel by the Cloud/DevOps team.                                                                     
                                                                                                                 
✻ Churned for 2m 35s                                                                                           

❯ Holy Molly!!! this is a lot!! we have 3 weeks to meet the deadline and we need the full thing. If those 3      
backend engineers are claude masters - how long will it take then?                                               
                                                                                                                 
⏺ Great question. Let me be realistic about this.                                                                
                                                                                                               
  With Claude-Augmented Engineers (3 devs, 3 weeks)                                                              
   
  Claude can massively accelerate the boilerplate-heavy parts of this work:                                      
                  
  ┌───────────────────────────────────┬───────────┬─────────┬───────────────────────────────────────────────┐    
  │             Work Area             │ Without   │  With   │                      Why                      │ 
  │                                   │  Claude   │ Claude  │                                               │    
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤ 
  │ CRUD endpoints (repos, branches,  │ 6-8 weeks │ 1-2     │ Straightforward DB models + Lambda handlers — │    
  │ contracts, config, findings)      │           │ weeks   │  Claude generates these near-perfectly        │    
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤ 
  │                                   │           │ 1-1.5   │ Well-documented API, tons of training data.   │    
  │ Stripe integration                │ 3-4 weeks │ weeks   │ Webhook handler, subscription state machine   │    
  │                                   │           │         │ are formulaic                                 │
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤    
  │ Infrastructure (CDK stacks, SQS,  │ 3-4 weeks │ 1-1.5   │ Existing patterns in backendless-api to crib  │
  │ EventBridge, Batch defs)          │           │ weeks   │ from                                          │
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤    
  │ DB migrations (new tables,        │ 1-2 weeks │ 2-3     │ Mechanical                                    │
  │ Alembic/SQLAlchemy)               │           │ days    │                                               │    
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤    
  │ GitHub webhook + repo integration │ 2-3 weeks │ 1 week  │ GitHub App SDK is well-known                  │
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤    
  │ Report/source serving (S3         │ 1-2 weeks │ 3-4     │ Standard patterns                             │
  │ pre-signed, XSS sanitization)     │           │ days    │                                               │    
  ├───────────────────────────────────┼───────────┼─────────┼───────────────────────────────────────────────┤
  │ Run orchestration + progress      │ 2-3 weeks │ 1-1.5   │ This has real logic — credit validation,      │    
  │ tracking                          │           │ weeks   │ idempotency, Batch submission                 │    
  └───────────────────────────────────┴───────────┴─────────┴───────────────────────────────────────────────┘
                                                                                                                 
  Revised total: ~6-8 weeks of "human-equivalent" work → fits in 3 calendar weeks with 3 devs.                   
   
  But here's what will actually eat the 3 weeks                                                                  
                  
  The hard parts are not code generation — they're decisions and integration:                                    
                  
  1. SSE vs polling — Just pick polling for MVP. Don't bikeshed. That alone saves a week.                        
  2. M2M auth — Still "in research." Someone needs to make a call, wire it up, and test it against real Cognito.
  ~2-3 days of real human debugging regardless.                                                                  
  3. Testing against real AWS — CDK deploys, Batch job definitions, EventBridge rules... Claude can write the IaC
   but someone has to deploy it, hit real errors, and iterate. This is the bottleneck.                           
  4. Builder security isolation — Can be deferred to post-launch if you only support pre-built zips (skip the
  sources/ path for now).                                                                                        
                  
  My Recommended 3-Week Plan                                                                                     
                  
  Week 1 — Foundation + CRUD (all 3 devs)                                                                        
  - Dev A: CDK infra (S3 bucket, Batch defs, EventBridge, SQS, Lambdas) — extend existing stack
  - Dev B: DB migrations + all CRUD endpoints (repos, branches, contracts, config, findings/feedback)            
  - Dev C: Stripe integration (subscription endpoints + webhook)                                     
                                                                                                                 
  Week 2 — Core Flow (all 3 devs)
  - Dev A: Run orchestration (POST /runs, Batch submission, status Lambda, polling-based progress)               
  - Dev B: GitHub integration (repo listing, webhook handler, auto-run trigger)                                  
  - Dev C: Report/source serving + usage endpoint + subscription gating middleware                               
                                                                                                                 
  Week 3 — Integration + Testing (all 3 devs)                                                                    
  - All: E2E integration testing on staging                                                                      
  - Polish: error handling, rate limiting, audit logging                                                         
  - Cut: /roundabout, /runs/estimate, /findings/diff, /contract-suggestions — ship these post-launch             
                                                                                                                 
  What I'd Cut to Make the Deadline                                                                              
                                                                                                                 
  - SSE progress → use GET /runs/{id} polling (P2)                                                               
  - /contract-suggestions → manual contract entry only (P2)                                                      
  - /findings/diff → users compare visually (P2)                                                                 
  - /runs/estimate → show flat credit cost per run (P2)
  - /runs/{id}/roundabout → defer (P2)                                                                           
  - Builder container → require pre-built zip upload only, skip source upload path (P2)                          
                                                                                                                 
  That cuts ~6 endpoints and the entire Builder container, which is the scariest security surface.               
                                                                                                                 
  Verdict                                                                                                        
                  
  It's tight but doable if the 3 devs are comfortable with the existing backendless-api codebase and have AWS    
  deployment access. The Claude acceleration is real for the CRUD/boilerplate (easily 3-4x), but the
  integration/deployment/debugging cycle is the true bottleneck and Claude can't do that for you.                
                  
  Want me to write up a more detailed task breakdown that the team could actually execute from?                  