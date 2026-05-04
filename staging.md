=== /plan #1 siblings:~/certora/autosetup ===
add the option to seelect the server used in preaudit and autosetup.
add this feature in a side branch shelly/stagingUse in both preaudit and setup.
the option should be called `--server` and take one of two values: `production` or `staging`.
default is `production`. It gets passed to all prover runs in autosetup and preaudit as `--server` too (certoraRun CLI). Preaudit should pass it to autosetup when it invokes it.
Then, change the CI to pass `--server staging` in all preaudit jobs and autosetup jobs. This should include the `parallel_*` scripts (they do not need a `--server` argument, they would always operate in staging). 