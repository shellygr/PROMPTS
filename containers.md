=== /plan #1 ===

We are going back to the containerization feature.
We need to be able to generate the images from CI and upload them to ghcr.
Then, we need to have a test workflow that checks that a simple dummy run (e.g. a-la dummyproject-integration) fully works, but instead of invoking the script directly, it should test two kinds of workflows:
1. run only preaudit docker image in a sterile environment with only docker
2. run first autobuild image, then 'upload' results like s3_sync does, then invoke the preaudit image on this output.
Let's focus on #1 for now.

In this plan, we focus only on setting up the ci workflows that build both images and publish them. In general, we want to release only when tags on main are created. For testing, we also want to be able to manually dispatch the task so that we could operate on the test images.

Explore the image definitions.
Plan the CI workflow for building them.

=== /plan #2 ===
Now, let's focus on planning the testing for bullet 1 out of plan #1. 
It should be runnable both locally and in CI. it should run the SimpleVault contract of the dummy project.

=== /plan #3 ===
After we completed plan #1 and #2 and just the first bullet out of #1, we need to plan the testing of the scenario described in the second bullet on the same contract as in plan #2. 