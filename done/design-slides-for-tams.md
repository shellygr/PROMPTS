=== /plan design-slides-for-tams ===

I want to create slides for the new product AI Security Suite with special focus on our most interesting technology launched with it, called AutoProver.

Certora has developed a cutting-edge foraml verification tool for smart contracts written in Solidity, Rust, and Move, called Prover.
Prover was, in the realm of fv tools, one of the most accessible industrial-grade tools.
However, it was still hard to use.
Come AI, when combined with Certora's 8 year of know-how building, leads to the first automatic Prover tool, that takes the codebase, along with its high-level, English description, formally verifies its core properties, and finds tricky bugs. We are introudcing _AutoProver_.
AutoProver is the only tool that can protect your from the next AI agent. In fact, it gets better as AI gets better. It will infer more properties, more module dependencies, surface more potential issues and hidden assumptions in the code. AutoProver can take AI-generated bug reports and judge them, by assessing the scenario with the lens of formal methods, mapping it to existing rules or writing new ones, and generating concrete validation or refutation of the bug report.
[Claude - I'm attaching FV reports so you can get a sense of what Certora has written as part of its formal verification services, and what kind of outputs AutoProver users can expect]

Together with AutoProver, we are releasing two more tools that complement it as part of our new AI Security Suite.
First is AI Auditor - it can study your code (any code!) and produces a full audit report with prioritized issues and impact assessment. We have designed it to prioritize high quality signal and low noise.
Second is Static Analyzer - a comprehensive scanner for potentially risky code patterns that is high signal and low noise. 
Unlike traditional scanners, Certora Static Analysis reasons about concrete behaviors of your code, powered by the Certora Prover technology, to give 100% coverage of your contract but with concrete program traces for problematic patterns. 
Violations are analyzed and prioritized, giving high quality signals only.
Data shows that over 25% of exploited smart contract vulnerabilities, causing damages in the billions, were due to issues discoverable with the static analysis. [Claude - check my claim!]


All 3 tools are connected to a unified memory system that is personalized for your project. It learns your project as you develop it, and as you run the different tools, they share the insight and build a stronger internal understanding of your code. 
Whne you give feedback on a finding from any one of the tools, other tools take note and improve.
The tools are also learning from each other. AI Auditor can judge findings from Static Analyzeer and AutoProver. AutoProver generalizes findings from Static Analysis to infer higher-level invariants of the system. AutoProver is a judge for AI Auditor generated findings.

Subscription information:
Each run of the tools consumes a certain amount of credits, with Static Analysis taking the lowest amount of credits, AI Auditor more, and AutoProver the highest consumption. Exact numbers are TBD.


-----------------

