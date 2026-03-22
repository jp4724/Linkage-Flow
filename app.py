import streamlit as st
import os

# Streamlit Cloud：在导入会读取 GEMINI_API_KEY 的模块之前，把 Secrets 写入环境变量
try:
    if hasattr(st, "secrets") and st.secrets and "GEMINI_API_KEY" in st.secrets:
        os.environ.setdefault("GEMINI_API_KEY", str(st.secrets["GEMINI_API_KEY"]))
except Exception:
    pass

import pandas as pd
import sqlite3
import time
from pathlib import Path
from generate_mail import generate_customized_mail
from datetime import datetime
from st_copy_to_clipboard import st_copy_to_clipboard
from dotenv import load_dotenv, set_key

# Import your custom modules
import db_func
import AI_func
from AI_func import invoke_gemini

env_path = '.env'
load_dotenv(env_path)

# Use st.cache_resource to ensure the connection is created only once
@st.cache_resource
def get_db_connection():
    """
    Creates a persistent connection to the SQLite database.
    check_same_thread=False is required for Streamlit's multi-threaded nature.
    """
    db_path = "JAA.db" # Or your path from settings.py
    conn = sqlite3.connect(db_path, check_same_thread=False)
    # This allows us to access columns by name like a dictionary
    conn.row_factory = sqlite3.Row 
    return conn

# Function to safely query data and return a DataFrame
def query_to_dataframe(query, params=(), *, show_error: bool = True):
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        if show_error:
            st.error(f"Database Query Error: {e}")
        return pd.DataFrame()


# 与 query.sql 中 alumni 表一致；查询失败时避免 0 列空表导致 KeyError
_ALUMNI_COLUMNS = [
    "id",
    "linkedin_url",
    "full_name",
    "location",
    "about",
    "cur_role",
    "experience",
    "education",
    "contact_info",
    "shared_connections",
    "skills",
    "languages",
    "num_conn",
    "yrs_at_cur",
    "yrs_aft_grad",
    "customized_mail_text",
    "raw_info_string",
]


def load_alumni_dataframe() -> pd.DataFrame:
    df = query_to_dataframe("SELECT * FROM alumni", show_error=False)
    if df.columns.size == 0 or "full_name" not in df.columns:
        return pd.DataFrame(columns=_ALUMNI_COLUMNS)
    return df


# --- 1. Page Configuration ---
_ROOT = Path(__file__).resolve().parent
_PAGE_ICON = _ROOT / "Linkage_Flow_Icon_reversed.png"

st.set_page_config(
    page_title="Linkage Flow",
    layout="wide",
    page_icon=str(_PAGE_ICON) if _PAGE_ICON.is_file() else "🤝",
)

# 无 JAA.db 则创建；无 alumni 表则执行 query.sql 中的 create_alumni_table
try:
    db_func.ensure_alumni_table(
        db_name=str(_ROOT / "JAA.db"),
        sql_path=str(_ROOT / "query.sql"),
    )
except Exception as e:
    st.error(f"数据库初始化失败：{e}")

# --- 2. Custom CSS for Professional Look ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar: Configuration & Settings ---
with st.sidebar:
    if _PAGE_ICON.is_file():
        st.image(str(_PAGE_ICON), width=100)
    st.title("Settings")
    
    st.subheader("API Configuration")
    existing_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", type="password",value=existing_api_key, help="Enter your Google AI Studio API Key")
    if st.button("Save Key"):
        set_key(env_path, "GEMINI_API_KEY", api_key)
        st.toast("API Key saved!", icon="✅")
    else:
        st.warning("Make sure to save your API Key after entering it.", icon="⚠️")
    
    # st.subheader("Matching Logic")
    # match_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.70)
     
    #st.info("This tool helps students automate personalized networking outreach using LLMs.")

# --- 4. Main Header ---
st.title("Linkage Flow")
#st.caption("Empowering your career search with Semantic Matching and LLM-powered Outreach.")

# --- 5. Navigation Tabs ---
tab1, tab2, tab3, tab4= st.tabs(["Self Information", "📊 Database Management", "✉️ Email Generator", "📈 Analytics"])

Path("data").mkdir(parents=True, exist_ok=True)
alumni_df = load_alumni_dataframe()

with tab1:
    st.header("Self Information")
    col1, col2 = st.columns([1,1])
    with col1:
        st.write("### Sender Context (Your Bio)")
        with open('data/self.txt','a+',encoding='utf-8') as file:
            self_info_text = file.read()
        self_info = st.text_area("Update your background for the prompt:", 
                                    placeholder="Share information about yourself or paste your Resume here", 
                                    value=self_info_text,
                                    height=400)
        if st.button("Save"):
            with open('data/self.txt', 'w', encoding='utf-8') as file:
                file.write(self_info)
            st.toast('Saved!', icon="✅")

# --- Tab 1: Database Management ---
with tab2:
    st.header("Linkedin Profile Ingestion")
    
    st.write("### Import Data")
    uploaded_file = st.file_uploader("Upload Raw Profile CSV", type=['csv'])
    if st.button("Run Extraction Pipeline"):
        if uploaded_file is not None:
            with st.spinner("Executing Parallel LLM Extraction..."):
                # Here you would call your ingest_raw_to_db() function
                # Example: ingest_raw_to_db(uploaded_file)
                st.success("Extraction Completed & Database Updated!")
        else:
            st.error("Please upload a CSV file first.")


    st.write("### Database Records Preview")
    if alumni_df.empty:
        st.info(
            "No alumni rows yet. On **Streamlit Cloud** the database is recreated when the app restarts; "
            "import data via your pipeline or use a local `JAA.db`."
        )
    else:
        preview_cols = [c for c in ("full_name", "cur_role") if c in alumni_df.columns]
        if preview_cols:
            st.dataframe(alumni_df[preview_cols], use_container_width=True)

# --- Tab 2: Email Generator ---
with tab3:
    st.header("Personalized Outreach Email Generator")
    
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.write("### Select Target")
        names_series = alumni_df["full_name"].dropna().astype(str)
        names_series = names_series[names_series.str.strip() != ""]
        contact_name_list = [""] + names_series.unique().tolist()
        contact_name = st.selectbox("Search Target Name", contact_name_list)

        selected_info = None
        display_text = ""
        if contact_name and not alumni_df.empty and "full_name" in alumni_df.columns:
            match = alumni_df[alumni_df["full_name"] == contact_name]
            if not match.empty:
                selected_info = match.iloc[0]
                display_text = "\n".join(
                    f"{k}: {v}" for k, v in selected_info.to_dict().items() if v == v
                )
        st.text_area("Contact Bio", value=display_text, disabled=True, height=600)

        if st.button("Generate Tailored Email"):
            with st.spinner("Analyzing profile and drafting..."):
                self_info = ""
                try:
                    with open("data/self.txt", "r", encoding="utf-8") as file:
                        self_info = file.read()
                except FileNotFoundError:
                    self_info = ""
                if alumni_df.empty:
                    st.error("No alumni in the database. Add contacts first (e.g. import CSV / local DB).")
                elif selected_info is None:
                    st.error("Please select a contact from the list before generating.")
                elif not self_info.strip():
                    st.error("Please fill in your Self Information in Tab 1 before generating emails.")
                else:
                    st.session_state["generated_email"] = generate_customized_mail(
                        self_info, selected_info
                    )

    with right_col:
        st.write("### Generated Output")
        if 'generated_email' in st.session_state:
            st.text_area("Draft Content", st.session_state['generated_email'], height=350)
            
            c1, c2 = st.columns(2)
            with c1:
                pass
            with c2:
                st_copy_to_clipboard(st.session_state['generated_email'], before_copy_label="📋 Copy to Clipboard", after_copy_label='Copied!✅')

# --- Tab 3: Analytics ---
with tab4:
    st.header("Networking Statistics")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Profiles Processed", alumni_df.shape[0])

# --- 6. Footer ---
st.divider()
st.markdown(f"**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developed by Jingming Peng | Powered by Gemini AI")
