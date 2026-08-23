# Coverage for solidity specs
New project, new repo, `SoliditySpecCoverage`. Create the repo here, and put your insight and plans into a docs/ folder within so that we track our requirements, design choices, algorithms, and evolution.

Our goal is to write a tool that consumes a list of certora conf files and produces an evaluation of coverage w.r.t. 
1) list of all source files from .all_sources of all confs (see how autosetup module in AutoProver gets it)
2) the spec files and their imports (again, refer to autosetup to see how we consume the spec file and get its full AST)

It is supposed to be fast and cheap (i.e. no LLMs for starters, no running the Prover itself).

the idea is to have several metrics of spec coverage:
1. Syntactical:
    - [C1] track what % of storage fields appear in asserts
    - [C2] and in different ways including relationship between different quantities in storage 
    - [C3] what % of methods are being called either parametrically or directly
    - [C4] in how many rules each method is being called
    - [C3] and [C4] should take into account the parametric_contracts and method and exclude_method flags of the conf
    - [C5] track % of methods being called with `@withrevert` and whether their `lastReverted` match appears on the left hand side of an assert, the right hand side of an assert, or both, or within a `<=>`
2. Penalties
    - [P1] each method with a summary (need to take into account wildcards too, having the weight of all matches from contracts that match) is penalizing
    - [P2] usage of getter functions instead of direct storage access is a penalty if `getterX()` has reverts in its solidity code.
3. Filtering
    - [F1] for subsumed rules (i.e. rule 1 implying rule 2 holds too) we're first of all removing subsumed rules from the list we consider.
            the idea is that given a rule R with the structure of { P } C { Q } where P is all requires, Q is all assertions, a second rule R' with { P' } C { Q' } where P' implies P, and Q implies Q', then R' is subsumed by R, because the postcondition of R' is implied by the postcondition of R and the precondition of R is weaker than that of R'. We will only check this for rules with this simple 'hoare-style' structure for now, where the idea is that we'll convert the rules to an SMT formula where all solidity functions are treated as uninterpreted functions, and all non-SMT native datatypes as new sorts.

the tentative coverage score formula is, after applying [F1] filtering and computing [C1]-[C5] and [P1]:
    [C1]*[C2] + [C3]*[C4] + [C5] - [P1] 

there's a LOT of heavy lifting we need to do in order to be able to compute this score and others.
1. we need to know which methods exist in all contracts and their visibility and arguments and returns. this all exists from info computed by autosetup by compiling the confs one-by-one and reading, e.g. .certora_build.json, but refer to autosetup code for definite information.
2. we need to be able to list all rules that are active, this was done in https://github.com/Certora/AutoProver/pull/177 and can be reused here
3. we need to build the universe of all contract states from storageLayout fields
4. we need to build a graph of how different contract states are related by asserts, i.e. if we have `stateUintX == 5` then there is a self edge from `stateUintX` to itself, if we have `stateUintX >= stateUintY` then we have an edge from `stateUintX` to `stateUintY` labeled `>=`. Each datatype defines which comparison operators apply to its labels. There are also composite labels denoted `*=`, `*L` and `*R` if we have something like `sUintX / sUintY REL sUintZ*100`, where `sUintX` and `sUintY` are `*=` to `sUintZ` if `REL` is `==`, `*L` if `REL` is `>=`, `*R` if `REL` is `<=`.


for the algorithm, I suggest you first convert the spec to use direct storage access instead of getters. this can be done by analyzing the solidity AST

I'll have more ideas later. For now, start drafting the different software components we needed. You may use AutoProver repo as a dependency.
Our goal is to write GOOD and MAINTAINABLE code, not rely on regex or string ops, and be SOUND in our analysis.
You can explore docs.certora.com for more info about CVL and its semantics, and you have various repos and data sources available as well.
Update in docs/ your initial plan for implementation and I'll give feedback. You may split it to multiple files with different modules that would be independent of each other but nevertheless useful in the final scoring algorithm.

=====

UX for speccov

the speccov tool should have a mode where it analyzes the git repo in full and produces an html report.
in particular you should take note of the work done in jobdiff tool as we want to reuse it and use it as a dependency for relevant software parts.
the left pane should show in the top a branch selector. upon selecting a branch, the left pane will show a list of all commits and their headlines.
the left pane should be resizable.
the latest commit appears first. on the left we'll see its score in a circle.
if the commit changes code, its text will have an underline.
the color of the commit's text indicates the score trend with the previous commit: red for going down, green for up, grey for neutral.
the right pane should show the actual spec diff a-la job diff.
take note to not fill up the disk with redundant AST. It should try to be as slim as possible in disk writes since those are one-time and not interesting, and for a large project with many commits we may have many files written. 
the speccov should show its progress when in this mode.
it should interact with git carefully, taking the repo as argument, and indexing everything computed very compactly.
it should use parallelism where possible.
here caching should be used because in case we run on the same repo again we don't want to recompute things.
it may make sense to use a local sqlite database to ensure consistency and caching works.