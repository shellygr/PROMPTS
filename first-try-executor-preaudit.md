=== /plan first-try ===
Let's fix up the saas entrypoints.
1. instead of the current env vars that match the names below, we want to use these names:
```
PREAUDIT_BUILDER_GH_TOKEN
PREAUDIT_BUILDER_REPO
PREAUDIT_BUILDER_GIT_REF
PREAUDIT_BUILDER_RESULTS_ZIP_URL
```

so gh_token is github_token, repo is the repo url, git_ref is the commit hash, and results_zip_url is simply a zip file we need to use instead of the current s3 uploads. the builder container will NOT have an access to s3, so it has to upload the zip. 

e.g.
```
def zip_and_upload(folder: Path, save_url: str | None = None) -> None:
    if not save_url:
        return

    with tempfile.SpooledTemporaryFile() as tmp_file:
        # Zip all results into tmp file
        with zipfile.ZipFile(tmp_file, "w") as zipf:
            for file in folder.rglob("*"):
                zipf.write(file, file.relative_to(folder))

        # Stream zipped results to S3
        tmp_file.seek(0)
        niquests.post(save_url, data=tmp_file)
```

review the needed changes to BUILDER only in this stage.
What are complications and risks? note we do not have anything in production yet, but we would need to make sure the testing via localstack can work still.