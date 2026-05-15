<!-- feature-loop: c756e9e7 -->

=== /plan #1 siblings:certora-cloud-cli ProverOutputUtility===
My colleague recommended that all database accesses done by preaudit would use HTTP requests. Basically, to assume it is part of the cloud-cli here `~/Certora/certora-cloud-cli` or a similar API as is used by ProverOutputUtilty.
This specifically pertains to the findings.db we are currently storing locally. 
Reminder: preaudit is a tool that runs on a particular project (repository), which is associated under an organization/account. We perform scans on a specific commit and on a specific contract which exists in that commit.
The user will likely run on new commits as they arrive, or trigger runs on older commits if they are important.
We assume only one preaudit run occurs per <account,repository,contract>. so one commmit runs at a time.
It is also the case that we cannot leak information between accounts. THIS IS A MUST HAVE REQUIREMENT.

Findings are identified using a fingerprint as we have worked on before as part of `FindingsStore`. 

The APIs we would need are:
1. Save the findings.db, or persisting it to a database under <account,repository,contract> + <commit>, with the date of the run.
2. Listing findings on this <account,repository,contract> + <commit> tuple - i.e. a saved run.
3. Listing findings from the last run of <account,repository,contract>.
4. Post a dismissal OR confirmation of a finding. The 3rd state possible for each finding is neither dismissed nor confirmed.
5. Undo-ing a dismissal or confirmation, of a finding, which makes it reach the 'no state' listed above.
6. Listing dismissals for <account,repository,contract> for all commits.

For all data entities we would create and ORM model and corresponding CRUD endpoints
on our API. So for exmaple we would have:
```
class Finding(MappedAsDataclass, Base):
    id: Mapped[UUID]
    fingerprint: Mapped[str]
    rule_name: Mapped[str]
    ...

def create_finding(fingerprint: str, rule_name: str) -> Finding:
    if settings.local:
        finding = Finding(id=uuid4(), fingeprint=fingerprint, ...)
        session.add(finding)
        session.commit()
        return finding
    else:
        # Call API endpoint get or crate
        response = client.post(
            f"{settings.api_url}/findings",
            json={"fingerprint": fingerprint, "rule_name": rule_name},
            # Auth
        )
        response.raise_for_status()
        data = response.json() # Even better pydantic so we get the validation right away
        return Finding(fingerprint=data["fingerprint"], rule_name=data["rule_name"])
```

maybe you can even automatically intercept the http calls in local mode and 'implement' the API, so that we can keep the code clean with just http calls.
