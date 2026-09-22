import os
import sqlite3
import webbrowser
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ====================================================
# 0. การตั้งค่าหน้าเว็บ & โฟลเดอร์เก็บเอกสาร
# ====================================================
st.set_page_config(
    page_title="ระบบบริหารจัดการรถเช่าส่วนกลาง (Car Rental ERP)",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====================================================
# ระบบเข้าสู่ระบบ (Authentication System)
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
    st.title("🔐 เข้าสู่ระบบ Car Rental ERP")
    st.caption("กรุณากรอกชื่อผู้ใช้และรหัสผ่านเพื่อเข้าใช้งาน")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 ชื่อผู้ใช้งาน (Username)")
            password = st.text_input("🔑 รหัสผ่าน (Password)", type="password")
            submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
            
            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success("✅ เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# ตรวจสอบว่าถ้ายังไม่ได้ล็อกอิน ให้แสดงหน้า Login แล้วหยุดรันส่วนอื่น
if not st.session_state["logged_in"]:
    login_page()
    st.stop()

DOCS_DIR = os.path.abspath("documents")
os.makedirs(DOCS_DIR, exist_ok=True)


# ====================================================
# 1. ระบบจัดการฐานข้อมูล (Database Management)
# ====================================================
def get_db_connection():
  conn = sqlite3.connect("car_rental_erp.db", check_same_thread=False)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_db_connection()
  cursor = conn.cursor()

  # 1. ตารางรถยนต์
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT UNIQUE, brand TEXT, model TEXT, year INTEGER, color TEXT,
            car_type TEXT DEFAULT 'รย.1', price_per_day REAL DEFAULT 1200, mileage INTEGER DEFAULT 0,
            insurance_exp TEXT, tax_exp TEXT, status TEXT DEFAULT 'ว่าง'
        )
    """)

  # 2. ตารางลูกค้า
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_code TEXT UNIQUE, name TEXT, phone TEXT, address TEXT,
            email TEXT, driver_license TEXT, license_exp TEXT
        )
    """)

  # 3. ตารางสัญญาเช่า
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_no TEXT UNIQUE, customer_id INTEGER, car_id INTEGER,
            start_date TEXT, end_date TEXT, days INTEGER, rental_rate REAL,
            subtotal REAL, discount REAL DEFAULT 0, deposit REAL DEFAULT 5000, grand_total REAL,
            status TEXT DEFAULT 'กำลังเช่า', payment_status TEXT DEFAULT 'รอชำระ',
            amount_paid REAL DEFAULT 0, created_at TEXT
        )
    """)

  # 4. ตารางประวัติการรับคืนรถ
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS returns_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER, return_date TEXT, mileage_in INTEGER,
            fuel_level TEXT, late_days INTEGER DEFAULT 0, late_fine REAL DEFAULT 0,
            damage_fee REAL DEFAULT 0, extra_costs REAL DEFAULT 0, total_settlement REAL,
            refund_or_due TEXT, notes TEXT
        )
    """)

  # 5. ตารางการชำระเงิน
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT UNIQUE, contract_id INTEGER, pay_type TEXT DEFAULT 'ค่าเช่ารถ',
            amount REAL, pay_date TEXT, method TEXT DEFAULT 'โอนเงิน / QR Code', ref_no TEXT DEFAULT ''
        )
    """)

  # 6. ตารางค่าใช้จ่ายและซ่อมบำรุง
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER, exp_type TEXT DEFAULT 'ค่าซ่อมบำรุง', title TEXT,
            vendor TEXT DEFAULT '', amount REAL, exp_date TEXT
        )
    """)

  # เพิ่มข้อมูลตัวอย่างเริ่มต้นหากยังไม่มีข้อมูล
  cursor.execute("SELECT COUNT(*) FROM cars")
  if cursor.fetchone()[0] == 0:
    sample_cars = [
        (
            "7ขจ 1099",
            "GWM",
            "Tank 300 Ultra",
            2023,
            "เทา",
            "รย.1 (เก๋ง/SUV)",
            2600,
            15000,
            "2026-10-15",
            "2026-10-15",
            "ว่าง",
        ),
        (
            "กก 1234",
            "Toyota",
            "Fortuner 2.8 V",
            2023,
            "ขาว",
            "รย.1 (เก๋ง/SUV)",
            1800,
            28000,
            "2026-05-20",
            "2026-05-20",
            "ว่าง",
        ),
        (
            "3ขก 8899",
            "Honda",
            "Civic FE 1.5 Turbo",
            2024,
            "ดำ",
            "รย.1 (เก๋ง/SUV)",
            1500,
            8500,
            "2026-12-10",
            "2026-12-10",
            "ว่าง",
        ),
        (
            "1กข 4567",
            "Toyota",
            "Yaris Ativ 1.2",
            2023,
            "แดง",
            "รย.1 (เก๋ง/SUV)",
            900,
            32000,
            "2026-08-05",
            "2026-08-05",
            "ว่าง",
        ),
        (
            "2กง 3344",
            "Isuzu",
            "D-Max Cab-4 3.0",
            2022,
            "บรอนซ์",
            "รย.2 (กระบะ)",
            1200,
            45000,
            "2026-04-12",
            "2026-04-12",
            "ว่าง",
        ),
    ]
    cursor.executemany(
        """INSERT INTO cars (license_plate, brand, model, year, color, car_type, price_per_day, mileage, insurance_exp, tax_exp, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        sample_cars,
    )

  cursor.execute("SELECT COUNT(*) FROM customers")
  if cursor.fetchone()[0] == 0:
    sample_customers = [
        (
            "CUST-001",
            "คุณอนันต์ สุขสวัสดิ์",
            "0812345678",
            "123/45 ถ.สุขุมวิท กรุงเทพฯ",
            "anan@email.com",
            "DL-998877",
            "2028-05-12",
        ),
        (
            "CUST-002",
            "Mr. John Smith",
            "0898765432",
            "88/12 คอนโดสุขุมวิท 24 กรุงเทพฯ",
            "john.smith@email.com",
            "DL-US-44321",
            "2027-11-20",
        ),
        (
            "CUST-003",
            "คุณจิราพร วงศ์สว่าง",
            "0865554321",
            "45/6 หมู่ 3 ต.บางกระสอ นนทบุรี",
            "jiraporn@email.com",
            "DL-554433",
            "2029-03-08",
        ),
    ]
    cursor.executemany(
        """INSERT INTO customers (cust_code, name, phone, address, email, driver_license, license_exp)
           VALUES (?,?,?,?,?,?,?)""",
        sample_customers,
    )

  conn.commit()
  conn.close()


init_db()


# ====================================================
# ฟังก์ชันช่วยเหลือ (Helper Functions)
# ====================================================
def format_date_th(date_str):
  if not date_str:
    return "-"
  try:
    parts = str(date_str).split("-")
    if len(parts) == 3:
      y, m, d = int(parts[0]), parts[1], parts[2]
      return f"{d}/{m}/{y + 543}"
  except Exception:
    pass
  return str(date_str)


# ====================================================
# เมนูหลักประจำแอปพลิเคชัน (Sidebar Navigation)
# ====================================================
st.sidebar.title("🚗 CAR RENTAL ERP")
st.sidebar.caption("ระบบบริหารจัดการรถเช่าส่วนกลาง")

# แสดงชื่อผู้ใช้งานและปุ่ม Logout ที่ Sidebar
st.sidebar.markdown(f"👤 ผู้ใช้งาน: **{st.session_state['username']}**")
if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()
st.sidebar.markdown("---")

module_choice = st.sidebar.radio(
    "📌 เลือกโมดูลการทำงาน",
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
)

conn = get_db_connection()

# ====================================================
# โมดูล 1: จัดการข้อมูลรถ (Car Management)
# ====================================================
if module_choice == "🚙 1. จัดการข้อมูลรถ":
  st.header("🚙 1. โมดูลจัดการข้อมูลรถยนต์")

  tab1, tab2, tab3 = st.tabs(
      ["📋 รายการรถทั้งหมด", "➕ เพิ่มรถยนต์ใหม่", "✏️ แก้ไข/ระงับใช้งานรถ"]
  )

  with tab1:
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
      search_plate = st.text_input("🔍 ค้นหาทะเบียน / ยี่ห้อ / รุ่น")
    with col_s2:
      status_filter = st.selectbox(
          "กรองตามสถานะ",
          ["ทั้งหมด", "ว่าง", "กำลังเช่า", "ซ่อมบำรุง", "ระงับใช้งาน"],
      )

    query = "SELECT * FROM cars WHERE 1=1"
    params = []
    if search_plate:
      query += (
          " AND (license_plate LIKE ? OR brand LIKE ? OR model LIKE ?)"
      )
      params.extend(
          [f"%{search_plate}%", f"%{search_plate}%", f"%{search_plate}%"]
      )
    if status_filter != "ทั้งหมด":
      query += " AND status = ?"
      params.append(status_filter)
    query += " ORDER BY id DESC"

    df_cars = pd.read_sql_query(query, conn, params=params)
    st.dataframe(df_cars, use_container_width=True)

  with tab2:
    st.subheader("➕ เพิ่มรถยนต์ใหม่เข้าสู่ระบบ")
    with st.form("add_car_form", clear_on_submit=True):
      c1, c2, c3 = st.columns(3)
      plate = c1.text_input("ทะเบียนรถ * (เช่น 7ขจ 1099)")
      brand = c2.text_input("ยี่ห้อ * (เช่น Toyota, GWM)")
      model = c3.text_input("รุ่นรถ * (เช่น Fortuner, Tank 300)")

      c4, c5, c6 = st.columns(3)
      year = c4.number_input(
          "ปี ค.ศ. *", min_value=2000, max_value=2030, value=2024
      )
      color = c5.text_input("สีรถ", value="ขาว")
      car_type = c6.selectbox(
          "ประเภทรถยนต์",
          [
              "รย.1 (เก๋ง/SUV)",
              "รย.2 (กระบะ)",
              "รย.3 (ตู้)",
              "EV รถยนต์ไฟฟ้า",
          ],
      )

      c7, c8, c9 = st.columns(3)
      price = c7.number_input("ราคาเช่ารายวัน (บาท) *", value=1200.0, step=100.0)
      mileage = c8.number_input("เลขไมล์ปัจจุบัน", value=10000, step=500)
      status = c9.selectbox(
          "สถานะเริ่มต้น", ["ว่าง", "ซ่อมบำรุง", "ระงับใช้งาน"]
      )

      c10, c11 = st.columns(2)
      ins_exp = c10.date_input("วันหมดอายุประกันภัย", value=datetime.now())
      tax_exp = c11.date_input("วันหมดอายุภาษี/พ.ร.บ.", value=datetime.now())

      submitted = st.form_submit_button("💾 บันทึกรถยนต์ใหม่")
      if submitted:
        if not plate or not brand or not model:
          st.error("กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบถ้วน")
        else:
          # ตรวจสอบทะเบียนรถซ้ำ
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id FROM cars WHERE license_plate = ?", (plate.strip(),)
          )
          if cursor.fetchone():
            st.error(f"❌ ทะเบียนรถ '{plate}' มีในระบบแล้ว ไม่สามารถเพิ่มซ้ำได้")
          else:
            cursor.execute(
                """INSERT INTO cars (license_plate, brand, model, year, color, car_type, price_per_day, mileage, insurance_exp, tax_exp, status)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    plate.strip(),
                    brand.strip(),
                    model.strip(),
                    year,
                    color.strip(),
                    car_type,
                    price,
                    mileage,
                    str(ins_exp),
                    str(tax_exp),
                    status,
                ),
            )
            conn.commit()
            st.success(f"✅ บันทึกรถยนต์ทะเบียน {plate} เรียบร้อยแล้ว")
            st.rerun()

  with tab3:
    st.subheader("✏️ แก้ไขข้อมูลรถ หรือ ปรับสถานะ")
    cars_df = pd.read_sql_query(
        "SELECT id, license_plate || ' - ' || brand || ' ' || model as name"
        " FROM cars",
        conn,
    )
    if not cars_df.empty:
      car_options = dict(zip(cars_df["id"], cars_df["name"]))
      selected_car_id = st.selectbox(
          "เลือกรถที่ต้องการแก้ไข",
          options=list(car_options.keys()),
          format_func=lambda x: car_options[x],
      )

      cursor = conn.cursor()
      cursor.execute("SELECT * FROM cars WHERE id = ?", (selected_car_id,))
      car_data = cursor.fetchone()

      if car_data:
        with st.form("edit_car_form"):
          e1, e2, e3 = st.columns(3)
          e_plate = e1.text_input("ทะเบียนรถ", value=car_data["license_plate"])
          e_brand = e2.text_input("ยี่ห้อ", value=car_data["brand"])
          e_model = e3.text_input("รุ่น", value=car_data["model"])

          e4, e5, e6 = st.columns(3)
          e_price = e4.number_input(
              "ราคาเช่ารายวัน", value=float(car_data["price_per_day"])
          )
          e_mileage = e5.number_input("เลขไมล์", value=int(car_data["mileage"]))
          e_status = e6.selectbox(
              "สถานะรถ",
              ["ว่าง", "กำลังเช่า", "ซ่อมบำรุง", "ระงับใช้งาน"],
              index=["ว่าง", "กำลังเช่า", "ซ่อมบำรุง", "ระงับใช้งาน"].index(
                  car_data["status"]
              ),
          )

          if st.form_submit_button("💾 บันทึกการแก้ไข"):
            cursor.execute(
                """UPDATE cars SET license_plate=?, brand=?, model=?, price_per_day=?, mileage=?, status=? WHERE id=?""",
                (
                    e_plate,
                    e_brand,
                    e_model,
                    e_price,
                    e_mileage,
                    e_status,
                    selected_car_id,
                ),
            )
            conn.commit()
            st.success("✅ อัปเดตข้อมูลเรียบร้อยแล้ว")
            st.rerun()

# ====================================================
# โมดูล 2: จัดการข้อมูลลูกค้า (Customer Management)
# ====================================================
elif module_choice == "👥 2. จัดการข้อมูลลูกค้า":
  st.header("👥 2. โมดูลจัดการข้อมูลลูกค้า (Customer Management)")

  tab1, tab2 = st.tabs(["📋 รายชื่อลูกค้า", "➕ เพิ่มลูกค้าใหม่"])

  with tab1:
    search_cust = st.text_input(
        "🔍 ค้นหาลูกค้า (ชื่อ / เบอร์โทร / เลขใบขับขี่)"
    )
    q = "SELECT * FROM customers WHERE 1=1"
    p = []
    if search_cust:
      q += " AND (name LIKE ? OR phone LIKE ? OR driver_license LIKE ?)"
      p.extend([f"%{search_cust}%", f"%{search_cust}%", f"%{search_cust}%"])
    q += " ORDER BY id DESC"
    st.dataframe(pd.read_sql_query(q, conn, params=p), use_container_width=True)

  with tab2:
    st.subheader("➕ ลงทะเบียนลูกค้าใหม่")
    # สุ่ม/สร้างรหัสลูกค้าอัตโนมัติ
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM customers")
    max_id = cursor.fetchone()[0] or 0
    auto_code = f"CUST-{max_id + 1:03d}"

    st.info(f"🆔 รหัสลูกค้าอัตโนมัติ: **{auto_code}**")

    with st.form("add_cust_form", clear_on_submit=True):
      col1, col2 = st.columns(2)
      c_name = col1.text_input("ชื่อ-นามสกุล *")
      c_phone = col2.text_input("เบอร์โทรศัพท์ *")

      col3, col4 = st.columns(2)
      c_email = col3.text_input("อีเมล")
      c_dl = col4.text_input("เลขที่ใบขับขี่ *")

      c_exp = st.date_input(
          "วันหมดอายุใบขับขี่", value=datetime.now() + timedelta(days=365)
      )
      c_address = st.text_area("ที่อยู่ตามบัตร/ที่อยู่ติดต่อ")

      if st.form_submit_button("💾 บันทึกข้อมูลลูกค้า"):
        if not c_name or not c_phone or not c_dl:
          st.error("กรุณากรอก ชื่อ, เบอร์โทร และ เลขใบขับขี่")
        else:
          cursor.execute(
              """INSERT INTO customers (cust_code, name, phone, address, email, driver_license, license_exp)
                             VALUES (?,?,?,?,?,?,?)""",
              (
                  auto_code,
                  c_name.strip(),
                  c_phone.strip(),
                  c_address.strip(),
                  c_email.strip(),
                  c_dl.strip(),
                  str(c_exp),
              ),
          )
          conn.commit()
          st.success(f"✅ บันทึกลูกค้า {c_name} เรียบร้อยแล้ว")
          st.rerun()

# ====================================================
# โมดูล 3: ทำสัญญาเช่ารถ (Rental Contract)
# ====================================================
elif module_choice == "📄 3. ทำสัญญาเช่ารถ":
  st.header("📄 3. โมดูลทำสัญญาเช่ารถ (Rental Agreement)")

  # สร้างเลขสัญญาอัตโนมัติ CNT-YYYYMMDD-XX
  prefix = datetime.now().strftime("CNT-%Y%m%d-")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT COUNT(*) FROM contracts WHERE contract_no LIKE ?", (f"{prefix}%",)
  )
  cnt_seq = cursor.fetchone()[0] + 1
  auto_cnt_no = f"{prefix}{cnt_seq:02d}"

  st.subheader(f"📝 สร้างสัญญาเช่าใหม่: `{auto_cnt_no}`")

  col_left, col_right = st.columns(2)

  with col_left:
    st.markdown("##### 1. เลือกลูกค้า")
    cust_df = pd.read_sql_query(
        "SELECT id, cust_code || ' - ' || name || ' (' || phone || ')' as label"
        " FROM customers ORDER BY name",
        conn,
    )
    if cust_df.empty:
      st.warning("โปรดเพิ่มข้อมูลลูกค้าก่อนทำสัญญา")
      selected_cust_id = None
    else:
      cust_map = dict(zip(cust_df["id"], cust_df["label"]))
      selected_cust_id = st.selectbox(
          "เลือกลูกค้า",
          options=list(cust_map.keys()),
          format_func=lambda x: cust_map[x],
      )

  with col_right:
    st.markdown("##### 2. เลือกรถเช่า (เฉพาะรถสถานะ 'ว่าง')")
    car_df = pd.read_sql_query(
        "SELECT id, license_plate || ' - ' || brand || ' ' || model || ' (' ||"
        " price_per_day || ' ฿/วัน)' as label, price_per_day FROM cars WHERE"
        " status = 'ว่าง' ORDER BY license_plate",
        conn,
    )
    if car_df.empty:
      st.error("⚠️ ไม่พบรถยนต์ที่มีสถานะ 'ว่าง' ในขณะนี้")
      selected_car_id = None
    else:
      car_map = dict(zip(car_df["id"], car_df["label"]))
      selected_car_id = st.selectbox(
          "เลือกรถยนต์",
          options=list(car_map.keys()),
          format_func=lambda x: car_map[x],
      )

  if selected_cust_id and selected_car_id:
    st.markdown("---")
    st.markdown("##### 3. กำหนดวันเช่าและคำนวณค่าบริการ")
    c1, c2, c3 = st.columns(3)
    start_d = c1.date_input("วันเริ่มเช่า", value=datetime.now())
    end_d = c2.date_input("วันกำหนดคืน", value=datetime.now() + timedelta(days=1))

    # ดึงราคาเช่าต่อวัน
    rate_per_day = float(
        car_df[car_df["id"] == selected_car_id]["price_per_day"].values[0]
    )

    days = max(1, (end_d - start_d).days)
    subtotal = days * rate_per_day

    c3.metric("จำนวนวันเช่า", f"{days} วัน", f"{rate_per_day:,.0f} ฿/วัน")

    c4, c5, c6 = st.columns(3)
    discount = c4.number_input("ส่วนลด (บาท)", value=0.0, step=100.0)
    deposit = c5.number_input("เงินมัดจำประกัน (บาท)", value=5000.0, step=500.0)
    grand_total = max(0.0, subtotal - discount)

    c6.metric(
        "ยอดรวมค่าเช่าสุทธิ",
        f"{grand_total:,.2f} บาท",
        f"มัดจำ: {deposit:,.2f} ฿",
    )

    if st.button("💾 บันทึกและออกสัญญาเช่า", type="primary"):
      # ตรวจสอบซ้ำว่ารถว่างจริง
      cursor.execute(
          "SELECT status FROM cars WHERE id = ?", (selected_car_id,)
      )
      curr_status = cursor.fetchone()[0]
      if curr_status != "ว่าง":
        st.error("❌ รถคันนี้ถูกทำสัญญาเช่าไปแล้ว ไม่สามารถเช่าซ้ำได้")
      else:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            """INSERT INTO contracts (contract_no, customer_id, car_id, start_date, end_date, days, rental_rate, subtotal, discount, deposit, grand_total, status, payment_status, created_at)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?, 'กำลังเช่า', 'รอชำระ', ?)""",
            (
                auto_cnt_no,
                selected_cust_id,
                selected_car_id,
                str(start_d),
                str(end_d),
                days,
                rate_per_day,
                subtotal,
                discount,
                deposit,
                grand_total,
                now_str,
            ),
        )

        # ปรับสถานะรถเป็น 'กำลังเช่า'
        cursor.execute(
            "UPDATE cars SET status = 'กำลังเช่า' WHERE id = ?",
            (selected_car_id,),
        )
        conn.commit()
        st.success(f"✅ บันทึกสัญญาเช่าเลขที่ {auto_cnt_no} เรียบร้อยแล้ว!")
        st.rerun()

# ====================================================
# โมดูล 4: ระบบรับคืนรถ (Car Return)
# ====================================================
elif module_choice == "🔄 4. ระบบรับคืนรถ":
  st.header("🔄 4. โมดูลรับคืนรถ (Car Return Management)")

  active_contracts = pd.read_sql_query(
      """
        SELECT c.id, c.contract_no, cu.name as cust_name, ca.brand || ' ' || ca.model || ' (' || ca.license_plate || ')' as car_info,
               c.end_date, c.deposit, c.grand_total, c.amount_paid, ca.id as car_id, ca.mileage
        FROM contracts c
        JOIN customers cu ON c.customer_id = cu.id
        JOIN cars ca ON c.car_id = ca.id
        WHERE c.status = 'กำลังเช่า'
    """,
      conn,
  )

  if active_contracts.empty:
    st.info("👍 ไม่มีรถที่อยู่ระหว่างการเช่าในขณะนี้")
  else:
    st.subheader("📋 รายการสัญญาที่อยู่ระหว่างการเช่า")
    st.dataframe(
        active_contracts[[
            "contract_no",
            "cust_name",
            "car_info",
            "end_date",
            "deposit",
            "grand_total",
        ]],
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("📥 บันทึกรับคืนรถ")

    cnt_map = dict(
        zip(
            active_contracts["id"],
            active_contracts["contract_no"]
            + " - "
            + active_contracts["cust_name"],
        )
    )
    sel_cnt_id = st.selectbox(
        "เลือกสัญญาที่ต้องการรับคืน",
        options=list(cnt_map.keys()),
        format_func=lambda x: cnt_map[x],
    )

    cnt_row = active_contracts[
        active_contracts["id"] == sel_cnt_id
    ].iloc[0]

    col1, col2, col3 = st.columns(3)
    ret_date = col1.date_input("วันรับคืนจริง", value=datetime.now())
    mileage_in = col2.number_input(
        "เลขไมล์ ณ วันคืน",
        value=int(cnt_row["mileage"]) + 100,
        min_value=int(cnt_row["mileage"]),
    )
    fuel_level = col3.selectbox(
        "ระดับน้ำมัน",
        ["เต็มถัง (100%)", "3/4 ถัง", "1/2 ถัง", "1/4 ถัง", "ไฟเตือนโชว์"],
    )

    # คำนวณวันคืนเกินกำหนด (Late Days)
    due_d = datetime.strptime(cnt_row["end_date"], "%Y-%m-%d").date()
    late_days = max(0, (ret_date - due_d).days)

    col4, col5, col6 = st.columns(3)
    late_fine = col4.number_input(
        f"ค่าปรับคืนล่าช้า ({late_days} วัน)",
        value=float(late_days * 500),
        step=100.0,
    )
    damage_fee = col5.number_input("ค่าเสียหาย / รอยขีดข่วน", value=0.0, step=100.0)
    extra_costs = col6.number_input(
        "ค่าใช้จ่ายอื่นๆ (ล้างรถ/น้ำมัน)", value=0.0, step=100.0
    )

    # รวมยอดค่าปรับและค่าเสียหาย
    total_extra = late_fine + damage_fee + extra_costs
    deposit_amt = float(cnt_row["deposit"])
    settlement = deposit_amt - total_extra

    st.markdown("##### 💵 สรุปยอดเงินมัดจำและการคืนเงิน")
    if settlement >= 0:
      st.success(
          f"💰 คืนเงินมัดจำแก่ลูกค้า: **{settlement:,.2f} บาท** (หักค่าใช้จ่าย"
          f" {total_extra:,.2f} ฿ จากมัดจำ {deposit_amt:,.2f} ฿)"
      )
      refund_txt = f"คืนมัดจำสุทธิ {settlement:,.2f} ฿"
    else:
      st.error(
          f"⚠️ ลูกค้าต้องชำระเพิ่ม: **{abs(settlement):,.2f} บาท**"
          f" (หักมัดจำแล้วไม่พอเคลียร์ค่าใช้จ่าย {total_extra:,.2f} ฿)"
      )
      refund_txt = f"ค้างชำระเพิ่ม {abs(settlement):,.2f} ฿"

    next_car_status = st.selectbox(
        "ปรับสถานะรถหลังรับคืน", ["ว่าง", "ซ่อมบำรุง", "ระงับใช้งาน"]
    )
    ret_notes = st.text_area("หมายเหตุการตรวจรับรถ")

    if st.button("💾 ยืนยันบันทึกรับคืนรถและปิดสัญญา", type="primary"):
      cursor = conn.cursor()
      # 1. บันทึกลง returns_log
      cursor.execute(
          """INSERT INTO returns_log (contract_id, return_date, mileage_in, fuel_level, late_days, late_fine, damage_fee, extra_costs, total_settlement, refund_or_due, notes)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
          (
              sel_cnt_id,
              str(ret_date),
              mileage_in,
              fuel_level,
              late_days,
              late_fine,
              damage_fee,
              extra_costs,
              settlement,
              refund_txt,
              ret_notes,
          ),
      )

      # 2. ปิดสัญญาเช่า
      cursor.execute(
          "UPDATE contracts SET status = 'ปิดสัญญา' WHERE id = ?", (sel_cnt_id,)
      )

      # 3. อัปเดตไมล์และสถานะรถ
      cursor.execute(
          "UPDATE cars SET status = ?, mileage = ? WHERE id = ?",
          (next_car_status, mileage_in, cnt_row["car_id"]),
      )

      conn.commit()
      st.success("✅ บันทึกรับคืนรถและอัปเดตสถานะเรียบร้อยแล้ว!")
      st.rerun()

# ====================================================
# โมดูล 5: ระบบรับชำระเงิน (Payment Management)
# ====================================================
elif module_choice == "💰 5. ระบบรับชำระเงิน":
  st.header("💰 5. โมดูลรับชำระเงิน & ออกใบเสร็จ")

  tab1, tab2 = st.tabs(["💳 บันทึกรับชำระเงินใหม่", "📜 ประวัติการรับเงิน"])

  with tab1:
    # เลือกสัญญาเช่า
    cnt_df = pd.read_sql_query(
        """
            SELECT c.id, c.contract_no || ' - ' || cu.name || ' (คงเหลือ: ' || (c.grand_total - c.amount_paid) || ' ฿)' as label,
                   c.grand_total, c.amount_paid
            FROM contracts c JOIN customers cu ON c.customer_id = cu.id
            ORDER BY c.id DESC
        """,
        conn,
    )

    if cnt_df.empty:
      st.info("ไม่มีสัญญาเช่าในระบบ")
    else:
      cnt_map = dict(zip(cnt_df["id"], cnt_df["label"]))
      sel_cnt_id = st.selectbox(
          "เลือกสัญญาเช่าที่ต้องการชำระเงิน",
          options=list(cnt_map.keys()),
          format_func=lambda x: cnt_map[x],
      )

      cnt_info = cnt_df[cnt_df["id"] == sel_cnt_id].iloc[0]
      due_amt = max(0.0, float(cnt_info["grand_total"] - cnt_info["amount_paid"]))

      st.info(
          f"ยอดรวมสัญญา: **{cnt_info['grand_total']:,.2f} ฿** | ชำระแล้ว:"
          f" **{cnt_info['amount_paid']:,.2f} ฿** | ยอดคงเหลือ:"
          f" **{due_amt:,.2f} ฿**"
      )

      # สร้างเลขใบเสร็จ REC-YYYYMMDD-XX
      rec_prefix = datetime.now().strftime("REC-%Y%m%d-")
      cursor = conn.cursor()
      cursor.execute(
          "SELECT COUNT(*) FROM payments WHERE receipt_no LIKE ?",
          (f"{rec_prefix}%",),
      )
      rec_seq = cursor.fetchone()[0] + 1
      auto_rec_no = f"{rec_prefix}{rec_seq:02d}"

      with st.form("pay_form"):
        p1, p2 = st.columns(2)
        rec_no = p1.text_input("เลขที่ใบเสร็จรับเงิน", value=auto_rec_no)
        pay_type = p2.selectbox(
            "ประเภทการรับเงิน",
            ["ค่าเช่ารถ", "เงินมัดจำ", "ชำระยอดค้าง", "ค่าเสียหาย/ค่าปรับ"],
        )

        p3, p4 = st.columns(2)
        pay_amt = p3.number_input(
            "จำนวนเงินที่ชำระ (บาท)", value=due_amt, step=500.0
        )
        pay_method = p4.selectbox(
            "วิธีชำระเงิน",
            ["โอนเงิน / QR Code", "เงินสด", "บัตรเครดิต", "เช็ค"],
        )

        ref_no = st.text_input(
            "เลขอ้างอิง / เลขสลิปการโอนเงิน", placeholder="เช่น Slip#123456"
        )

        if st.form_submit_button("💾 บันทึกการรับชำระเงิน"):
          if pay_amt <= 0:
            st.error("จำนวนเงินต้องมากกว่า 0")
          else:
            now_dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute(
                """INSERT INTO payments (receipt_no, contract_id, pay_type, amount, pay_date, method, ref_no)
                               VALUES (?,?,?,?,?,?,?)""",
                (
                    rec_no,
                    sel_cnt_id,
                    pay_type,
                    pay_amt,
                    now_dt,
                    pay_method,
                    ref_no,
                ),
            )

            # อัปเดตยอดชำระแล้วในสัญญา
            new_paid = float(cnt_info["amount_paid"]) + pay_amt
            tot_val = float(cnt_info["grand_total"])

            if new_paid >= tot_val:
              p_stat = "ชำระครบ"
            elif new_paid > 0:
              p_stat = "ชำระบางส่วน"
            else:
              p_stat = "รอชำระ"

            cursor.execute(
                "UPDATE contracts SET amount_paid = ?, payment_status = ?"
                " WHERE id = ?",
                (new_paid, p_stat, sel_cnt_id),
            )
            conn.commit()
            st.success(
                f"✅ บันทึกการรับชำระเงิน {rec_no} ยอด {pay_amt:,.2f} ฿"
                " เรียบร้อยแล้ว"
            )
            st.rerun()

  with tab2:
    st.dataframe(
        pd.read_sql_query(
            """
            SELECT p.receipt_no, c.contract_no, cu.name as cust_name, p.pay_type, p.amount, p.method, p.ref_no, p.pay_date
            FROM payments p
            JOIN contracts c ON p.contract_id = c.id
            JOIN customers cu ON c.customer_id = cu.id
            ORDER BY p.id DESC
        """,
            conn,
        ),
        use_container_width=True,
    )

# ====================================================
# โมดูล 6: ค่าใช้จ่ายและซ่อมบำรุงรถ (Expenses & Maintenance)
# ====================================================
elif module_choice == "🔧 6. ค่าใช้จ่าย & ซ่อมบำรุง":
  st.header("🔧 6. โมดูลค่าใช้จ่ายและซ่อมบำรุงรถ (Expenses)")

  tab1, tab2 = st.tabs(["🔧 บันทึกค่าใช้จ่ายใหม่", "📋 ประวัติค่าใช้จ่ายทั้งหมด"])

  cars_df = pd.read_sql_query(
      "SELECT id, license_plate || ' - ' || brand || ' ' || model as name FROM"
      " cars",
      conn,
  )

  with tab1:
    if cars_df.empty:
      st.warning("ไม่มีข้อมูลรถในระบบ")
    else:
      car_opts = dict(zip(cars_df["id"], cars_df["name"]))
      car_opts[0] = "ค่าใช้จ่ายส่วนกลาง / ไม่ระบุรถ"

      with st.form("exp_form", clear_on_submit=True):
        sel_car = st.selectbox(
            "เลือกรถยนต์",
            options=list(car_opts.keys()),
            format_func=lambda x: car_opts[x],
        )

        e1, e2 = st.columns(2)
        exp_type = e1.selectbox(
            "ประเภทค่าใช้จ่าย",
            [
                "ค่าซ่อมบำรุง",
                "ค่าอะไหล่",
                "ค่ายาง",
                "ค่าประกันภัย",
                "ภาษีรถยนต์",
                "พ.ร.บ.",
                "ค่าล้างรถ / คาร์แคร์",
                "อื่นๆ",
            ],
        )
        exp_amt = e2.number_input("จำนวนเงิน (บาท) *", value=500.0, step=100.0)

        e3, e4 = st.columns(2)
        title = e3.text_input("รายการ / รายละเอียด *", placeholder="เช่น ถ่ายน้ำมันเครื่อง")
        vendor = e4.text_input("ผู้ให้บริการ / อู่ / ร้านค้า", placeholder="เช่น บีควิก สาขาบางใหญ่")

        set_suspended = st.checkbox("🔧 ปรับสถานะรถเป็น 'ซ่อมบำรุง' ทันที")

        if st.form_submit_button("💾 บันทึกค่าใช้จ่าย"):
          if exp_amt <= 0 or not title:
            st.error("กรุณากรอกรายการและจำนวนเงินให้ถูกต้อง")
          else:
            now_dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            car_id_val = None if sel_car == 0 else sel_car
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO expenses (car_id, exp_type, title, vendor, amount, exp_date)
                               VALUES (?,?,?,?,?,?)""",
                (car_id_val, exp_type, title, vendor, exp_amt, now_dt),
            )

            if set_suspended and car_id_val:
              cursor.execute(
                  "UPDATE cars SET status = 'ซ่อมบำรุง' WHERE id = ?",
                  (car_id_val,),
              )

            conn.commit()
            st.success("✅ บันทึกค่าใช้จ่ายเรียบร้อยแล้ว")
            st.rerun()

  with tab2:
    st.dataframe(
        pd.read_sql_query(
            """
            SELECT e.id, COALESCE(c.license_plate || ' (' || c.brand || ')', 'ส่วนกลาง') as car_info,
                   e.exp_type, e.title, e.vendor, e.amount, e.exp_date
            FROM expenses e LEFT JOIN cars c ON e.car_id = c.id
            ORDER BY e.id DESC
        """,
            conn,
        ),
        use_container_width=True,
    )

# ====================================================
# โมดูล 7: Dashboard และรายงานผู้บริหาร (Executive Dashboard)
# ====================================================
elif module_choice == "📊 7. Dashboard & รายงาน":
  st.header("📊 7. Executive Dashboard & รายงานผู้บริหาร")

  # 1. KPI Cards
  cursor = conn.cursor()
  cursor.execute("SELECT status, COUNT(*) FROM cars GROUP BY status")
  status_counts = dict(cursor.fetchall())

  total_cars = sum(status_counts.values())
  avail_cars = status_counts.get("ว่าง", 0)
  rented_cars = status_counts.get("กำลังเช่า", 0)
  maint_cars = status_counts.get("ซ่อมบำรุง", 0) + status_counts.get(
      "ระงับใช้งาน", 0
  )

  k1, k2, k3, k4 = st.columns(4)
  k1.metric("🚘 รถทั้งหมด", f"{total_cars} คัน")
  k2.metric("✅ รถว่างพร้อมเช่า", f"{avail_cars} คัน")
  k3.metric("🔑 อยู่ระหว่างการเช่า", f"{rented_cars} คัน")
  k4.metric("🔧 ซ่อมบำรุง/ระงับ", f"{maint_cars} คัน")

  # คำนวณรายได้/ค่าใช้จ่ายเดือนนี้
  cur_month = datetime.now().strftime("%Y-%m")
  cursor.execute(
      "SELECT COALESCE(SUM(grand_total), 0) FROM contracts WHERE start_date"
      " LIKE ?",
      (f"{cur_month}%",),
  )
  month_rev = cursor.fetchone()[0]

  cursor.execute(
      "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE exp_date LIKE ?",
      (f"{cur_month}%",),
  )
  month_exp = cursor.fetchone()[0]
  profit = month_rev - month_exp

  st.markdown("---")
  f1, f2, f3 = st.columns(3)
  f1.metric("💰 รายได้เดือนนี้", f"{month_rev:,.2f} ฿")
  f2.metric("💸 ค่าใช้จ่ายเดือนนี้", f"{month_exp:,.2f} ฿")
  f3.metric("📈 กำไรขั้นต้นเดือนนี้", f"{profit:,.2f} ฿")

  # 2. Charts
  st.markdown("---")
  col_chart1, col_chart2 = st.columns(2)

  with col_chart1:
    st.subheader("📊 เปรียบเทียบรายได้ - ค่าใช้จ่าย 12 เดือนย้อนหลัง")
    months, revs, exps = [], [], []
    for i in range(11, -1, -1):
      m_dt = datetime.now() - timedelta(days=i * 30)
      m_str = m_dt.strftime("%Y-%m")
      m_lbl = m_dt.strftime("%b %Y")
      months.append(m_lbl)

      cursor.execute(
          "SELECT COALESCE(SUM(grand_total), 0) FROM contracts WHERE start_date"
          " LIKE ?",
          (f"{m_str}%",),
      )
      revs.append(cursor.fetchone()[0])

      cursor.execute(
          "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE exp_date LIKE ?",
          (f"{m_str}%",),
      )
      exps.append(cursor.fetchone()[0])

    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    x = range(len(months))
    ax1.bar([i - 0.2 for i in x], revs, width=0.4, label="รายได้", color="#2ecc71")
    ax1.bar([i + 0.2 for i in x], exps, width=0.4, label="ค่าใช้จ่าย", color="#e74c3c")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(months, rotation=45, fontsize=8)
    ax1.legend()
    st.pyplot(fig1)

  with col_chart2:
    st.subheader("🍰 สัดส่วนสถานะรถยนต์ในสถิติปัจจุบัน")
    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    labels = ["ว่าง", "กำลังเช่า", "ซ่อมบำรุง/ระงับ"]
    sizes = [avail_cars, rented_cars, maint_cars]
    if sum(sizes) == 0:
      sizes = [1, 0, 0]
    ax2.pie(
        sizes,
        labels=labels,
        colors=["#2ecc71", "#e67e22", "#e74c3c"],
        autopct="%1.1f%%",
        startangle=140,
    )
    st.pyplot(fig2)

  # 3. Reports
  st.markdown("---")
  r_col1, r_col2 = st.columns(2)

  with r_col1:
    st.subheader("🏆 รถยนต์ที่สร้างรายได้สูงสุด (Top Revenue Cars)")
    top_cars = pd.read_sql_query(
        """
            SELECT ca.license_plate as ทะเบียน, ca.brand || ' ' || ca.model as รถยนต์, SUM(cnt.grand_total) as รายได้รวม
            FROM contracts cnt JOIN cars ca ON cnt.car_id = ca.id
            GROUP BY cnt.car_id ORDER BY รายได้รวม DESC LIMIT 5
        """,
        conn,
    )
    st.dataframe(top_cars, use_container_width=True)

  with r_col2:
    st.subheader("⚠️ รายงานลูกหนี้ & ยอดค้างชำระ (Accounts Receivable)")
    ar_df = pd.read_sql_query(
        """
            SELECT c.contract_no as เลขสัญญา, cu.name as ลูกค้า, c.grand_total as ค่าเช่ารวม, c.amount_paid as ชำระแล้ว, (c.grand_total - c.amount_paid) as ค้างชำระ
            FROM contracts c JOIN customers cu ON c.customer_id = cu.id
            WHERE (c.grand_total - c.amount_paid) > 0
        """,
        conn,
    )
    st.dataframe(ar_df, use_container_width=True)

# ====================================================
# โมดูล 8: ระบบแจ้งเตือน (Notifications & Alerts)
# ====================================================
elif module_choice == "🔔 8. ระบบแจ้งเตือน":
  st.header("🔔 8. โมดูลระบบแจ้งเตือนอัจฉริยะ")

  today = datetime.now().date()
  today_str = str(today)
  soon_3d = str(today + timedelta(days=3))
  soon_30d = str(today + timedelta(days=30))

  alert_type = st.radio(
      "เลือกประเภทการแจ้งเตือน",
      [
          "🚨 ครบกำหนดคืนวันนี้/เกินกำหนด",
          "⏳ ใกล้กำหนดคืน (1-3 วัน)",
          "🛡️ ประกัน/ภาษีใกล้หมดอายุ (30 วัน)",
          "🔧 รถซ่อมบำรุง/ระงับใช้งาน",
      ],
      horizontal=True,
  )

  if alert_type == "🚨 ครบกำหนดคืนวันนี้/เกินกำหนด":
    st.subheader("❌ รถที่เกินกำหนดคืน (Overdue)")
    overdue_df = pd.read_sql_query(
        """
            SELECT c.contract_no, cu.name as cust_name, cu.phone, ca.license_plate || ' (' || ca.brand || ')' as car_info, c.end_date
            FROM contracts c JOIN customers cu ON c.customer_id = cu.id JOIN cars ca ON c.car_id = ca.id
            WHERE c.status = 'กำลังเช่า' AND c.end_date < ?
        """,
        conn,
        params=[today_str],
    )
    st.dataframe(overdue_df, use_container_width=True)

    st.subheader("⏰ รถที่ครบกำหนดคืนวันนี้")
    today_due = pd.read_sql_query(
        """
            SELECT c.contract_no, cu.name as cust_name, cu.phone, ca.license_plate || ' (' || ca.brand || ')' as car_info, c.end_date
            FROM contracts c JOIN customers cu ON c.customer_id = cu.id JOIN cars ca ON c.car_id = ca.id
            WHERE c.status = 'กำลังเช่า' AND c.end_date = ?
        """,
        conn,
        params=[today_str],
    )
    st.dataframe(today_due, use_container_width=True)

  elif alert_type == "⏳ ใกล้กำหนดคืน (1-3 วัน)":
    st.subheader("⏳ รถที่ใกล้ครบกำหนดคืนภายใน 3 วัน")
    soon_df = pd.read_sql_query(
        """
            SELECT c.contract_no, cu.name as cust_name, cu.phone, ca.license_plate || ' (' || ca.brand || ')' as car_info, c.end_date
            FROM contracts c JOIN customers cu ON c.customer_id = cu.id JOIN cars ca ON c.car_id = ca.id
            WHERE c.status = 'กำลังเช่า' AND c.end_date > ? AND c.end_date <= ?
        """,
        conn,
        params=[today_str, soon_3d],
    )
    st.dataframe(soon_df, use_container_width=True)

  elif alert_type == "🛡️ ประกัน/ภาษีใกล้หมดอายุ (30 วัน)":
    st.subheader("🛡️ ประกันภัย/ภาษีรถยนต์ที่ใกล้หรือหมดอายุแล้ว")
    exp_df = pd.read_sql_query(
        """
            SELECT license_plate, brand, model, insurance_exp, tax_exp, status
            FROM cars
            WHERE insurance_exp <= ? OR tax_exp <= ?
        """,
        conn,
        params=[soon_30d, soon_30d],
    )
    st.dataframe(exp_df, use_container_width=True)

  elif alert_type == "🔧 รถซ่อมบำรุง/ระงับใช้งาน":
    st.subheader("🔧 รายการรถยนต์ในสถานะซ่อมบำรุงหรือระงับใช้งาน")
    maint_df = pd.read_sql_query(
        """
            SELECT license_plate, brand, model, color, mileage, status
            FROM cars WHERE status IN ('ซ่อมบำรุง', 'ระงับใช้งาน')
        """,
        conn,
    )
    st.dataframe(maint_df, use_container_width=True)

# ====================================================
# โมดูล 9: ระบบเอกสารและ PDF (Document Management Hub)
# ====================================================
elif module_choice == "📁 9. ศูนย์เอกสาร & PDF":
  st.header("📁 9. ศูนย์รวมเอกสาร & ออกไฟล์ PDF/HTML")

  doc_type = st.selectbox(
      "เลือกประเภทเอกสารที่ต้องการสร้าง",
      [
          "📄 สัญญาเช่ารถยนต์ (Rental Contract)",
          "🔄 ใบรับคืนรถ (Return Receipt)",
          "🧾 ใบเสร็จรับเงิน (Official Receipt)",
      ],
  )

  if doc_type == "📄 สัญญาเช่ารถยนต์ (Rental Contract)":
    cnt_df = pd.read_sql_query(
        "SELECT c.id, c.contract_no || ' - ' || cu.name as label FROM contracts"
        " c JOIN customers cu ON c.customer_id = cu.id ORDER BY c.id DESC",
        conn,
    )
    if not cnt_df.empty:
      cnt_map = dict(zip(cnt_df["id"], cnt_df["label"]))
      sel_cnt = st.selectbox(
          "เลือกสัญญา",
          options=list(cnt_map.keys()),
          format_func=lambda x: cnt_map[x],
      )

      cursor = conn.cursor()
      cursor.execute(
          """
                SELECT c.contract_no, c.start_date, c.end_date, c.days, c.grand_total, c.deposit, c.created_at,
                       cu.name as cust_name, cu.phone, cu.driver_license, cu.address,
                       ca.brand, ca.model, ca.license_plate, ca.color, ca.mileage
                FROM contracts c JOIN customers cu ON c.customer_id = cu.id JOIN cars ca ON c.car_id = ca.id
                WHERE c.id = ?
            """,
          (sel_cnt,),
      )
      row = cursor.fetchone()

      if row:
        html_content = f"""
                <!DOCTYPE html>
                <html><head><meta charset="utf-8"><title>สัญญาเช่ารถ {row['contract_no']}</title>
                <style>
                    body {{ font-family: 'Sarabun', Arial, sans-serif; padding: 20px; line-height: 1.6; }}
                    .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background: #f2f2f2; }}
                </style></head><body>
                <div class="header">
                    <h2>SAWASDEE CAR RENT CO., LTD.</h2>
                    <h3>สัญญาเช่ารถยนต์ (CAR RENTAL AGREEMENT)</h3>
                    <p>เลขที่สัญญา: <strong>{row['contract_no']}</strong> | วันที่ทำสัญญา: {row['created_at']}</p>
                </div>
                <h4>1. ข้อมูลผู้เช่า</h4>
                <p><strong>ชื่อ-นามสกุล:</strong> {row['cust_name']} | <strong>เบอร์โทร:</strong> {row['phone']} | <strong>ใบขับขี่:</strong> {row['driver_license']}</p>
                <p><strong>ที่อยู่:</strong> {row['address']}</p>
                <h4>2. ข้อมูลรถยนต์เช่า</h4>
                <p><strong>ยี่ห้อ/รุ่น:</strong> {row['brand']} {row['model']} | <strong>ทะเบียน:</strong> {row['license_plate']} | <strong>สี:</strong> {row['color']} | <strong>ไมล์เริ่มต้น:</strong> {row['mileage']:,} km</p>
                <h4>3. รายละเอียดการเช่า</h4>
                <p><strong>วันเริ่มเช่า:</strong> {row['start_date']} | <strong>กำหนดคืน:</strong> {row['end_date']} ({row['days']} วัน)</p>
                <p><strong>เงินมัดจำประกัน:</strong> {row['deposit']:,.2f} บาท | <strong>ยอดรวมค่าเช่าสุทธิ:</strong> {row['grand_total']:,.2f} บาท</p>
                <br><br>
                <div style="display:flex; justify-content:space-between; text-align:center;">
                    <div>_______________________<br>ลงชื่อ ผู้ให้เช่า</div>
                    <div>_______________________<br>ลงชื่อ ผู้เช่า</div>
                </div>
                </body></html>
                """

        # บันทึกไฟล์ HTML ลงโฟลเดอร์ documents/
        file_path = os.path.join(DOCS_DIR, f"Contract_{row['contract_no']}.html")
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(html_content)

        st.subheader("👁️ ตัวอย่างเอกสารก่อนพิมพ์ / พิมพ์เป็น PDF")
        st.components.v1.html(html_content, height=500, scrolling=True)

        st.download_button(
            label="📥 ดาวน์โหลดเอกสาร (HTML/PDF)",
            data=html_content,
            file_name=f"Contract_{row['contract_no']}.html",
            mime="text/html",
        )

  elif doc_type == "🔄 ใบรับคืนรถ (Return Receipt)":
    ret_df = pd.read_sql_query(
        """
            SELECT r.id, c.contract_no || ' - ' || cu.name as label
            FROM returns_log r JOIN contracts c ON r.contract_id = c.id JOIN customers cu ON c.customer_id = cu.id
            ORDER BY r.id DESC
        """,
        conn,
    )
    if not ret_df.empty:
      ret_map = dict(zip(ret_df["id"], ret_df["label"]))
      sel_ret = st.selectbox(
          "เลือกประวัติการรับคืน",
          options=list(ret_map.keys()),
          format_func=lambda x: ret_map[x],
      )

      cursor = conn.cursor()
      cursor.execute(
          """
                SELECT r.return_date, r.mileage_in, r.fuel_level, r.refund_or_due, r.notes,
                       c.contract_no, cu.name as cust_name, ca.brand, ca.model, ca.license_plate
                FROM returns_log r JOIN contracts c ON r.contract_id = c.id JOIN customers cu ON c.customer_id = cu.id JOIN cars ca ON c.car_id = ca.id
                WHERE r.id = ?
            """,
          (sel_ret,),
      )
      row = cursor.fetchone()

      if row:
        html_ret = f"""
                <!DOCTYPE html><html><head><meta charset="utf-8"><title>ใบรับคืนรถ {row['contract_no']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                </style></head><body>
                <div class="header">
                    <h2>SAWASDEE CAR RENT CO., LTD.</h2>
                    <h3>ใบรับคืนรถยนต์ (CAR RETURN RECEIPT)</h3>
                    <p>อ้างอิงสัญญาเลขที่: {row['contract_no']} | วันเวลาที่รับคืน: {row['return_date']}</p>
                </div>
                <p><strong>ชื่อผู้เช่า:</strong> {row['cust_name']}</p>
                <p><strong>รถยนต์:</strong> {row['brand']} {row['model']} ({row['license_plate']})</p>
                <p><strong>เลขไมล์ ณ วันคืน:</strong> {row['mileage_in']:,} km | <strong>ระดับน้ำมัน:</strong> {row['fuel_level']}</p>
                <p><strong>ผลการเคลียร์เงินมัดจำ:</strong> {row['refund_or_due']}</p>
                <p><strong>หมายเหตุเพิ่มเติม:</strong> {row['notes'] or '-'}</p>
                </body></html>
                """

        file_path = os.path.join(
            DOCS_DIR, f"Return_Receipt_{row['contract_no']}.html"
        )
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(html_ret)

        st.components.v1.html(html_ret, height=450, scrolling=True)
        st.download_button(
            label="📥 ดาวน์โหลดใบรับคืนรถ",
            data=html_ret,
            file_name=f"Return_Receipt_{row['contract_no']}.html",
            mime="text/html",
        )

  elif doc_type == "🧾 ใบเสร็จรับเงิน (Official Receipt)":
    pay_df = pd.read_sql_query(
        """
            SELECT p.id, p.receipt_no || ' - ' || cu.name || ' (' || p.amount || ' ฿)' as label
            FROM payments p JOIN contracts c ON p.contract_id = c.id JOIN customers cu ON c.customer_id = cu.id
            ORDER BY p.id DESC
        """,
        conn,
    )
    if not pay_df.empty:
      pay_map = dict(zip(pay_df["id"], pay_df["label"]))
      sel_pay = st.selectbox(
          "เลือกรายการใบเสร็จ",
          options=list(pay_map.keys()),
          format_func=lambda x: pay_map[x],
      )

      cursor = conn.cursor()
      cursor.execute(
          """
                SELECT p.receipt_no, p.pay_date, p.pay_type, p.amount, p.method, p.ref_no,
                       c.contract_no, cu.name as cust_name, ca.brand, ca.license_plate
                FROM payments p JOIN contracts c ON p.contract_id = c.id JOIN customers cu ON c.customer_id = cu.id JOIN cars ca ON c.car_id = ca.id
                WHERE p.id = ?
            """,
          (sel_pay,),
      )
      row = cursor.fetchone()

      if row:
        html_pay = f"""
                <!DOCTYPE html><html><head><meta charset="utf-8"><title>ใบเสร็จรับเงิน {row['receipt_no']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                    th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                    th {{ background: #2c3e50; color: white; }}
                </style></head><body>
                <div class="header">
                    <h2>SAWASDEE CAR RENT CO., LTD.</h2>
                    <h3>ใบเสร็จรับเงิน (OFFICIAL RECEIPT)</h3>
                    <p>เลขที่ใบเสร็จ: <strong>{row['receipt_no']}</strong> | วันที่ชำระ: {row['pay_date']}</p>
                </div>
                <table>
                    <tr><th>ได้รับเงินจาก</th><td>{row['cust_name']}</td></tr>
                    <tr><th>อ้างอิงสัญญา</th><td>{row['contract_no']} ({row['brand']} {row['license_plate']})</td></tr>
                    <tr><th>ประเภทการรับเงิน</th><td>{row['pay_type']}</td></tr>
                    <tr><th>วิธีชำระเงิน</th><td>{row['method']} {f'(สลิป/อ้างอิง: {row["ref_no"]})' if row['ref_no'] else ''}</td></tr>
                    <tr><th>จำนวนเงินทั้งสิ้น</th><td><strong style="font-size:18px; color:#27ae60;">{row['amount']:,.2f} บาท</strong></td></tr>
                </table>
                </body></html>
                """

        file_path = os.path.join(
            DOCS_DIR, f"Receipt_{row['receipt_no']}.html"
        )
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(html_pay)

        st.components.v1.html(html_pay, height=450, scrolling=True)
        st.download_button(
            label="📥 ดาวน์โหลดใบเสร็จรับเงิน",
            data=html_pay,
            file_name=f"Receipt_{row['receipt_no']}.html",
            mime="text/html",
        )

  st.markdown("---")
  st.subheader("📂 รายการเอกสารทั้งหมดในโฟลเดอร์ `./documents/`")
  doc_files = [
      f
      for f in os.listdir(DOCS_DIR)
      if f.endswith(".html") or f.endswith(".pdf")
  ]
  if doc_files:
    for f in doc_files:
      st.write(f"📄 `{f}`")
  else:
    st.info("ยังไม่มีไฟล์เอกสารบันทึกในโฟลเดอร์")

conn.close()