=== /plan slack-later-items ===

  1. mulDiv with a Rounding enum — #dev-rounding-direction-detector (Apr 13 2026)
  
  Full exchange: You posted the overload that wraps the CRT-based mulDiv(x,y,denominator) and bumps the result by 1 when rounding == Rounding.Up && mulmod(x,y,denominator) > 0, asking whether
  the detector can reason about it precisely as Up/Down or whether it always degrades to "Either." Julian answered directly: "in cases where it's called with a constant, we could definitely
  tell — we have enough context sensitivity now, but we are not using it yet," adding that the constant-mode call is "the overwhelmingly common case." You replied you'd test it once CRT
  mulDiv is handled (👍'd), and Chandrakana filed CERT-10042 to track the CRT work "as soon as possible."
  My read: This is blocked-on-dependency, not unresolved — the answer is "yes, precisely, for constant modes, once we wire up the existing context-sensitivity." Your own next action (test
  after CRT mulDiv lands) is gated on CERT-10042.
  Suggested next step: Keep this saved as a tickler against CERT-10042; nothing to do until that ticket moves.

  2. Struct-expression rounding markings in Aave SpokeInstance — #dev-rounding-direction-detector (Mar 15 2026)

  Full context: You were reviewing Aave's SpokeInstance (src/spoke/libraries/LiquidationLogic.sol), where code passes/returns memory structs. The expression assigned to debtReserveBalance is
  marked round-up but the whole call is "Either"; the same rounded-up expression appears as a field of the struct passed to ValidateLiquidationCallParams with no rounding info attached. You
  questioned what it even means for "a struct expression to round," and hypothesized it traces to MathUtils.mulDivDown being marked Inconsistent (you pasted its assembly impl). You followed
  with a screenshot (image.png) one message later.
  My read: This one has no reply in the channel — it's an open question you raised and self-illustrated, never answered. It's the conceptual sibling of #1 (how the detector attributes
  rounding through struct fields / library calls).
  Suggested next step: This is the one most worth re-surfacing to Julian/Chandra — it never got a response and it's a genuine semantics gap ("rounding on a struct expression" + why mulDivDown
  is Inconsistent).

  3. ChainSecurity 6.2 — rule or governance? — #cs-aave-v4-private (Mar 5 2026)

  Full thread (Phil ↔ Nurit, 6 msgs): Phil laid out three ChainSecurity findings — 6.1 (≤2 wei extra premium debt from rounding; fixed by increasing premium-debt precision), 6.2 (liquidation
  reverts if an unrelated asset is paused, because premium is refreshed on liquidation; fixed via a new halted flag on the hub), and 6.3 (≈ your issue M-04, struck through). Nurit mapped 6.1
  to the existing frontRunOnRefreshPremium rule (marked failed-before-fix, though the 2-wei issue isn't in the issues list) and said 6.2 has no rule because revert-rules are extremely hard.
  Phil agreed 6.2 is "more of a governance issue than a code issue." Nurit floated a theoretical rule ("if an account is liquidatable, it stays liquidatable after some operations") but noted
  too many legitimate cases where it's OK to become non-liquidatable. Phil concluded the same.
  My read: Consensus reached — 6.1 is covered by frontRunOnRefreshPremium; 6.2 won't get a rule (governance, and revert-rules too broad). The only loose thread is that the 2-wei issue isn't 
  recorded in the issues list.
  Suggested next step: If anything, ensure 6.1's 2-wei finding is logged in the issues tracker; otherwise this is closeable.

  4. ENSv2 preliminary pre-audit run — Group DM w/ Jaroslav & Gad Elbaz (Feb 20 2026)

  Full exchange: You shared a preliminary pre-audit run on ENSv2 (attached ens-preaudit1-20feb2026.html, 599 KB) flagging a single possibly-false-positive issue, asking the assigned SR for
  feedback to improve the analysis. Gad replied he'd pass it to the team "once we assemble it" and update with feedback.
  My read: Ball is in Gad's court — you're waiting on the SR team to form and give feedback on the one flagged issue. This is a follow-up tracker.
  Suggested next step: This is a "ping if stale" item — worth a nudge to Gad if the ENSv2 team has since assembled and you haven't heard back.

  5. "Solves the inlining problem for internal functions" — #dev-autosetup (Feb 13 2026)

  Full context: The message is a standalone bookmark — "just to not lose track of it, we should keep this somewhere. I wasn't aware this is solving the inlining problem for internal
  functions." There is no surrounding thread or reply in the channel window, and what "this" points to (a linked PR/message/feature) isn't captured in the message itself.
  My read: This is the least self-contained of the nine — a note-to-self whose referent ("this") lives outside the saved message. I can't reconstruct what the actual mechanism is from Slack
  alone.
  Suggested next step: Tell me what "this" was (a PR, a doc, an autosetup feature?) and I can chase the real context; otherwise it's an orphaned bookmark.

  6. Coinbase USDC deposit address — DM w/ Amit Sassi (Feb 8 2026)

  Full context: Amit posted the Coinbase USDC-only (Ethereum mainnet) deposit address 0xF83B…33AA with the warning not to send from other networks. The surrounding (Hebrew) thread is
  personal/treasury finance: comparing where you get the best USDC rate (1inch vs Paraswap vs Velora/"meta.matcha.xyz"), Aaron/Yora's recommendation, fees (~$450 via Aave's interface vs ~$80
  loss below peg on 1inch), a test transfer of ~$16, then moving ~455,000 USDC, and Coinbase asking that you use the exchange going forward.
  My read: Purely operational/financial — not work-tracking. It's saved as a reference to the deposit address.
  Suggested next step: Keep as an address reference; nothing to action.

  7. Timeout-cracker vs. timeouter script — #sync-shadow-cabal (Nov 17 2025)

  Full thread: Jaroslav explained the mode "runs a portfolio of strategies over individual splits in tacverifier," "so yes, it solves timeouts — we proved the Holy Grail rule (some subrules)
  because of it." You asked if it's part of Antti's script; Jaroslav: "I think yes… 90% sure, can check," then concluded: "looks like it's not part of the timeouter script. But I know R&D 
  mentors use the timeout-cracker mode."
  My read: Net finding — the timeout-cracker (portfolio-over-splits) is effective and used by R&D mentors, but it is not wired into the standard timeouter script. That's an integration gap
  worth noting given your earlier #rnd-mentors thread about timeout handling.
  Suggested next step: If you want this capability available to FV researchers (not just R&D mentors), it'd need to be folded into the timeouter tooling — possibly a ticket.

  8. Rule-ideas brainstorm (note-to-self) — your own DM (Jul 22 2025)

  Full context: A multi-message self-note listing candidate rules: withdraw front-running must be proven alongside solvency (credited to Nurit), Clones library, Lido new rules, then a
  follow-on list — functions that never revert, "one-time" functions, one-time-on-same-arguments functions, detect functions protected with a lock — plus reentrancy ideas (the old "no writes
  before external calls" sense, and "address(this) cannot call functions") with a link to the NoGuardSafety.spec example in Certora/Examples.
  My read: A genuine backlog of generic/library-level rule ideas — still useful as a source list for reusable specs.
  Suggested next step: This is the most "actionable backlog" item — could become tickets or a Notion list of candidate generic rules.
