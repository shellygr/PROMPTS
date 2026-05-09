<!-- feature-loop: b64cf3b0 -->

=== /plan inputvalidation ===
we need to cover something we forgot in the input validation rules which is environment variables, prominently msg.sender and msg.value. so for each method checked in input_validation rules and dependent_inputs rules, we need to add a variant where all inputs are the same but only msg.sender changes.
msg.value has to be checked only if the method checked is payable, otherwise no need to generate a rule.