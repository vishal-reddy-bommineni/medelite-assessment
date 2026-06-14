"""
MedElite - Facility Assessment Report Generator
Enhanced UI + simple proven PDF format.
"""

import streamlit as st
import requests
import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

st.set_page_config(
    page_title="INFINITE - Facility Assessment",
    page_icon="🏥",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.brand-banner {
    background: linear-gradient(135deg, #1B2A4A 0%, #243659 100%);
    border-radius: 10px; padding: 20px 28px; margin-bottom: 28px;
    border-bottom: 3px solid #00A99D;
}
.brand-infinite { font-size:30px; font-weight:900; color:#00A99D; letter-spacing:5px; margin:0; line-height:1; }
.brand-sub      { font-size:10px; color:#6B85B0; letter-spacing:3px; margin:3px 0 12px 0; }
.brand-title    { font-size:13px; font-weight:700; color:#E8EDF5; letter-spacing:2px; margin:0; }

.fac-card {
    background:white; border:1px solid #E2E8F0; border-radius:10px;
    padding:20px 24px; margin:16px 0; box-shadow:0 2px 12px rgba(0,0,0,0.06);
}
.fac-name     { font-size:19px; font-weight:700; color:#1B2A4A; margin:0 0 3px 0; }
.fac-location { font-size:13px; color:#64748B; margin:0 0 14px 0; }
.fac-toprow   { display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px; margin-bottom:14px; }
.star-row     { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:14px; }
.star-block   { text-align:center; }
.sc { width:50px; height:50px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:19px; font-weight:900; color:white; margin:0 auto 3px; }
.sc1{background:#DC2626;} .sc2{background:#EA580C;} .sc3{background:#D97706;}
.sc4{background:#16A34A;} .sc5{background:#15803D;} .sc0{background:#94A3B8;}
.star-label   { font-size:10px; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }
.risk-badge   { display:inline-block; padding:5px 14px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:1px; }
.risk-low    { background:#DCFCE7; color:#166534; border:1px solid #86EFAC; }
.risk-medium { background:#FEF9C3; color:#854D0E; border:1px solid #FDE047; }
.risk-high   { background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; }
.med-link    { font-size:11px; color:#00A99D; text-decoration:none; border:1px solid #00A99D; padding:4px 10px; border-radius:4px; }
.clin-summary { background:#F8FAFC; border-left:4px solid #00A99D; border-radius:0 8px 8px 0; padding:11px 15px; margin-top:12px; font-size:13px; color:#374151; line-height:1.6; }

.section-label { background:#E6F7F6; border-left:4px solid #00A99D; padding:7px 14px; font-size:11px; font-weight:700; color:#1B2A4A; border-radius:0 6px 6px 0; margin:20px 0 4px 0; letter-spacing:0.5px; text-transform:uppercase; }
.irow { display:flex; justify-content:space-between; padding:7px 14px; border-bottom:1px solid #F1F5F9; font-size:13px; }
.ilabel { color:#1B2A4A; font-weight:600; flex:1; }
.ival   { color:#374151; flex:1; text-align:right; }
.srow   { display:flex; justify-content:space-between; align-items:center; padding:7px 14px; border-bottom:1px solid #F1F5F9; font-size:13px; }
.sc-small { width:28px; height:28px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; color:white; }

.bench-row   { padding:9px 14px; border-bottom:1px solid #F1F5F9; }
.bench-top   { display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; font-size:12px; }
.blabel      { color:#1B2A4A; font-weight:600; }
.bench-track { height:8px; background:#E2E8F0; border-radius:4px; position:relative; margin-bottom:3px; }
.bench-fill  { height:100%; border-radius:4px; }
.bench-mark  { position:absolute; top:-3px; width:2px; height:14px; background:#1B2A4A; border-radius:1px; }
.bench-vals  { font-size:10px; color:#94A3B8; margin-top:2px; }
.bworse  { background:#FEE2E2; color:#991B1B; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; }
.bbetter { background:#DCFCE7; color:#166534; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; }
.bna     { background:#F1F5F9; color:#64748B;  border-radius:4px; padding:2px 8px; font-size:11px; }
.med-footer { padding:10px 14px; font-size:12px; color:#94A3B8; border-top:1px solid #F1F5F9; }
.med-footer a { color:#00A99D; text-decoration:none; }
.empty-state { text-align:center; padding:70px 20px; color:#94A3B8; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

CMS_BASE     = "https://data.cms.gov/provider-data/api/1/datastore/query"
DS_PROVIDER  = "4pq5-n9py"
DS_CLAIMS    = "ijh5-nb2v"
DS_STATE_AVG = "xcdc-v8bm"

COL_CCN          = "cms_certification_number_ccn"
COL_STATE_NATION = "state_or_nation"

F_NAME     = "provider_name"
F_ADDRESS  = "provider_address"
F_CITY     = "citytown"
F_STATE    = "state"
F_ZIP      = "zip_code"
F_BEDS     = "number_of_certified_beds"
F_LOCATION = "location"
F_OVERALL  = "overall_rating"
F_HEALTH   = "health_inspection_rating"
F_STAFFING = "staffing_rating"
F_QM       = "qm_rating"

F_STR_HOSP = "percentage_of_short_stay_residents_who_were_rehospitalized__1d02"
F_STR_ED   = "percentage_of_short_stay_residents_who_had_an_outpatient_em_d911"
F_LT_HOSP  = "number_of_hospitalizations_per_1000_longstay_resident_days"
F_LT_ED    = "number_of_outpatient_emergency_department_visits_per_1000_l_de9d"

F_MEASURE_CODE = "measure_code"
F_ADJ_SCORE    = "adjusted_score"
F_OBS_SCORE    = "observed_score"

# ─────────────────────────────────────────────────────────────────────────────
# CMS API
# ─────────────────────────────────────────────────────────────────────────────

def cms_query(dataset_id: str, field: str, value: str, limit: int = 50) -> list:
    url = (
        f"{CMS_BASE}/{dataset_id}/0"
        f"?conditions[0][property]={field}"
        f"&conditions[0][value]={value}"
        f"&conditions[0][operator]=="
        f"&limit={limit}"
    )
    try:
        r = requests.get(url, timeout=20, headers={"Accept": "application/json"})
        if r.status_code == 200:
            return r.json().get("results", [])
        st.error(f"CMS API {r.status_code}: {r.text[:200]}")
        return []
    except Exception as e:
        st.error(f"Network error: {e}")
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_provider(ccn: str) -> dict | None:
    r = cms_query(DS_PROVIDER, COL_CCN, ccn, limit=1)
    return r[0] if r else None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_claims(ccn: str) -> list:
    return cms_query(DS_CLAIMS, COL_CCN, ccn, limit=50)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_state_avg(state: str) -> dict | None:
    r = cms_query(DS_STATE_AVG, COL_STATE_NATION, state, limit=1)
    return r[0] if r else None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nat_avg() -> dict | None:
    for v in ["US", "NATION"]:
        r = cms_query(DS_STATE_AVG, COL_STATE_NATION, v, limit=1)
        if r:
            return r[0]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def safe_float(v) -> float | None:
    try:
        f = float(str(v).replace("%", "").strip())
        return None if f != f else f
    except (TypeError, ValueError):
        return None


def get(d: dict, key: str, default="") -> str:
    v = d.get(key, default)
    if v is None or str(v).lower() in ("nan", "none", ""):
        return default
    return str(v)


def ascii_only(s: str) -> str:
    return (s.replace("\u2014", "-").replace("\u2013", "-")
             .replace("\u2018", "'").replace("\u2019", "'")
             .replace("\u201c", '"').replace("\u201d", '"')
             .encode("ascii", "replace").decode("ascii"))


def fmt_pct(v) -> str:
    f = safe_float(v)
    return f"{f:.1f}%" if f is not None else "N/A"


def fmt_rate(v) -> str:
    f = safe_float(v)
    return f"{f:.2f}" if f is not None else "N/A"


def star_css_class(n: int) -> str:
    return {0:"sc0",1:"sc1",2:"sc2",3:"sc3",4:"sc4",5:"sc5"}.get(n, "sc0")


def star_bg(n: int) -> str:
    return {0:"#94A3B8",1:"#DC2626",2:"#EA580C",3:"#D97706",
            4:"#16A34A",5:"#15803D"}.get(n, "#94A3B8")


# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# STR scores stored as percentages already (e.g. 25.6 = 25.6%) - no multiply
# LT scores are rates per 1000 resident days - display as float
# ─────────────────────────────────────────────────────────────────────────────

def build_metrics(claims: list, state_avg: dict | None, nat_avg: dict | None) -> list:
    if not claims:
        return []
    by_code = {row.get(F_MEASURE_CODE, "").strip(): row for row in claims}

    MEASURES = [
        ("Short Term Hospitalization",       "521", F_STR_HOSP, True,  True),
        ("Short Term ED Visit",              "526", F_STR_ED,   True,  True),
        ("LT Hospitalization (per 1k days)", "551", F_LT_HOSP,  False, True),
        ("LT ED Visit (per 1k days)",        "552", F_LT_ED,    False, True),
    ]

    out = []
    for label, code, avg_col, is_pct, lower_better in MEASURES:
        row = by_code.get(code)
        if not row:
            continue
        raw   = get(row, F_ADJ_SCORE) or get(row, F_OBS_SCORE)
        nat_v = get(nat_avg   or {}, avg_col)
        sta_v = get(state_avg or {}, avg_col)

        fac_s = fmt_pct(raw)   if is_pct else fmt_rate(raw)
        nat_s = fmt_pct(nat_v) if is_pct else fmt_rate(nat_v)
        sta_s = fmt_pct(sta_v) if is_pct else fmt_rate(sta_v)

        fac_f, nat_f = safe_float(raw), safe_float(nat_v)
        if fac_f is not None and nat_f is not None:
            is_worse = (fac_f > nat_f) if lower_better else (fac_f < nat_f)
        else:
            is_worse = None

        bar_pct = None
        if fac_f is not None and nat_f is not None and nat_f > 0:
            bar_pct = min(int((fac_f / (nat_f * 2)) * 100), 100)

        out.append({
            "label": label, "facility_val": fac_s,
            "nat_val": nat_s, "state_val": sta_s,
            "is_worse": is_worse, "bar_pct": bar_pct,
        })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# RISK SCORING
# ─────────────────────────────────────────────────────────────────────────────

def compute_risk(facility: dict, metrics: list):
    score = 0
    overall  = safe_float(get(facility, F_OVERALL))
    health   = safe_float(get(facility, F_HEALTH))
    staffing = safe_float(get(facility, F_STAFFING))

    if overall  is not None and overall  <= 2: score += 2
    elif overall  is not None and overall  <= 3: score += 1
    if health   is not None and health   <= 2: score += 2
    elif health   is not None and health   <= 3: score += 1
    if staffing is not None and staffing <= 2: score += 1

    worse  = sum(1 for m in metrics if m["is_worse"] is True)
    better = sum(1 for m in metrics if m["is_worse"] is False)
    score += worse

    level = "high" if score >= 5 else "medium" if score >= 2 else "low"
    label = {"high":"HIGH RISK","medium":"MEDIUM RISK","low":"LOW RISK"}[level]

    parts = []
    if overall is not None:
        parts.append(f"{int(overall)}-star overall rating")
    if health is not None and health <= 2:
        parts.append("critically low health inspection score")
    if worse > 0:
        parts.append(
            f"performs above the national average on "
            f"{worse} of {len(metrics)} hospitalization metric{'s' if worse>1 else ''}"
        )
    elif better > 0:
        parts.append("performs at or below national averages on all measured hospitalization metrics")
    if staffing is not None and staffing <= 2:
        parts.append("understaffed relative to CMS benchmarks")

    intros = {
        "high":   "Elevated risk profile - this facility carries a ",
        "medium": "Moderate risk profile - this facility has a ",
        "low":    "Favorable risk profile - this facility has a ",
    }
    summary = (intros[level] + ", ".join(parts) + ". Review recommended before partnership discussions."
               if parts else "Insufficient data to generate a clinical assessment.")

    return level, label, summary


# ─────────────────────────────────────────────────────────────────────────────
# PDF  — simple proven format from working version, ASCII-safe
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(facility: dict, manual: dict, metrics: list, ccn: str,
                 risk_label: str, risk_summary: str, analyst_note: str) -> bytes:

    NAVY  = (27,42,74);   TEAL  = (0,169,157);   LTEAL = (230,247,246)
    WHITE = (255,255,255); LGRAY = (247,248,250);  DGRAY = (85,85,85)
    RED   = (217,79,79);   GREEN = (46,158,107);   AMBER = (232,144,58)

    display_name = ascii_only(manual.get("custom_name") or get(facility, F_NAME))
    state    = ascii_only(get(facility, F_STATE))
    location = ascii_only(get(facility, F_LOCATION)
                or ", ".join(filter(None, [
                    get(facility, F_ADDRESS),
                    get(facility, F_CITY),
                    f"{state} {get(facility, F_ZIP)}".strip(),
                ])))
    med_url = f"https://www.medicare.gov/care-compare/details/nursing-home/{ccn}"
    beds    = ascii_only(get(facility, F_BEDS))
    summary = ascii_only(risk_summary)
    note    = ascii_only(analyst_note or "")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=22)

    # Header banner
    pdf.set_fill_color(*NAVY); pdf.rect(0, 0, 210, 34, "F")
    pdf.set_font("Helvetica","B",18); pdf.set_text_color(*TEAL)
    pdf.set_xy(10,5); pdf.cell(0,8,"INFINITE",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_font("Helvetica","",7); pdf.set_text_color(136,153,187)
    pdf.set_x(10); pdf.cell(0,4,"Managed by MEDELITE",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_font("Helvetica","B",10); pdf.set_text_color(*WHITE)
    pdf.set_xy(10,5); pdf.cell(190,8,"FACILITY ASSESSMENT SNAPSHOT",align="R",
                               new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_font("Helvetica","",8); pdf.set_text_color(136,153,187)
    pdf.set_x(10); pdf.cell(190,4,state,align="R",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(8)

    def shdr(title):
        pdf.set_fill_color(*TEAL); pdf.rect(pdf.get_x(),pdf.get_y(),2.5,7,"F")
        pdf.set_fill_color(*LTEAL); pdf.set_x(pdf.get_x()+2.5)
        pdf.set_font("Helvetica","B",9); pdf.set_text_color(*NAVY)
        pdf.cell(0,7,f"  {title}",fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        pdf.ln(1)

    def irow(label, value, shade=False):
        pdf.set_fill_color(*(LGRAY if shade else WHITE))
        pdf.set_draw_color(221,227,237); pdf.set_line_width(0.2)
        pdf.set_font("Helvetica","B",8.5); pdf.set_text_color(*NAVY)
        pdf.cell(78,7,f"  {ascii_only(label)}",border="B",fill=True)
        pdf.set_font("Helvetica","",8.5); pdf.set_text_color(34,34,34)
        pdf.cell(0,7,f"  {ascii_only(value or '-')}",border="B",fill=True,
                 new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    def srow(label, stars, shade=False):
        pdf.set_fill_color(*(LGRAY if shade else WHITE))
        pdf.set_font("Helvetica","B",8.5); pdf.set_text_color(*NAVY)
        pdf.cell(78,7,f"  {label}",border="B",fill=True)
        pdf.set_font("Helvetica","",9); pdf.set_text_color(*AMBER)
        pdf.cell(50,7,"  " + ("*" * stars) + ("o" * (5-stars)),border="B",fill=True)
        pdf.set_text_color(*DGRAY); pdf.set_font("Helvetica","",7.5)
        pdf.cell(0,7,f"  ({stars}/5)",border="B",fill=True,
                 new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    # Risk summary
    shdr("Risk Assessment")
    pdf.set_fill_color(*LTEAL)
    pdf.set_draw_color(*TEAL); pdf.set_line_width(0.4)
    pdf.set_font("Helvetica","B",8.5); pdf.set_text_color(*NAVY)
    pdf.cell(0,6,f"  Risk Level: {risk_label}",border="B",fill=True,
             new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_font("Helvetica","",8); pdf.set_text_color(55,65,81)
    pdf.set_fill_color(*LTEAL)
    pdf.multi_cell(0,5,f"  {summary}",border="LB",fill=True,
                   new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(4)

    # Facility information
    shdr("Facility Information")
    for i,(lbl,val) in enumerate([
        ("Name of Facility",                            display_name),
        ("Location",                                    location),
        ("EMR",                                         manual.get("emr","")),
        ("Census Capacity",                             beds),
        ("Current Census",                              manual.get("current_census","")),
        ("Type of Patient",                             manual.get("patient_type","")),
        ("Previous Coverage from Medelite",             manual.get("prev_coverage","")),
        ("Previous Provider Performance from Medelite", manual.get("prev_performance","")),
        ("Medical Coverage",                            manual.get("medical_coverage","")),
    ]):
        irow(lbl, val, shade=i%2==1)
    pdf.ln(4)

    # Star ratings
    shdr("Star Ratings  (CMS Five-Star System)")
    for i,(lbl,key) in enumerate([
        ("Overall Star Rating",      F_OVERALL),
        ("Health Inspection",        F_HEALTH),
        ("Staffing",                 F_STAFFING),
        ("Quality of Resident Care", F_QM),
    ]):
        val = get(facility, key)
        n   = int(float(val)) if safe_float(val) is not None else 0
        srow(lbl, n, shade=i%2==1)
    pdf.ln(4)

    # Hospitalization metrics
    if metrics:
        shdr("Hospitalization & ED Metrics  (CMS Claims-Based)")
        pdf.set_fill_color(*NAVY); pdf.set_text_color(*WHITE); pdf.set_font("Helvetica","B",8)
        for t,w in [("Metric",78),("Facility",28),("National Avg",33),("State Avg",28),("vs Nat",25)]:
            pdf.cell(w,7,f"  {t}",fill=True,border=0)
        pdf.ln()
        for i,m in enumerate(metrics):
            s = i%2==1
            pdf.set_fill_color(*(LGRAY if s else WHITE))
            pdf.set_font("Helvetica","",8); pdf.set_text_color(34,34,34)
            pdf.set_draw_color(221,227,237); pdf.set_line_width(0.2)
            pdf.cell(78,7,f"  {m['label']}",       border="B",fill=True)
            pdf.cell(28,7,f"  {m['facility_val']}", border="B",fill=True)
            pdf.cell(33,7,f"  {m['nat_val']}",      border="B",fill=True)
            pdf.cell(28,7,f"  {m['state_val']}",    border="B",fill=True)
            if m["is_worse"] is True:
                pdf.set_fill_color(*RED);   pdf.set_text_color(*WHITE)
                pdf.cell(25,7,"  ^ Worse",  border="B",fill=True)
            elif m["is_worse"] is False:
                pdf.set_fill_color(*GREEN); pdf.set_text_color(*WHITE)
                pdf.cell(25,7,"  v Better", border="B",fill=True)
            else:
                pdf.set_fill_color(*(LGRAY if s else WHITE)); pdf.set_text_color(*DGRAY)
                pdf.cell(25,7,"  N/A",      border="B",fill=True)
            pdf.set_text_color(34,34,34); pdf.set_fill_color(*(LGRAY if s else WHITE)); pdf.ln()
        pdf.ln(4)

    # Analyst note
    if note.strip():
        shdr("Assessment Notes")
        pdf.set_font("Helvetica","",8); pdf.set_text_color(55,65,81)
        pdf.multi_cell(0,5,f"  {note}",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        pdf.ln(2)

    # Footer
    pdf.set_font("Helvetica","",7.5); pdf.set_text_color(0,169,157)
    pdf.cell(0,6,f"Medicare Source: {med_url}",link=med_url,
             new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_y(-18); pdf.set_font("Helvetica","I",7); pdf.set_text_color(150,150,150)
    pdf.cell(0,5,
             f"Data sourced from CMS Provider Data Catalog  |  "
             f"Generated {datetime.date.today().strftime('%B %d, %Y')}  |  "
             f"CONFIDENTIAL - INTERNAL USE ONLY",
             align="C")
    return bytes(pdf.output())


# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="brand-banner">'
    '<p class="brand-infinite">INFINITE</p>'
    '<p class="brand-sub">MANAGED BY MEDELITE</p>'
    '<p class="brand-title">FACILITY ASSESSMENT SNAPSHOT</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("#### Facility Lookup")
st.caption("Enter a 6-digit CMS Certification Number to pull live facility data.")

c1, c2 = st.columns([3,1])
with c1:
    ccn_input = st.text_input("CCN", placeholder="e.g. 686123", max_chars=6,
                               label_visibility="collapsed")
with c2:
    fetch_btn = st.button("Fetch Data", type="primary", use_container_width=True)

ccn_clean = ccn_input.strip().zfill(6) if ccn_input.strip() else ""
facility  = None
metrics   = []

if fetch_btn:
    if not ccn_input.strip().isdigit():
        st.error("Please enter a numeric CCN - digits only.")
    else:
        with st.spinner("Pulling data from CMS..."):
            facility = fetch_provider(ccn_clean)
        if facility is None:
            st.error("No facility found for that CCN. "
                     "Verify at [medicare.gov/care-compare](https://www.medicare.gov/care-compare).")
        else:
            st.session_state["facility"] = facility
            st.session_state["ccn"]      = ccn_clean
            with st.spinner("Fetching quality measures..."):
                claims    = fetch_claims(ccn_clean)
                state_v   = get(facility, F_STATE)
                state_avg = fetch_state_avg(state_v) if state_v else None
                nat_avg   = fetch_nat_avg()
                metrics   = build_metrics(claims, state_avg, nat_avg)
                st.session_state["metrics"] = metrics

if facility is None and "facility" in st.session_state:
    facility  = st.session_state["facility"]
    ccn_clean = st.session_state.get("ccn", ccn_clean)
    metrics   = st.session_state.get("metrics", [])

if facility:
    name     = get(facility, F_NAME)
    city     = get(facility, F_CITY)
    state_v  = get(facility, F_STATE)
    beds     = get(facility, F_BEDS)
    location = (get(facility, F_LOCATION)
                or ", ".join(filter(None,[
                    get(facility,F_ADDRESS), city,
                    f"{state_v} {get(facility,F_ZIP)}".strip()
                ])))
    med_url  = f"https://www.medicare.gov/care-compare/details/nursing-home/{ccn_clean}"

    stars = {k: safe_float(get(facility, f))
             for k,f in [("overall",F_OVERALL),("health",F_HEALTH),
                          ("staffing",F_STAFFING),("qm",F_QM)]}
    star_labels = {"overall":"Overall","health":"Health Insp.",
                   "staffing":"Staffing","qm":"Quality Care"}

    risk_level, risk_label, risk_summary = compute_risk(facility, metrics)
    risk_cls = f"risk-{risk_level}"

    # Facility header card — single concatenated string (no multiline HTML)
    circles = ""
    for k in ["overall","health","staffing","qm"]:
        n   = int(stars[k]) if stars[k] is not None else 0
        cls = star_css_class(n)
        circles += (f'<div class="star-block">'
                    f'<div class="sc {cls}">{n}</div>'
                    f'<div class="star-label">{star_labels[k]}</div>'
                    f'</div>')

    prev_badge = ""
    card = (
        '<div class="fac-card">'
        '<div class="fac-toprow">'
        f'<div><p class="fac-name">{name}</p><p class="fac-location">{location}</p></div>'
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">'
        f'<span class="risk-badge {risk_cls}">{risk_label}</span>'
        f'<a class="med-link" href="{med_url}" target="_blank">Medicare</a>'
        '</div></div>'
        f'<div class="star-row">{circles}</div>'
        f'<div class="clin-summary">{risk_summary}</div>'
        '</div>'
    )
    st.markdown(card, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Operational Inputs")
    st.caption("Internal fields not available in the public CMS database.")

    c1, c2 = st.columns(2)
    with c1:
        custom_name      = st.text_input("Facility Name Override (optional)", placeholder=name)
        emr              = st.text_input("EMR System", placeholder="e.g. PCC, MatrixCare")
        current_census   = st.text_input("Current Census", placeholder="e.g. 112")
        patient_type     = st.text_input("Type of Patient",
                            placeholder="e.g. Long-term & Short-term")
    with c2:
        prev_coverage    = st.selectbox("Previous Coverage from Medelite", ["Yes","No"])
        prev_performance = st.text_input("Previous Provider Performance",
                            placeholder="e.g. About 30 patients/day")
        medical_coverage = st.text_input("Medical Coverage",
                            placeholder="e.g. Optometry, PCP, Podiatry")
        analyst_note     = st.text_area("Assessment Notes (appears in PDF)",
                            placeholder="Internal observations, flags, or context...",
                            height=80)

    if prev_coverage == "Yes":
        st.success("Previous Medelite coverage on file for this facility.")

    manual = {
        "custom_name": custom_name, "emr": emr, "current_census": current_census,
        "patient_type": patient_type, "prev_coverage": prev_coverage,
        "prev_performance": prev_performance, "medical_coverage": medical_coverage,
    }
    display_name = custom_name or name

    st.divider()
    st.markdown("#### Report Preview")

    # Facility info table
    st.markdown('<div class="section-label">Facility Information</div>', unsafe_allow_html=True)
    irows = ""
    for i,(lbl,val) in enumerate([
        ("Name of Facility",                             display_name or "-"),
        ("Location",                                     location or "-"),
        ("EMR",                                          emr or "-"),
        ("Census Capacity",                              beds or "-"),
        ("Current Census",                               current_census or "-"),
        ("Type of Patient",                              patient_type or "-"),
        ("Previous Coverage from Medelite",              prev_coverage),
        ("Previous Provider Performance from Medelite",  prev_performance or "-"),
        ("Medical Coverage",                             medical_coverage or "-"),
    ]):
        bg = "#F8FAFC" if i%2 else "white"
        irows += (f'<div class="irow" style="background:{bg};">'
                  f'<span class="ilabel">{lbl}</span>'
                  f'<span class="ival">{val}</span></div>')
    st.markdown(irows, unsafe_allow_html=True)

    # Star ratings with dynamic color
    st.markdown('<div class="section-label">Star Ratings</div>', unsafe_allow_html=True)
    srows = ""
    for i,(lbl,key) in enumerate([
        ("Overall Star Rating",      F_OVERALL),
        ("Health Inspection",        F_HEALTH),
        ("Staffing",                 F_STAFFING),
        ("Quality of Resident Care", F_QM),
    ]):
        val = get(facility, key)
        n   = int(float(val)) if safe_float(val) is not None else 0
        bg  = "#F8FAFC" if i%2 else "white"
        col = star_bg(n)
        srows += (
            f'<div class="srow" style="background:{bg};">'
            f'<span class="ilabel">{lbl}</span>'
            f'<span style="display:flex;align-items:center;gap:8px;">'
            f'<span class="sc-small" style="background:{col};">{n}</span>'
            f'<span style="color:#94A3B8;font-size:12px;">/5</span>'
            f'</span></div>'
        )
    st.markdown(srows, unsafe_allow_html=True)

    # Benchmark bars
    if metrics:
        st.markdown('<div class="section-label">Hospitalization & ED Metrics</div>',
                    unsafe_allow_html=True)
        for i, m in enumerate(metrics):
            bg = "#F8FAFC" if i%2 else "white"
            if m["is_worse"] is True:
                badge = '<span class="bworse">Above Nat Avg</span>'
                fill_color = "#DC2626"
            elif m["is_worse"] is False:
                badge = '<span class="bbetter">Below Nat Avg</span>'
                fill_color = "#16A34A"
            else:
                badge = '<span class="bna">No Data</span>'
                fill_color = "#94A3B8"

            bar_html = ""
            if m["bar_pct"] is not None:
                bar_html = (
                    f'<div class="bench-track">'
                    f'<div class="bench-fill" style="width:{m["bar_pct"]}%;background:{fill_color};"></div>'
                    f'<div class="bench-mark" style="left:50%;"></div>'
                    f'</div>'
                    f'<div class="bench-vals">'
                    f'Facility: {m["facility_val"]} &nbsp;|&nbsp; '
                    f'National avg: {m["nat_val"]} &nbsp;|&nbsp; '
                    f'State: {m["state_val"]}'
                    f'</div>'
                )

            st.markdown(
                f'<div class="bench-row" style="background:{bg};">'
                f'<div class="bench-top"><span class="blabel">{m["label"]}</span>{badge}</div>'
                f'{bar_html}'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        st.info("No claims-based quality measures found for this facility.")

    st.markdown(
        f'<div class="med-footer">Medicare Source: '
        f'<a href="{med_url}" target="_blank">{med_url}</a></div>',
        unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Download Report")
    try:
        pdf_bytes = generate_pdf(
            facility, manual, metrics, ccn_clean,
            risk_label, risk_summary, analyst_note
        )
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"MedElite_Assessment_{ccn_clean}_{datetime.date.today()}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
        st.caption("Includes facility info, star ratings, hospitalization benchmarks, "
                   "risk assessment, and assessment notes.")
    except Exception as e:
        st.error(f"PDF error: {e}")

else:
    st.markdown(
        '<div class="empty-state">'
        '<div style="font-size:52px;margin-bottom:14px;">&#127973;</div>'
        '<div style="font-size:16px;font-weight:600;color:#475569;margin-bottom:6px;">'
        'Enter a CCN to begin'
        '</div>'
        '<div style="font-size:13px;margin-bottom:16px;">'
        'Pull live CMS data and generate a facility assessment report in seconds.'
        '</div>'
        '<div style="font-size:12px;background:#F8FAFC;display:inline-block;'
        'padding:8px 16px;border-radius:6px;border:1px solid #E2E8F0;">'
        'Test with CCN <strong style="color:#1B2A4A;">686123</strong>'
        ' &mdash; Kendall Lakes Healthcare and Rehab Center, Miami FL'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )