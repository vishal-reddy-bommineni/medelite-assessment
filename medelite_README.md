# MedElite – Facility Assessment Report Generator

A Streamlit web application that allows MedElite Directors to instantly generate a polished Facility Assessment PDF for any skilled nursing facility using a single CMS Certification Number (CCN).

**[Live Demo →](https://your-app-url.streamlit.app)**

---

## What It Does

Enter a 6-digit CCN and the app pulls live data from the CMS Provider Data Catalog API, runs a risk assessment, and generates a branded PDF report — in seconds, with no manual data entry beyond internal operational fields.

> **Test it with CCN `686123`** — Kendall Lakes Healthcare and Rehab Center, Miami FL (the reference facility from the case study).

---

## Features

**Core**
- Live CMS API integration — facility name, location, star ratings, bed count, all pulled in real time
- Manual operational inputs — EMR, census, patient type, Medelite coverage history, medical coverage
- One-click PDF download with INFINITE / MEDELITE branding

**Beyond the MVP**
- Risk scoring engine — computes LOW / MEDIUM / HIGH risk from star ratings and hospitalization benchmarks, displayed as a color-coded badge
- Auto-generated clinical summary — a one-sentence analyst-style assessment derived from live CMS data
- Dynamic star color circles — red (1★), orange (2★), amber (3★), green (4–5★)
- All 4 claims-based hospitalization & ED metrics with national and state benchmark comparisons
- Visual benchmark bars showing facility position relative to national average
- Assessment notes field that flows into the PDF
- Previous Medelite coverage badge
- Comprehensive error handling — invalid CCNs, missing API fields, network timeouts, PDF encoding edge cases

---

## Tech Stack

| | |
|---|---|
| App | Streamlit |
| PDF | fpdf2 |
| Data | CMS Provider Data Catalog REST API (public, no key required) |
| Hosting | Streamlit Community Cloud |

---

## Project Structure

```
medelite-assessment/
├── app.py              # Complete application — all logic in one file
├── requirements.txt
└── README.md
```

---

## Engineering Notes

**CMS API operator quirk** — the query API requires `==` sent as a literal string. Python's `requests` params dict URL-encodes it as `%3D%3D`, causing a 400 error. URLs are built manually as f-strings to keep `==` literal.

**Column names verified from live API (June 2026)** — the CCN field is `cms_certification_number_ccn`, the state averages join key is `state_or_nation`, and the hospitalization columns use CMS-truncated names with hash suffixes. The State Averages dataset ID also changed from `s2uc-8wxp` to `xcdc-v8bm` between releases.

**Claims measure codes used:**
- `521` — Short-Stay rehospitalization rate
- `526` — Short-Stay ED visit rate
- `551` — Long-Stay hospitalization per 1,000 resident days
- `552` — Long-Stay ED visits per 1,000 resident days

**STR metric values** are stored as whole percentage values in the API (e.g. `25.6` = 25.6%) — no multiplication applied. LT metrics are rates per 1,000 resident days displayed as decimals.

**PDF encoding** — fpdf2's Helvetica only supports ASCII. All strings are sanitized through `ascii_only()` before rendering to handle em dashes, smart quotes, and other non-ASCII characters.

**Risk scoring** — weighted point system: overall/health rating ≤2 (+2 pts each), rating of 3 (+1 pt), staffing ≤2 (+1 pt), each hospitalization metric above national average (+1 pt). Score ≥5 = HIGH, ≥2 = MEDIUM, else LOW.

**Caching** — CMS API responses cached for 1 hour via `@st.cache_data` to avoid redundant calls while filling in operational fields.