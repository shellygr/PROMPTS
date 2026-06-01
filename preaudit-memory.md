<!-- feature-loop: c3b8c325 -->

=== /plan preaudit-memory ===
We tried to run preaudit on c7a.medium machines with 1vcpu and 2gb ram, and got an oom error soon after downloading zipOutput files of some jobs.
1. can you check in which places in the code we still fetch zipOutput and not use the newer POU enabled methods? is it for autosetup sanity only?
2. which points in the run could lead to such a high memory consumption?