def build_logic(q_type, data):
    s1, p1, s2, p2 = data['s1'], data['p1'], data['s2'], data['p2']
    main_sent = data['main_sent']
    subj_real, pred_real = (s1 if s1 else "He"), (p1 if p1 else "is here")
    subj_trick = s2 if s2 != "-" else s1
    pred_trick = p2 if p2 != "-" else p1

    def swap_front(s, p):
        parts = p.split()
        return f"{parts[0].capitalize()} {s} {' '.join(parts[1:])}".strip().replace("  ", " ")

    if q_type == "Statement": return main_sent
    if q_type == "Negative":
        if has_be_verb(pred_trick) or is_present_perfect(pred_trick):
            parts = pred_trick.split()
            return f"No, {subj_trick} {parts[0]} not {' '.join(parts[1:])}."
        aux = get_auxiliary(subj_trick, pred_trick, pred_real)
        return f"No, {subj_trick} {aux.lower()} not {to_infinitive(pred_trick, pred_real)}."
    if q_type == "Yes-Q":
        if has_be_verb(pred_real) or is_present_perfect(pred_real): return swap_front(subj_real, pred_real) + "?"
        aux = get_auxiliary(subj_real, pred_real, pred_trick)
        return f"{aux} {subj_real} {to_infinitive(pred_real, pred_trick)}?"
    if q_type == "No-Q":
        if has_be_verb(pred_trick) or is_present_perfect(pred_trick): return swap_front(subj_trick, pred_trick) + "?"
        aux = get_auxiliary(subj_trick, pred_trick, pred_real)
        return f"{aux} {subj_trick} {to_infinitive(pred_trick, pred_real)}?"
    if q_type == "Either/Or":
        if s2 != "-" and s1.lower().strip() != s2.lower().strip():
            if has_be_verb(pred_real) or is_present_perfect(pred_real):
                v_f = pred_real.split()[0].capitalize(); v_r = " ".join(pred_real.split()[1:])
                return f"{v_f} {subj_real} or {subj_trick} {v_r}?"
            aux = get_auxiliary(subj_real, pred_real, pred_trick)
            return f"{aux} {subj_real} or {subj_trick} {to_infinitive(pred_real, pred_trick)}?"
        else:
            p_alt = p2 if p2 != "-" else "something else"
            if has_be_verb(pred_real) or is_present_perfect(pred_real): return f"{swap_front(subj_real, pred_real)} or {p_alt}?"
            aux = get_auxiliary(subj_real, pred_real, p_alt)
            return f"{aux} {subj_real} {to_infinitive(pred_real, p_alt)} or {to_infinitive(p_alt, pred_real)}?"
    
    # --- แก้ไขเฉพาะส่วนนี้ (Who Logic) ---
    if q_type == "Who":
        words = pred_real.split()
        if not words: return "Who?"
        v_orig = words[0].lower()
        rest = " ".join(words[1:])
        
        # 1. จัดการ Be Verbs
        if v_orig in ['am', 'are']: 
            return f"Who is {rest}?".strip()
        if v_orig == 'were': 
            return f"Who was {rest}?".strip()
        
        # 2. ถ้าเป็น Action Verb ปกติ (ไม่ใช่ Modal และไม่ใช่อดีต) ให้ทำให้เป็นเอกพจน์
        be_modals = ['is', 'was', 'has', 'can', 'will', 'must', 'should', 'could', 'would']
        if v_orig not in be_modals and check_tense_type(pred_real) != "past":
            # เรียกใช้ฟังก์ชันแปลงกริยาเป็นรูปเติม s/es (conjugate_singular)
            v_singular = conjugate_singular(pred_real)
            return f"Who {v_singular}?"
        
        # 3. กรณีอื่นๆ (Past Tense หรือ Modal) ใช้รูปเดิม
        return f"Who {pred_real}?"

    # --- ส่วนของ What, Where, etc. คงไว้ตามเดิม ---
    if q_type in ["What", "Where", "When", "How", "Why"]:
        if has_be_verb(pred_real) or is_present_perfect(pred_real):
            parts = pred_real.split(); return f"{q_type} {parts[0]} {subj_real} {' '.join(parts[1:])}?"
        aux = get_auxiliary(subj_real, pred_real, pred_trick)
        return f"{q_type} {aux.lower()} {subj_real} {to_infinitive(pred_real, pred_trick)}?"
    
    return main_sent
