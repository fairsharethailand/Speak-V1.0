import streamlit as st
from gtts import gTTS
import base64
import os
import uuid
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="TPRS Magic Wheel V58.4 (Grammar Fix)", layout="wide")

# 2. Session State
if 'display_text' not in st.session_state:
    st.session_state.display_text = ""
if 'audio_key' not in st.session_state:
    st.session_state.audio_key = 0

# --- Grammar Logic ---
PAST_TO_INF = {
    "went": "go", "ate": "eat", "saw": "see", "bought": "buy", 
    "had": "have", "did": "do", "drank": "drink", "slept": "sleep", 
    "wrote": "write", "came": "come", "ran": "run", "met": "meet",
    "spoke": "speak", "took": "take", "found": "find", "gave": "give",
    "thought": "think", "brought": "bring", "told": "tell", "made": "make",
    "cut": "cut", "put": "put", "hit": "hit", "read": "read", "cost": "cost"
}

# รายการคำนามพหูพจน์ไม่ปกติ (Irregular Plural Nouns)
IRREGULAR_PLURALS = ["children", "people", "men", "women", "mice", "teeth", "feet", "geese", "oxen"]

def is_present_perfect(predicate):
    words = predicate.lower().split()
    if len(words) >= 2 and words[0] in ['have', 'has', 'had']:
        v2 = words[1]
        if v2.endswith('ed') or v2 in PAST_TO_INF or v2 in ['been', 'done', 'gone', 'seen', 'eaten']:
            return True
    return False

def check_tense_type(predicate):
    words = predicate.split()
    if not words: return "unknown"
    v = words[0].lower().strip()
    if v.endswith("ed") or v in ["went", "ate", "saw", "bought", "did", "drank", "slept", "wrote", "came", "ran", "met", "spoke", "took", "found", "gave", "thought", "brought", "told", "made"]:
        return "past"
    if v.endswith("s") or v.endswith("es") or v in ["go", "eat", "see", "buy", "do", "drink", "sleep", "write", "come", "run", "meet", "speak", "take", "find", "give", "think", "bring", "tell", "make"]:
        return "present"
    return "unknown"

def conjugate_singular(predicate):
    """ฟังก์ชันเติม s/es ให้กริยาหลักสำหรับคำถาม Who"""
    words = predicate.split()
    if not words: return ""
    v = words[0].lower(); rest = " ".join(words[1:])
    if v.endswith(('ch', 'sh', 'x', 's', 'z', 'o')): v += "es"
    elif v.endswith('y') and len(v) > 1 and v[-2] not in 'aeiou': v = v[:-1] + "ies"
    else: v += "s"
    return f"{v} {rest}".strip()

def get_auxiliary(subject, pred_target, pred_other):
    if is_present_perfect(pred_target):
        return None 
    tense_target = check_tense_type(pred_target)
    tense_other = check_tense_type(pred_other)
    if tense_target == "past" or tense_other == "past":
