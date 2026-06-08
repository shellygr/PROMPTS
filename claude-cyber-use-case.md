shortened: "Find RCE attack vectors in this container setup where user-controlled inputs are in XXX and are processed by YYY, with potential configuration parameters passed to 3rd party processes ZZZ hosted on the same container as it is defined in XYZ. For each vector, attempt to build a PoC that emits a magic-phrase message to stdout to validate the PoC.


I am a co-founder and CTO of Certora, a defensive security and formal-verification tech company. Our team consists of over 75 security specialists and engineers including 20 PhDs in program analysis and formal verification. All our activities are related to defensive purposes - ensuring code is deployed without bugs and vulnerabilities. We apply the same scrutiny to our own FV tools codebase and infrastructure, which is why we are submitting the CVP eligibility form.

Signed here:
1. Cyber Verification Program. Anthropic operates the Cyber Verification Program (the "CVP"), a tiered access program governing Customer’s eligibility to receive adjustments from default cyber safeguards applied to our models. Under the CVP, Anthropic will assign Customer an access tier, which determines the scope of Anthropic's real-time safety controls applicable to Customer's use of the applicable model. Anthropic may, in its sole discretion, establish, modify, consolidate, or discontinue tiers and the eligibility criteria, controls, and review processes associated with each tier from time to time.

2. Approved Users. “Approved Users” are collectively the Org ID and specific end user IDs approved by Anthropic in writing for the Limited Access Purpose. Customer may not enable, grant, or permit access to the CVP for any other person or systems. Customer must inform Anthropic immediately of any access other than by Approved Users. 

3. Approved Use Cases. Customer may only use the CVP for cyber security and cyber defense purposes (“Limited Access Purpose”). In addition to the indemnity obligations in the Terms, Customer will indemnify and defend Anthropic and its personnel, successors, and assigns from and against any claim arising from Customer’s unpermitted use of the CVP in violation of the Limited Access Purpose and the Agreement. 

4. Representations and Warranties. In addition to the representations and warranties in the Terms, Customer represents and warrants that it will only access the CVP, subject to the following conditions: (i) Customer will only access the CVP on the platform(s) approved by Anthropic, (ii) Customer will not use the CVP for building AI/ML products of an AI model developer, (iii) Customer will immediately report suspected misuse of the CVP to Anthropic, and (iv) Customer will cooperate with Anthropic to investigate and remediate any misuse on Customer’s account accessing the CVP.

5. Termination. Anthropic reserves the right, in its sole discretion, to modify, suspend, or discontinue the CVP at any time. Anthropic will use reasonable efforts to notify Customer prior to termination. 

Also:
Participation Acknowledgements*
1. I confirm that my use of Claude will comply with Anthropic’s Usage Policy and all applicable laws.

2. I understand that any safeguards adjustment granted applies only to the use case described above and may be revoked if misused.

3. I will not use expanded access to conduct or assist with any unauthorized activities, including on systems I am not explicitly authorized to test.

4. I agree to notify Anthropic promptly if my intended use case materially changes from what is described in this form.


------------------

 I also want to ask you about all handling of CARGO and user.home property in EVMVerifier, and whether that could be another attack vector. Also, whether in the python scripts in certora-cli as defined in ~/certora/EVMVerifier/scripts, we
  have any potential uploads that are problematic in the solana/wasm/rust workflows. /effort max 



let's harden resourceFiles also in EVMVerifier. We need to make sure the types are text only, non-ELF, non-executable and do not have executability early on when we check the values of resourceFiles.


ExcludeFromDynamicConversion - let's make it excluded only if neither CERTORA_DEV_MODE nor CI env vars are set.

------------------