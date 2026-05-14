<!-- feature-loop: 4fea1a2a -->

=== /plan pou-skills siblings:ProverOutputUtility siblings:ctac-fly ===
consider www.github.com/1arie1/ctac-fly as a template for good claude skills repo.
in parallel, look at this ProverOutputUtility repo and what it allows people to investigate about prover jobs as a whole.
I want you to convert the APIs to skills using the same format as the claude skills repo, and make the skills easily installable.
we will create a new skills repo under ~/Certora/SwissArmyKnife and create a repo under the Certora org called SwissArmyKnife.

=== /plan include-viol-analyzer ===
I want you to include now running the violation analyzer from github.com/certora/ViolationAnalyzer (locally: ~/Certora/ViolationAnalyzer-release/) as part of the skills.

=== /plan include-to-solver ===
Now also include https://github.com/Certora/timeout-squad locally ~/Certora/timeout-squad as part of the skills suite.

=== /plan combine siblings:ProverOutputUtility ===
now let's combine timeouter skill together with pou skill.
we need a new option from the timeouter to not only execute the timeouter, but also to watch for the first successful result (verified OR violated), and continue to CANCEL all the other jobs. 
Cancelling should be a capability of ProverOutputUtility. If ProverOutputUtility currently does not expose this API, then let's add a side-branch and create a PR where we add to ProverOutputUtility this capability. 
This is the API:
```
/v1/domain/jobs/cancel
Cancel multiple jobs.

Cancel multiple jobs.
Parameters

No parameters
Request body

{
  "ids": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  ]
}
```

Expected responses are of the form:
```
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "accepted": true
  }
]
```