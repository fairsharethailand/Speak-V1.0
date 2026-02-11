import streamlit as st
from gtts import gTTS
import base64, os, uuid, random

st.set_page_config(page_title="TPRS Magic Wheel V58.7", layout="wide")
if 'display_text' not in st.session_state: st.session_state.display_text = ""
if 'audio_key' not in st.session_state: st.session_state.audio_key = 0

# --- Database & Grammar Logic ---
PAST_TO_INF = {"went":"go","ate":"eat","saw":"see","bought":"buy","had":"have","did":"do","drank":"drink","slept":"sleep","wrote":"write","came":"come","ran":"run","met":"meet","spoke":"speak","took":"take","found":"find","gave":"give","thought":"think","brought":"bring","told":"tell","made":"make","cut":"cut","put":"put","hit":"hit","read":"read","cost":"cost"}
IRR_PL = ["children", "people", "men", "women", "mice", "teeth", "feet", "geese", "oxen"]

def get_tense(p):
    v = p.split()[0].lower() if p.split() else ""
    return "past" if (v.endswith("ed") or v in PAST_TO_INF) else "pres"

def conj_sing(p):
    w = p.split(); v = w[0].lower(); r = " ".join(w[1:])
    if v.endswith('s') or get_tense(v)=="past" or v in ['is','was','has','can','will']: return p
    if v.endswith(('ch','sh','x','s','z','o')): v += "es"
    elif v.endswith('y') and len(v)>1 and v[-2] not in 'aeiou': v = v[:-1] + "ies"
    else: v += "s"
    return f"{v} {r}".strip()

def get_aux(s, p1, p2):
    if get_tense(p1)=="past" or get_tense(p2)=="past": return "Did"
    s_l = s.lower().strip()
    if s_l in IRR_PL or 'and' in s_l or s_l in ['i','you','we','they'] or (s_l.endswith('s') and s_l not in ['james','charles','boss']): return "Do"
    return "Does"

def to_inf(p, o):
    w = p.split(); v = w[0].lower(); r = " ".join(w[1:])
    if get_tense(p)=="past" or get_tense(o)=="past" or v in ['had','has','have']:
        inf = "have" if v in ['had','has','have'] else (PAST_TO_INF.get(v, v[:-2] if v.endswith("ed") else v))
    else:
        inf = v[:-2] if v.endswith("es") else (v[:-1] if (v.endswith("s") and not v.endswith("ss")) else v)
    return f"{inf} {r}".strip()

def build_logic(q, d):
    s1, p1, s2, p2 = d['s1'], d['p1'], d['s2'], d['p2']
    sr, pr = (s1 or "He"), (p1 or "is here")
    st_subj = s2 if s2 != "-" else s1
    pt = p2 if p2 != "-" else p1
    be = ['is','am','are','was','were','can','will','must','should']
    def is_be(p): return p.lower().split() and p.lower().split()[0] in be
    def swap(s, p): return f"{p.split()[0].capitalize()} {s} {' '.join(p.split()[1:])}".strip()

    if q == "Statement": return d['m']
    if q == "Negative":
        if is_be(pt): return f"No, {st_subj} {pt.split()[0]} not {' '.join(pt.split()[1:])}."
        return f"No, {st_subj} {get_aux(st_subj,pt,pr).lower()} not {to_inf(pt,pr)}."
    if q == "Yes-Q":
        return (swap(sr,pr)+"?") if is_be(pr) else f"{get_aux(sr,pr,pt)} {sr} {to_inf(pr,pt)}?"
    if q == "No-Q":
        return (swap(st_subj,pt)+"?") if is_be(pt) else f"{get_aux(st_subj,pt,pr)} {st_subj} {to_inf(pt,pr)}?"
    if q == "Either/Or":
        if s2 != "-" and s1.lower() != s2.lower():
            return (swap(sr,pr).replace('?','') + f" or {st_subj}?") if is_be(pr) else f"{get_aux(sr,pr,pt)} {sr} or {st_subj} {to_inf(pr,pt)}?"
        alt = p2 if p2 != "-" else "something else"
        return (swap(sr,pr) + f" or {alt}?") if is_be(pr) else f"{get_aux(sr,pr,alt)} {sr} {to_inf(pr,alt)} or {to_inf(alt,pr)}?"
    if q == "Who":
        v = pr.lower().split()[0]
        if v in ['am','are']: return f"Who is {' '.join(pr.split()[1:])}?"
        if v == 'were': return f"Who was {' '.join(pr.split()[1:])}?"
        return f"Who {conj_sing(pr)}?" if not is_be(pr) else f"Who {pr}?"
    if q in ["What","Where","When","How","Why"]:
        return f"{q} {pr.split()[0]} {sr} {' '.join(pr.split()[1:])}?" if is_be(pr) else f"{q} {get_aux(sr,pr,pt).lower()} {sr} {to_inf(pr,pt)}?"
    return d['m']

def play_voice(text):
    if not text: return
    try:
        t = text.split(":")[-1].strip().replace("🎯","")
        tts = gTTS(text=t, lang='en')
        fn = f"v_{uuid.uuid4()}.mp3"
        tts.save(fn)
        with open(fn, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        st.session_state.audio_key += 1
        st.markdown(f'<audio autoplay key="{st.session_state.audio_key}"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        os.remove(fn)
    except: pass

# --- UI ---
st.title("🎡 TPRS Magic Wheel V58.7")
m = st.text_input("📝 Main Sentence", "The children eat the cake.")
c1, c2 = st.columns(2)
with c1: sr, pr = st.text_input("Subject (R):", "The children"), st.text_input("Predicate (R):", "eat the cake")
with c2: st_subj, pt = st.text_input("Subject (T):", "-"), st.text_input("Predicate (T):", "eat the bread")
data = {'s1':sr, 'p1':pr, 's2':st_subj, 'p2':pt, 'm':m}

clicked = None
if st.button("🎰 RANDOM TRICK", use_container_width=True, type="primary"):
    clicked = random.choice(["Statement","Yes-Q","No-Q","Negative","Either/Or","Who","What","Where","When","How","Why"])
r1 = st.columns(5)
for i, (l, mode) in enumerate([("📢 Statement","Statement"),("✅ Yes-Q","Yes-Q"),("❌ No-Q","No-Q"),("🚫 Negative","Negative"),("⚖️ Either/Or","Either/Or")]):
    if r1[i].button(l, use_container_width=True): clicked = mode
r2 = st.columns(6)
for i, wh in enumerate(["Who","What","Where","When","How","Why"]):
    if r2[i].button(f"❓ {wh}", use_container_width=True): clicked = wh

if clicked:
    res = build_logic(clicked, data)
    st.session_state.display_text = f"🎯 {clicked}: {res}"
    play_voice(res)
if st.session_state.display_text: st.info(st.session_state.display_text)
