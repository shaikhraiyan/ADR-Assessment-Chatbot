import streamlit as st

st.set_page_config(page_title="ADR Assessment Chatbot", page_icon="💊", layout="wide")

# Visual theme only: all questions, scoring rules and assessment content remain unchanged.
st.markdown("""
<style>
:root {
  --ink: #203247;
  --muted: #64748b;
  --teal: #167c80;
  --teal-dark: #12666a;
  --cream: #f7f8f5;
  --line: #dce6e5;
}
.stApp {
  background: linear-gradient(145deg, #f4f8f7 0%, #f8f7f2 55%, #eef5f5 100%);
  color: var(--ink);
}
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #203b50 !important; letter-spacing: -0.025em; }
h1 { font-weight: 800 !important; padding-bottom: .35rem; }
h2 { font-weight: 750 !important; margin-top: 1.1rem !important; }
h3 { font-weight: 700 !important; }
[data-testid="stCaptionContainer"] { color: var(--muted); }
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stExpander"] {
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  background: rgba(255,255,255,.76) !important;
}
[data-testid="stAlert"] { border-radius: 12px; border-width: 1px; }
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: #ffffff !important;
  border: 1px solid #d5e1e1 !important;
  border-radius: 10px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--teal) !important;
  box-shadow: 0 0 0 2px rgba(22,124,128,.12) !important;
}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  background: linear-gradient(105deg, #167c80, #236b82) !important;
  color: white !important;
  border: 0 !important;
  border-radius: 10px !important;
  padding: .58rem 1.15rem !important;
  font-weight: 650 !important;
  box-shadow: 0 4px 12px rgba(24,91,105,.16);
  transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(105deg, #12666a, #1d5c70) !important;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(24,91,105,.22);
}
input[type="radio"] { accent-color: var(--teal); }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
hr { border-color: #d8e4e2 !important; margin: 1.6rem 0 !important; }
[data-testid="stMarkdownContainer"] a { color: #14777b; font-weight: 600; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
st.title("💊 ADR Assessment Chatbot")
st.caption("Scale-based pharmacovigilance decision-support prototype")

st.warning("Educational/documentation aid only; not a diagnostic tool or substitute for clinician review. Do not enter patient identifiers.")

def naranjo_score(a):
    weights = {
        "q1": {"Yes": 1, "No": 0, "Unknown": 0},
        "q2": {"Yes": 2, "No": -1, "Unknown": 0},
        "q3": {"Yes": 1, "No": 0, "Unknown": 0},
        "q4": {"Yes": 2, "No": -1, "Unknown": 0},
        "q5": {"Yes": -1, "No": 2, "Unknown": 0},
        "q6": {"Yes": -1, "No": 1, "Unknown": 0},
        "q7": {"Yes": 1, "No": 0, "Unknown": 0},
        "q8": {"Yes": 1, "No": 0, "Unknown": 0},
        "q9": {"Yes": 1, "No": 0, "Unknown": 0},
        "q10": {"Yes": 1, "No": 0, "Unknown": 0},
    }
    points = {q: weights[q][a[q]] for q in weights}
    total = sum(points.values())
    label = "Definite" if total >= 9 else "Probable" if total >= 5 else "Possible" if total >= 1 else "Doubtful"
    return total, label, points

def who_umc(time_ok, alternatives, withdrawal, adequate, definitive):
    if not adequate:
        return "Unassessable / Unclassifiable", "Insufficient or contradictory information."
    if not time_ok:
        return "Unlikely", "The time relationship makes causality improbable."
    if alternatives == "Unlikely" and withdrawal == "Clinically reasonable":
        return "Probable / Likely", "Reasonable time relationship; alternative causes are unlikely; response to withdrawal is clinically reasonable. Rechallenge is not required."
    if alternatives in ["Possible", "Likely"] or withdrawal in ["Unknown / unclear", "Not assessable"]:
        return "Possible", "The event could also be explained by disease/other drugs and/or withdrawal information is unclear."
    if alternatives == "Unlikely" and withdrawal == "No response / not supportive":
        return "Possible", "Temporal relationship exists, but withdrawal response does not support Probable/Likely."
    return "Conditional / Unclassified", "Additional information is required."

st.header("1. Case information")
c1, c2 = st.columns(2)
with c1:
    case_code = st.text_input("Non-identifying case code", placeholder="ADR-001")
    age = st.number_input("Age (years)", 0, 120, 30)
    sex = st.selectbox("Sex", ["Not recorded", "Female", "Male", "Other / prefer not to say"])
    drug = st.text_input("Suspected medicine (generic name)")
with c2:
    route = st.selectbox("Route", ["Oral", "Intravenous", "Intra-arterial", "Intramuscular", "Subcutaneous", "Other / unknown"])
    indication = st.text_input("Indication")
    onset = st.text_input("Time from administration to reaction", placeholder="e.g. 30 seconds")
    outcome = st.selectbox("Outcome", ["Recovered", "Recovering", "Not recovered", "Recovered with sequelae", "Fatal", "Unknown"])

reaction = st.text_area("Describe symptoms, signs, vital signs and investigations")
treatment = st.text_area("Treatment given and response")
other_meds = st.text_area("Other medicines / exposures around the event")
alternative_notes = st.text_area("Potential alternative causes (disease, procedure, other medicines)")

st.divider()
st.header("2. Causality")

st.subheader("A. WHO–UMC causality assessment")
st.caption("WHO–UMC categories are criteria-based: Certain, Probable/Likely, Possible, Unlikely, Conditional/Unclassified, Unassessable/Unclassifiable.")
w1, w2 = st.columns(2)
with w1:
    time_ok = st.radio("Is the time relationship reasonable?", ["Yes", "No"], horizontal=True)
    alternatives = st.radio("Could the disease or other medicines explain the reaction?", ["Unlikely", "Possible", "Likely", "Not assessed"])
with w2:
    withdrawal = st.radio("Was the response after withdrawal clinically reasonable?", ["Clinically reasonable", "Unknown / unclear", "No response / not supportive", "Not assessable"])
    adequate = st.checkbox("Enough reliable information is available", value=True)
    definitive = st.checkbox("The event is a definitive, clinically recognised event / objective abnormality")
who_label, who_reason = who_umc(time_ok == "Yes", alternatives, withdrawal, adequate, definitive)
st.info(f"**WHO–UMC result: {who_label}**\n\n{who_reason}")
rechallenge = st.selectbox("Rechallenge status", ["Not done", "Positive", "Negative", "Unknown"], help="Rechallenge is not required for WHO–UMC Probable/Likely. Never rechallenge solely to obtain a score.")

st.subheader("B. Naranjo ADR Probability Scale")
st.caption("Naranjo et al., 1981. Use Unknown if the record does not establish Yes or No.")
qs = [
("q1", "Are there previous conclusive reports of this reaction?"),
("q2", "Did the event appear after the suspected drug was administered?"),
("q3", "Did the reaction improve when the drug was discontinued or a specific antagonist was administered?"),
("q4", "Did the reaction reappear when the drug was re-administered?"),
("q5", "Are there alternative causes (other than the drug) that could on their own have caused the reaction?"),
("q6", "Did the reaction reappear when a placebo was given?"),
("q7", "Was the drug detected in blood or other fluids at concentrations known to be toxic?"),
("q8", "Was the reaction more severe when the dose increased, or less severe when the dose decreased?"),
("q9", "Did the patient have a similar reaction to the same or similar drugs in a previous exposure?"),
("q10", "Was the adverse event confirmed by objective evidence?"),
]
with st.form("naranjo"):
    answers = {}
    for key, question in qs:
        answers[key] = st.radio(question, ["Unknown", "Yes", "No"], horizontal=True, key=key)
    calc = st.form_submit_button("Calculate Naranjo score", type="primary")
if calc:
    total, label, points = naranjo_score(answers)
    st.session_state["naranjo"] = (total, label, answers.copy(), points)
if "naranjo" in st.session_state:
    total, label, saved, points = st.session_state["naranjo"]
    st.success(f"Naranjo score: {total} — {label}")
    st.dataframe([{"No.": i, "Question": q, "Answer": saved[k], "Points": points[k]} for i, (k, q) in enumerate(qs, 1)], use_container_width=True, hide_index=True)

st.divider()
st.header("3. Other ADR assessment domains")
st.caption("Severity, seriousness and causality are different concepts.")
hartwig = st.selectbox("Hartwig–Siegel severity level (select only if supported by records)", [
"Not assessed",
"Level 1 — No change in treatment; no treatment required",
"Level 2 — Required treatment / change in treatment, without increased length of stay",
"Level 3 — Required treatment and/or increased length of stay by at least one day",
"Level 4 — Required intensive medical care",
"Level 5 — Permanent harm",
"Level 6 — Contributed to death",
"Level 7 — Directly caused death"
])
serious_criteria = st.multiselect("ICH E2A seriousness criteria", [
"Death", "Life-threatening at the time", "Required inpatient hospitalisation or prolonged hospitalisation",
"Persistent/significant disability or incapacity", "Congenital anomaly/birth defect",
"Other medically important event requiring intervention to prevent a serious outcome"
])
serious = "Serious" if serious_criteria else "No seriousness criterion selected — verify record"
contrast = st.checkbox("Is this a radiologic contrast-agent reaction?")
acr = "Not applicable"
if contrast:
    acr = st.selectbox("ACR acute contrast reaction category (review the ACR Manual)", [
        "Not classified / insufficient detail", "Mild allergic-like", "Moderate allergic-like",
        "Severe allergic-like", "Mild physiologic", "Moderate physiologic", "Severe physiologic"
    ])
    st.caption("Do not infer anaphylaxis from isolated pruritus. Select only after reviewing the documented manifestations.")
limitations = st.text_area("Missing information / assessor notes")

st.divider()
if st.button("Generate final assessment summary"):
    n = st.session_state.get("naranjo")
    summary = {
        "Case code": case_code or "Not entered",
        "Suspected drug": drug or "Not entered",
        "Reaction": reaction or "Not entered",
        "WHO–UMC": who_label,
        "WHO–UMC rationale": who_reason,
        "Rechallenge": rechallenge,
        "Naranjo": f"{n[0]} — {n[1]}" if n else "Not calculated",
        "Hartwig–Siegel": hartwig,
        "ICH seriousness": serious,
        "ACR classification": acr,
        "Outcome": outcome,
        "Limitations": limitations or "Not entered"
    }
    st.session_state["summary"] = summary
if "summary" in st.session_state:
    st.subheader("Assessment summary")
    for k, v in st.session_state["summary"].items():
        st.markdown(f"**{k}:** {v}")
    st.download_button("Download summary (.txt)", "\n".join(f"{k}: {v}" for k, v in st.session_state["summary"].items()),
                       file_name=f"{case_code or 'ADR'}_assessment.txt", mime="text/plain")

st.divider()
st.header("Scale references")
st.markdown("""
- **Naranjo:** Naranjo CA, et al. A method for estimating the probability of adverse drug reactions. *Clin Pharmacol Ther.* 1981;30(2):239–245. [doi:10.1038/clpt.1981.154](https://doi.org/10.1038/clpt.1981.154)
- **WHO–UMC:** [WHO–UMC causality assessment criteria](https://who-umc.org/media/164200/who-umc-causality-assessment_new-logo.pdf); India: [PvPI toolkit](https://www.ipc.gov.in/PvPI/toolkit.html).
- **Hartwig–Siegel:** Hartwig SC, Siegel J, Schneider PJ. *Am J Hosp Pharm.* 1992;49(9):2229–2232.
- **ICH seriousness:** ICH E2A, *Clinical Safety Data Management: Definitions and Standards for Expedited Reporting*.
- **ACR contrast reactions:** [ACR Manual on Contrast Media](https://www.acr.org/Clinical-Resources/Clinical-Tools-and-Reference/Contrast-Manual).
""")
st.caption("WHO–UMC and Naranjo are independent methods and may yield different categories. Do not force a desired score; preserve Unknown answers and obtain qualified review.")
