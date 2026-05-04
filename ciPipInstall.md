<!-- feature-loop: 0ab26f83 -->

=== /question #1 siblings:autosetup ===
The team is really annoyed that because pyproject.toml contains renamed hostnames for github for CI to work properly with ssh, we cannot install with `pip install -e .`.
We had the idea as follows: how about we write normal pyproject.toml no renamed hostnames, and in a comment with `#` in the toml at the end of the relevant line write the right hostname addition for CI only? i.e. next to proveroutpututility declaration we will write `# pou`
then we have to monkey patch pyproject.toml of both autosetup and preaudit before we start installing in CI. Would that work?

=== /plan ===
plan it for both repos. work in worktrees.
