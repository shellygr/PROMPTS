=== /plan money ===

Collect discount letters:
I gave you access to my certora gmail. you'll find there messages from bank דיסקונט.  these are starred. each contains a link. each has a link under the word "כאן". I need you to collect all of these links.
there should be 328 links in total.


MONEY_CERTORA directory:
you may only read the files in this directory `~/Downloads/MONEY_CERTORA` and not write anything. Write everything you need in a folder above, sibling dir, called `workdir_money_certora`.
Study all of the files, build a summary. Focus on:
- closed client deals from agreement copies
- Invoices sent to matching clients
Ideally we have a table associating each agreement file to one or more invoice files. We should be able to group by client name, company name, and sum ranges.
build a separate memory about this folder and the insights. Later, we would like to build a dashboard that gets live feeds as new information is given from various sources, and shows the active deals, the completed deals, and even computes profitability. more on that later. for now just learn the folder and the available data and think about further indices we could build to drive business information and visibility. apply as many subagents as needed. this is your top priority



Get me all enterprise deals from monday and salesforce and how many people are working on those. only repeated clients and reputable names.


........

 1 SOL currently mints ~0.78 JitoSOL (JitoSOL is worth ~1.28 SOL because it has accrued staking + MEV rewards — so you receive fewer JitoSOL than the SOL you put in; that's expected, not a fee).

  Three ways to convert

  1. Jito's stake pool directly (recommended — no slippage)
  - Go to jito.network/staking, connect a Solana wallet (Phantom, Solflare, Backpack…) holding SOL.
  - Enter the SOL amount → "Stake" → approve the tx. You receive JitoSOL at the exact pool exchange rate.
  - Deposit fee is 0% (Jito charges a management fee on rewards, not on deposit). No minimum, no lockup — JitoSOL is liquid, redeem/swap anytime.

  2. DEX / aggregator swap (instant, market price)
  - Use Jupiter (or Orca/Raydium) and swap SOL→JitoSOL.
  - Instant and uses the same wallet flow, but subject to slippage and pool liquidity. For large amounts the direct stake-pool route (option 1) usually gives a cleaner rate; for small amounts a swap is fine.

  3. CLI (programmatic / treasury ops)
  spl-stake-pool deposit-sol Jito4APyf642JPZPx3hGc6WWJ8zPKtRbRs4P815Awbb <AMOUNT_SOL>
  (Jito4APy…Awbb is the Jito stake-pool address.) Good for scripting from a treasury wallet.

  ⚠️  Caveat that connects to what we just discussed

  Depositing SOL → JitoSOL does not stake to Certora's own validator. Jito's pool delegates across its own validator set via the StakeNet algorithm, so this is liquid-staking as a holder, not self-staking your validator. If the goal is to put skin-in-the-game on your
  validator (the concentration-risk hedge from before), you'd use a native stake account delegated to A5ed2x2w…, not JitoSOL.

  Conversely — if Certora's validator runs the Jito-Solana client and meets StakeNet criteria, it could receive delegation from the Jito pool. That's a legitimate path to diversify away from the single 636k-SOL delegator. Want me to check whether your validator currently
  qualifies for / receives Jito pool delegation?

  Sources: Jito — Stake SOL for JitoSOL, Jito staking dashboard, JitoSOL stake-pool stats (Solana Compass)