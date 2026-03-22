import streamlit as st
import pandas as pd
import sqlite3
import time
import os
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
def query_to_dataframe(query, params=()):
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        return pd.DataFrame()


# --- 1. Page Configuration ---
_APP_DIR = Path(__file__).resolve().parent
_PAGE_ICON = _APP_DIR / "Linkage_Flow_Icon_reversed.png"

st.set_page_config(
    page_title="Linkage Flow",
    layout="wide",
    page_icon=str(_PAGE_ICON) if _PAGE_ICON.is_file() else "🤝",
)

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
    # Example logic to display DB
    # 1. Fetch alumni names for the dropdown
    alumni_df = query_to_dataframe("SELECT * FROM alumni")
    alumni_df[['full_name','cur_role']]
    # names_list = alumni_df['full_name'].tolist() if not alumni_df.empty else []

    # # 2. Display the selectbox in the UI
    # if names_list:
    #     selected_name = st.selectbox("Select Alumni to Contact:", names_list)
        
    #     # 3. Once a name is selected, fetch their full details
    #     if selected_name:
    #         # Using parameterized query to prevent SQL injection
    #         details_query = "SELECT * FROM alumni WHERE full_name = ?"
    #         details_df = query_to_dataframe(details_query, params=(selected_name,))
            
    #         if not details_df.empty:
    #             target_profile = details_df.iloc[0] # Get the first (and only) row
    #             st.write(f"**Target Role:** {target_profile['job_title']} @ {target_profile['company']}")
    # else:
    #     st.warning("No alumni records found. Please ingest data in Tab 1.")
    # # df = db_func.get_all_alumni()
    # # st.dataframe(df, use_container_width=True)
    # st.info("Record preview will appear here once the database is connected.")

# --- Tab 2: Email Generator ---
with tab3:
    st.header("Personalized Outreach Email Generator")
    
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.write("### Select Target")
        # This would be populated from your DB
        contact_name_list = [""] + alumni_df['full_name'].to_list()
        contact_name = st.selectbox("Search Target Name", contact_name_list)

        
        display_text = ""
        if contact_name and contact_name in alumni_df['full_name'].values:
            selected_info = alumni_df[alumni_df['full_name'] == contact_name].iloc[0]

            display_text = '\n'.join([f"{k}: {v}" for k, v in selected_info.to_dict().items() if v == v])
        else:
            display_text = ""
        st.text_area('Contact Bio',value=display_text,disabled=True,height=600)

        if st.button("Generate Tailored Email"):
            with st.spinner("Analyzing profile and drafting..."):
                # Your generate_customized_mail(qresult) logic goes here
                self_info = ""
                with open('data/self.txt', 'r', encoding='utf-8') as file:
                    self_info = file.read()
                if self_info == "":
                    st.error("Please fill in your Self Information in Tab 1 before generating emails.")
                else:
                    st.session_state['generated_email'] = generate_customized_mail(self_info, selected_info)

    with right_col:
        st.write("### Generated Output")
        # st.session_state
        # st.success("Done!", icon='✅')
        # st.button("Rerun!")
        if 'generated_email' in st.session_state:
            st.text_area("Draft Content", st.session_state['generated_email'], height=350)
            
            c1, c2 = st.columns(2)
            with c1:
                pass
                # if st.button("✅ Save to Networking Log"):
                #     st.toast("Record saved to Database!")
            with c2:
                st_copy_to_clipboard(st.session_state['generated_email'], before_copy_label="📋 Copy to Clipboard", after_copy_label='Copied!✅')

# --- Tab 3: Analytics ---
with tab4:
    st.header("Networking Statistics")
    
    # Showcase your Stats background here!
    col1, col2, col3 = st.columns(3)
    col1.metric("Profiles Processed", alumni_df.shape[0])
    # col2.metric("Avg Match Score", "0.82", "+0.05")
    # col3.metric("Response Rate", "15%", "Personalized")
    
    # st.write("### Alumni Industry Distribution")
    # Example Chart
    # chart_data = pd.DataFrame({'Industry': ['Finance', 'Tech', 'Consulting'], 'Count': [45, 30, 15]})
    # st.bar_chart(chart_data, x='Industry', y='Count')

# --- 6. Footer ---
st.divider()
st.markdown(f"**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developed by Jingming Peng | Powered by Gemini AI")