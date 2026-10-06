import streamlit as st
import pandas as pd
import datetime
import random
import requests
import json
from dateutil.relativedelta import relativedelta

# הגדרות עמוד
st.set_page_config(
    page_title="מרפאת שיניים ברור חיל - ניהול",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- מנגנון אימות בסיסמה -----------------
APP_PASSWORD = "2267"  # כאן מגדירים את הסיסמה לכניסה למערכת

def check_password():
    """הצגת מסך התחברות נקי אם המשתמש טרם התחבר"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # עיצוב מותאם למסך הכניסה
    st.markdown("""
    <style>
        .login-box {
            max-width: 450px;
            margin: 60px auto;
            padding: 30px;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-top: 6px solid #006b3f;
            direction: rtl;
            text-align: center;
        }
        .login-title {
            color: #006b3f;
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .login-subtitle {
            color: #555555;
            font-size: 15px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="login-box">
            <div class="login-title">🦷 מרפאת שיניים ברור חיל 🇧🇷</div>
            <div class="login-subtitle">מערכת ניהול פנימית — נא להזין סיסמה לכניסה</div>
        </div>
        """, unsafe_allow_html=True)

        pwd = st.text_input("סיסמה:", type="password", key="login_pwd")
        
        if st.button("כניסה למערכת", use_container_width=True, type="primary"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("סיסמה שגויה. אנא נסה שוב.")

    return False

# בדיקת אימות — אם טרם הוקלדה סיסמה, עוצרים כאן ולא מציגים שום מידע!
if not check_password():
    st.stop()

# ----------------- עיצוב ברזילאי מודגש + נעילת סרגל צד ללא חיצים -----------------
st.markdown("""
<style>
    /* יישור עברית כללי */
    .element-container, .stMarkdown, p, h1, h2, h3, h4, label, span, div {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* שדות תאריך משמאל לימין כמקובל DD/MM/YYYY */
    div[data-testid="stDateInput"] input {
        direction: ltr !important;
        text-align: center !important;
    }

    /* העלמת כפתורי החיצים של סרגל הצד */
    [data-testid="collapsedControl"],
    button[kind="header"],
    [data-testid="stSidebarCollapseButton"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* רקע ראשי */
    .stApp {
        background: linear-gradient(180deg, #f3f9f4 0%, #fefcf3 100%);
    }

    /* כותרת עליונה מודגשת */
    h1 {
        color: #006b3f !important;
        font-weight: 800 !important;
        border-bottom: 4px solid #ffcc00;
        padding-bottom: 12px;
        margin-bottom: 20px !important;
    }

    h2, h3 {
        color: #005230 !important;
        font-weight: 700 !important;
    }

    /* סרגל צד מעוצב */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #005a28 0%, #003818 100%) !important;
        border-left: 5px solid #ffcc00 !important;
        min-width: 280px !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 8px 10px;
    }

    /* כפתורי פעולה */
    .stButton>button {
        background: linear-gradient(90deg, #008744 0%, #00994c 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 2px solid #ffcc00 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 10px rgba(0, 135, 68, 0.25) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #00994c 0%, #ffcc00 100%) !important;
        color: #003818 !important;
    }

    /* קוביות מדדים בדשבורד */
    .metric-box {
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        background-color: #ffffff;
    }
    .box-green {
        border: 2px solid #28a745;
        border-top: 6px solid #28a745;
    }
    .box-green h2, .box-green span {
        color: #1e7e34 !important;
    }
    .box-red {
        border: 2px solid #dc3545;
        border-top: 6px solid #dc3545;
    }
    .box-red h2, .box-red span {
        color: #bd2130 !important;
    }

    /* טבלה חודשית מעוצבת */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        direction: rtl;
        font-size: 15px;
        background-color: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .styled-table th {
        background-color: #005a28;
        color: #ffffff;
        text-align: right;
        padding: 12px;
    }
    .styled-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #eef2ee;
        text-align: right;
    }
    .styled-table tr:hover {
        background-color: #f7fbf8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- קבועים וחיבור ל-Google Sheets -----------------
GOOGLE_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwl5EEjgx7zoiC3JO60SJYTcCEg-c23aVE8RcxnNP-7QXPAy2MawiNd3dqkAdMhZfIHRg/exec"
SECRET_KEY = "BarorHeil2026"

def parse_hebrew_date(val):
    """פענוח תאריך מדויק ומונע בלבול ישראלי-אמריקאי"""
    if not val or pd.isna(val):
        return None
    s = str(val).strip()
    if s in ["", "0", "None", "תאריך"]:
        return None
    
    try:
        if len(s) >= 10 and s[4] == '-' and s[7] == '-':
            return datetime.datetime.strptime(s[:10], "%Y-%m-%d").date()
    except Exception:
        pass
    
    try:
        parts = s.split("/") if "/" in s else s.split("-")
        if len(parts) == 3:
            p1, p2, p3 = int(parts[0]), int(parts[1]), int(parts[2][:4])
            if p3 > 2000:
                return datetime.date(p3, p2, p1)
            elif p1 > 2000:
                return datetime.date(p1, p2, p3)
    except Exception:
        pass
    
    try:
        dt = pd.to_datetime(s, errors='coerce', dayfirst=True)
        if pd.notna(dt):
            return dt.date()
    except Exception:
        pass
    return None

def send_to_google_sheets(sheet_name, row_data):
    """שליחת שורה ל-Google Sheets בפורמט מאובטח"""
    payload = {
        "secret_key": SECRET_KEY,
        "sheet_name": sheet_name,
        "row_data": json.dumps(row_data, ensure_ascii=False)
    }
    try:
        res = requests.post(GOOGLE_WEBHOOK_URL, data=payload, allow_redirects=True, timeout=20)
        return "Success" in res.text
    except Exception as e:
        st.error(f"שגיאת תקשורת: {str(e)}")
        return False

@st.cache_data(ttl=300)
def get_sheet_data_from_cloud(sheet_name):
    """משיכת נתונים מ-Google Sheets עם זיכרון מטמון"""
    try:
        params = {"secret_key": SECRET_KEY, "sheet_name": sheet_name}
        res = requests.get(GOOGLE_WEBHOOK_URL, params=params, allow_redirects=True, timeout=20)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

# ----------------- טעינת מחירון דינמי מהענן -----------------
@st.cache_data(ttl=600)
def load_prices():
    raw_data = get_sheet_data_from_cloud("מחירון")
    treatments = []
    price_map = {}
    
    if raw_data:
        col_t_idx = 2
        for r_idx, row in enumerate(raw_data):
            for c_idx, val in enumerate(row):
                if str(val).strip() == "שם הטיפול":
                    col_t_idx = c_idx
                    break
        
        for row in raw_data:
            if len(row) > col_t_idx:
                t_val = str(row[col_t_idx]).strip()
                if t_val and t_val != "שם הטיפול" and t_val != '""':
                    treatments.append(t_val)
                    price_map[t_val] = {
                        "חברי קיבוץ מבוטחים": row[col_t_idx + 1] if len(row) > col_t_idx + 1 else "",
                        "מבוטחים": row[col_t_idx + 2] if len(row) > col_t_idx + 2 else "",
                        "לקוחות חוץ וחברים לא מבוטחים": row[col_t_idx + 3] if len(row) > col_t_idx + 3 else "",
                        "מיוחד לחברי ניצנים": row[col_t_idx + 4] if len(row) > col_t_idx + 4 else ""
                    }
    return sorted(list(set(treatments))), price_map

treatment_list, treatment_prices = load_prices()

# ----------------- פונקציית עיבוד מהירה לדשבורד -----------------
@st.cache_data(ttl=120)
def process_financial_dashboard():
    """מעבד את הנתונים במהירות שיא ושומר בזיכרון מטמון"""
    inc_raw = get_sheet_data_from_cloud("הכנסות")
    exp_raw = get_sheet_data_from_cloud("הוצאות")

    detected_years = set([2026, datetime.date.today().year])
    monthly_inc = {}
    monthly_exp = {}

    # 1. עיבוד הכנסות
    if inc_raw and len(inc_raw) > 1:
        for r in inc_raw[1:]:
            if len(r) > 18:
                d_val = r[1]
                amt_val = r[18]
                inst_val = r[19] if len(r) > 19 else 1
                
                parsed_d = parse_hebrew_date(d_val)
                if parsed_d:
                    try:
                        clean_amt = float(str(amt_val).replace("₪", "").replace(",", "").strip())
                        n_inst = int(str(inst_val).strip()) if str(inst_val).strip().isdigit() and int(str(inst_val).strip()) > 0 else 1
                        
                        if clean_amt > 0:
                            m_portion = clean_amt / n_inst
                            for p_i in range(n_inst):
                                p_date = parsed_d + relativedelta(months=p_i)
                                y = p_date.year
                                m = p_date.month
                                detected_years.add(y)
                                
                                if y not in monthly_inc:
                                    monthly_inc[y] = {i: 0.0 for i in range(1, 13)}
                                monthly_inc[y][m] += m_portion
                    except Exception:
                        pass

    # 2. עיבוד הוצאות
    if exp_raw and len(exp_raw) > 1:
        for r in exp_raw[1:]:
            if len(r) > 6:
                d_val = r[1]
                amt_val = r[6]
                parsed_d = parse_hebrew_date(d_val)
                if parsed_d:
                    try:
                        clean_amt = float(str(amt_val).replace("₪", "").replace(",", "").strip())
                        if clean_amt > 0:
                            y = parsed_d.year
                            m = parsed_d.month
                            detected_years.add(y)
                            
                            if y not in monthly_exp:
                                monthly_exp[y] = {i: 0.0 for i in range(1, 13)}
                            monthly_exp[y][m] += clean_amt
                    except Exception:
                        pass

    return sorted(list(detected_years), reverse=True), monthly_inc, monthly_exp

# ----------------- ברכה יומית מותאמת לפי שעה -----------------
now_hour = datetime.datetime.now().hour

if 5 <= now_hour < 12:
    time_greeting = "בוקר אור לרותי האלופה! ☕🇧🇷"
    greetings_pool = [
        "שיהיה יום עבודה מקסים, מלא אנרגיות חיוביות וסדר במרפאה. אל תשכחי לוודא הזנה מלאה של כל הנתונים!",
        "עוד בוקר שבו הניהול המקצועי שלך מוביל את המרפאה להצלחה. תודה על המסירות!",
        "איזה כיף לפתוח איתך את הבוקר! בואי נוודא יחד שכל ביקור והוצאה נרשמים בקפידה.",
        "הסדר והדיוק שלך עושים את כל ההבדל במרפאה. יום פורה ומוצלח!",
        "את פשוט מספר אחת! יום נעים, זורם ומחויך. זכרי לעדכן את כל נתוני הבוקר ברוגע."
    ]
elif 12 <= now_hour < 17:
    time_greeting = "צהריים טובים לרותי המדהימה! 🌿🇧🇷"
    greetings_pool = [
        "המשך יום עבודה פורה ורגוע. תודה על השקט והניהול המופתי במרפאה!",
        "צהריים נעימים! הזדמנות מעולה לוודא שכל הטיפולים מהבוקר כבר עודכנו במערכת.",
        "חצי יום כבר מאחורינו, והכל מתוקתק בזכותך! תודה על כל ההשקעה.",
        "עבודה נעימה ורגועה במשמרת הצהריים. אין על הסדר והארגון שלך!"
    ]
elif 17 <= now_hour < 21:
    time_greeting = "ערב טוב לרותי היקרה! 🌸🇧🇷"
    greetings_pool = [
        "מסיימים עוד יום מוצלח במרפאה! אנא ודאי שכל הנתונים וההוצאות נשמרו כראוי.",
        "ערב נעים ורגוע. תודה על יום שלם של מסירות, סבלנות וניהול למופת!",
        "עוד יום שהסתיים בהצלחה בזכותך. סגירת משמרת קלה ונעימה!"
    ]
else:
    time_greeting = "לילה טוב לרותי! ✨🇧🇷"
    greetings_pool = [
        "תודה על יום עבודה מסור. לילה שקט ומנוחה נעימה!",
        "יישר כוח על כל ההשקעה היום. שיהיה לילה רגוע ונעים!"
    ]

today_str = datetime.date.today().isoformat()
if "last_greeting_date" not in st.session_state or st.session_state.last_greeting_date != today_str:
    st.session_state.show_daily_modal = True
    st.session_state.last_greeting_date = today_str
    st.session_state.chosen_greeting = f"{time_greeting}\n\n{random.choice(greetings_pool)}"

@st.dialog("✨ הודעה יומית לרותי")
def show_greeting_dialog():
    st.markdown(f"### {st.session_state.chosen_greeting}")
    st.balloons()
    if st.button("המשך ליום עבודה מוצלח! 🦷", type="primary"):
        st.session_state.show_daily_modal = False
        st.rerun()

if st.session_state.get("show_daily_modal", False):
    show_greeting_dialog()

# ----------------- כותרת ותפריט -----------------
st.title("🦷 מרפאת שיניים ברור חיל — מערכת ניהול 🇧🇷")

# כפתור התנתקות קטן בסרגל הצד
if st.sidebar.button("🚪 התנתק מהמערכת"):
    st.session_state.authenticated = False
    st.rerun()

menu = st.sidebar.radio("תפריט פעולות", [
    "➕ הזנת ביקור חדש (הכנסה)",
    "💸 הזנת הוצאה / משכורת",
    "📊 דשבורד רווח והפסד (תזרים חודשי)"
])

st.sidebar.divider()
if st.sidebar.button("🔄 רענן נתונים מהענן"):
    st.cache_data.clear()
    st.rerun()

ALL_SUPPLIERS = [
    "-- בחר ספק / עובד --",
    "שוועדנט", "שן זן", "נמרוד - טכנאי", "פרודנטל", "ג'ורדן",
    "אייבי שתלים לביא", "אלפא ביו שתלים ויטלי", "דיבידנט mis שתלים", "אוסדה מחשבים יניב",
    "ד\"ר קלמן", "סייעת יעל", "שיננית עינב", "אורתודנטית יעל", "רותי מנהלת",
    "ספק / עובד אחר..."
]

if "num_treatments" not in st.session_state:
    st.session_state.num_treatments = 4

if "income_form_key" not in st.session_state:
    st.session_state.income_form_key = 0

# =========================================================================
# 1. הזנת ביקור חדש (הכנסה בלבד)
# =========================================================================
if menu == "➕ הזנת ביקור חדש (הכנסה)":
    st.subheader("רישום ביקור ותקבולים למטופל")
    
    col_d, col_n, col_s = st.columns([1.2, 1.5, 1.5])
    with col_d:
        v_date = st.date_input("תאריך הביקור (יום/חודש/שנה)", datetime.date.today(), min_value=datetime.date(2020, 1, 1), format="DD/MM/YYYY")
    with col_n:
        p_name = st.text_input("שם המטופל *", key=f"inp_p_{st.session_state.income_form_key}")
    with col_s:
        status_opts = ["-- בחר מעמד מטופל --", "חברי קיבוץ מבוטחים", "מבוטחים", "לקוחות חוץ וחברים לא מבוטחים", "מיוחד לחברי ניצנים"]
        p_status = st.selectbox("מעמד המטופל *", status_opts, index=0, key=f"inc_status_{st.session_state.income_form_key}")

    col_inst, col_disc = st.columns([1, 1])
    with col_inst:
        installments = st.number_input("מספר תשלומים * (1 עד 12)", min_value=1, max_value=12, value=1, step=1, key=f"inst_{st.session_state.income_form_key}")
    with col_disc:
        discount = st.number_input("אחוז הנחה כללי לביקור (%)", min_value=0, max_value=100, value=0, step=5, key=f"disc_{st.session_state.income_form_key}")

    st.divider()
    st.write(f"### טיפולים בביקור ({st.session_state.num_treatments} טיפולים):")

    treatments_opts = ["-- בחר טיפול --"] + treatment_list

    selected_treatments = []
    total_calculated_income = 0.0
    total_original_income = 0.0
    has_textual_treatment = False

    for i in range(st.session_state.num_treatments):
        c_tr, c_q, c_pr, c_del = st.columns([3, 1, 1.8, 0.5])
        with c_tr:
            t_choice = st.selectbox(f"טיפול {i+1}", treatments_opts, index=0, key=f"treat_sel_{i}_{st.session_state.income_form_key}")
        with c_q:
            q_val = st.number_input(f"כמות", min_value=1, value=1, key=f"treat_qty_{i}_{st.session_state.income_form_key}")
        
        item_unit_price = 0.0
        display_text = ""
        is_numeric = False

        if t_choice != "-- בחר טיפול --" and p_status != "-- בחר מעמד מטופל --":
            raw_val = treatment_prices.get(t_choice, {}).get(p_status)
            if raw_val is None or pd.isna(raw_val) or str(raw_val).strip() == "" or str(raw_val).lower() == "nan":
                display_text = "טיפול לא קיים ללקוח זה"
            else:
                clean_str = str(raw_val).replace("₪", "").replace(",", "").strip()
                try:
                    item_unit_price = float(clean_str)
                    is_numeric = True
                except ValueError:
                    display_text = str(raw_val).strip()

        with c_pr:
            if t_choice != "-- בחר טיפול --":
                if p_status == "-- בחר מעמד מטופל --":
                    st.caption("נא לבחור מעמד מטופל")
                elif is_numeric:
                    line_orig = item_unit_price * q_val
                    line_final = line_orig * (1.0 - (discount / 100.0))
                    total_original_income += line_orig
                    total_calculated_income += line_final
                    st.markdown(f"**לתשלום:** ₪{line_final:,.1f}<br><small style='color:gray;'>מקורי: ₪{line_orig:,.0f}</small>", unsafe_allow_html=True)
                    selected_treatments.append({
                        "name": t_choice, "qty": q_val, "orig_price": line_orig, "final_price": line_final, "is_textual": False
                    })
                else:
                    has_textual_treatment = True
                    st.markdown(f"<span style='color:#c0392b; font-weight:600;'>{display_text}</span>", unsafe_allow_html=True)
                    selected_treatments.append({
                        "name": t_choice, "qty": q_val, "orig_price": 0.0, "final_price": 0.0, "note": display_text, "is_textual": True
                    })
            else:
                st.caption("לא נבחר")

        with c_del:
            if i >= 4:
                if st.button("❌", key=f"del_treat_{i}_{st.session_state.income_form_key}", help="הסר טיפול זה"):
                    st.session_state.num_treatments -= 1
                    st.rerun()

    if st.session_state.num_treatments < 8:
        if st.button("➕ הוסף טיפול נוסף לביקור זה"):
            st.session_state.num_treatments += 1
            st.rerun()

    monthly_pay = total_calculated_income / installments if installments > 0 else 0.0

    st.markdown(f"""
    <div style="background: #ffffff; border: 2px solid #28a745; padding: 14px; border-radius: 10px; margin: 18px 0;">
        <b style="color: #005a28; font-size: 16px;">סה"כ מחושב לביקור:</b> <span style="font-size: 18px; font-weight: bold; color: #28a745;">₪{total_calculated_income:,.2f}</span> | 
        <b style="color: #005a28;">חלוקה ל-{installments} תשלומים:</b> <span style="font-weight: bold;">₪{monthly_pay:,.2f} לחודש</span>
    </div>
    """, unsafe_allow_html=True)

    @st.dialog("⚠️ שגיאה בהזנת טיפולים")
    def show_textual_warning_dialog():
        st.error("לפי המחירון, קיים טיפול אחד (או יותר) שאינו מתאים למעמד המטופל. יש לפנות ליובל")
        if st.button("הבנתי, חזרה לעריכה", type="primary", use_container_width=True):
            st.rerun()

    @st.dialog("אישור והזנת ביקור")
    def confirm_income_dialog():
        st.write("### אנא ודאי את פרטי הביקור לפני השמירה:")
        st.write(f"**מטופל/ת:** {p_name}")
        st.write(f"**תאריך:** {v_date.strftime('%d/%m/%Y')} | **מעמד:** {p_status}")
        st.write(f"**תשלומים:** {installments} תשלומים של ₪{monthly_pay:,.2f}")
        st.write("**טיפולים:**")
        for itm in selected_treatments:
            price_desc = f"₪{itm['final_price']:,.1f}" if itm['final_price'] > 0 else itm['note']
            st.write(f"- {itm['name']} (כמות: {itm['qty']}) — {price_desc}")
        st.write(f"**סה\"כ סופי: ₪{total_calculated_income:,.2f}**")
        
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("אישור ושמירה סופית", type="primary", use_container_width=True):
                t1_name = selected_treatments[0]["name"] if len(selected_treatments) > 0 else ""
                t1_qty = selected_treatments[0]["qty"] if len(selected_treatments) > 0 else ""
                t1_price = selected_treatments[0]["orig_price"] if len(selected_treatments) > 0 else ""

                t2_name = selected_treatments[1]["name"] if len(selected_treatments) > 1 else ""
                t2_qty = selected_treatments[1]["qty"] if len(selected_treatments) > 1 else ""
                t2_price = selected_treatments[1]["orig_price"] if len(selected_treatments) > 1 else ""

                t3_name = selected_treatments[2]["name"] if len(selected_treatments) > 2 else ""
                t3_qty = selected_treatments[2]["qty"] if len(selected_treatments) > 2 else ""
                t3_price = selected_treatments[2]["orig_price"] if len(selected_treatments) > 2 else ""

                if len(selected_treatments) == 4:
                    t4_name = selected_treatments[3]["name"]
                    t4_qty = selected_treatments[3]["qty"]
                    t4_price = selected_treatments[3]["orig_price"]
                elif len(selected_treatments) > 4:
                    extra_names = [f"{t['name']} (x{t['qty']})" for t in selected_treatments[3:]]
                    t4_name = " + ".join(extra_names)
                    t4_qty = sum(t["qty"] for t in selected_treatments[3:])
                    t4_price = sum(t["orig_price"] for t in selected_treatments[3:])
                else:
                    t4_name, t4_qty, t4_price = "", "", ""

                row_for_income = [
                    "",
                    v_date.strftime("%Y-%m-%d"),
                    p_name,
                    p_status,
                    t1_name, t1_qty, t1_price,
                    t2_name, t2_qty, t2_price,
                    t3_name, t3_qty, t3_price,
                    t4_name, t4_qty, t4_price,
                    float(total_original_income),
                    float(discount) / 100.0,
                    float(total_calculated_income),
                    int(installments)
                ]

                with st.spinner("שומר נתונים ב-Google Sheets..."):
                    ok = send_to_google_sheets("הכנסות", row_for_income)

                if ok:
                    st.success(f"הביקור של {p_name} נשמר בהצלחה ב-Google Sheets!")
                    st.session_state.income_form_key += 1
                    st.session_state.num_treatments = 4
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("חלה שגיאה בשמירה ל-Google Sheets.")
        with c_no:
            if st.button("שינוי נתונים", use_container_width=True):
                st.rerun()

    if st.button("שמירה", type="primary"):
        if not p_name.strip():
            st.error("נא להזין את שם המטופל.")
        elif p_status == "-- בחר מעמד מטופל --":
            st.error("נא לבחור מעמד מטופל מתוך הרשימה.")
        elif not selected_treatments:
            st.error("נא לבחור לפחות טיפול אחד.")
        elif has_textual_treatment:
            show_textual_warning_dialog()
        else:
            confirm_income_dialog()

# =========================================================================
# 2. הזנת הוצאה / משכורת
# =========================================================================
elif menu == "💸 הזנת הוצאה / משכורת":
    st.subheader("רישום הוצאה או משכורת")
    
    col_ed, col_ec = st.columns([1.2, 1.5])
    with col_ed:
        exp_date = st.date_input("תאריך ההוצאה (יום/חודש/שנה)", datetime.date.today(), min_value=datetime.date(2020, 1, 1), format="DD/MM/YYYY")
    with col_ec:
        cat_opts = ["-- בחר קטגוריה --", "חומרים ומעבדה", "משכורות", "הוצאות קליניקה שוטפות", "שונות"]
        exp_cat = st.selectbox("קטגוריית הוצאה *", cat_opts, index=0)

    col_ep, col_edesc = st.columns([1, 1.5])
    with col_ep:
        patient_ref = st.text_input("שם מטופל (אם רלוונטי למעבדה/שתלים)")
    with col_edesc:
        exp_desc = st.text_input("פירוט ההוצאה / הנרכש *")

    col_esup, col_eamt = st.columns([1.5, 1])
    with col_esup:
        chosen_sup = st.selectbox("ספק / עובד *", ALL_SUPPLIERS, index=0)
        if chosen_sup == "ספק / עובד אחר...":
            final_sup = st.text_input("הקלד שם ספק/עובד חדש:")
        else:
            final_sup = chosen_sup
    with col_eamt:
        exp_amount = st.number_input("סכום בש\"ח (₪) *", min_value=0.0, step=50.0)

    @st.dialog("אישור והזנת הוצאה")
    def confirm_expense_dialog():
        st.write("### אנא ודאי את פרטי ההוצאה:")
        st.write(f"**תאריך:** {exp_date.strftime('%d/%m/%Y')}")
        st.write(f"**קטגוריה:** {exp_cat}")
        st.write(f"**ספק / עובד:** {final_sup}")
        st.write(f"**פירוט:** {exp_desc}")
        st.write(f"**סכום לתשלום: ₪{exp_amount:,.2f}**")
        
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("אישור ושמירה סופית", type="primary", use_container_width=True):
                row_for_sheets = [
                    "",
                    exp_date.strftime("%Y-%m-%d"),
                    exp_cat,
                    patient_ref,
                    exp_desc,
                    final_sup,
                    exp_amount
                ]
                with st.spinner("שומר הוצאה ב-Google Sheets..."):
                    ok = send_to_google_sheets("הוצאות", row_for_sheets)
                
                if ok:
                    st.success("ההוצאה נשמרה בהצלחה ב-Google Sheets בענן!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("חלה שגיאה בשמירה ל-Google Sheets.")
        with c_no:
            if st.button("שינוי נתונים", use_container_width=True):
                st.rerun()

    if st.button("שמירה", type="primary"):
        if exp_cat == "-- בחר קטגוריה --":
            st.error("נא לבחור קטגוריית הוצאה.")
        elif chosen_sup == "-- בחר ספק / עובד --":
            st.error("נא לבחור ספק או עובד מתוך הרשימה.")
        elif not exp_desc.strip() or exp_amount <= 0:
            st.error("נא להזין פירוט הוצאה וסכום תקין.")
        else:
            confirm_expense_dialog()

# =========================================================================
# 3. דשבורד רווח והפסד (תזרים חודשי)
# =========================================================================
elif menu == "📊 דשבורד רווח והפסד (תזרים חודשי)":
    years_list, all_inc, all_exp = process_financial_dashboard()

    c_head, c_yr = st.columns([3, 1])
    with c_head:
        st.subheader("דוח רווח והפסד — תזרים מזומנים חודשי")
    with c_yr:
        default_idx = years_list.index(2026) if 2026 in years_list else 0
        selected_year = st.selectbox("בחר שנת פעילות:", years_list, index=default_idx)

    st.markdown(f"#### 📅 תזרים מזומנים לשנת **{selected_year}** (לפי חודשי פירעון בפועל)")

    inc_dict = all_inc.get(selected_year, {m: 0.0 for m in range(1, 13)})
    exp_dict = all_exp.get(selected_year, {m: 0.0 for m in range(1, 13)})

    total_income = sum(inc_dict.values())
    total_expense = sum(exp_dict.values())
    net_profit = total_income - total_expense

    profit_box_class = "box-green" if net_profit >= 0 else "box-red"
    profit_label = f"רווח נקי לשנת {selected_year}" if net_profit >= 0 else f"הפסד נקי לשנת {selected_year}"

    c_inc, c_exp, c_prof = st.columns(3)
    with c_inc:
        st.markdown(f"""
        <div class="metric-box box-green">
            <span style="font-size: 15px; font-weight:600;">סה"כ הכנסות שהתקבלו ({selected_year})</span>
            <h2 style="margin: 6px 0 0 0; font-size: 32px;">₪{total_income:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c_exp:
        st.markdown(f"""
        <div class="metric-box box-red">
            <span style="font-size: 15px; font-weight:600;">סה"כ הוצאות ({selected_year})</span>
            <h2 style="margin: 6px 0 0 0; font-size: 32px;">₪{total_expense:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c_prof:
        st.markdown(f"""
        <div class="metric-box {profit_box_class}">
            <span style="font-size: 15px; font-weight:600;">{profit_label}</span>
            <h2 style="margin: 6px 0 0 0; font-size: 32px;">₪{net_profit:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.write(f"### פירוט חודשי: הכנסות בפועל, הוצאות ורווח/הפסד ({selected_year})")

    months_names = [
        "ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני",
        "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"
    ]

    table_rows = []
    for m in range(1, 13):
        m_inc = inc_dict.get(m, 0.0)
        m_exp = exp_dict.get(m, 0.0)
        m_prof = m_inc - m_exp
        prof_color = "#28a745" if m_prof >= 0 else "#dc3545"
        
        row_html = (
            f"<tr>"
            f"<td><b>{months_names[m-1]}</b></td>"
            f"<td style='color:#28a745; font-weight:600;'>₪{m_inc:,.2f}</td>"
            f"<td style='color:#dc3545; font-weight:600;'>₪{m_exp:,.2f}</td>"
            f"<td style='color:{prof_color}; font-weight:bold;'>₪{m_prof:,.2f}</td>"
            f"</tr>"
        )
        table_rows.append(row_html)

    complete_table_html = (
        f"<table class='styled-table'>"
        f"<thead>"
        f"<tr>"
        f"<th>חודש</th>"
        f"<th>הכנסות בפועל (₪)</th>"
        f"<th>הוצאות (₪)</th>"
        f"<th>רווח / הפסד (₪)</th>"
        f"</tr>"
        f"</thead>"
        f"<tbody>{''.join(table_rows)}</tbody>"
        f"</table>"
    )

    st.markdown(complete_table_html, unsafe_allow_html=True)