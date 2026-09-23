import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ====================================================
# 0. การตั้งค่าหน้าเว็บ & เชื่อมต่อ Cloud Supabase
# ====================================================
st.set_page_config(
    page_title="ระบบบริหารจัดการรถเช่าส่วนกลาง (Car Rental ERP)",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------
# Custom CSS: Sidebar ตัวอักษรสีขาวสว่าง + Luxury Navy & Gold Trim
# ----------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Kanit', sans-serif !important;
    }

    /* 1. เส้นสีทองคาดขอบบนสุดของหน้าจอ */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #b8860b 0%, #fef08a 50%, #d4af37 100%);
        z-index: 999999;
    }

    /* พื้นหลังหลัก Off-White สบายตา */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], .main {
        background-color: #f1f5f9 !important;
    }

    /* 2. แถบ Sidebar สไตล์ Prody Modern UI (โทนกรมเข้มตัดทอง) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1.5px solid #d4af37 !important;
        padding-top: 1rem;
    }

    /* บังคับตัวอักษรและข้อความทั้งหมดใน Sidebar ให้เป็นสีขาวสว่าง */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* ตกแต่งช่อง Search บน Sidebar */
    [data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #1e293b !important;
        border: 1px solid #d4af37 !important;
        border-radius: 10px !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="input"] input {
        color: #ffffff !important;
        font-size: 14px !important;
    }

    /* ตกแต่ง Radio Buttons ใน Sidebar */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: transparent !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 4px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid transparent !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label p,
    [data-testid="stSidebar"] div[role="radiogroup"] > label span {
        color: #ffffff !important;
        font-size: 15px !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #1e293b !important;
        border-color: #475569 !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid #d4af37 !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p,
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] span,
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
        color: #fef08a !important;
    }

    /* 3. แถบหัวข้อโมดูล (Module Header Banner) */
    h1 {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: #ffffff !important;
        padding: 1.2rem 1.8rem !important;
        border-radius: 14px !important;
        border-left: 6px solid #d4af37 !important;
        border-bottom: 2px solid #d4af37 !important;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08) !important;
        margin-bottom: 1.8rem !important;
        font-size: 1.75rem !important;
    }

    h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 3.5px solid #d4af37 !important;
        border-radius: 14px !important;
        padding: 1.2rem !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
    }

    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #64748b !important;
    }

    /* Form สไตล์การ์ดเข้ม */
    [data-testid="stForm"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid #334155 !important;
        border-top: 4px solid #d4af37 !important;
        border-radius: 16px !important;
        padding: 2.2rem !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2) !important;
    }

    /* บังคับตัวอักษรและ Label ภายใน Form ทั้งหมด (รวมหน้า Login) ให้เป็นสีขาวสว่าง */
    [data-testid="stForm"] label,
    [data-testid="stForm"] label p,
    [data-testid="stForm"] label span,
    [data-testid="stForm"] p,
    [data-testid="stForm"] span {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* ปรับแต่ง Label ของ Input ในหน้าหลัก (อยู่นอก Form) ให้เป็นสีดำเข้ม */
    .stMain div:not([data-testid="stForm"]) > .stTextInput label, 
    .stMain div:not([data-testid="stForm"]) > .stSelectbox label, 
    .stMain div:not([data-testid="stForm"]) > .stNumberInput label, 
    .stMain div:not([data-testid="stForm"]) > .stDateInput label, 
    .stMain div:not([data-testid="stForm"]) > .stTextArea label {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    .stSelectbox div[data-baseweb="select"] * {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%) !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        border-color: #fef08a !important;
        box-shadow: 0 6px 18px rgba(212, 175, 55, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 3px solid #d4af37 !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อ Supabase ได้: {e}")
    st.info("กรุณาตรวจสอบการตั้งค่าไฟล์ .streamlit/secrets.toml หรือ Secrets บน Streamlit Cloud")
    st.stop()

# ====================================================
# 1. ระบบเข้าสู่ระบบ (Authentication System)
# ====================================================
USERS = {
    "admin": "1234",
    "user1": "1234"
}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def login_page():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br/><br/>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); width: 75px; height: 75px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; box-shadow: 0 8px 20px rgba(212, 175, 55, 0.35); border: 2.5px solid #d4af37;">
                    <span style="font-size: 38px;">🚗</span>
                </div>
                <h1 style="color: #ffffff !important; text-align: center;">CAR RENTAL ERP</h1>
                <p style="color: #cbd5e1 !important; font-size: 15px; font-weight: 500;">ระบบบริหารจัดการรถเช่าส่วนกลาง ระดับพรีเมียม</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; color: #fef08a !important; margin-bottom: 20px; font-weight: 600;'>🔐 เข้าสู่ระบบ</h3>", unsafe_allow_html=True)
            username = st.text_input("👤 ชื่อผู้ใช้งาน (Username)")
            password = st.text_input("🔑 รหัสผ่าน (Password)", type="password")
            st.markdown("<br/>", unsafe_allow_html=True)
            submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
            
            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success("✅ เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

if not st.session_state["logged_in"]:
    login_page()
    st.stop()

DOCS_DIR = os.path.abspath("documents")
os.makedirs(DOCS_DIR, exist_ok=True)

# ====================================================
# 2. เมนูหลักประจำแอปพลิเคชัน (Sidebar Navigation + Search)
# ====================================================
st.sidebar.markdown("""
    <div style="padding: 10px 5px 10px 5px; display: flex; align-items: center; gap: 12px;">
        <div style="background: linear-gradient(135deg, #1e3a8a, #0f172a); width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; border: 1.5px solid #d4af37;">
            <span style="font-size: 22px;">🚗</span>
        </div>
        <div>
            <h3 style="color: #ffffff !important; margin: 0; font-size: 18px; font-weight: 700;">ProRental</h3>
            <p style="color: #d4af37 !important; font-size: 12px; margin: 0; font-weight: 500;">Enterprise ERP</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# 🔍 ช่องค้นหาด่วน (Global Search Bar) บน Sidebar
global_search = st.sidebar.text_input("Search", placeholder="ค้นหา", label_visibility="collapsed")
st.sidebar.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

module_choice = st.sidebar.radio(
    "NAVIGATION",
    [
        "🚙 1. จัดการข้อมูลรถ",
        "👥 2. จัดการข้อมูลลูกค้า",
        "📄 3. ทำสัญญาเช่ารถ",
        "🔄 4. ระบบรับคืนรถ",
        "💰 5. ระบบรับชำระเงิน",
        "🔧 6. ค่าใช้จ่าย & ซ่อมบำรุง",
        "📊 7. Dashboard & รายงาน",
        "🔔 8. ระบบแจ้งเตือน",
        "📁 9. ศูนย์เอกสาร & PDF",
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br/><hr style='border-color: #334155;'>", unsafe_allow_html=True)
st.sidebar.markdown(f"👤 ผู้ใช้งาน: **{st.session_state['username']}**")

if st.sidebar.button("🚪 ออกจากระบบ", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()

# ====================================================
# โมดูล 1: จัดการข้อมูลรถ (Car Management)
# ====================================================
if module_choice == "🚙 1. จัดการข้อมูลรถ":
    st.title("🚙 1. โมดูลจัดการข้อมูลรถยนต์")

    tab1, tab2, tab3 = st.tabs(["📋 รายการรถทั้งหมด", "➕ เพิ่มรถยนต์ใหม่", "✏️ แก้ไข/ระงับใช้งานรถ"])

    with tab1:
        status_filter = st.selectbox("เลือกสถานะ", ["ทั้งหมด", "ว่าง", "กำลังเช่า", "ซ่อมบำรุง", "ระงับใช้งาน"])

        res = supabase.table("cars").select("*").order("id", desc=False).execute()
        df_cars = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df_cars.empty:
            if global_search:
                df_cars = df_cars[
                    df_cars["license_plate"].astype(str).str.contains(global_search, case=False, na=False) |
                    df_cars["brand"].astype(str).str.contains(global_search, case=False, na=False) |
                    df_cars["model"].astype(str).str.contains(global_search, case=False, na=False)
                ]
            if status_filter != "ทั้งหมด":
                df_cars = df_cars[df_cars["status"] == status_filter]

        st.dataframe(df_cars, use_container_width=True)

    with tab2:
        st.subheader("➕ เพิ่มรถยนต์ใหม่เข้าสู่ระบบ")
        with st.form("add_car_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            plate = c1.text_input("ทะเบียนรถ * (เช่น 7ขจ 1099)")
            brand = c2.text_input("ยี่ห้อ * (เช่น Toyota, GWM)")
            model = c3.text_input("รุ่นรถ * (เช่น Fortuner, Tank 300)")

            c4, c5, c6 = st.columns(3)
            year = c4.number_input("ปี ค.ศ. *", min_value=2000, max_value=2030, value=2025)
            color = c5.text_input("สีรถ", value="ขาว")
            car_type = c6.selectbox("ประเภทรถยนต์", ["รย.1 (เก๋ง/SUV)", "รย.2 (กระบะ)", "รย.3 (ตู้)", "EV รถยนต์ไฟฟ้า"])

            c7, c8, c9 = st.columns(3)
            price = c7.number_input("ราคาเช่ารายวัน (บาท) *", value=1200.0, step=100.0)
            mileage = c8.number_input("เลขไมล์ปัจจุบัน", value=10000, step=500)
            status = c9.selectbox("สถานะเริ่มต้น", ["ว่าง", "ซ่อมบำรุง", "ระงับใช้งาน"])

            c10, c11 = st.columns(2)
            ins_exp = c10.date_input("วันหมดอายุประกันภัย", value=datetime.now())
            tax_exp = c11.date_input("วันหมดอายุภาษี/พ.ร.บ.", value=datetime.now())

            submitted = st.form_submit_button("💾 บันทึกรถยนต์ใหม่")
            if submitted:
                if not plate or not brand or not model:
                    st.error("กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบถ้วน")
                else:
                    check = supabase.table("cars").select("id").eq("license_plate", plate.strip()).execute()
                    if check.data:
                        st.error(f"❌ ทะเบียนรถ '{plate}' มีในระบบแล้ว")
                    else:
                        new_car = {
                            "license_plate": plate.strip(),
                            "brand": brand.strip(),
                            "model": model.strip(),
                            "year": int(year),
                            "color": color.strip(),
                            "car_type": car_type,
                            "price_per_day": float(price),
                            "mileage": int(mileage),
                            "insurance_exp": str(ins_exp),
                            "tax_exp": str(tax_exp),
                            "status": status,
                        }
                        supabase.table("cars").insert(new_car).execute()
                        st.success(f"✅ บันทึกรถยนต์ทะเบียน {plate} เรียบร้อยแล้ว")
                        st.rerun()

    with tab3:
        st.subheader("✏️ แก้ไขข้อมูลรถ หรือ ปรับสถานะ")
        res = supabase.table("cars").select("id, license_plate, brand, model").order("id", desc=False).execute()
        cars_list = res.data or []

        if cars_list:
            car_options = {c["id"]: f"{c['license_plate']} - {c['brand']} {c['model']}" for c in cars_list}
            selected_car_id = st.selectbox("เลือกรถที่ต้องการแก้ไข", options=list(car_options.keys()), format_func=lambda x: car_options[x])

            car_data = supabase.table("cars").select("*").eq("id", selected_car_id).single().execute().data

            if car_data:
                with st.form("edit_car_form"):
                    e1, e2, e3 = st.columns(3)
                    e_plate = e1.text_input("ทะเบียนรถ", value=car_data["license_plate"])
                    e_brand = e2.text_input("ยี่ห้อ", value=car_data["brand"])
                    e_model = e3.text_input("รุ่น", value=car_data["model"])

                    e4, e5, e6 = st.columns(3)
                    e_price = e4.number_input("ราคาเช่ารายวัน", value=float(car_data["price_per_day"] or 0))
                    e_mileage = e5.number_input("เลขไมล์", value=int(car_data["mileage"] or 0))
                    status_opts = ["ว่าง", "กำลังเช่า", "ซ่อมบำรุง", "ระงับใช้งาน"]
                    status_idx = status_opts.index(car_data["status"]) if car_data["status"] in status_opts else 0
                    e_status = e6.selectbox("สถานะรถ", status_opts, index=status_idx)

                    if st.form_submit_button("💾 บันทึกการแก้ไข"):
                        updated_data = {
                            "license_plate": e_plate,
                            "brand": e_brand,
                            "model": e_model,
                            "price_per_day": float(e_price),
                            "mileage": int(e_mileage),
                            "status": e_status,
                        }
                        supabase.table("cars").update(updated_data).eq("id", selected_car_id).execute()
                        st.success("✅ อัปเดตข้อมูลเรียบร้อยแล้ว")
                        st.rerun()

# ====================================================
# โมดูล 2: จัดการข้อมูลลูกค้า (Customer Management)
# ====================================================
elif module_choice == "👥 2. จัดการข้อมูลลูกค้า":
    st.title("👥 2. โมดูลจัดการข้อมูลลูกค้า")

    tab1, tab2 = st.tabs(["📋 รายชื่อลูกค้า", "➕ เพิ่มลูกค้าใหม่"])

    with tab1:
        res = supabase.table("customers").select("*").order("id", desc=False).execute()
        df_cust = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df_cust.empty and global_search:
            df_cust = df_cust[
                df_cust["name"].astype(str).str.contains(global_search, case=False, na=False) |
                df_cust["phone"].astype(str).str.contains(global_search, case=False, na=False) |
                df_cust["driver_license"].astype(str).str.contains(global_search, case=False, na=False)
            ]
        st.dataframe(df_cust, use_container_width=True)

    with tab2:
        st.subheader("➕ ลงทะเบียนลูกค้าใหม่")
        res = supabase.table("customers").select("id").order("id", desc=True).limit(1).execute()
        max_id = res.data[0]["id"] if res.data else 0
        auto_code = f"CUST-{max_id + 1:03d}"

        st.info(f"🆔 รหัสลูกค้าอัตโนมัติ: **{auto_code}**")

        with st.form("add_cust_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            c_name = col1.text_input("ชื่อ-นามสกุล *")
            c_phone = col2.text_input("เบอร์โทรศัพท์ *")

            col3, col4 = st.columns(2)
            c_email = col3.text_input("อีเมล")
            c_dl = col4.text_input("เลขที่ใบขับขี่ *")

            c_exp = st.date_input("วันหมดอายุใบขับขี่", value=datetime.now() + timedelta(days=365))
            c_address = st.text_area("ที่อยู่ตามบัตร/ที่อยู่ติดต่อ")

            if st.form_submit_button("💾 บันทึกข้อมูลลูกค้า"):
                if not c_name or not c_phone or not c_dl:
                    st.error("กรุณากรอก ชื่อ, เบอร์โทร และ เลขใบขับขี่")
                else:
                    new_cust = {
                        "cust_code": auto_code,
                        "name": c_name.strip(),
                        "phone": c_phone.strip(),
                        "address": c_address.strip(),
                        "email": c_email.strip(),
                        "driver_license": c_dl.strip(),
                        "license_exp": str(c_exp),
                    }
                    supabase.table("customers").insert(new_cust).execute()
                    st.success(f"✅ บันทึกลูกค้า {c_name} เรียบร้อยแล้ว")
                    st.rerun()

# ====================================================
# โมดูล 3: ทำสัญญาเช่ารถ (Rental Contract)
# ====================================================
elif module_choice == "📄 3. ทำสัญญาเช่ารถ":
    st.title("📄 3. โมดูลทำสัญญาเช่ารถ (Rental Agreement)")

    prefix = datetime.now().strftime("CNT-%Y%m%d-")
    res_cnt = supabase.table("contracts").select("id").ilike("contract_no", f"{prefix}%").execute()
    cnt_seq = len(res_cnt.data or []) + 1
    auto_cnt_no = f"{prefix}{cnt_seq:02d}"

    st.subheader(f"📝 สร้างสัญญาเช่าใหม่: `{auto_cnt_no}`")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 1. เลือกลูกค้า")
        cust_res = supabase.table("customers").select("id, cust_code, name, phone").order("name").execute()
        custs = cust_res.data or []
        if not custs:
            st.warning("⚠️ ไม่พบข้อมูลลูกค้า โปรดลงทะเบียนลูกค้าก่อน")
            selected_cust_id = None
        else:
            cust_map = {c["id"]: f"{c['cust_code']} - {c['name']} ({c['phone']})" for c in custs}
            selected_cust_id = st.selectbox("เลือกลูกค้า", options=list(cust_map.keys()), format_func=lambda x: cust_map[x])

    with col_right:
        st.markdown("##### 2. เลือกรถเช่า (เฉพาะรถสถานะ 'ว่าง')")
        car_res = supabase.table("cars").select("id, license_plate, brand, model, price_per_day").eq("status", "ว่าง").order("license_plate").execute()
        cars = car_res.data or []
        if not cars:
            st.error("⚠️ ไม่พบรถยนต์ที่มีสถานะ 'ว่าง' ในขณะนี้")
            selected_car_id = None
        else:
            car_map = {c["id"]: f"{c['license_plate']} - {c['brand']} {c['model']} ({c['price_per_day']} ฿/วัน)" for c in cars}
            selected_car_id = st.selectbox("เลือกรถยนต์", options=list(car_map.keys()), format_func=lambda x: car_map[x])

    if selected_cust_id and selected_car_id:
        st.markdown("---")
        st.markdown("##### 3. กำหนดวันเช่าและคำนวณค่าบริการ")
        c1, c2, c3 = st.columns(3)
        start_d = c1.date_input("วันเริ่มเช่า", value=datetime.now())
        end_d = c2.date_input("วันกำหนดคืน", value=datetime.now() + timedelta(days=1))

        car_info = next(item for item in cars if item["id"] == selected_car_id)
        rate_per_day = float(car_info["price_per_day"])

        days = max(1, (end_d - start_d).days)
        subtotal = days * rate_per_day

        c3.metric("จำนวนวันเช่า", f"{days} วัน", f"{rate_per_day:,.0f} ฿/วัน")

        c4, c5, c6 = st.columns(3)
        discount = c4.number_input("ส่วนลด (บาท)", value=0.0, step=100.0)
        deposit = c5.number_input("เงินมัดจำประกัน (บาท)", value=5000.0, step=500.0)
        grand_total = max(0.0, subtotal - discount)

        c6.metric("ยอดรวมค่าเช่าสุทธิ", f"{grand_total:,.2f} บาท", f"มัดจำ: {deposit:,.2f} ฿")

        if st.button("💾 บันทึกและออกสัญญาเช่า", type="primary"):
            check_car = supabase.table("cars").select("status").eq("id", selected_car_id).single().execute()
            if check_car.data["status"] != "ว่าง":
                st.error("❌ รถคันนี้ถูกทำสัญญาเช่าไปแล้ว")
            else:
                new_contract = {
                    "contract_no": auto_cnt_no,
                    "customer_id": selected_cust_id,
                    "car_id": selected_car_id,
                    "start_date": str(start_d),
                    "end_date": str(end_d),
                    "days": days,
                    "rental_rate": rate_per_day,
                    "subtotal": subtotal,
                    "discount": discount,
                    "deposit": deposit,
                    "grand_total": grand_total,
                    "status": "กำลังเช่า",
                    "payment_status": "รอชำระ",
                    "amount_paid": 0,
                }
                supabase.table("contracts").insert(new_contract).execute()
                supabase.table("cars").update({"status": "กำลังเช่า"}).eq("id", selected_car_id).execute()
                st.success(f"✅ บันทึกสัญญาเช่าเลขที่ {auto_cnt_no} เรียบร้อยแล้ว!")
                st.rerun()

# ====================================================
# โมดูล 4: ระบบรับคืนรถ (Vehicle Return)
# ====================================================
elif module_choice == "🔄 4. ระบบรับคืนรถ":
    st.title("🔄 4. โมดูลรับคืนรถยนต์ (Return System)")

    active_cnts = supabase.table("contracts").select("*, cars(license_plate, brand, model, mileage), customers(name)").eq("status", "กำลังเช่า").execute().data or []

    if not active_cnts:
        st.info("ℹ️ ขณะนี้ไม่มีสัญญาที่อยู่ระหว่างการเช่า (ไม่มีรถที่ต้องรับคืน)")
    else:
        cnt_options = {c["id"]: f"{c['contract_no']} | {c['cars']['license_plate']} ({c['cars']['brand']} {c['cars']['model']}) - คุณ{c['customers']['name']}" for c in active_cnts}
        selected_cnt_id = st.selectbox("เลือกสัญญาที่ต้องการรับคืนรถ", options=list(cnt_options.keys()), format_func=lambda x: cnt_options[x])

        cnt_data = next(c for c in active_cnts if c["id"] == selected_cnt_id)

        st.markdown("---")
        st.subheader(f"📋 รายละเอียดสัญญา: `{cnt_data['contract_no']}`")
        
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        col_i1.write(f"**ผู้เช่า:** คุณ{cnt_data['customers']['name']}")
        col_i2.write(f"**ทะเบียนรถ:** {cnt_data['cars']['license_plate']}")
        col_i3.write(f"**กำหนดคืน:** {cnt_data['end_date']}")
        col_i4.write(f"**เงินมัดจำรับไว้:** {float(cnt_data['deposit'] or 0):,.2f} ฿")

        with st.form("return_car_form"):
            r1, r2, r3 = st.columns(3)
            return_d = r1.date_input("วันที่รับคืนจริง", value=datetime.now())
            old_mileage = int(cnt_data['cars']['mileage'] or 0)
            mileage_in = r2.number_input("เลขไมล์เมื่อรับคืน *", min_value=old_mileage, value=old_mileage + 100)
            fuel_level = r3.selectbox("ระดับน้ำมัน", ["เต็มถัง (100%)", "3/4 ถัง", "1/2 ถัง", "1/4 ถัง", "ต้องเติมเพิ่ม"])

            r4, r5, r6 = st.columns(3)
            late_days = r4.number_input("จำนวนวันคืนเกินกำหนด", min_value=0, value=0)
            late_fine = r5.number_input("ค่าปรับคืนเกิน (บาท)", value=0.0, step=100.0)
            damage_fee = r6.number_input("ค่าเสียหาย/รอยขีดข่วน (บาท)", value=0.0, step=100.0)

            extra_costs = st.number_input("ค่าใช้จ่ายเพิ่มเติมอื่นๆ (เช่น ค่าน้ำมัน/ค่าทำความสะอาด)", value=0.0, step=100.0)
            notes = st.text_area("หมายเหตุการรับคืน")

            total_extra = late_fine + damage_fee + extra_costs
            deposit_held = float(cnt_data['deposit'] or 0)
            net_settlement = deposit_held - total_extra

            st.markdown("##### 💵 สรุปยอดเคลียร์มัดจำ:")
            if net_settlement >= 0:
                st.success(f"💰 คืนเงินมัดจำแก่ลูกค้า: **{net_settlement:,.2f} บาท** (หักค่าปรับ/เสียหาย {total_extra:,.2f} ฿)")
                refund_str = f"คืนมัดจำ {net_settlement:,.2f} ฿"
            else:
                st.error(f"⚠️ ลูกค้าต้องชำระเพิ่ม: **{abs(net_settlement):,.2f} บาท** (ค่าปรับเกินมัดจำ)")
                refund_str = f"เรียกเก็บเพิ่ม {abs(net_settlement):,.2f} ฿"

            if st.form_submit_button("✅ บันทึกรับคืนรถยนต์"):
                ret_log = {
                    "contract_id": selected_cnt_id,
                    "return_date": str(return_d),
                    "mileage_in": int(mileage_in),
                    "fuel_level": fuel_level,
                    "late_days": int(late_days),
                    "late_fine": float(late_fine),
                    "damage_fee": float(damage_fee),
                    "extra_costs": float(extra_costs),
                    "total_settlement": float(net_settlement),
                    "refund_or_due": refund_str,
                    "notes": notes,
                }
                supabase.table("returns_log").insert(ret_log).execute()
                supabase.table("contracts").update({"status": "คืนรถแล้ว"}).eq("id", selected_cnt_id).execute()
                supabase.table("cars").update({"status": "ว่าง", "mileage": int(mileage_in)}).eq("id", cnt_data["car_id"]).execute()

                st.success("🎉 บันทึกการรับคืนรถเรียบร้อย รถเปลี่ยนสถานะเป็น 'ว่าง' พร้อมเช่าต่อ!")
                st.rerun()

# ====================================================
# โมดูล 5: ระบบรับชำระเงิน (Payment System)
# ====================================================
elif module_choice == "💰 5. ระบบรับชำระเงิน":
    st.title("💰 5. โมดูลระบบรับชำระเงิน (Payments & Receipts)")

    tab1, tab2 = st.tabs(["💵 บันทึกการชำระเงิน", "🧾 ประวัติการรับชำระ"])

    with tab1:
        cnt_res = supabase.table("contracts").select("*, customers(name)").order("id", desc=True).execute().data or []
        
        if not cnt_res:
            st.info("ยังไม่มีข้อมูลสัญญาเช่าในระบบ")
        else:
            cnt_map = {c["id"]: f"{c['contract_no']} - คุณ{c['customers']['name']} (ยอดรวม: {float(c['grand_total'] or 0):,.2f} ฿ | ชำระแล้ว: {float(c['amount_paid'] or 0):,.2f} ฿)" for c in cnt_res}
            sel_cnt_id = st.selectbox("เลือกสัญญาเช่าที่ต้องการบันทึกชำระ", options=list(cnt_map.keys()), format_func=lambda x: cnt_map[x])

            curr_cnt = next(c for c in cnt_res if c["id"] == sel_cnt_id)
            due_amount = float(curr_cnt["grand_total"] or 0) - float(curr_cnt["amount_paid"] or 0)

            st.write(f"📌 **ยอดคงค้างชำระ:** `{max(0.0, due_amount):,.2f}` บาท")

            prefix_pay = datetime.now().strftime("REC-%Y%m%d-")
            pay_count = len(supabase.table("payments").select("id").execute().data or []) + 1
            rec_no = f"{prefix_pay}{pay_count:03d}"

            with st.form("pay_form"):
                p1, p2 = st.columns(2)
                p_type = p1.selectbox("ประเภทการชำระ", ["ค่าเช่ารถ", "ค่าปรับ/ค่าเสียหาย", "เงินมัดจำประกัน"])
                p_amount = p2.number_input("จำนวนเงินที่รับชำระ (บาท) *", value=max(0.0, due_amount), step=500.0)

                p3, p4 = st.columns(2)
                p_method = p3.selectbox("ช่องทางชำระเงิน", ["โอนเงิน / QR Code", "เงินสด", "บัตรเครดิต/เดบิต"])
                p_ref = p4.text_input("เลขที่อ้างอิง / สลิปโอนเงิน")

                if st.form_submit_button("💳 บันทึกใบเสร็จรับเงิน"):
                    new_pay = {
                        "receipt_no": rec_no,
                        "contract_id": sel_cnt_id,
                        "pay_type": p_type,
                        "amount": float(p_amount),
                        "method": p_method,
                        "ref_no": p_ref.strip(),
                    }
                    supabase.table("payments").insert(new_pay).execute()

                    new_paid = float(curr_cnt["amount_paid"] or 0) + float(p_amount)
                    p_status = "ชำระแล้ว" if new_paid >= float(curr_cnt["grand_total"] or 0) else "ชำระบางส่วน"
                    supabase.table("contracts").update({"amount_paid": new_paid, "payment_status": p_status}).eq("id", sel_cnt_id).execute()

                    st.success(f"✅ บันทึกชำระเงินสำเร็จ ออกใบเสร็จเลขที่ `{rec_no}`")
                    st.rerun()

    with tab2:
        pays = supabase.table("payments").select("*, contracts(contract_no)").order("id", desc=True).execute().data or []
        df_pay = pd.DataFrame(pays)
        if not df_pay.empty:
            st.dataframe(df_pay, use_container_width=True)
        else:
            st.info("ยังไม่มีประวัติการรับชำระเงิน")

# ====================================================
# โมดูล 6: ค่าใช้จ่าย & ซ่อมบำรุง (Expenses & Maintenance)
# ====================================================
elif module_choice == "🔧 6. ค่าใช้จ่าย & ซ่อมบำรุง":
    st.title("🔧 6. โมดูลบันทึกค่าใช้จ่าย & ซ่อมบำรุง")

    tab1, tab2 = st.tabs(["➕ บันทึกค่าใช้จ่าย", "📊 ประวัติค่าใช้จ่ายทั้งหมด"])

    with tab1:
        cars = supabase.table("cars").select("id, license_plate, brand, model").order("license_plate").execute().data or []
        if not cars:
            st.warning("โปรดเพิ่มข้อมูลรถยนต์ก่อนบันทึกค่าใช้จ่าย")
        else:
            car_opts = {c["id"]: f"{c['license_plate']} - {c['brand']} {c['model']}" for c in cars}
            sel_car = st.selectbox("เลือกรถยนต์", options=list(car_opts.keys()), format_func=lambda x: car_opts[x])

            with st.form("exp_form", clear_on_submit=True):
                e1, e2 = st.columns(2)
                exp_type = e1.selectbox("ประเภทค่าใช้จ่าย", ["ค่าซ่อมบำรุง/ถ่ายน้ำมันเครื่อง", "ค่าน้ำมันเชื้อเพลิง", "ค่าประกันภัย/พ.ร.บ.", "ค่าล้างรถ/ทำความสะอาด", "อื่นๆ"])
                title = e2.text_input("รายการ / รายรายละเอียด * (เช่น เช็กระยะ 50,000 กม.)")

                e3, e4 = st.columns(2)
                amount = e3.number_input("จำนวนเงิน (บาท) *", value=1500.0, step=100.0)
                vendor = e4.text_input("ศูนย์บริการ / ร้านค้า (เช่น ศูนย์บริการโตโยต้า)")

                exp_d = st.date_input("วันที่เกิดค่าใช้จ่าย", value=datetime.now())

                if st.form_submit_button("💾 บันทึกรายการค่าใช้จ่าย"):
                    if not title or amount <= 0:
                        st.error("กรุณากรอกรายการและจำนวนเงินให้ถูกต้อง")
                    else:
                        new_exp = {
                            "car_id": sel_car,
                            "exp_type": exp_type,
                            "title": title.strip(),
                            "vendor": vendor.strip(),
                            "amount": float(amount),
                            "exp_date": str(exp_d),
                        }
                        supabase.table("expenses").insert(new_exp).execute()
                        st.success("✅ บันทึกค่าใช้จ่ายเรียบร้อยแล้ว")
                        st.rerun()

    with tab2:
        exps = supabase.table("expenses").select("*, cars(license_plate, brand)").order("id", desc=True).execute().data or []
        df_exp = pd.DataFrame(exps)
        if not df_exp.empty:
            total_exp = df_exp["amount"].sum() if "amount" in df_exp.columns else 0
            st.metric("รวมค่าใช้จ่ายทั้งหมด", f"{total_exp:,.2f} บาท")
            st.dataframe(df_exp, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลค่าใช้จ่าย")

# ====================================================
# โมดูล 7: Executive Dashboard
# ====================================================
elif module_choice == "📊 7. Dashboard & รายงาน":
    st.title("📊 7. Executive Dashboard & Financial Overview")

    cars_data = supabase.table("cars").select("*").execute().data or []
    contracts_data = supabase.table("contracts").select("grand_total, amount_paid, created_at, status").execute().data or []
    expenses_data = supabase.table("expenses").select("amount, exp_date, title").execute().data or []
    payments_data = supabase.table("payments").select("*, contracts(contract_no)").order("id", desc=True).limit(5).execute().data or []

    total_cars = len(cars_data)
    rented_cars = sum(1 for c in cars_data if c.get("status") == "กำลังเช่า")
    available_cars = sum(1 for c in cars_data if c.get("status") == "ว่าง")
    maint_cars = sum(1 for c in cars_data if c.get("status") == "ซ่อมบำรุง")

    total_rev = sum(float(c.get("amount_paid") or 0) for c in contracts_data)
    total_exp = sum(float(e.get("amount") or 0) for e in expenses_data)
    net_profit = total_rev - total_exp
    profit_margin = ((net_profit / total_rev) * 100) if total_rev > 0 else 0.0

    # 1. Main Balance Banner
    st.markdown(f"""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 25px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="color: #64748b; font-size: 15px; font-weight: 500;">Net Profit Balance ❯</span>
                    <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 5px;">
                        <span style="font-size: 42px; font-weight: 800; color: #0f172a;">฿{net_profit:,.0f}</span>
                        <span style="font-size: 26px; font-weight: 600; color: #94a3b8;">.{(net_profit % 1) * 100:02.0f}</span>
                        <span style="background-color: #dcfce7; color: #166534; font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 20px; margin-left: 10px;">
                            ▲ {profit_margin:.1f}%
                        </span>
                    </div>
                </div>
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 4px 12px; font-size: 13px; color: #475569; font-weight: 500;">
                    All time ▾
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Smooth Line Chart
    dates = pd.date_range(end=datetime.now(), periods=12, freq='ME').strftime('%b')
    rev_trend = [35000, 48000, 42000, 58000, 51000, 68000, 62000, 79000, 72000, 88000, 84000, max(95000.0, total_rev)]
    
    fig1, ax1 = plt.subplots(figsize=(12, 2.2))
    fig1.patch.set_facecolor('#ffffff')
    ax1.set_facecolor('#ffffff')

    x = np.arange(len(dates))
    x_smooth = np.linspace(x.min(), x.max(), 200)
    
    try:
        from scipy.interpolate import make_interp_spline
        spl = make_interp_spline(x, rev_trend, k=3)
        y_smooth = spl(x_smooth)
    except Exception:
        y_smooth = np.interp(x_smooth, x, rev_trend)

    ax1.plot(x_smooth, y_smooth, color='#2563eb', linewidth=2.5)
    ax1.scatter(x[-2], rev_trend[-2], color='#2563eb', s=40, zorder=5)
    
    for spine in ax1.spines.values():
        spine.set_visible(False)
    ax1.get_yaxis().set_visible(False)
    ax1.tick_params(colors='#94a3b8', labelsize=10)
    plt.xticks(x, dates)
    plt.tight_layout()
    st.pyplot(fig1)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 2. Middle Row
    col_mid1, col_mid2 = st.columns([1, 1])

    with col_mid1:
        st.markdown("""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #0f172a;">สรุปสถานะรายคัน (Top Vehicles) ℹ️</h3>
                    <span style="color: #2563eb; font-size: 13px; font-weight: 600;">See all ❯</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if cars_data:
            for car in cars_data[:3]:
                plate = car.get("license_plate", "-")
                brand = f"{car.get('brand', '')} {car.get('model', '')}"
                price = float(car.get("price_per_day") or 0)
                status_color = "#16a34a" if car.get("status") == "ว่าง" else "#2563eb" if car.get("status") == "กำลังเช่า" else "#dc2626"
                
                st.markdown(f"""
                    <div style="background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">🚗</div>
                            <div>
                                <div style="font-weight: 700; color: #0f172a; font-size: 14px;">{plate}</div>
                                <div style="color: #94a3b8; font-size: 12px;">{brand}</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700; color: #0f172a; font-size: 14px;">฿{price:,.0f} <span style='font-size:10px; color:#94a3b8;'>/วัน</span></div>
                            <div style="color: {status_color}; font-size: 12px; font-weight: 600;">● {car.get('status')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีข้อมูลรถยนต์")

    with col_mid2:
        util_rate = int((rented_cars / total_cars * 100)) if total_cars > 0 else 0
        
        st.markdown("""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 22px 22px 5px 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #0f172a;">Fleet Utilization Index ℹ️</h3>
                    <span style="color: #2563eb; font-size: 13px; font-weight: 600;">See all ❯</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        fig2, ax2 = plt.subplots(figsize=(4, 2.2))
        fig2.patch.set_facecolor('#ffffff')
        ax2.set_facecolor('#ffffff')

        colors = ['#ef4444', '#f97316', '#a855f7', '#22c55e']
        values = [25, 25, 25, 25]

        ax2.pie(values, colors=colors, startangle=180, counterclock=False, 
                wedgeprops=dict(width=0.35, edgecolor='w', linewidth=2))

        ax2.text(0, -0.1, f"{util_rate}%", ha='center', va='center', fontsize=26, fontweight='bold', color='#0f172a')
        ax2.text(0, -0.38, "Rental Utilization Rate", ha='center', va='center', fontsize=9, color='#64748b', fontweight='500')

        ax2.axis('equal')
        for spine in ax2.spines.values():
            spine.set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 3. Bottom Row
    col_bot1, col_bot2 = st.columns([1, 1])

    with col_bot1:
        st.markdown("""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #0f172a;">รายการธุรกรรมล่าสุด (Recent Activities) ℹ️</h3>
                    <span style="color: #2563eb; font-size: 13px; font-weight: 600;">See all ❯</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if payments_data:
            for pay in payments_data[:3]:
                rec_no = pay.get("receipt_no", "REC-000")
                amount = float(pay.get("amount") or 0)
                pay_type = pay.get("pay_type", "ค่าเช่ารถ")
                
                st.markdown(f"""
                    <div style="background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background-color: #eff6ff; color: #2563eb; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold;">↗</div>
                            <div>
                                <div style="font-weight: 700; color: #0f172a; font-size: 13px;">{rec_no}</div>
                                <div style="color: #16a34a; font-size: 11px; font-weight: 600;">● ชำระสำเร็จ (Completed)</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700; color: #0f172a; font-size: 14px;">+{amount:,.2f} ฿</div>
                            <div style="color: #94a3b8; font-size: 11px;">{pay_type}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีประวัติการชำระเงิน")

    with col_bot2:
        st.markdown(f"""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: #0f172a;">สรุปยอดรายได้ / ค่าใช้จ่ายประจำเดือน ℹ️</h3>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #166534; font-weight: 600;">💰 รายได้รวม (Revenues)</div>
                        <div style="font-size: 22px; font-weight: 800; color: #15803d; margin-top: 5px;">฿{total_rev:,.0f}</div>
                    </div>
                    <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #991b1b; font-weight: 600;">💸 ค่าใช้จ่ายรวม (Expenses)</div>
                        <div style="font-size: 22px; font-weight: 800; color: #b91c1c; margin-top: 5px;">฿{total_exp:,.0f}</div>
                    </div>
                </div>
                <div style="margin-top: 15px; background-color: #f8fafc; border-radius: 12px; padding: 12px; text-align: center; border: 1px dashed #cbd5e1;">
                    <span style="font-size: 13px; color: #475569;">🚗 รถพร้อมใช้งาน: <b>{available_cars} คัน</b> | 🛠️ กำลังซ่อมบำรุง: <b>{maint_cars} คัน</b></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ====================================================
# โมดูล 8: ระบบแจ้งเตือน (Alerts System)
# ====================================================
elif module_choice == "🔔 8. ระบบแจ้งเตือน":
    st.title("🔔 8. โมดูลระบบแจ้งเตือน (System Alerts)")

    st.subheader("🗓️ 1. แจ้งเตือนภาษี / พ.ร.บ. / ประกันภัยใกล้อาจหมดอายุ (ภายใน 30 วัน)")
    today = datetime.now().date()
    next_30 = today + timedelta(days=30)

    cars_all = supabase.table("cars").select("*").execute().data or []
    expiring_cars = []

    for c in cars_all:
        tax_d = datetime.strptime(c["tax_exp"], "%Y-%m-%d").date() if c.get("tax_exp") else None
        ins_d = datetime.strptime(c["insurance_exp"], "%Y-%m-%d").date() if c.get("insurance_exp") else None

        if (tax_d and tax_d <= next_30) or (ins_d and ins_d <= next_30):
            expiring_cars.append({
                "ทะเบียน": c["license_plate"],
                "ยี่ห้อ-รุ่น": f"{c['brand']} {c['model']}",
                "วันหมดอายุภาษี": c["tax_exp"],
                "วันหมดอายุประกัน": c["insurance_exp"],
                "สถานะเตือน": "⚠️ ใกล้หมดอายุ"
            })

    if expiring_cars:
        st.warning(f"พบรถยนต์ที่ต้องต่อภาษี/ประกันจำนวน {len(expiring_cars)} คัน")
        st.dataframe(pd.DataFrame(expiring_cars), use_container_width=True)
    else:
        st.success("✅ ไม่พบรถยนต์ที่ภาษีหรือประกันหมดอายุใน 30 วันนี้")

    st.markdown("---")
    st.subheader("⏰ 2. แจ้งเตือนสัญญาเช่าที่เกินกำหนดคืน (Overdue)")
    overdue_cnts = supabase.table("contracts").select("*, cars(license_plate), customers(name, phone)").eq("status", "กำลังเช่า").lt("end_date", str(today)).execute().data or []

    if overdue_cnts:
        st.error(f"🚨 พบสัญญาเช่าเกินกำหนดคืนจำนวน {len(overdue_cnts)} รายการ!")
        df_overdue = pd.DataFrame([
            {
                "เลขที่สัญญา": c["contract_no"],
                "ทะเบียนรถ": c["cars"]["license_plate"],
                "ผู้เช่า": c["customers"]["name"],
                "เบอร์โทร": c["customers"]["phone"],
                "กำหนดคืน": c["end_date"],
            } for c in overdue_cnts
        ])
        st.dataframe(df_overdue, use_container_width=True)
    else:
        st.success("✅ ไม่มีรายการเช่าเกินกำหนดคืนในขณะนี้")

# ====================================================
# โมดูล 9: ศูนย์เอกสาร & PDF (Documents Center)
# ====================================================
elif module_choice == "📁 9. ศูนย์เอกสาร & PDF":
    st.title("📁 9. ศูนย์เอกสาร & พิมพ์สัญญาเช่า (Document Center)")

    cnts = supabase.table("contracts").select("*, customers(name, phone, driver_license, address), cars(license_plate, brand, model)").order("id", desc=True).execute().data or []

    if not cnts:
        st.info("ยังไม่มีข้อมูลสัญญาเช่า")
    else:
        cnt_opts = {c["id"]: f"{c['contract_no']} - คุณ{c['customers']['name']} ({c['cars']['license_plate']})" for c in cnts}
        sel_id = st.selectbox("เลือกสัญญาเช่าเพื่อแสดงเอกสาร", options=list(cnt_opts.keys()), format_func=lambda x: cnt_opts[x])

        doc = next(c for c in cnts if c["id"] == sel_id)

        st.markdown("---")
        st.markdown("### 📄 สัญญาเช่ารถยนต์ (Rental Agreement)")
        
        doc_html = f"""
        <div style="border:2.5px solid #d4af37; padding:25px; background-color:#ffffff; color:#0f172a; font-family:'Kanit', sans-serif; border-radius:12px; box-shadow:0 4px 15px rgba(212,175,55,0.15);">
            <div style="text-align:center; border-bottom:2px solid #d4af37; padding-bottom:10px; margin-bottom:15px;">
                <h2 style="color:#0f172a; margin:0; font-weight:700;">เอกสารสัญญาเช่ารถยนต์</h2>
                <p style="color:#64748b; margin:5px 0 0 0;">เลขที่สัญญา: <b style="color:#0f172a;">{doc['contract_no']}</b> | วันที่ทำสัญญา: {doc['created_at'][:10] if doc.get('created_at') else '-'}</p>
            </div>
            <p><b>ผู้เช่า:</b> คุณ{doc['customers']['name']} | <b>เบอร์โทรศัพท์:</b> {doc['customers']['phone']}</p>
            <p><b>เลขที่ใบขับขี่:</b> {doc['customers']['driver_license']} | <b>ที่อยู่:</b> {doc['customers']['address']}</p>
            <hr style="border:0.5px solid #e2e8f0;"/>
            <p><b>ข้อมูลรถยนต์ที่เช่า:</b> ทะเบียน {doc['cars']['license_plate']} ({doc['cars']['brand']} {doc['cars']['model']})</p>
            <p><b>ระยะเวลาเช่า:</b> ตั้งแต่วันที่ {doc['start_date']} ถึงวันที่ {doc['end_date']} (รวม {doc['days']} วัน)</p>
            <p><b>อัตราค่าเช่า:</b> {float(doc['rental_rate']):,.2f} บาท/วัน | <b>เงินมัดจำประกัน:</b> {float(doc['deposit']):,.2f} บาท</p>
            <p><b>ยอดรวมค่าเช่าสุทธิ:</b> <span style="font-size:20px; font-weight:bold; color:#1e3a8a;">{float(doc['grand_total']):,.2f} บาท</span></p>
            <br/><br/>
            <table width="100%" style="text-align:center; margin-top:30px;">
                <tr>
                    <td>ลงชื่อ...................................................ผู้เช่า<br/>(คุณ{doc['customers']['name']})</td>
                    <td>ลงชื่อ...................................................ผู้ให้เช่า<br/>(เจ้าหน้าที่ผู้รับเรื่อง)</td>
                </tr>
            </table>
        </div>
        """
        st.components.v1.html(doc_html, height=480, scrolling=True)
        st.info("💡 สามารถกด `Ctrl + P` เพื่อพิมพ์หรือบันทึกเอกสารสัญญานี้เป็นไฟล์ PDF ได้ทันที")