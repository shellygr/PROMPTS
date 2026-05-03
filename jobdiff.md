=== ===
we want to reuse parts of the local dashboard responsible for diffing runs. 
the idea is that we will build a tool that takes as input 2 job urls and produces an HTML page that renders the diff in conf, code, and spec visually and interactively. right now we have diff for all three components but it is relative to a file system state. instead we want to download two jobs using tarball management with caching and run the diff, record the results in Json format just like local dashboard does now, and produce a static independent HTML report. 

your goal is first to study the existing infrastructure and code that performs the diff in the current code. 
then, device a plan on how to implement this tool using shared code from local dashboard. then, package the tool using UV and make it easily installable.
finally, we should have proper CI test for this tool. when the time is right I will provide you with multiple pairs of runs that will be compared.

now that you know the overall picture start with the first goal and proceed with planning building the tool. we will continue with other tasks in further plans.