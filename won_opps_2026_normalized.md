# 2026 Won Opportunities — Normalized by Service (from signed agreements)

**Method.** For each Closed-Won opportunity since 2026-01-01 I located the *signed* DocuSign quote / agreement PDF in the `MONEY_CERTORA` dump and read the real pricing — **not** the Salesforce `Amount` (which is systematically too high because it usually equals the pre-discount **Subtotal** and ignores the quote's footer "Discount / Add'l Fee" line). Where a deal bundles several services and carries a single overall discount, the discount is spread across services **in proportion to each service's pre-discount subtotal** (value weight). Per-line discounts already baked into a line subtotal are left as-is. Price = real contracted amount, net of all discounts.

**Service codes:** AUD = Audit · FV = Formal Verification · AR = Architecture/Design Review · CUST = Custom (retainer / fuzzing / governance / offchain / SLA) · ENT = Enterprise bundle · DD = Due Diligence.

## Normalized table (one row per service)

| Close | Opportunity | Account | Service | Weeks | Normalized $ | Signed total | SF Amount | Discount captured |
|---|---|---|---|---|---|---|---|---|
| 01-07 | Ether.fi Enterprise 2026 | Ether.fi | ENT (Audit+FV+Prover) | 18 | 360,000 | 360,000 | 540,000 | −180,000 (33%) |
| 01-07 | Light CToken V3 Extension | Light Protocol | AUD | 3.5 | 70,000 | 70,000 | 70,000 | −35,000 (line) |
| 01-12 | AAVE v3.6 Audit+FV | BGD/Aave | AUD+FV (gov payload) | — | 30,400 | 30,400 | 30,400 | none |
| 01-14 | Veda – Boring Vault Yield Streaming | Veda | AUD | 1.5 | 45,000 | 125,000 | 125,000 | none |
| 01-14 | Veda – Boring Vault Yield Streaming | Veda | CUST (fuzzing) | 4 | 80,000 | (combined) | | |
| 01-15 | Iota FV | Iota | FV | 5 | 100,000 | 100,000 | 100,000 | none |
| 01-16 | Fluid – Solana + Solidity | Fluid | AUD | 3 | 67,408 | 367,000 | 400,000 | −123,000 (25%) |
| 01-16 | Fluid – Solana + Solidity | Fluid | FV | 20 | 299,592 | (combined) | | |
| 01-19 | APYX Audit | APYX | AUD | 1.5 | 27,000 | 27,000 | 45,000 | −18,000 (40%) |
| 01-21 | Calastone CTD V1.1 + CCN | Calastone | AUD | 2 | 60,000 | 60,000 | 60,000 | none |
| 01-28 | Voltr Audit | Voltr | AUD | 3 | 42,000 | 42,000 | 90,000 | −48,000 (53%) |
| 02-03 | Lightcone Trade Audit | Lightcone | AUD | 8 | 104,000 | 104,000 | 160,000 | −56,000 footer (+−80k line) |
| 02-16 | Den Wallet Audit | Den | AUD | 4 | 108,000 | 108,000 | 120,000 | −12,000 (10%) |
| 02-26 | Saturn M0 – FV + Audit | Saturn | AUD | 1 | 25,500 | 68,000 | 80,000 | −12,000 (15%) |
| 02-26 | Saturn M0 – FV + Audit | Saturn | FV | 2.5 | 42,500 | (combined) | | |
| 02-26 | TradePort 2nd Audit | TradePort | AUD | 3 | 60,000 | 60,000 | 90,000 | −30,000 (33%) |
| 02-27 | Galaxy/Alluvial Audit (Liquid Collective) | Alluvial | AUD | 1.5 | 30,000 | 30,000 | 45,000 | −15,000 (SOW rate) |
| 02-27 | Lido – Staking Router DR+Audit, CSM v2/v3 | Lido | AR (design review) | 3 | 33,750 | 483,750 | 645,000 | −161,250 (25%) |
| 02-27 | Lido – Staking Router DR+Audit, CSM v2/v3 | Lido | AUD | 20 | 450,000 | (combined) | | |
| 02-27 | Catalysis New Audit | Catalysis | AUD | 1 | 19,500 | 19,500 | 30,000 | −10,500 (35%) |
| 03-02 | Umia / Chainbound Audit | Umia | AUD | 3.5 | 65,000 | 65,000 | 105,000 | −40,000 (38%) |
| 03-02 | Reserve FV | Reserve | FV | 3.5 | 59,500 | 59,500 | 59,500 | −10,500 (line) |
| 03-03 | Polymarket DepositWallet Audit | Polymarket | AUD | 1 | 30,000 | 30,000 | 30,000 | none |
| 03-07 | Credit Coop Audit Retainer | Credit Coop | CUST (retainer) | 6 | 153,000 | 153,000 | 153,000 | −27,000 (line) |
| 03-10 | Cozy Router contract diff | Cozy | AUD | 0.3 | 9,000 | 9,000 | 9,000 | none |
| 03-11 | MezFi FV | MezFi | FV | 4 | 56,000 | 56,000 | 56,000 | −24,000 (line) |
| 03-11 | Jito whitelisted instructions Audit | Jito | AUD | 1.5 | 30,000 | 30,000 | 45,000 | −15,000 (33%) |
| 03-13 | Kite AI Monitoring/IR SLA | Kite AI | CUST (SLA) | 3 | 48,000 | 48,000 | 48,000 | none |
| 03-17 | Hadron Fi Audit | Hadron | AUD | 5 | 65,000 | 65,000 | 100,000 | −35,000 footer (+−50k line) |
| 03-18 | Catalysis reAudit | Catalysis | AUD | 1 | 18,000 | 18,000 | 18,000 | −12,000 (line, 40%) |
| 03-19 | Navi VoloVault Audit | Navi | AUD | 2 | 34,000 | 34,000 | 60,000 | −26,000 (43%) |
| 03-24 | Polymarket Enterprise Mar-2026 | Polymarket | CUST (engineer wks) | 26 | 253,500 | 253,500 | 253,500 | −136,500 (line) |
| 03-26 | Veda Enterprise Custom | Veda | CUST | 16 | 204,000 | 204,000 | 204,000 | −36,000 (line) |
| 03-30 | Royco – Audit & FV | Royco (Waymont) | FV | 3.5 | 46,073 | 90,000 | 100,005 | −10,005 footer (+line) |
| 03-30 | Royco – Audit & FV | Royco (Waymont) | AUD | 2.5 | 43,927 | (combined) | | |
| 03-31 | Exponent Vault Program Audit | Exponent | AUD | 3 | 50,000 | 50,000 | 90,000 | −40,000 (44%) |
| 03-31 | Morpho Continuous FV (Q2 retainer) | Morpho | FV (quarterly) | per-Q | 104,000/qtr | 104,000/qtr | — | −52,000/qtr (33%) |
| 04-01 | Solana Foundation – Audit+FV+DD pkg | Solana | AUD+FV+DD (4-mo pkg) | ~4 mo | 714,000 | 714,000 | 714,000 | n/a (SOL delegation) |
| 04-02 | AAVE Audit | Aave | AUD | 0.6 | 18,000 | 18,000 | 18,000 | none |
| 04-08 | Atlas Forge Audit | Atlas Forge | AUD | 5.5 | 99,000 | 99,000 | 30,000 | −66,000 (line) |
| 04-08 | Light Protocol Token program PR | Light Protocol | AUD | 0.4 | 8,000 | 8,000 | 12,000 | −4,000 (33%) |
| 04-10 | Superis Labs Audit | Superis (Cumberland) | AUD | 2.5 | 50,000 | 50,000 | 75,000 | −25,000 (33%) |
| 04-15 | Cloak Audit | Cloak | AUD | 2.5 | 35,000 | 35,000 | 75,000 | −40,000 (53%) |
| 04-21 | APYX Governance review | APYX | CUST | 1 | 20,000 | 20,000 | 20,000 | none |
| 04-30 | Sky Frontier (Glenn Kennedy) | Sky Frontier | AUD (retainer) | 10 | 250,000 | 250,000 | 300,000 | −50,000 (17%) |
| 04-30 | Reyts (SDF/Stellar SOW) | Reyts | AUD | ~1.5 | 30,000 | 30,000 | 45,000 | −15,000 (SOW) |
| 05-04 | Spectra (SDF/Stellar SOW) | Spectra | AUD | ~3 | 60,000 | 60,000 | 90,000 | −30,000 (SOW) |
| 05-05 | Squads – Audit & FV | Squads | AUD | 3 | 63,529 | 120,000 | 170,000 | −50,000 (29%) |
| 05-05 | Squads – Audit & FV | Squads | FV | 4 | 56,471 | (combined) | | |
| 05-11 | Saturn offchain | Saturn | CUST | 3 | 80,000 | 80,000 | 90,000 | −10,000 (11%) |
| 05-19 | Royco Dusk | Royco (Waymont) | AUD | 1.5 | 31,500 | 89,250 | — | −38,250 (30%) |
| 05-19 | Royco Dusk | Royco (Waymont) | FV | 3 | 47,250 | (combined) | | |
| 05-19 | Royco Dusk | Royco (Waymont) | AR | 1 | 10,500 | (combined) | | |
| 05-21 | Alluvial – Liquid Collective retainer | Alluvial (Galaxy) | CUST (retainer) | 16 | 204,000 | 204,000 | 240,000 | −36,000 (SOW rate) |
| 05-26 | Superis Audit Extension | Superis (Cumberland) | AUD | 6 | 45,000 | 45,000 | 180,000 | −135,000 (75%) |
| 05-27 | DFlow Audit | DFlow | AUD | 1 | 30,000 | 30,000 | 30,000 | none |
| 05-28 | Saturn Offchain audit extension | Saturn | CUST | 1 | 23,000 | 23,000 | 30,000 | −7,000 (23%) |
| 05-28 | Luca Money | Luca Money | CUST | 1.5 | 29,500 | 29,500 | 90,000 | −15,500 + SF 2nd line not in agmt |
| 05-15 | Lightcone Audit Expansion | Lightcone | AUD | 1 | 13,000 | 13,000 | — | −17,000 (line) |

### Deals with NO signed agreement in the dump (dump is a 2026-05-31 snapshot; recent/unfiled) — SF figure shown, NOT verified
| Close | Opportunity | Account | Service | Weeks | SF $ (unverified) |
|---|---|---|---|---|---|
| 05-07 | Exponent Retainer Jun–Sep 2026 | Exponent | CUST | 2 | 30,000 |
| 06-04 | DFlow Audit Extension | DFlow | AUD | 1 | 30,000 |
| 06-04 | Re Inc – Staking | Re Inc | AUD | 0.8 | 24,000 |
| 06-05 | Aftermath Audit | Aftermath | AUD | 10 | 300,000 |
| 02-18 | ProtoFire | ProtoFire | — | — | 20,000 (no folder at all) |

### Excluded (not a priced Certora service deal)
Internal_Projects, Vacations (internal); Sui partner deal ($0); Canton ($0 strategic); Bullish / ADI Predict Street / Consensys (**HyperNative** reseller bundles, no Certora service line); Uniswap Concord (sponsorship); Arbitrum Security Council, Revolut, Warp (orig+ext), CashXChain (no priced line items); Solana Workshop / Office Hours (marketing).

## Notes / caveats
- **Lido** & **Solana**: signed docs give a single bundled total with no per-line prices. Lido's $483,750 is split AR/AUD by each service's list value (3wk×$15k vs 20wk×$30k). Solana's $714k (paid via 780k SOL delegation, recalibrated 6-monthly) is left as one package row — no clean per-service split exists.
- **Atlas Forge**: real signed deal (5.5wk, $99k) is *bigger* than the SF stub (1wk/$30k) — SF was stale.
- **Luca Money**: agreement has only ONE "Custom" line ($45k → $29,500); SF's second line (audit) is not in the signed agreement.
- **Morpho**: standing quarterly Continuous-FV retainer ($156k list → $104k/quarter); first invoice was $67,600 after one-time partial-period + 10% upfront discounts.
- **AAVE v3.6** ($30,400) closed via on-chain Aave Governance Proposal 429, not a quote.
- "Discount captured" labelled *(line)* = discount embedded in the line subtotal; *(footer)* = overall "Discount / Add'l Fee" spread across services; *(SOW rate)* = fixed-price SOW priced below list week-rate.
