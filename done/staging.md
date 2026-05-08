<!-- feature-loop: 782582ce -->

=== /plan #1-investigation siblings:autosetup proveroutpututility ===
add the option to select the server used in preaudit and autosetup, via an environment variable.
we have a secret AWS_ROLE_ARN that is controlled via `environment` field in the github action definition.
Question 1 is whether this information about the environment is available to running processes.
If yes, we would like to capture this environment variable holding the environment string.

Otherwise, tell me how else we can know which environment we are operating on.

=== /plan #2 siblings:autosetup proveroutpututility ===
add this feature in a side branch shelly/staging.
Apply in both preaudit and setup.
the option should be called `--server` and take one of two values: `production` or `staging`.
default is `production`. It gets passed to all prover runs in autosetup and preaudit as `--server` too (certoraRun CLI). Preaudit should pass it to autosetup when it invokes it.
Then, change the CI to pass `--server staging` in all preaudit jobs and autosetup jobs. This should include the `parallel_*` scripts (they do not need a `--server` argument, they would always operate in staging). 

in particular, it should match the ci. in ci, we can specify now `environment` as follows:
```
dummyproject-integration:
    environment: production
    runs-on: ubuntu-latest
    needs: [test]
    permissions:
      id-token: write
      contents: read
    env:
      ANTHROPIC_API_KEY: ${{ secrets.AUTOSETUP_CLAUDE_API_KEY }}
      CERTORAKEY: ${{ secrets.CERTORAKEY }}

    steps:
```

=== DONE ===