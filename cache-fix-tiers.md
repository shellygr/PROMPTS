=== /plan fix-get_referenced_file_with_hashes-and-more ===
In ~/certora/Autosetup we have a soundnedss bug in the cache useed by prover_runner.py. 
the function get_referenced_file_with_hashes does not check the file hashes of all solidity imports.
I propose a tiered approach. current `get_cache_key` becomes tier 1 cache just for main files and everything computed
by get_referenced_file_with_hashes today. 
We add to cache_data the list of sources 
Then, if we have a hit on the first tier, we also check the list of the files and their content hashes CURRENTLY - if ALL match the saved(cached) content hashes per-file, then this is a hit.
Otherwise, it's a miss, we have to recompute everything including the content hashes for this cache key. We do not store separate caches per different content-hash mappings of the sources.