import streamlit as st
from datetime import datetime
import uuid
from twilio.rest import Client

# ─── TWILIO CONFIG (paste your keys once) ───
TWILIO_SID = st.secrets.get("TWILIO_SID", "your_sid_here")
TWILIO_TOKEN = st.secrets.get("TWILIO_TOKEN", "your_token_here")
FROM_NUMBER = st.secrets.get("FROM_NUMBER", "+15551234567")  # your Twilio number
PLUMBER_NUMBER = st.secrets.get("PLUMBER_NUMBER", "+15559876543")  # Chris's cell

client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID != "your_sid_here" else None

def send_sms(to, body):
    if client:
        client.messages.create(to=to, from_=FROM_NUMBER, body=body)

# ─── APP START ───
st.set_page_config(page_title="PlumbGuard BMS", page_icon="🔧", layout="centered")
st.title("🔧 PlumbGuard BMS v4")
st.markdown("**Photos • Videos • Live Call • Instant SMS Alerts**")

if "requests" not in st.session_state:
    st.session_state.requests = []

# ─── CUSTOMER FORM ───
st.header("Get Quote in Minutes")

with st.form("quote_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
        phone = st.text_input("Phone*", placeholder="555-123-4567")
    with col2:
        address = st.text_input("Address")
        email = st.text_input("Email (optional)")

    issue = st.selectbox("Problem*", ["", "Burst Pipe 🚨", "Leaky Faucet", "Water Heater", "Clogged Drain", "No Hot Water", "Running Toilet", "Other"])
    details = st.text_area("Describe (optional)")

    colA, colB = st.columns(2)
    with colA:
        photos = st.file_uploader("Photos", type=["jpg","jpeg","png"], accept_multiple_files=True)
    with colB:
        videos = st.file_uploader("Videos", type=["mp4","mov"], accept_multiple_files=True)

    col_send, col_call = st.columns(2)
    submit_btn = col_send.form_submit_button("📤 Send & Get Quote")
    live_btn = col_call.form_submit_button("📹 Live Video Call NOW")

    if submit_btn and phone and issue:
        call_id = str(uuid.uuid4())[:8]
        entry = {
            "id": call_id, "time": datetime.now().strftime("%b %d %I:%M%p"),
            "name": name or "Anonymous", "phone": phone, "address": address,
            "issue": issue, "details": details or "—",
            "photos": photos or [], "videos": videos or [], "type": "Quote"
        }
        st.session_state.requests.append(entry)

        # SMS to plumber instantly
        sms_body = f"🚨 NEW JOB\n{name or 'Customer'} | {phone}\n{issue}\n{address or '—'}"
        send_sms(PLUMBER_NUMBER, sms_body)

        st.success("✅ Sent! Chris was just texted — quote coming fast")
        st.balloons()

    if live_btn and phone:
        call_id = phone[-4:] + str(uuid.uuid4())[:4]
        live_url = f"https://plumbguard.live/call/{call_id}"
        entry = {"id": call_id, "time": datetime.now().strftime("%b %d %I:%M%p"),
                 "name": name or "Live", "phone": phone, "issue": "LIVE CALL", "live_url": live_url, "type": "Live"}
        st.session_state.requests.append(entry)

        # SMS with live link
        sms_body = f"🔴 LIVE CALL STARTED\nCustomer: {name or phone}\nJoin NOW → {live_url}"
        send_sms(PLUMBER_NUMBER, sms_body)

        st.success("🔴 LIVE CALL ACTIVE — Chris just got the link on his phone!")
        st.code(live_url)
        st.markdown(f"[Join Call]({live_url})")
        st.balloons()

# ─── ADMIN DASHBOARD ───
st.divider()
if st.checkbox("Plumber Login"):
    pwd = st.text_input("Password", type="password")
    if pwd == "plumb2025":
        st.success("Logged in")
        for r in reversed(st.session_state.requests):
            label = f"{'🔴' if 'LIVE' in r['issue'] else '🚨'} {r['time']} — {r['name']} — {r['issue']}"
            with st.expander(label, expanded="LIVE" in r['issue']):
                st.write(f"📞 {r['phone']} | 📍 {r.get('address','—')}")
                st.write(r['details'])
                for p in r.get('photos', []): st.image(p, width=300)
                for v in r.get('videos', []): st.video(v)
                if r.get('live_url'):
                    st.markdown(f"### 🔴 [JOIN LIVE CALL]({r['live_url']})")
                    st.code(r['live_url'])
