=== /plan #1 ===
we need to move localdashboard project to use uv/pip instead of docker.
first, we note that the main reason for docker was that we relied on docker anyway for the violation analyzer. but since then, we moved it to chromadb. 
so there's really no reason not to use it in the local mode with the local rag.
the local rag db can be fetched from ~/certora/aicomposerragdb 