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

# settings
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

# new repos
- I tried to add openzeppelin but it has no mocked commits so i cannot run. it's also weird it shows "This is not the latest commit" message when there are 0 commits. fix it.
- it's weird it allows clicking "Start Run" with no commit selected.
- remove the estimated cost label. not useful

------------------------

=== /plan fix-reports ===
the reports are broken. a blank screen is opened.


=== /plan feedback-from-colleagues ===
- in AI Auditor configurations, remove AI Auditor effort level and the other settings. 
The only settings is a radio selection that says either of two options
1. Analyze all contracts in the repository
2. Analyze only contracts listed for static analysis

Option 2 is only available if we defined contracts for static analysis.

- in Static analysis report:
- - the Verified tab should be 3rd
- - keep only high priority, low priority, verified tabs. instead of the rest, add a "+ Additional Views" tab which opens a menu with additional views - Input Validation, One-Time Functions, Results By Function, Rounding Analysis Viewer
- - update the title to include Certora AI Security Suite Static Analysis Report
- - add some margins between the rows in the header
- - remove the number of total rules checked.
- - "X iterations/rule" becomes "X AI judgement iterations per finding"
- - Remove "Jobs analyzed"
- - "Generated [date]" becomes "Report generated at [date]"

- main page:
- - the settings page from the "..." next to each repo goes to global settings instead of the repo's settings.
- - the label under "..." should be "Project Settings" not "Open Settings".

=== /plan verified-tab ===
the verified tab currently does not account for dismissed findings. i.e. if you dismiss a finding, it should not count negatively.. i.e if total verified + total dismissed = total # of findings of the checker , it means we have 100% coverage. worth using 'grey' color to indicate the dismissed ones but still show 100%.

=== /plan priority-tabs ===
add a chcekbox in the toc in high priority, low priority tabs that allows to group findings by checker, and within each checker group to sort as usual in descending confidence order. each group should be titled with the checker name.

=== /plan onetime-count ===
 I tried to dismiss all and I still don't get 100% in verified tab. turns out one-time do not show up in low priority. this should be changed actually. all findings should be in one of the         
priority tabs. 

=== /plan judge-integration ===
in the findings view, do not show judge validation section at all. impact and likelihood section should be folder under detailed analysis section