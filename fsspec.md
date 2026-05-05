=== /plan #1 ===
A colleague proposed we use fsspec for dual lcoal filesystem/s3 update.
What do you think if we used fsspec for some of the files we write in preaudit instead of syncing them via s3_sync.py? I thought about all the cache/state related writes in autosetup and preaudit. 
The certora/ folder would still have to be synced manually by s3_sync.py, since it's read by the jar and thus won't be available for the jar running.

But it would be particularly useful to get rid of specific files since those may change be preaudit/autosetup and thus we'll be chasing changes in both these repos and s3_sync.py. It would make renaming folders easier.
For example this part of s3_sync.py is very sensitive to changes and I believe already broke since we wrote it:
```

# Individual files (not directories) to preserve across runs.
CACHE_FILES = [
    ".certora_internal/autosetup_result.json", # TODO We would need to update this. also, brittle.
]
```