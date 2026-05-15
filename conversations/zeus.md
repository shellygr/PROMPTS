 explain to me how Zeus saas invokes zeus-llm-orchestrator                                                                                                                                                         
                                                                  
⏺ Explore(Find Zeus SaaS to LLM orchestrator invocation)                                                                                                                                                            
  ⎿  Done (28 tool uses · 84.1k tokens · 1m 9s)                                                                                                                                                                     
  (ctrl+o to expand)                                                                                                                                                                                                
                                                                                                                                                  
⏺ Here's how Zeus SaaS invokes zeus-llm-orchestrator:                                                                                                                                                               
                                                                                                                                                                                                                    
  Invocation Method: Direct REST API over HTTP                                                                                                                                                                      
                                                                                                                                                                                                                    
  Zeus SaaS calls the orchestrator (referred to as "Zeus API" / "Zeus backend" internally) via synchronous HTTP requests with async webhook callbacks for completion. No message queues involved.                   
                                                                                                                                                                                                                    
  Configuration                                                                                                                                                                                                     
                                                                                                                                                                                                                    
  In zeus-saas/src/lib/env.ts, three env vars define the connection:                                                                                                                                                
  - ZEUS_API_BASE_URL — base URL (e.g. https://api-zeus.certora.com)
  - ZEUS_API_KEY — auth key sent as X-API-Key header                                                                                                                                                                
  - ZEUS_WEBHOOK_SECRET — HMAC-SHA256 secret for verifying completion callbacks
                                                                                                                                                                                                                    
  The HTTP Client 
                                                                                                                                                                                                                    
  zeus-saas/src/lib/zeus-api/client.ts wraps all calls to the orchestrator:                                                                                                                                         
                                                                                                                                                                                                                    
  ┌──────────────────────────┬────────┬─────────────────────────┐                                                                                                                                                   
  │         Endpoint         │ Method │         Purpose         │
  ├──────────────────────────┼────────┼─────────────────────────┤
  │ /audits                  │ POST   │ Create a full audit     │
  ├──────────────────────────┼────────┼─────────────────────────┤
  │ /diff-audits             │ POST   │ Create a diff audit     │                                                                                                                                                   
  ├──────────────────────────┼────────┼─────────────────────────┤
  │ /audits/{jobId}          │ GET    │ Get audit status        │                                                                                                                                                   
  ├──────────────────────────┼────────┼─────────────────────────┤
  │ /audits/{jobId}/progress │ GET    │ Poll progress           │
  ├──────────────────────────┼────────┼─────────────────────────┤                                                                                                                                                   
  │ /audits/{jobId}/result   │ GET    │ Stream download results │
  ├──────────────────────────┼────────┼─────────────────────────┤                                                                                                                                                   
  │ /audits/{jobId}          │ DELETE │ Cancel an audit         │
  └──────────────────────────┴────────┴─────────────────────────┘                                                                                                                                                   
   
  Three Entry Points Trigger Invocation                                                                                                                                                                             
                  
  1. Web UI — server action in app/orgs/[orgSlug]/(navigation)/audit/audit.action.ts                                                                                                                                
  2. AI Agent (Colab) — tools in src/features/agent/tools/launch-zeus-audit.tool.ts and launch-zeus-diff-audit.tool.ts
  3. Public API — POST /api/v1/audits in app/api/v1/audits/route.ts                                                                                                                                                 
                                                                                                                                                                                                                    
  All three converge on the same flow.                                                                                                                                                                              
                                                                                                                                                                                                                    
  End-to-End Flow                                                                                                                                                                                                   
                  
  1. Request arrives (UI / Agent / API)
  2. Validation (SSRF check on git URL, commit SHA format, rate limit)                                                                                                                                              
  3. Balance precheck — calls previewContext() to estimate cost,                                                                                                                                                    
     atomically reserves funds in Postgres                                                                                                                                                                          
  4. POST ${ZEUS_API_BASE_URL}/audits with X-API-Key header                                                                                                                                                         
     → receives {job_id, status: "pending"}                                                                                                                                                                         
  5. Links reservation to job_id in DB                                                                                                                                                                              
  6. Returns success to caller                                                                                                                                                                                      
           ...time passes, Zeus backend runs the audit...                                                                                                                                                           
  7. Zeus backend POSTs to /api/webhooks/zeus/ with HMAC signature                                                                                                                                                  
     → SaaS verifies signature (timingSafeEqual + 5-min replay window)                                                                                                                                              
     → Reconciles billing (charge actual cost, refund excess reservation)                                                                                                                                           
     → Sends notifications (email, in-app, agent terminal)                                                                                                                                                          
                                                                                                                                                                                                                    
  Zeus SaaS                        Zeus LLM Orchestrator                                                                                                                                                            
      │                                    │                                                                                                                                                                        
      ├── POST /audits ───────────────────>│
      │<── {job_id, status} ──────────────┤                                                                                                                                                                         
      │                                    │                                                                                                                                                                        
      │  [optional: GET /progress poll]    │                                                                                                                                                                        
      │                                    │                                                                                                                                                                        
      │<── POST /webhooks/zeus ───────────┤  (completion callback)                                                                                                                                                  
      │── 200 OK ─────────────────────────>│
                                                                                                                                                                                                                    
  Key takeaway: It's a straightforward synchronous HTTP POST to create the job, with an asynchronous webhook callback when the orchestrator finishes.                                                               
                                                                                                                                                                                                                    
✻ Cogitated for 1m 42s                                                                                                                                                                                              
                  
❯ 1. where is the API hosted? 2. what inputs are passed to the API? it runs on github repos?                                                                                                                        
                                                                                             
⏺ Let me look at the actual code for precise answers.                                                                                                                                                               
  ⎿  Loaded zeus-saas/CLAUDE.md                                                                                                                                                                                     
  ⎿  Loaded zeus-saas/.claude/rules/file-naming.md            
  ⎿  Loaded zeus-saas/.claude/rules/mandatory-dependencies.md                                                                                                                                                       
  ⎿  Loaded zeus-saas/.claude/rules/code-conventions.md
  ⎿  Loaded zeus-saas/.claude/rules/middleware-proxy.md                                                                                                                                                             
  ⎿  Loaded zeus-saas/.claude/rules/changelog.md                                   
  ⎿  Loaded zeus-saas/.claude/rules/testing.md                                                                                                                                                                      
  ⎿  Loaded zeus-saas/.claude/rules/development-commands.md                                                                                                                                                         
  ⎿  Loaded zeus-saas/.claude/rules/fetching-patterns.md                                                                                                                                                            
  ⎿  Loaded zeus-saas/.claude/rules/architecture-overview.md                                                                                                                                                        
  ⎿  Loaded zeus-saas/.claude/rules/ui-ux.md
  ⎿  Loaded zeus-saas/.claude/rules/authentication.md

  Searched for 1 pattern, read 2 files (ctrl+o to expand)     
                        
⏺ 1. Where is the API hosted?
                         
  From the .env-template (line 43):                                                                                                                                                                                 
  
  ZEUS_API_BASE_URL="https://api-zeus.certora.com"                                                                                                                                                                  
                                                                                                                                                                                                                    
  The orchestrator is hosted at https://api-zeus.certora.com. This is configurable via the ZEUS_API_BASE_URL env var — the SaaS codebase doesn't contain or deploy the orchestrator itself; it just calls it as an  
  external service.                                                                                                                                                                                                 
                                                                                                                                                                                                                    
  2. What inputs are passed?

  Yes, it operates on git repos (not just GitHub — any git URL that passes SSRF validation). Here are the inputs for each audit type:                                                                               
  
  Full Audit (POST /audits)                                                                                                                                                                                         
                  
  From schemas.ts:211-233:                                                                                                                                                                                          
                  
  ┌──────────────────────┬──────────┬──────────────────────────────────────────────────────────────────────────────┐                                                                                                
  │        Field         │ Required │                                 Description                                  │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ target               │ yes      │ Git repo URL (e.g. https://github.com/org/repo)                              │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ branch               │ yes*     │ 40-char commit SHA (not a branch name — enforced to prevent TOCTOU attacks)  │                                                                                                
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ context              │ yes      │ Array of glob patterns for files the LLM should read (e.g. ["src/**/*.sol"]) │                                                                                                
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ scope                │ no       │ Specific file paths to audit (defaults to context if omitted)                │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ preprompt            │ no       │ Custom system prompt instructions (max 8KB)                                  │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ token                │ no       │ GitHub PAT for private repo access                                           │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ skip_submodules      │ no       │ Whether to skip git submodules                                               │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ max_iterations       │ no       │ LLM iteration count (4–10)                                                   │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ debug                │ no       │ Debug mode flag                                                              │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ organization_id      │ yes      │ Billing org ID                                                               │
  ├──────────────────────┼──────────┼──────────────────────────────────────────────────────────────────────────────┤                                                                                                
  │ created_by_member_id │ no       │ Who triggered it                                                             │
  └──────────────────────┴──────────┴──────────────────────────────────────────────────────────────────────────────┘                                                                                                
  
  Diff Audit (POST /diff-audits)                                                                                                                                                                                    
                  
  From schemas.ts:246-265 — same as above but instead of a single branch, it takes:                                                                                                                                 
   
  ┌─────────────────┬────────────────────────────────────┐                                                                                                                                                          
  │      Field      │            Description             │
  ├─────────────────┼────────────────────────────────────┤
  │ branch_starting │ 40-char SHA of the "before" commit │
  ├─────────────────┼────────────────────────────────────┤
  │ branch_ending   │ 40-char SHA of the "after" commit  │                                                                                                                                                          
  └─────────────────┴────────────────────────────────────┘                                                                                                                                                          
                                                                                                                                                                                                                    
  So the orchestrator clones the repo at the specified commit, matches files against the context globs, and runs the LLM audit over those files. For diff audits, it compares the two commits and audits the        
  changes.        
                                                                                                                                                                                                                    
❯ how does it gain access to private repos?                                                                                                                                                                         
                                                                                   
  Searched for 2 patterns, read 2 files (ctrl+o to expand)                                                                                                                                                          
                                                                                                                                                                                                                    
⏺ There are two paths for private repo access, both resolved server-side before the token is forwarded to the orchestrator:                                                                                         
                                                                                                                                                                                                                    
  Path 1: GitHub OAuth (preferred — githubConnectionId)                                                                                                                                                             
                                                                                                                                                                                                                    
  1. User clicks "Connect GitHub" in the audit form → opens an OAuth popup                                                                                                                                          
  2. The OAuth callback (/api/auth/github/repo-callback) exchanges the code for an access token with repo scope                                                                                                     
  3. The token is never sent to the browser. Instead it's stored in Redis with a 1-hour TTL, keyed by an opaque connection ID scoped to {userId, organizationId}                                                    
  4. The browser only receives the connection ID (+ display metadata like @octocat)                                                                                                                                 
  5. When the audit is created, the server action receives the githubConnectionId, calls resolveGithubOAuthConnection() to look up the real token from Redis (verifying the user/org match), and forwards it as the 
  token field to the orchestrator                                                                                                                                                                                   
                                                                                                                                                                                                                    
  This is documented as M-07 in the codebase — the security concern was that a repo-scoped OAuth token sitting in React state could be exfiltrated by XSS or a compromised dependency.                              
                  
  Path 2: Manual PAT (fallback — token)                                                                                                                                                                             
                  
  The user can paste a GitHub Personal Access Token directly in the form. It's sent as-is to the server action, which forwards it to the orchestrator in the token field.                                           
  
  What the orchestrator does with it                                                                                                                                                                                
                  
  The token is passed as token in the JSON body to POST /audits. The orchestrator uses it to git clone the private repo. The SaaS layer also validates that tokens are only forwarded to trusted git providers      
  (github.com, gitlab.com, bitbucket.org) — from audit.action.ts:152:
                                                                                                                                                                                                                    
  "GitHub tokens can only be used with trusted Git providers (github.com, gitlab.com, bitbucket.org)"
                                                                                                                                                                                                                    
  This prevents a user from pointing target at a malicious server to steal the token.    