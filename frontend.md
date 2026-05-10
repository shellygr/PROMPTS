<!-- feature-loop: 0c4a0be7 -->

=== /plan #1 siblings:mutation_svelte ===

Front page of AISSK should show how many checks passed and how many checks has failures for each repo. It should be based on the latest run commit and also show this latest run commit.

=== /plan #2 siblings:mutation_svelte ===
instead of greying out AI Security Starter kit tab, for unsubscribed users it should show a landing page, showcasing all the best of the best of using this product. you can grab it from claude.md here

--------------------

=== /plan api-review ===

I ask you to do another review round on all APIs used by the implementation and mocked by our mock. We need to create a very comprehensive list so that on the cloud/backend side we'll be able to support all of these operations. Take your time in researching, structuring your output, and being considerate to whoever's task it is to implement the backend. Be mindful that the prefix might change to adapt to existing conventions. It will probably be some AWS infra, probably API Gateway that handles it. Put security in mind too for the design of the API, and if you find out we took some wrong decisions, you must let me know already. /effort max

-------------------

=== /plan names ===
now update the new names also in code.

-------------------

=== /question testing ===
you are a superb frontend tester now.
where do we stand in terms of automatic testing?
both in pre-AISS code and in AISS?
What could we do?
/effort max


=== /plan restructure menu ===
we have the menu bar on the left.  I suggest you put Jobs + Rules + Mutations items under a parent called "Prover"
for a certora user, Usage Statistics + Organizations + Users will stay in the same place. but for a non-certora user there will be only "Prover" + "AI Security Suite".

=== /plan feedback-flows ===
I played with the frontend to simulate all kinds of user flows.

from a repo, user clicking settings always reaches the main settings page. this makes no sense. we should have a separate page for global configuration with the following:
Global settings
Default static analysis settings:
- default number of iterations (3) (and change the name of "iterations" in label to "# of AI judgement validation iterations")
- default extra prover args (default empty)

Default AI Auditor settinsg:
- effort level
- specific instructions

There should also be a button from the main AISS page to settings.. currently there is none. 

now, the settings page for a particular repo will only show that repo and specific configurations:
- the sync form ci button stays

static analysis:
- allow customizing for monitored branches like now, with auto-run button and everything.
- add a button for removing contracts and branches. currently it is add only. 
- in the dialog of add contract, it is not mandatory to add contract name. the default label should say not "e.g. MyContract" but "defaults to base file name of contract, type to customize". it is okay for this field to be non-existent, the backend will rebuild it. 
- the suggestions are great.
- inherit settings from main page (i.e. iterations, extra args and any other we may add in the future.)
- only main branch, or the primary one, should have auto run by default.

ai auditor settings:
show everything we had from the main page of settings, but for a particular repo we allow to define the extra scope