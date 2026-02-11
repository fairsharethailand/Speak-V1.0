import streamlit as st
from gtts import gTTS
import base64, os, uuid, random

# 1. Config
st.set_page_config(page_title="TPRS Magic Wheel V58.3 Fix", layout="wide")

if 'display_text' not in st.session_state: st.session_state.display_text = ""
if 'audio_key' not in st.session_state: st.session_state.audio_key = 0

# --- Grammar Helpers ---
PAST_TO_INF = {"went": "go", "ate": "eat", "saw": "see", "bought": "buy", "had": "have", "did": "do", "drank": "drink", "slept": "sleep", "wrote": "write", "came": "come", "ran": "run", "met": "meet", "spoke": "speak", "took": "take", "found": "find", "gave": "give", "thought": "think", "brought": "bring", "told": "tell", "made": "make", "cut": "cut", "put": "put", "hit": "hit", "read": "read", "cost": "cost"}
IRREGULAR_PLURALS = ["children", "people", "men", "women", "mice", "teeth", "feet", "geese", "oxen"]

def is_present_perfect(pred):
    w = pred.lower().split()
    return len(w) >= 2 and w[0] in ['have', 'has', 'had'] and (w[1].endswith('ed') or w[1] in PAST_TO_INF or w[1] in ['been', 'done', 'gone', 'seen', 'eaten'])

def check_tense(pred):
    w = pred.split()
    if not w: return "unknown"
    v = w[0].lower().strip()
    if v.endswith("ed") or v in PAST_TO_INF: return "past"
    if v.endswith("s") or v.endswith("es") or v in ["go", "eat", "see", "buy", "do", "drink", "sleep", "write", "come", "run", "meet", "speak", "take", "find", "give", "think", "bring", "tell", "make"]: return "present"
    return "unknown"

def conjugate_singular(pred):
    w = pred.split(); v = w[0].lower(); rest = " ".join(w[1:])
    if v.endswith('s') or check_tense(v) == "past": return pred
    if v.endswith(('ch', 'sh', 'x', 's', 'z', 'o')): v += "es"
    elif v.endswith('y') and len(v) > 1 and v[-2] not in 'aeiou': v = v[:-1] + "ies"
    else: v += "s"
    return f"{v} {rest}".strip()

def get_aux(subj, p1, p2):
    if is_present_perfect(p1): return None
    if check_tense(p1) == "past" or check_tense(p2) == "past": return "Did"
    s = subj.lower().strip()
    if s in IRREGULAR_PLURALS or 'and' in s or s in ['i', 'you', 'we', 'they'] or (s.endswith('s') and s not in ['james', 'charles', 'boss']): return "Do"
    return "Does"

def to_inf(pred, other):
    w = pred.split(); v = w[0].lower(); rest = " ".join(w[1:])
    is_past = (check_tense(pred) == "past" or check_tense(other) == "past")
    if is_past or v in ['had', 'has', 'have']:
        if v in ['had', 'has', 'have']: inf = "have"
        elif v in PAST_TO_INF: inf = PAST_TO_INF[v]
        elif v.endswith("ied"): inf = v[:-3] + "y"
        elif v.endswith("ed"): inf = v[:-2]
        else: inf = v
    else:
        if v.endswith("es"):
            for sfx in ['sses', 'ches', 'shes', 'xes']:
                if v.endswith(sfx): inf = v[:-2]; break
            else: inf = v[:-2]
        elif v.endswith("s") and not v.endswith("ss"): inf = v[:-1]
        else: inf = v
    return f"{inf} {rest}".strip()

def has_be(pred):
    v = pred.lower().split()
    return v and v[0] in ['is', 'am', 'are', 'was', 'were', 'can', 'will', 'must', 'should', 'could', 'would']

def build_logic(q_type, d):
    s1, p1, s2, p2 = d['s1'], d['p1'], d['s2'], d['p2']
    subj_r, pred_r = (s1 or "He"), (p1 or "is here")
    subj_t = s2 if s2 != "-" else s1
    pred_t = p2 if p2 != "-" else p1

    def swap(s, p):
        pts = p.split()
        return f"{pts[0].capitalize()} {s} {' '.join(pts[1:])}".strip()

    if q_type == "Statement": return d['main_sent']
    if q_type == "Negative":
        if has_be(pred_t) or is_present_perfect(pred_t):
            pts = pred_t.split()
            return f"No, {subj_t} {pts[0]} not {' '.join(pts[1:])}."
        aux = get_aux(subj_t, pred_t, pred_r)
        return f"No, {subj_t} {aux.lower()} not {to_inf(pred_t, pred_r)}."
    
    if q_type == "Yes-Q":
        if has_be(pred_r) or is_present_perfect(pred_r): return swap(subj_r, pred_r) + "?"
        return f"{get_aux(subj_r, pred_r, pred_t)} {subj_r} {to_inf(pred_r, pred_t)}?"

    if q_type == "No-Q":
        if has_be(pred_t) or is_present_perfect(pred_t): return swap(subj_t, pred_t) + "?"
        return f"{get
