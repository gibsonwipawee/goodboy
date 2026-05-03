import streamlit as st
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. ตั้งค่าพื้นฐาน ---
START_TIME = datetime(2026, 5, 2, 11, 0, 0)
INITIAL_HOURS = 957

# --- 2. เชื่อมต่อ Supabase ---
# แนะนำให้ใช้ st.secrets เพื่อความปลอดภัย (ตั้งค่าในหน้า Streamlit Cloud)
if "supabase_url" in st.secrets:
    URL = st.secrets["supabase_url"]
    KEY = st.secrets["supabase_key"]
else:
    # สำหรับรันเทสในเครื่องตัวเอง
    URL = "YOUR_SUPABASE_URL"
    KEY = "YOUR_SUPABASE_KEY"

supabase: Client = create_client(URL, KEY)

# --- 3. ฟังก์ชันจัดการฐานข้อมูล ---
def load_adjustment():
    response = supabase.table("time_tracker").select("adjustment_hours").eq("id", 1).execute()
    return response.data[0]["adjustment_hours"]

def save_adjustment(new_val):
    supabase.table("time_tracker").update({"adjustment_hours": new_val}).eq("id", 1).execute()

# --- 4. เริ่มต้นแอป ---
st.set_page_config(page_title="Time Tracker Pro", page_icon="🚀")

# โหลดข้อมูล
if 'adj_hrs' not in st.session_state:
    st.session_state.adj_hrs = load_adjustment()

# --- 5. ส่วนการคำนวณ ---
now = datetime.now()
time_passed = now - START_TIME
hours_passed = time_passed.total_seconds() / 3600
net_remaining = INITIAL_HOURS - hours_passed + st.session_state.adj_hrs

days = int(net_remaining // 24)
hrs = int(net_remaining % 24)
end_date = now + timedelta(hours=net_remaining)

# --- 6. การแสดงผล UI ---
st.title("⌛ ระบบคำนวณเวลา (Supabase)")
st.caption(f"ซิงค์ข้อมูลแบบ Real-time | เริ่มต้น: {START_TIME.strftime('%d/%m/%Y %H:%M')}")

col1, col2 = st.columns(2)
with col1:
    st.metric("เวลาที่เหลือ", f"{days} วัน {hrs} ชม.")
with col2:
    st.metric("ชั่วโมงสุทธิ", f"{net_remaining:.2f} ชม.")

if net_remaining > 0:
    st.success(f"📅 **สิ้นสุดวันที่:** {end_date.strftime('%d/%m/%Y เวลา %H:%M:%S')}")
else:
    st.error("⚠️ เวลาสิ้นสุดลงแล้ว")

st.divider()

# --- 7. ปุ่มกด (Update ฐานข้อมูล) ---
st.subheader("⚙️ จัดการเวลา (ข้อมูลไม่หาย)")
c1, c2 = st.columns(2)

with c1:
    add_val = st.number_input("เพิ่ม (ชม.)", min_value=0.0, step=1.0, key="add_btn")
    if st.button("➕ ยืนยันเพิ่มเวลา", use_container_width=True):
        new_val = st.session_state.adj_hrs + add_val
        save_adjustment(new_val)
        st.session_state.adj_hrs = new_val
        st.rerun()

with c2:
    sub_val = st.number_input("ลด (ชม.)", min_value=0.0, step=1.0, key="sub_btn")
    if st.button("➖ ยืนยันลดเวลา", use_container_width=True):
        new_val = st.session_state.adj_hrs - sub_val
        save_adjustment(new_val)
        st.session_state.adj_hrs = new_val
        st.rerun()