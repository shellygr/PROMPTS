=== /plan benchmarks ===
we have spent a while building collect_solidity_benchmarks.py which is a useful tool for summarizing what is available as potential benchmark tests.
each main directory in the output csv of this script could be considered a "collection". 
I would like to make it easy to fetch those benchmarks and run on them.

Here's my plan for you which you should execute one-by-one:
1. What is the full size of each collection? Look only at the path column, and compute how much storage each of the collections take by summing over projects' storage.
2. What would be the expected size of each collection if we tar-gzipped it?
3. Would it be feasible to upload these gzipped tarballs to a new repository under Certora?
4. If yes, we should create a new repo github.com/Certora/CertoraBench 
5. We prepare all tarballs within /Volumes/PREAUDIT/CertoraBench, which would be the local copy of the new repo
6. We add the CSV generated from collect_solidity_benchmarks.py script to the repo, normalizing the paths to be relative to /Volumes/PREAUDIT
7. We add a script cert_bench_helper.py to help fetching and extracting individual tarballs into a sibling dir of the repo if the sibling dir does not exist already.
8. We create a readme where we recommend cloning CertoraBench into a directory with CertoraBench repo as one subdirectory and extracted_bench/ as the other.
9. We add to cert_bench_helper the capability to create new collections from a directory or to update existing ones.
10. Before we update an existing collection we allow the user to study the diff (which projects are removed and which are added) along with the diff of the csv that would be needed, to make sure changes are correlated.