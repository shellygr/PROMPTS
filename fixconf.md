<!-- feature-loop: 35d75c53 -->

=== /plan #1 ===
fix conf should be tested. let's take for example the spol example from ci, and inject into one of its confs a 'mistake' that can be fixed with fixconf.
then, we'll have some CI test, that takes a snapshot of this code, the minimal thing that is needed, not the whole repo, and replicates the fixable mistake there.
the test would run fixconf and show that the running of certoraRun succeeds after running on the fixed conf.