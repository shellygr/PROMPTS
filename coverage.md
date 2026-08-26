# Coverage for solidity specs
## Initial [done]
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

## UX for speccov [done-almost]

the speccov tool should have a mode where it analyzes the git repo in full and produces an html report.
in particular you should take note of the work done in jobdiff tool as we want to reuse it and use it as a dependency for relevant software parts.
the left pane should show in the top a branch selector. upon selecting a branch, the left pane will show a list of all commits and their headlines.
the left pane should be resizable.
the latest commit appears first. on the left of it, we'll see its score in a circle.
if the commit changes code, its text will have an underline.
the color of the commit's text indicates the score trend with the previous commit: red for going down, green for up, grey for neutral.
the right pane should show two elements.
1. an explanation of how the score was computed for each of the components and the overall score.  use drop downs to avoid condensation of elements.
2. the actual spec diff a-la job diff.

technical implementation note.
take note to not fill up the disk with redundant ASTs and other large files. 
It should try to be as slim as possible in disk writes since those are one-time and not interesting, and for a large project with many commits we may have many files written. 
the speccov should show its progress when in this mode.
speccov should use concurrency.
it should interact with git carefully, taking the repo as argument, cloning to a temp folder, and indexing everything computed very compactly.
here caching should be used because in case we run on the same repo again we don't want to recompute things.
it may make sense to use a local sqlite database to ensure consistency by forcing a schema, and caching works. use pydantic for classes if you haven't done it so far.

note that this work should not be affected by the changes we do to scoring in other branches. if the current way we are fed scores is not sufficiently modular,
report so, and still continue to build the rest of the UX while leaving a doc instructing and recommending how to build the reportage in a more compatible way with integrations such as the UX.

## Standardizes scores [in progress]
Propose ways in which the score can be standardized across different projects and different source versions. For example, I am pretty sure C3, C4 and C5 should take into account only non-view and non-pure functions. I also think the scoring for immutables should be different than scoring of storage fields and complex paths (e.g. mapping m[address][uint256] to a uint256, arrays, etc...) that change in multiple places of the code, refining C1. The result of your investigation should be emitted to a file scoring-review-aug23-2026.md in docs folder.

## impact of input arguments [todo]
one tricky aspect of FV is that it does not know what it does not know. what I mean by that is that there is a large family of bugs
related to insufficient input validation. the problem is that if the code does not validate an input, the blindspot in many cases persists in the spec.
to avoid that, we want to score for each mutable (non view and non pure) external/public function, not only that it appears in this and many rules, but also
that its inputs participate in either requires or asserts in signifcant ways. so if an input value flows into a hash function and we require something on the hash function,
this contributes something to coverage. if it's then participating in an assertion, too. I want to be careful about distinguishing requires and asserts because we understand that some asserts can be written using implication and effectively being empty (false implies everything).
on the other hand some inputs are opaque and are supposed to be. it's okay that they're penalizing the code by a bit.
we should compute how many of the input arguments (count struct fields separately, deepest level) are flowing into requires or asserts out of all input arguments. the percentage is the score for this aspect of the overall score (we can call it C6).

## normalizing for tricky assertions [todo]
there's a way to trick us a bit, by pushing requires into assertions.
e.g. a require P; C; assert Q; can be also written, roughly, as C1; C; assert P => Q;
this is bad for us because we understand this can hide vacuous P's. I want to deincentivize such writing.
if there's just one assert in the rule, the normalizer should run an additional pass on top of the one that rewrites getters, which will do as follows:
it will convert the assert P => Q; into require P; assert Q;
if there's more than one assert with this form, it will prune out the rule, which should affect adversely on the score (it would also need to tell the user the reason for this penalty).

## native balances blindspot [todo]
If the contract contains any payable method, we penalize if `nativeBalances` is not reasoned about as if it was part of the contract state in [C1], [C2].

## Review, from Codex [done]
shelly/codex-review

## Best-effort unsat core computation [in progress]
Let's introduce a second potential input for speccov, which is a json file with a list of all Prover runs that correspond to this project.
our goal is to use this for computing a second score based on unsat cores.
the components that we need to build here are related to downloading, fetching, resubmitting with, coverage info advanced information from the prover, and
analyzing the unsat core txt files similarly to how it is done for sanity in autosetup module.
therefore, the new software components should be clearly separated from the synatctical based approaches we implemented earlier,
while reusing software components from dependencies as I describe here.

for each one of the run links provided, we should download the outputs. use ProverOutputUtility API to download sources and unsat core outputs with ease, use most recent version of it.
specifically: `extract_unsat_core_files` from `src/prover_output_utility/api/main.py`.
if there is coverage info advanced mode in the confs, we take the available information from there.
if not, we rerun the spec with coverage info and hope the result does not timeout.
if the result timesout then we mark all lines of code as 'unknown' (orange).
if we have any sort of coverage info we parse it to get the covered and uncovered parts of the code.
any line of code covered by at least one rule is considered covered (green).
any line of code not covered by any rule is conisdered uncovered (red).
lines of code that do not contain statements e.g. containing a `{` alone, should not be counted or marked with any color, similarly comment-only,
function declarations, imports, pragmas, blanks.
if there are partially covered lines they will constitute 50% cover (yellow).
The score is then the ratio betwee green lines vs green+yellow+orange+red in the denominator.

finally, before we start the computation based on unsat cores, we need to make sure that the set of run links we got is indeed fully covering all the conf files and all the rules that are checked, aggregated, by all conf files.
this should be written in a separate component as we'll use run links for more metrics later, and should be done in a separate module.

## Mutation testing, efficient [tbd]
The idea is to first generate a wide set of 'test' data that can be used to kill mutants quickly.
for each rule we'll build such a suite of tests. rules may share a test suite if they call the same set of non-view and non-pure methods.