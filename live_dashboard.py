import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wattwise — Smart Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS (safe — only style rules, no HTML content) ───────────────────
st.markdown("""
<style>

/* ───── GLOBAL ───── */
html, body {
    scroll-behavior: smooth;
}

/* Smooth everything */
* {
    transition: all 0.25s ease;
}

/* ───── CARD INTERACTION ───── */
.ww-card {
    background: radial-gradient(circle at top left, #0f1c2e, #060b14);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    height: 120px;

    /* 🔥 glow + depth */
    box-shadow: 
        0 8px 25px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.05);

    transition: all 0.3s ease;
}

/* 🔥 hover effect */
.ww-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: rgba(0,229,160,0.6);
    box-shadow: 
        0 12px 35px rgba(0,229,160,0.15),
        inset 0 1px 0 rgba(255,255,255,0.08);
}

/* 🔥 curved light effect */
.ww-card::after {
    content: "";
    position: absolute;
    bottom: -40px;
    left: -20px;
    width: 200%;
    height: 100px;
    background: radial-gradient(circle, rgba(0,229,160,0.15), transparent);
    transform: rotate(-5deg);
}

/* label */
.ww-card-label {
    color: rgba(255,255,255,0.5);
    font-size: 11px;
    margin-bottom: 6px;
}

/* main value */
.ww-card-value {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
}

/* subtext */
.ww-card-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.4);
}

/* ───── BUTTON INTERACTION ───── */
.stButton > button {
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#00e5a0,#00b8ff) !important;
    color: #060b14 !important;
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(0,229,160,0.5);
}

/* ───── INPUT INTERACTION ───── */
input:focus {
    transform: scale(1.02);
}

/* ───── SCROLLBAR GLOW ───── */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(#00e5a0,#00b8ff);
    border-radius: 10px;
}

/* ───── CURSOR GLOW EFFECT ───── */
body {
    cursor: none;
}

.cursor-dot {
    width: 12px;
    height: 12px;
    background: #00e5a0;
    border-radius: 50%;
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
}

.cursor-outline {
    width: 35px;
    height: 35px;
    border: 2px solid rgba(0,229,160,0.5);
    border-radius: 50%;
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
}

/* ───── HOVER TEXT EFFECT ───── */
h1, h2, h3 {
    transition: all 0.3s ease;
}
h1:hover, h2:hover, h3:hover {
    color: #00e5a0;
}

/* ───── FADE-IN ANIMATION ───── */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.block-container {
    animation: fadeInUp 0.6s ease;
}

</style>

<script>
// Cursor animation
const dot = document.createElement('div');
dot.classList.add('cursor-dot');
document.body.appendChild(dot);

const outline = document.createElement('div');
outline.classList.add('cursor-outline');
document.body.appendChild(outline);

document.addEventListener('mousemove', (e) => {
    dot.style.left = e.clientX + 'px';
    dot.style.top = e.clientY + 'px';

    outline.style.left = e.clientX + 'px';
    outline.style.top = e.clientY + 'px';
});
</script>

""", unsafe_allow_html=True)
# ─── Session State ────────────────────────────────────────────────────────────
for k, v in [("page","landing"),("logged_in",False),("user_data",{})]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Demo users (replace with real DB calls) ─────────────────────────────────
if "DEMO_USERS" not in st.session_state:
    st.session_state.DEMO_USERS = {
        "SMT_1001": {"name": "Arjun Sharma",  "password": "demo123", "phone": "+919876543210", "plan": "Domestic"},
        "SMT_1002": {"name": "Priya Nair",    "password": "demo123", "phone": "+919123456789", "plan": "Commercial"},
        "SMT_1003": {"name": "Karthik Rajan", "password": "demo123", "phone": "+919988776655", "plan": "Industrial"},
    }

# ─── Data helpers ─────────────────────────────────────────────────────────────
def generate_data(meter_id, days=30):
    np.random.seed(abs(hash(meter_id)) % 9999)
    base = 4.5 if "1001" in meter_id else 12.0 if "1002" in meter_id else 45.0 if "1003" in meter_id else 5.0
    dates = [datetime.now() - timedelta(hours=i) for i in range(days * 24, 0, -1)]
    hours = [d.hour for d in dates]
    peak = [1.6 if (7<=h<=10 or 18<=h<=22) else 0.65 if h<=5 else 1.0 for h in hours]
    usage = [max(0.1, base * p * (1 + np.random.normal(0, 0.12))) for p in peak]
    forecast = [max(0.1, u * (1 + np.random.normal(0.02, 0.05))) for u in usage[-48:]]
    df = pd.DataFrame({"datetime": dates, "usage_kwh": usage, "hour": hours})
    return df, forecast

def get_stats(df):
    total = df["usage_kwh"].sum()
    daily = df.groupby(df["datetime"].dt.date)["usage_kwh"].sum().mean()
    return {
        "total":     round(total, 1),
        "daily_avg": round(daily, 1),
        "peak":      round(df["usage_kwh"].max(), 2),
        "bill":      round(total * 7.5, 0),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE  — built entirely with Streamlit + inline-style HTML snippets
# ═══════════════════════════════════════════════════════════════════════════════
def page_landing():
    # ── Nav bar ──
    st.markdown("""
    <div style="background:#0a1220;border-bottom:1px solid rgba(255,255,255,0.07);
                padding:18px 48px;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
            background:linear-gradient(135deg,#00e5a0,#00b8ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            ⚡ Wattwise
        </div>
        <div style="display:flex;gap:32px;font-size:14px;color:rgba(255,255,255,0.45);">
            <span>Features</span><span>How it works</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
    <div style="padding:80px 60px 56px;max-width:1100px;margin:0 auto;">
        <div style="display:inline-flex;align-items:center;gap:8px;
            background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.25);
            color:#00e5a0;padding:6px 18px;border-radius:100px;
            font-size:12px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:28px;">
            ⚡ Smart Electricity Analytics Platform
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:68px;font-weight:800;
            line-height:1.05;letter-spacing:-2px;color:#fff;margin-bottom:24px;">
            Know your power.<br>
            <span style="background:linear-gradient(135deg,#00e5a0,#00b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                Cut your bill.
            </span>
        </div>
        <div style="font-size:18px;color:rgba(255,255,255,0.48);max-width:520px;
            line-height:1.75;font-weight:300;margin-bottom:48px;">
            Real-time electricity consumption monitoring, AI-powered forecasting,
            and instant SMS alerts — personalized to your meter ID.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA buttons (Streamlit native so they work) ──
    _, c1, c2, _ = st.columns([3, 1.2, 1, 5])
    with c1:
        if st.button("🚀  Get Started", key="land_signup", use_container_width=True):
            st.session_state.page = "signup"; st.rerun()
    with c2:
        if st.button("🔑  Sign In", key="land_login", use_container_width=True):
            st.session_state.page = "login"; st.rerun()

    st.markdown("""
    <style>
    /* landing CTA button colours — scoped to first two content columns after hero */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(135deg,#00e5a0,#00c48a) !important;
        color: #060b14 !important; border: none !important;
        font-size: 15px !important; font-weight:700 !important; height:52px !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) button {
        background: transparent !important; color: #fff !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        font-size: 15px !important; height:52px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Stats row ──
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:32px 60px;border-top:1px solid rgba(255,255,255,0.05);
                border-bottom:1px solid rgba(255,255,255,0.05);
                display:flex;gap:64px;max-width:1100px;margin:0 auto;">
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;
                background:linear-gradient(135deg,#00e5a0,#00b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">40%</div>
            <div style="color:rgba(255,255,255,0.38);font-size:13px;margin-top:4px;">Average bill reduction</div>
        </div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;
                background:linear-gradient(135deg,#00e5a0,#00b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">12K+</div>
            <div style="color:rgba(255,255,255,0.38);font-size:13px;margin-top:4px;">Active meters monitored</div>
        </div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;
                background:linear-gradient(135deg,#00e5a0,#00b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">99.8%</div>
            <div style="color:rgba(255,255,255,0.38);font-size:13px;margin-top:4px;">Forecast accuracy</div>
        </div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;
                background:linear-gradient(135deg,#00e5a0,#00b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">&lt;30s</div>
            <div style="color:rgba(255,255,255,0.38);font-size:13px;margin-top:4px;">Real-time alert delivery</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Features grid ──
    st.markdown("<div style='padding:64px 60px 32px;max-width:1100px;margin:0 auto;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
        color:#00e5a0;margin-bottom:12px;">What we offer</div>
    <div style="font-family:'Syne',sans-serif;font-size:38px;font-weight:800;
        color:#fff;letter-spacing:-1px;margin-bottom:40px;">
        Everything you need<br>to optimize energy
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("📡", "Live Monitoring",      "Stream hourly consumption from your smart meter directly into your personalized dashboard."),
        ("🧠", "LSTM Forecasting",     "Deep learning predicts your next 48 hours of usage with ±3% accuracy using historical patterns."),
        ("🔔", "SMS Alerts",           "Instant Twilio-powered SMS when usage spikes, bills hit thresholds, or anomalies are detected."),
        ("💡", "Recommendations",      "AI tips to shift load off-peak and reduce wasteful appliance usage based on your fingerprint."),
        ("📊", "Bill Prediction",      "XGBoost estimates your end-of-month bill in real time — no billing surprises."),
        ("⚖️", "Peer Benchmarking",   "Compare your usage against similar households in your locality and tariff category."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                border-radius:20px;padding:28px;margin-bottom:16px;
                transition:border-color 0.2s;">
                <div style="width:46px;height:46px;background:rgba(0,229,160,0.1);
                    border-radius:12px;display:flex;align-items:center;justify-content:center;
                    font-size:22px;margin-bottom:18px;">{icon}</div>
                <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;
                    color:#fff;margin-bottom:8px;">{title}</div>
                <div style="color:rgba(255,255,255,0.42);font-size:13px;line-height:1.65;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("""
    <div style="padding:32px 60px;border-top:1px solid rgba(255,255,255,0.05);margin-top:32px;
        color:rgba(255,255,255,0.22);font-size:12px;display:flex;justify-content:space-between;">
        <span>⚡ Wattwise — Smart Energy Analytics</span>
        <span>© 2025 · LSTM + XGBoost · Twilio</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def page_login():
    st.markdown("""
    <div style="text-align:center;padding:48px 0 0;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
            background:linear-gradient(135deg,#00e5a0,#00b8ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            ⚡ Wattwise
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;
            color:#fff;margin-top:20px;">Welcome back</div>
        <div style="color:rgba(255,255,255,0.4);font-size:14px;margin-top:6px;margin-bottom:32px;">
            Sign in with your Meter ID to continue
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        meter_id = st.text_input("Meter ID", placeholder="e.g. SMT_1001", key="li_meter")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="li_pass")
        phone    = st.text_input("📱 Phone Number (for SMS alerts)", placeholder="+91XXXXXXXXXX", key="li_phone")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        do_login = st.button("Sign In →", key="do_login", use_container_width=True)

        if do_login:
            uid = meter_id.strip().upper()
            users = st.session_state.DEMO_USERS
            if uid in users and users[uid]["password"] == password.strip():
                u = users[uid]
                st.session_state.logged_in = True
                st.session_state.user_data = {
                    "meter_id": uid, "name": u["name"],
                    "phone": phone.strip() or u["phone"], "plan": u["plan"]
                }
                st.session_state.page = "dashboard"
                st.success(f"✅ Welcome back, {u['name'].split()[0]}!")
                time.sleep(0.6); st.rerun()
            else:
                st.error("❌ Invalid Meter ID or password.")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Create account →", key="go_signup_from_login", use_container_width=True):
            st.session_state.page = "signup"; st.rerun()
        if st.button("← Back to Home", key="login_home"):
            st.session_state.page = "landing"; st.rerun()

    # Demo hint
    st.markdown("""
    <div style="max-width:420px;margin:20px auto 0;background:rgba(0,229,160,0.06);
        border:1px solid rgba(0,229,160,0.2);border-radius:12px;padding:14px 18px;">
        <div style="color:#00e5a0;font-size:12px;font-weight:600;margin-bottom:6px;">
            🔑 DEMO CREDENTIALS
        </div>
        <div style="color:rgba(255,255,255,0.55);font-size:12px;line-height:1.9;">
            Meter IDs: <b style="color:#fff">SMT_1001</b> &nbsp;|&nbsp;
                       <b style="color:#fff">SMT_1002</b> &nbsp;|&nbsp;
                       <b style="color:#fff">SMT_1003</b><br>
            Password: <b style="color:#fff">demo123</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Sign In primary button */
    button[data-testid="baseButton-secondary"]:first-of-type {
        background: linear-gradient(135deg,#00e5a0,#00c48a) !important;
        color: #060b14 !important; border: none !important; font-weight:700 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIGN UP PAGE  — FIX: all fields collected before validation
# ═══════════════════════════════════════════════════════════════════════════════
def page_signup():
    st.markdown("""
    <div style="text-align:center;padding:48px 0 0;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
            background:linear-gradient(135deg,#00e5a0,#00b8ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            ⚡ Wattwise
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;
            color:#fff;margin-top:20px;">Create your account</div>
        <div style="color:rgba(255,255,255,0.4);font-size:14px;margin-top:6px;margin-bottom:32px;">
            Connect your smart meter and start saving
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        # ── All fields declared BEFORE the button so values exist when button fires ──
        nc1, nc2 = st.columns(2)
        with nc1:
            fname = st.text_input("First Name *", placeholder="Arjun", key="su_fname")
        with nc2:
            lname = st.text_input("Last Name *",  placeholder="Sharma", key="su_lname")

        email    = st.text_input("Email Address *",        placeholder="you@email.com", key="su_email")
        meter_id = st.text_input("Meter ID *",             placeholder="e.g. SMT_1001 (from your bill)", key="su_meter")
        phone    = st.text_input("📱 Mobile Number (for alerts) *", placeholder="+91XXXXXXXXXX", key="su_phone")
        plan     = st.selectbox("Connection Type *", ["Domestic","Commercial","Industrial","Agricultural"], key="su_plan")
        password = st.text_input("Create Password *",      type="password", placeholder="Min. 8 characters", key="su_pass")
        confirm  = st.text_input("Confirm Password *",     type="password", placeholder="Repeat password", key="su_confirm")
        agree    = st.checkbox("I agree to receive SMS alerts on the above number via Twilio", value=True, key="su_agree")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        do_signup = st.button("Create Account & Connect Meter →", key="do_signup", use_container_width=True)

        if do_signup:
            # ── Collect values at button-click time (they are already in session state) ──
            v_fname    = st.session_state.get("su_fname", "").strip()
            v_lname    = st.session_state.get("su_lname", "").strip()
            v_email    = st.session_state.get("su_email", "").strip()
            v_meter    = st.session_state.get("su_meter", "").strip()
            v_phone    = st.session_state.get("su_phone", "").strip()
            v_password = st.session_state.get("su_pass",  "").strip()
            v_confirm  = st.session_state.get("su_confirm","").strip()
            v_plan     = st.session_state.get("su_plan",  "Domestic")

            # ── Validation ──
            missing = []
            if not v_fname:    missing.append("First Name")
            if not v_lname:    missing.append("Last Name")
            if not v_email:    missing.append("Email")
            if not v_meter:    missing.append("Meter ID")
            if not v_phone:    missing.append("Phone Number")
            if not v_password: missing.append("Password")
            if not v_confirm:  missing.append("Confirm Password")

            if missing:
                st.error(f"Please fill in: {', '.join(missing)}")
            elif v_password != v_confirm:
                st.error("Passwords do not match.")
            elif len(v_password) < 8:
                st.error("Password must be at least 8 characters.")
            elif "@" not in v_email:
                st.error("Please enter a valid email address.")
            else:
                uid = v_meter.upper()
                st.session_state.DEMO_USERS[uid] = {
                    "name": f"{v_fname} {v_lname}",
                    "password": v_password,
                    "phone": v_phone,
                    "plan": v_plan,
                }
                st.session_state.logged_in = True
                st.session_state.user_data = {
                    "meter_id": uid,
                    "name": f"{v_fname} {v_lname}",
                    "phone": v_phone,
                    "plan": v_plan,
                }
                st.success(f"✅ Account created! Welcome, {v_fname}!")
                time.sleep(0.6)
                st.session_state.page = "dashboard"
                st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Already have an account? Sign In →", key="go_login_su", use_container_width=True):
            st.session_state.page = "login"; st.rerun()
        if st.button("← Back to Home", key="signup_home"):
            st.session_state.page = "landing"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    user     = st.session_state.user_data
    meter_id = user.get("meter_id","SMT_1001")
    df, forecast = generate_data(meter_id)
    stats = get_stats(df)

    # ── Top nav ──
    st.markdown(f"""
    <div style="background:#0a1220;border-bottom:1px solid rgba(255,255,255,0.07);
                padding:14px 32px;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
            background:linear-gradient(135deg,#00e5a0,#00b8ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            ⚡ Wattwise
        </div>
        <div style="display:flex;align-items:center;gap:20px;font-size:13px;">
            <span style="color:rgba(255,255,255,0.4);">
                Meter: <span style="color:#00e5a0;font-weight:600;">{meter_id}</span>
            </span>
            <span style="color:rgba(255,255,255,0.4);">
                Plan: <span style="color:#fff;">{user.get('plan','Domestic')}</span>
            </span>
            <div style="background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.25);
                border-radius:100px;padding:5px 14px;color:#00e5a0;font-weight:600;">
                👤 {user.get('name','User').split()[0]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Page title ──
    st.markdown("""
    <div style="padding:24px 32px 8px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#fff;">
            Energy Dashboard
        </div>
        <div style="color:rgba(255,255,255,0.3);font-size:13px;margin-top:3px;">
            Last 30 days · Live data from your smart meter
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ──
    st.markdown("<div style='padding:0 32px;'>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "Total Consumption", f"{stats['total']:,.0f}", "kWh this month",  "badge-y", "⬆ +6% vs last month"),
        (k2, "Estimated Bill",    f"₹{stats['bill']:,.0f}", "at ₹7.50/kWh",    "badge-r", "⬆ High usage alert"),
        (k3, "Daily Average",     f"{stats['daily_avg']}", "kWh per day",       "badge-g", "✓ Within normal range"),
        (k4, "Peak Demand",       f"{stats['peak']}",      "kW peak",           "badge-y", "⚠ Off-peak savings possible"),
    ]
    for col, label, val, sub, badge_cls, badge_txt in kpis:
        with col:
            st.markdown(f"""
            <div class="ww-card">
                <div class="ww-card-value">{val}</div>
                <div class="ww-card-label">{label}</div>
                <div class="ww-card-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div><div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Charts ──
    st.markdown("<div style='padding:0 32px;'>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Consumption", "🔮 48h Forecast", "🌡️ Heatmap", "⚡ Peak Analysis"])

    PLOT_LAYOUT = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Epilogue", color="rgba(255,255,255,0.45)"),
        margin=dict(l=10,r=10,t=20,b=10), height=320,
        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.3)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   color="rgba(255,255,255,0.3)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

    with tab1:
        daily = df.groupby(df["datetime"].dt.date)["usage_kwh"].sum().reset_index()
        daily.columns = ["date","kwh"]
        daily["date"] = pd.to_datetime(daily["date"])
        daily["ma7"]  = daily["kwh"].rolling(7, center=True).mean()
        fig = go.Figure([
            go.Scatter(x=daily["date"], y=daily["kwh"],
                       fill="tozeroy", fillcolor="rgba(0,229,160,0.08)",
                       line=dict(color="#00e5a0",width=2), name="Daily usage",
                       hovertemplate="<b>%{x|%b %d}</b><br>%{y:.1f} kWh<extra></extra>"),
            go.Scatter(x=daily["date"], y=daily["ma7"],
                       line=dict(color="#00b8ff",width=1.5,dash="dot"), name="7-day avg",
                       hovertemplate="7-day avg: %{y:.1f} kWh<extra></extra>"),
        ])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fc_dates = [datetime.now() + timedelta(hours=h) for h in range(1,49)]
        hist48   = df.tail(48)
        lower = [max(0, f*0.92) for f in forecast]
        upper = [f*1.08 for f in forecast]
        fig2 = go.Figure([
            go.Scatter(x=hist48["datetime"], y=hist48["usage_kwh"],
                       line=dict(color="rgba(255,255,255,0.28)",width=1.5), name="Historical"),
            go.Scatter(x=fc_dates+fc_dates[::-1], y=upper+lower[::-1],
                       fill="toself", fillcolor="rgba(0,184,255,0.07)",
                       line=dict(color="rgba(0,0,0,0)"), showlegend=False, name="Confidence"),
            go.Scatter(x=fc_dates, y=forecast,
                       line=dict(color="#00b8ff",width=2.5,dash="dot"), name="LSTM Forecast",
                       hovertemplate="Forecast: %{y:.2f} kWh<extra></extra>"),
        ])
        # ✅ convert everything to string (100% safe fix)
        hist_x = hist48["datetime"].astype(str)
        fc_dates = [(datetime.now() + timedelta(hours=h)).isoformat() for h in range(1, 49)]

        fig2 = go.Figure([
            go.Scatter(
                x=hist_x,
                y=hist48["usage_kwh"],
                name="Historical"
            ),
            go.Scatter(
                x=fc_dates,
                y=forecast,
                name="Forecast"
            )
        ])

        # ✅ safe vertical line
        current_time = datetime.now().isoformat()

        fig2.add_vline(
            x=current_time,
            line_color="rgba(0,229,160,0.5)",
            line_dash="dash"
        )
        fig2.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        hm = df.copy()
        hm["date"] = hm["datetime"].dt.strftime("%b %d")
        pivot = hm.groupby(["date","hour"])["usage_kwh"].mean().unstack(fill_value=0)
        fig3 = go.Figure(go.Heatmap(
            z=pivot.values[-14:],
            x=[f"{h:02d}:00" for h in range(24)],
            y=pivot.index.tolist()[-14:],
            colorscale=[[0,"#0a1220"],[0.4,"#005f4e"],[0.7,"#00e5a0"],[1,"#ff5050"]],
            hovertemplate="<b>%{y}</b> %{x}<br>%{z:.2f} kWh<extra></extra>",
        ))
        fig3.update_layout(**{**PLOT_LAYOUT, "height": 380})
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        ha   = df.groupby("hour")["usage_kwh"].mean().reset_index()
        cols_bar = ["#ff5050" if (7<=h<=10 or 18<=h<=22) else "#00b8ff" if h<=5 else "#00e5a0"
                    for h in ha["hour"]]
        st.markdown("""
        <div style="display:flex;gap:20px;font-size:12px;margin-bottom:8px;">
            <span style="color:#ff5050">■ Peak (7-10am, 6-10pm)</span>
            <span style="color:#00e5a0">■ Normal</span>
            <span style="color:#00b8ff">■ Off-peak (midnight-5am)</span>
        </div>""", unsafe_allow_html=True)
        fig4 = go.Figure(go.Bar(
            x=[f"{h:02d}:00" for h in ha["hour"]], y=ha["usage_kwh"],
            marker_color=cols_bar,
            hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh<extra></extra>"
        ))
        fig4.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Alerts + Recommendations ──
    st.markdown("<div style='padding:0 32px 32px;'>", unsafe_allow_html=True)
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#fff;margin-bottom:14px;">🔔 Recent Alerts</div>', unsafe_allow_html=True)
        alerts = [
            ("⚠️","High consumption 7–9 PM. Shift heavy loads off-peak.","2 hours ago","rgba(255,193,7,0.07)","rgba(255,193,7,0.25)"),
            ("📊",f"Est. bill crossing ₹{int(stats['bill']*0.7):,}. On track for ₹{int(stats['bill']):,}.","6 hours ago","rgba(255,193,7,0.07)","rgba(255,193,7,0.25)"),
            ("✅","Consumption back to normal after 11 PM last night.","Yesterday","rgba(0,229,160,0.07)","rgba(0,229,160,0.25)"),
            ("🚨","Spike: 3.2× above hourly average at 8:47 PM.","2 days ago","rgba(255,80,80,0.07)","rgba(255,80,80,0.25)"),
        ]
        for icon, msg, ts, bg, border in alerts:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:12px;
                padding:13px 16px;margin-bottom:9px;display:flex;gap:11px;">
                <div style="font-size:18px;margin-top:2px;">{icon}</div>
                <div>
                    <div style="color:rgba(255,255,255,0.8);font-size:13px;line-height:1.5;">{msg}</div>
                    <div style="color:rgba(255,255,255,0.28);font-size:11px;margin-top:3px;">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-family:Syne,sans-serif;font-size:14px;font-weight:700;color:#fff;margin:16px 0 8px;">📲 Send SMS Alert</div>', unsafe_allow_html=True)
        sms_c1, sms_c2 = st.columns([3,1])
        with sms_c1:
            sms_msg = st.text_input("Message", key="sms_text",
                value=f"⚡ Wattwise: Meter {meter_id} usage HIGH. Est bill ₹{int(stats['bill']):,}. Login to check.")
        with sms_c2:
            st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
            if st.button("📤 Send SMS", key="send_sms"):
                with st.spinner("Sending…"):
                    time.sleep(1.2)
                    # Plug in real Twilio here:
                    # from twilio.rest import Client
                    # Client(SID, TOKEN).messages.create(body=sms_msg, from_=FROM, to=user['phone'])
                    st.success(f"✅ Sent to {user.get('phone','')}")

    with right:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#fff;margin-bottom:14px;">💡 AI Recommendations</div>', unsafe_allow_html=True)
        recs = [
            ("🌙","Shift washing machine & geyser to 11 PM–5 AM off-peak","Save ~₹420/mo"),
            ("❄️","AC at 24°C vs 18°C saves 18%. Ideal for Chennai climate.","Save ~₹310/mo"),
            ("🔌","3 phantom loads detected — unplug idle chargers/STBs.","Save ~₹90/mo"),
            ("📅","Peak usage: Wed evenings. Schedule appliances better.","Save ~₹180/mo"),
        ]
        for icon, tip, saving in recs:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:14px;margin-bottom:10px;display:flex;gap:11px;">
                <div style="font-size:20px;">{icon}</div>
                <div>
                    <div style="color:rgba(255,255,255,0.78);font-size:13px;line-height:1.5;">{tip}</div>
                    <div style="background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.2);
                        color:#00e5a0;font-size:11px;font-weight:600;padding:3px 10px;
                        border-radius:100px;display:inline-block;margin-top:7px;">{saving}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-family:Syne,sans-serif;font-size:14px;font-weight:700;color:#fff;margin:16px 0 4px;">📊 Peer Comparison</div>', unsafe_allow_html=True)
        peer = {"You": stats["daily_avg"],
                "Locality avg": round(stats["daily_avg"]*0.82,1),
                "Top 10%":      round(stats["daily_avg"]*0.55,1)}
        fig_p = go.Figure(go.Bar(
            x=list(peer.keys()), y=list(peer.values()),
            marker_color=["#00b8ff","rgba(255,255,255,0.18)","rgba(0,229,160,0.6)"],
            text=[f"{v} kWh" for v in peer.values()], textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.65)",size=12)
        ))
        fig_p.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Epilogue",color="rgba(255,255,255,0.35)"),
            yaxis=dict(visible=False), xaxis=dict(showgrid=False,color="rgba(255,255,255,0.35)"),
            margin=dict(l=0,r=0,t=28,b=0), height=200, showlegend=False
        )
        st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Sign out ──
    st.markdown("<div style='padding:0 32px 28px;'>", unsafe_allow_html=True)
    if st.button("← Sign Out", key="logout"):
        st.session_state.logged_in = False
        st.session_state.user_data = {}
        st.session_state.page = "landing"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
p = st.session_state.page
if   p == "landing":   page_landing()
elif p == "login":     page_login()
elif p == "signup":    page_signup()
elif p == "dashboard":
    if st.session_state.logged_in: page_dashboard()
    else: st.session_state.page = "login"; st.rerun()