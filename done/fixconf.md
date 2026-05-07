<!-- feature-loop: 35d75c53 -->

=== /plan #1 ===
fix conf should be tested. let's take for example the spol example from ci, and inject into one of its confs a 'mistake' that can be fixed with fixconf.
then, we'll have some CI test, that takes a snapshot of this code, the minimal thing that is needed, not the whole repo, and replicates the fixable mistake there.
the test would run fixconf and show that the running of certoraRun succeeds after running on the fixed conf.

=== /plan #2 ===
got feedback from a colleague and now we have additions to fix conf tool. 
let's look at ~/certora/customersprojects/morpho/morpho-v2.
it has 3 buggy confs Consume1.conf, Consume2.conf, Consume3.conf.
the msg field in each defines what's wrong.
I will summarize here what you should do:
1. Fix malformed prover_args. you can see in Consume3.conf we have `-splitParallel=true` but it should really be `-splitParallel true`. this is a common mistake. another possibility is a typo: for example Consume2.conf has `-destructiveOptimizationz` instead of `-destructiveOptimizations`. The names of configs are taken from https://github.com/Certora/CertoraProver/blob/master/lib/Shared/src/main/kotlin/config/Config.kt and thus if we see the key-value pair, espeically the key, is sufficiently similar to one that appears in the kotlin file, then we can replace by the one that appears. a simple search in the kt file and looking for matches within quotes `"` can be sufficient to detect the right options. you can use the most reasonable metric for distance from the right option.
2. check if files actually exist in "files" in the conf with respect to root of the repo. if not, maybe you can find the right file in a different path, the highest possible (closest to the root of the repo).
3. if the contract name in "verify" does not match any of the contract handles in "files", find one that is the best fit from the actual handles. e.g. maybe the verify says "AContract:someSpec" but files has "A.sol"
4. fixing of solc. if you find the right solc, fix conf usually uses solcX.YY. but some people use solc-select based symlinks which have the form "solc-0.X.YY". your task is to detect that and configure the original workarounds to use that convention instead. how can you know?  do a preliminary investigative search for all solc version pragmas in the repo and see whether the machine you run on has solcX.YY convention or solc-0.X.YY used.

=== DONE ==