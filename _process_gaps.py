import json, csv, datetime, re

PAGE1 = "/Users/shelly/.claude/projects/-Users-shelly-Certora-PROMPTS/1f8cfe83-5d15-464f-940e-482ee3157a04/tool-results/mcp-claude_ai_monday_com-get_board_items_page-1780492220544.txt"
PAGE2 = "/Users/shelly/Certora/PROMPTS/_mday_page2.json"
OUT   = "/Users/shelly/Certora/PROMPTS/deal_timeline_gap.csv"

items = []
with open(PAGE1) as f:
    items += json.load(f)["items"]
with open(PAGE2) as f:
    items += json.load(f)["items"]

# work-type -> (EE col, timeline col, team col, standard people staffing)
WT = {
    "Audit":         ("numbers__1",        "timeline",            "people",                   2),
    "FV":            ("numeric_mkpb451a",  "timerange_mkpdmyya",  "multiple_person_mkpbxeyz", 1),
    "Design Review": ("numeric_mkpdkf8b",  "timerange_mkpegxn2",  "multiple_person_mkpezh0z", 1),
    "Fixes Review":  ("numeric_mkxk3m1m",  "timerange_mkxkp014",  None,                       1),
}

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def client_name(cv, name):
    d = cv.get("dropdown_mkpc1j1")
    if isinstance(d, str) and d.strip():
        return d.strip()
    if cv.get("text_mkrecpds"):
        return cv["text_mkrecpds"].strip()
    # derive from item name
    if " - " in name:
        return name.split(" - ")[0].strip()
    # strip trailing work-type words
    return re.sub(r"\b(Audit|FV|Fixes?\s*Review|Design\s*Review|DD|project)\b.*$", "", name, flags=re.I).strip() or name

def team_size(cv, col):
    if not col:
        return None
    v = cv.get(col)
    if not v or not isinstance(v, str):
        return None
    return len([p for p in v.split(",") if p.strip()])

def cal_weeks(cv, col):
    v = cv.get(col)
    if not v or not isinstance(v, str) or " - " not in v:
        return None, None, None, None
    a, b = [x.strip() for x in v.split(" - ")]
    try:
        d0 = datetime.date.fromisoformat(a)
        d1 = datetime.date.fromisoformat(b)
    except ValueError:
        return None, a, b, v
    wk = round((d1 - d0).days / 7.0, 1)
    return wk, a, b, v

rows = []
no_ee_but_timeline = 0
for it in items:
    cv = it["column_values"]
    name = it["name"]
    client = client_name(cv, name)
    proj = cv.get("text1__1") or name
    start = cv.get("date__1")
    status = cv.get("status") or ""
    for wt, (ee_c, tl_c, team_c, std) in WT.items():
        ee = num(cv.get(ee_c))
        acal, astart, aend, tlstr = cal_weeks(cv, tl_c)
        if ee is None or ee <= 0:
            if acal is not None and ee is None:
                no_ee_but_timeline += 1
            continue
        agreed_cal = round(ee, 2)                 # EE as written = agreed calendar weeks
        agreed_pw  = round(ee * std, 2)           # person-weeks via standard staffing
        tsize = team_size(cv, team_c)
        actual_cal = acal
        actual_pw  = round(acal * tsize, 2) if (acal is not None and tsize) else None
        gap_cal = round(actual_cal - agreed_cal, 2) if actual_cal is not None else None
        gap_pw  = round(actual_pw - agreed_pw, 2) if actual_pw is not None else None
        rows.append({
            "Client": client, "Project": proj, "WorkType": wt,
            "Agreed_cal_wk": agreed_cal, "Agreed_personwk": agreed_pw,
            "Actual_cal_wk": actual_cal, "Actual_team": tsize, "Actual_personwk": actual_pw,
            "Gap_cal_wk": gap_cal, "Gap_personwk": gap_pw,
            "Agreed_start": start, "Actual_start": astart, "Actual_end": aend,
            "Status": status,
        })

rows.sort(key=lambda r: (r["Agreed_start"] or ""))
cols = ["Client","Project","WorkType","Agreed_cal_wk","Agreed_personwk","Actual_cal_wk","Actual_team","Actual_personwk","Gap_cal_wk","Gap_personwk","Agreed_start","Actual_start","Actual_end","Status"]
with open(OUT,"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)

# ---- summary ----
total_items = len(items)
with_actual = [r for r in rows if r["Gap_cal_wk"] is not None]
print(f"Projects (2025+ start): {total_items}")
print(f"Work-type rows with an agreed EE>0: {len(rows)}")
print(f"  of which have an actual timeline (gap computable): {len(with_actual)}")
print(f"  rows with timeline but NO agreed EE (excluded): {no_ee_but_timeline}")
print()
by = {}
for r in rows:
    by[r["WorkType"]] = by.get(r["WorkType"],0)+1
print("By work-type:", by)
print()
def show(title, lst):
    print(title)
    print(f"{'Client':20}{'Project':30}{'Type':7}{'Agr':>5}{'Act':>5}{'GapC':>6}{'GapPW':>7}{'AgrStart':>12}{'ActStart':>12}{'ActEnd':>12}")
    for r in lst:
        print(f"{(r['Client'] or '')[:19]:20}{(r['Project'] or '')[:29]:30}{r['WorkType'][:6]:7}"
              f"{r['Agreed_cal_wk']:>5}{(r['Actual_cal_wk'] if r['Actual_cal_wk'] is not None else '-'):>5}"
              f"{(r['Gap_cal_wk'] if r['Gap_cal_wk'] is not None else '-'):>6}"
              f"{(r['Gap_personwk'] if r['Gap_personwk'] is not None else '-'):>7}"
              f"{(r['Agreed_start'] or '-'):>12}{(r['Actual_start'] or '-'):>12}{(r['Actual_end'] or '-'):>12}")
    print()

over = sorted([r for r in with_actual], key=lambda r:r["Gap_cal_wk"], reverse=True)
show("TOP 15 OVERRUNS (actual calendar >> agreed):", over[:15])
show("TOP 10 UNDER (finished faster than agreed):", over[-10:])

tot_agr = sum(r["Agreed_personwk"] for r in with_actual)
tot_act = sum(r["Actual_personwk"] for r in with_actual if r["Actual_personwk"] is not None)
print(f"Totals over {len(with_actual)} computable rows: agreed {round(tot_agr,1)} person-wk vs actual {round(tot_act,1)} person-wk (where team known)")
print(f"CSV written: {OUT}")
