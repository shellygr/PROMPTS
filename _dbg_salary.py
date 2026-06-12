import os, json
from dotenv import load_dotenv
import fetch_employees as fe

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
url = os.environ.get("SHAPES_API_URL", fe.DEFAULT_URL)
refresh = os.environ.get("SHAPES_REFRESH_TOKEN")
token = fe.exchange_refresh_token(url, refresh) if refresh else os.environ.get("SHAPES_API_KEY")
gql = fe.make_client(url, token, refresh_token=refresh)

SALARY_FT = "103320"

data, _ = gql("query { employees { id firstName lastName } }")
emp = next(e for e in data["employees"] if "jarosl" in (e["firstName"] + " " + e["lastName"]).lower())
eid = emp["id"]
print(f"employee: {emp['firstName']} {emp['lastName']} ({eid})\n")

Q = "query($f: EmployeeFieldValueFilters){ employeeFieldValues(filters:$f){ id employeeFieldTypeId textValue fieldValue effectiveDate updatedAt employeeFieldType { fieldName context } } }"

# all field values for Jaroslav
data, _ = gql(Q, {"f": {"employeeId": [eid]}})
rows = data.get("employeeFieldValues") or []
print(f"total field values for Jaroslav: {len(rows)}")

# salary rows specifically
sal = [r for r in rows if r["employeeFieldTypeId"] == SALARY_FT]
print(f"\nsalary_amount rows: {len(sal)}")
for r in sal:
    print("   ", json.dumps({"id": r["id"], "text": r["textValue"], "eff": r["effectiveDate"], "upd": r["updatedAt"]}))

# any field type that appears more than once for Jaroslav
from collections import Counter
c = Counter(r["employeeFieldTypeId"] for r in rows)
print("\nfields with >1 row for Jaroslav:")
names = {r["employeeFieldTypeId"]: (r.get("employeeFieldType") or {}).get("fieldName") for r in rows}
for ftid, n in c.items():
    if n > 1:
        vals = [r for r in rows if r["employeeFieldTypeId"] == ftid]
        print(f'  {names[ftid]!r} x{n}: ' + " | ".join(f'{v["textValue"]}@{v["effectiveDate"]}' for v in vals))
