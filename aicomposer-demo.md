=== /plan aicomposer-demo ===
Using AIComposer, Write a contract that allows 2 or more distinct parties to share the proceedings of a stream.                                                                                                                                
  The recipient of the stream is this contract. It stores the list of recipients who are supposed to take equal share.                                                                                                                           
  Each withdrawal from our new share contract triggers a computation. We track how much each participant has withdrawn and ensures it's not more than 1/n of the sum it has accumulated.                                                         
  So 1st withdrawer sees balance is X, so it can take at most X/2. We account that the participant withdrew X/2. Now, balance is X/2, so when we add the previous withdrawal it is X.                                                            
  Let's suppose we withdrew from stream Y. So now we in total took X+Y. First user took X/2. It is eligible for another (X+Y)/2-X/2. How do we know? We have Y+X/2 currently, and we add X/2. Notably we cannot really know how much was added   
  in each withdrawal from the stream, but by tracking how much each party withdrew from their share, we can make sure that nobody takes more than their share. There's dust related to the division which can accumulate if there are many many  
  withdrawals, but it should even out. In the end, if the sum expected from the stream is divisible by N, each party would get exactly it's share. If not, the dust is not accessible to any party. Your goal is to come up with the formally    
  verified contract that satisfies the requirements I wrote above. You can build inputs to AIComposer as you see fit in order to facilitate this end goal. I prefer the inputs and outputs are all in ~/certora/StreamSharingContractDemo    

ANSWER FROM CLAUDE:
Plan: Use AIComposer to generate a verified Stream-Share contract

 Context

 You want a Solidity contract that acts as a fair "splitter" for an incoming
 ERC20 stream. Funds arrive at the contract address (from a Sablier-style
 stream, or just plain transfers). N >= 2 distinct participants are fixed
 at construction. Each can call withdraw() to pull out their current
 share, computed on the fly from observable state.

 Per-withdraw formula (the design you described):
 totalSeen      = token.balanceOf(this) + totalWithdrawn
 share[p]       = totalSeen / N  - withdrawnBy[p]      // integer division
 On success: transfer share[p], then withdrawnBy[p] += share[p] and
 totalWithdrawn += share[p]. Reverts on non-participant or zero share.

 Why this works (and what we will formally prove):
 - After any withdraw, N * withdrawnBy[p] <= token.balanceOf(this) + totalWithdrawn
 is preserved (the share calc uses floor of the same sum). Deposits only
 grow totalSeen, so the inequality remains true between withdraws too.
 This is the invariant that guarantees nobody ever pulls more than 1/N.
 - Dust = (total ever deposited) mod N < N accumulates in the contract
 and is unrecoverable. If the cumulative stream is divisible by N, every
 participant ends up with exactly total/N.

 Goal: prepare AIComposer inputs (CVL spec + Solidity interface + system
 doc) in ~/Certora/StreamSharingContractDemo/, hand off the exact run
 command. You execute AIComposer; outputs land in the same directory.

 Output directory layout

 Create /Users/shelly/Certora/StreamSharingContractDemo/ containing:

 StreamSharingContractDemo/
 ├── IStreamShare.sol      # interface AIComposer must implement
 ├── system_doc.txt        # plain-language design doc for the LLM
 ├── rules.spec            # CVL spec — the formal contract
 ├── README.md             # how to run AIComposer on these inputs
 └── out/                  # populated by `resume.py materialize` after a run

 Inputs only. We do not run AIComposer in this plan.

 Input file designs

 1. IStreamShare.sol — the interface AIComposer must implement

 The interface intentionally cannot declare a constructor; the system_doc
 describes constructor semantics. Keep view methods so CVL can read state
 envfree.

 // SPDX-License-Identifier: MIT
 pragma solidity ^0.8.0;

 interface IStreamShare {
     /// Withdraw the caller's currently available share of accumulated funds.
     /// Reverts if `msg.sender` is not a registered participant.
     /// Reverts if the caller's currently available share is zero.
     /// Otherwise transfers exactly the available share and returns it.
     function withdraw() external returns (uint256 amount);

     /// Cumulative amount this participant has withdrawn.
     function withdrawnBy(address participant) external view returns (uint256);

     /// Sum over all participants of withdrawnBy.
     function totalWithdrawn() external view returns (uint256);

     /// True iff the address was registered as a participant in the constructor.
     function isParticipant(address candidate) external view returns (bool);

     /// Number of participants registered in the constructor (N >= 2).
     function numParticipants() external view returns (uint256);

     /// ERC20 token whose stream is being split.
     function token() external view returns (address);
 }

 2. system_doc.txt — design narrative (what AIComposer needs to know beyond the spec)

 Outline of sections:

 - Purpose. Equal split of an incoming ERC20 stream between N fixed
 participants. The contract address itself is the stream recipient. The
 contract is unaware of the stream mechanism — it only observes its own
 ERC20 balance.
 - Constructor. constructor(address tokenAddress, address[] memory participants).
 Require: tokenAddress != 0, participants.length >= 2, every element
 non-zero and all pairwise distinct. Store the participant set as a
 mapping plus the count N.
 - Storage. ERC20 token, uint256 N, mapping(address => bool) participant,
 mapping(address => uint256) withdrawn, uint256 totalWithdrawnVal.
 - withdraw() algorithm. Exactly the formula from the Context
 section. Use a checks-effects-interactions ordering: compute share,
 require non-zero, update withdrawn[msg.sender] and totalWithdrawnVal,
 then token.transfer(msg.sender, share); require return-true.
 - Dust. (deposits) mod N < N is unreachable to any party. If the
 total stream is divisible by N, every participant cumulatively receives
 exactly total/N.
 - Out of scope. No pausing, no governance, no fees, no add/remove
 participants, no ETH support. Solidity ^0.8.29; relies on built-in
 overflow checks.
 - Concrete numeric examples. Reproduce the X then Y example you
 described, plus a 3-participant case showing dust = T mod N.

 3. rules.spec — the CVL contract

 Use the ERC20-ghost mocking pattern from
 /Users/shelly/Certora/AIComposer/examples/cccp_fixed/rules.spec
 (reuse tokenBalanceOf, transferCVL, balanceByToken ghost, etc.).

 Methods block highlights:
 methods {
     function withdraw() external returns (uint256);
     function withdrawnBy(address) external returns (uint256) envfree;
     function totalWithdrawn()      external returns (uint256) envfree;
     function isParticipant(address)external returns (bool)    envfree;
     function numParticipants()     external returns (uint256) envfree;
     function token()               external returns (address) envfree;

     function _.transfer(address to, uint256 amount) external with (env e) =>
         transferCVL(calledContract, e.msg.sender, to, amount) expect bool;
     function _.balanceOf(address account) external =>
         tokenBalanceOf(calledContract, account) expect uint256;
 }

 Ghosts and helper:
 - Reuse balanceByToken ghost + transferCVL / tokenBalanceOf from
 the cccp_fixed example.
 - Add ghost mathint sumOfWithdrawn with hooks on withdrawn[KEY a] to
 keep it equal to totalWithdrawn().

 Rules (file-level comments explain each; AIComposer will read them):

 1. invariant noOverWithdrawal(address p) — the load-bearing rule
 isParticipant(p) =>  numParticipants() * withdrawnBy(p)  <= tokenBalanceOf(token(), currentContract) + totalWithdrawn().
 2. invariant totalWithdrawnIsSum —
 totalWithdrawn() == sumOfWithdrawn.
 3. rule withdrawComputesFloorShare — for a successful withdraw()
 by participant p, the returned amount equals
 (balPre + twPre) / N - wPre[p] and is strictly positive.
 4. rule withdrawTransfersExactly — token balance of contract drops
 by amount, recipient balance grows by amount, withdrawnBy[p]
 and totalWithdrawn both grow by amount.
 5. rule nonParticipantReverts — !isParticipant(e.msg.sender) => withdraw@withrevert reverts.
 6. rule zeroShareReverts — participant whose current entitlement
 is zero gets a revert (no silent success path).
 7. rule withdrawnByMonotone(method f) — parametric: any method
 leaves withdrawnBy(p) non-decreasing.
 8. rule participantSetImmutable(method f) — isParticipant(p),
 numParticipants(), and token() never change post-construction.
 9. rule onlyCallerWithdrawnByChanges — when p calls withdraw,
 for all q != p, withdrawnBy(q) is unchanged.
 10. rule dustBoundAfterFairExit — if every participant has called
 withdraw until their entitlement is zero, token.balanceOf(this) < N.

 Rule 1 is the safety property the user asked for. 3 + 4 + 9 pin down the
 exact transfer semantics. 6 makes the "revert on zero share" choice
 explicit in the spec. 10 captures the dust claim.

 4. README.md

 Short instructions on how to invoke AIComposer with these inputs and how
 to materialize the output (see "Run command" below).

 Run command (for you, not executed by this plan)

 From the AIComposer repo root, after the one-time Docker/RAG/prover setup
 in /Users/shelly/Certora/AIComposer/README.md:

 cd /Users/shelly/Certora/AIComposer
 python3 ./main.py \
     /Users/shelly/Certora/StreamSharingContractDemo/rules.spec \
     /Users/shelly/Certora/StreamSharingContractDemo/IStreamShare.sol \
     /Users/shelly/Certora/StreamSharingContractDemo/system_doc.txt
     cd /Users/shelly/Certora/AIComposer
     python3 ./main.py \
         /Users/shelly/Certora/StreamSharingContractDemo/rules.spec \
         /Users/shelly/Certora/StreamSharingContractDemo/IStreamShare.sol \
         /Users/shelly/Certora/StreamSharingContractDemo/system_doc.txt

     Note the thread id printed early in stdout (e.g.
     Selected thread id: crypto_session_<uuid>). When the workflow
     completes, materialize the deliverable:

     python3 ./resume.py materialize <thread-id> \
         /Users/shelly/Certora/StreamSharingContractDemo/out

     Prerequisites (flagged, not actioned here):
     - ANTHROPIC_API_KEY exported.
     - Local Postgres up via scripts/docker compose start.
     - CERTORA env var pointing at a built CertoraProver target.
     - solc8.29 available on $PATH.
     - RAG DB populated (./populate_rag.sh once).

     Verification

     After AIComposer finishes and you materialize to out/:

     1. The materialized directory should contain a .sol file implementing
     IStreamShare. Skim for the share formula and the revert paths.
     2. Re-run the Prover against out/ with the same rules.spec to confirm
     all rules pass (AIComposer does this internally but a clean rerun is
     good hygiene):
     cd /Users/shelly/Certora/StreamSharingContractDemo/out
     certoraRun <generated>.sol --verify <generated>:../rules.spec
     2. (Exact contract name comes from the generated file.)
     3. Optional sanity check: a tiny Foundry script that deposits X, has
     user 1 withdraw, deposits Y, lets users 1 and 2 withdraw, and asserts
     each ends with X/2 + Y/2 when X+Y is even — reproducing the narrative
     from your request.

     Critical files referenced

     - /Users/shelly/Certora/AIComposer/main.py — entry point.
     - /Users/shelly/Certora/AIComposer/resume.py — materializer.
     - /Users/shelly/Certora/AIComposer/examples/cccp_fixed/rules.spec — the
     ERC20 ghost-mock pattern to reuse (transferCVL, tokenBalanceOf,
     balanceByToken).
     - /Users/shelly/Certora/AIComposer/examples/trivial/ — shows the
     minimum-viable shape of the three input files.
     - /Users/shelly/Certora/AIComposer/README.md — env setup.
