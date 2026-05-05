# --- เพิ่มฟังก์ชันนี้ต่อจาก save_adjustment ---
def save_log(action_type, amount, total_after):
    supabase.table("time_track_log").insert({
        "action_type": action_type,
        "amount": amount,
        "total_after": total_after
    }).execute()

# --- ส่วนของปุ่มกด (Update ฐานข้อมูล) ให้แก้เป็นแบบนี้ ---
st.subheader("⚙️ จัดการเวลา (พร้อมบันทึก Log)")
c1, c2 = st.columns(2)

with c1:
    add_val = st.number_input("เพิ่ม (ชม.)", min_value=0.0, step=1.0, key="add_btn")
    if st.button("➕ ยืนยันเพิ่มเวลา", use_container_width=True):
        new_val = st.session_state.adj_hrs + add_val
        # บันทึกค่าใหม่
        save_adjustment(new_val)
        # บันทึก Log
        save_log("add", add_val, new_val)
        
        st.session_state.adj_hrs = new_val
        st.success(f"บันทึกการเพิ่ม {add_val} ชม. เรียบร้อย!")
        st.rerun()

with c2:
    sub_val = st.number_input("ลด (ชม.)", min_value=0.0, step=1.0, key="sub_btn")
    if st.button("➖ ยืนยันลดเวลา", use_container_width=True):
        new_val = st.session_state.adj_hrs - sub_val
        # บันทึกค่าใหม่
        save_adjustment(new_val)
        # บันทึก Log
        save_log("sub", sub_val, new_val)
        
        st.session_state.adj_hrs = new_val
        st.warning(f"บันทึกการลด {sub_val} ชม. เรียบร้อย!")
        st.rerun()

# --- (Optional) เพิ่มส่วนแสดง Log ด้านล่างสุด ---
st.divider()
st.subheader("📜 ประวัติการปรับปรุง (5 รายการล่าสุด)")
log_response = supabase.table("time_track_log").select("*").order("created_at", desc=True).limit(5).execute()
if log_response.data:
    for l in log_response.data:
        color = "green" if l['action_type'] == "add" else "red"
        st.write(f":{color}[{l['action_type'].upper()}] | {l['amount']} ชม. | เมื่อ: {l['created_at'][:19].replace('T', ' ')}")