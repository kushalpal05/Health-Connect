   # app.py
import streamlit as st
import google.generativeai as genai
import requests
import os
import hashlib
import json
from datetime import datetime
import pandas as pd

# Import our modules
from database import user_db
from language_manager import language_manager, t
from ai_translator import AITranslator
from emergency_services import emergency_services_page  # Add this import

# Initialize language manager
lm = language_manager

# --- SESSION STATE PERSISTENCE ---
def init_session_state():
    """Initialize and persist session state"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    # Initialize language if not set
    if 'current_language' not in st.session_state:
        st.session_state.current_language = 'en'
    
    # Try to restore from query parameters (for page refresh)
    if not st.session_state.logged_in and 'username' in st.query_params:
        username = st.query_params['username']
        # Verify user still exists in database
        if username == "admin":
            st.session_state.current_user = username
            st.session_state.logged_in = True
            st.session_state.is_admin = True
        elif user_db.user_exists(username):
            st.session_state.current_user = username
            st.session_state.logged_in = True
            st.session_state.is_admin = False

def set_session_persistence(username, is_admin=False):
    """Set session persistence for page refresh"""
    st.session_state.logged_in = True
    st.session_state.current_user = username
    st.session_state.is_admin = is_admin
    st.query_params['username'] = username

def clear_session_persistence():
    """Clear session persistence on logout"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False
    if 'username' in st.query_params:
        del st.query_params['username']

# --- AUTHENTICATION FUNCTIONS ---
def create_user(username, password, email=""):
    success, message = user_db.create_user(username, password, email)
    if success:
        set_session_persistence(username)
    return success, message

def authenticate_user(username, password):
    if username == "admin" and password == "admin123":
        set_session_persistence(username, is_admin=True)
        return True, "Admin login successful"
    
    success, message = user_db.authenticate_user(username, password)
    if success:
        set_session_persistence(username)
    return success, message

def save_symptom_search(username, symptoms, conditions, location):
    severity_level, _ = assess_symptom_severity(symptoms)
    return user_db.save_symptom_history(username, symptoms, severity_level, conditions, location)

def get_user_history(username):
    return user_db.get_symptom_history(username)

# --- SYMPTOM ANALYSIS FUNCTIONS ---
def assess_symptom_severity(symptoms):
    critical_keywords = [
        'chest pain', 'heart attack', 'stroke', 'difficulty breathing',
        'severe bleeding', 'unconscious', 'choking', 'severe burn',
        'poisoning', 'severe allergic reaction', 'cannot breathe',
        'heavy bleeding', 'sudden paralysis', 'seizure'
    ]
    
    symptoms_lower = symptoms.lower()
    for critical in critical_keywords:
        if critical in symptoms_lower:
            return "HIGH", t('urgent_warning')
    
    warning_keywords = ['high fever', 'persistent vomiting', 'severe pain', 'head injury']
    for warning in warning_keywords:
        if warning in symptoms_lower:
            return "MEDIUM", t('medium_warning')
    
    return "LOW", t('non_emergency')

def get_emergency_contacts(location):
    emergency_numbers = {
        'india': [
            {'service': 'Police', 'number': '100'},
            {'service': 'Ambulance', 'number': '102'}, 
            {'service': 'Emergency', 'number': '112'}
        ],
        'us': [
            {'service': 'Emergency', 'number': '911'},
            {'service': 'Poison Control', 'number': '1-800-222-1222'}
        ],
        'uk': [
            {'service': 'Emergency', 'number': '999'},
            {'service': 'NHS Non-emergency', 'number': '111'}
        ],
        'default': [
            {'service': 'International Emergency', 'number': '112'},
            {'service': 'Local Police', 'number': 'Check locally'}
        ]
    }
    
    location_lower = location.lower()
    for country in ['india', 'us', 'uk']:
        if country in location_lower:
            return emergency_numbers[country]
    
    return emergency_numbers['default']

# --- API CONFIGURATION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")
    # Initialize AI Translator
    ai_translator = AITranslator(gemini_model)
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}")
    gemini_model = None
    ai_translator = None

def get_nearby_hospitals(location_query):
    try:
        headers = {"User-Agent": "HealthFinderApp/1.0"}
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"hospital near {location_query}",
            "format": "json",
            "limit": 15
        }
        resp = requests.get(url, params=params, headers=headers)
        results = resp.json()

        if not results:
            return {"status": "ZERO_RESULTS", "results": []}

        hospitals = []
        for h in results:
            hospitals.append({
                "name": h.get("display_name", "Unnamed Hospital"),
                "lat": float(h["lat"]),
                "lon": float(h["lon"])
            })
        return {"status": "OK", "results": hospitals}

    except Exception as e:
        return {"status": "ERROR", "error": str(e), "results": []}

def get_disease_suggestion(symptoms):
    """Get disease suggestions in the current language"""
    if not gemini_model or not ai_translator:
        return t('api_not_configured', "Gemini API is not configured.")
    
    current_language = st.session_state.current_language
    return ai_translator.get_multi_lingual_suggestion(symptoms, current_language)

# --- ADMIN DASHBOARD ---
def admin_dashboard():
    st.set_page_config(layout="wide", page_title=t('admin_dashboard'))
    
    # Language selector in sidebar
    with st.sidebar:
        lm.create_language_selector()
        st.markdown("---")
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title(f"👨‍⚕️ {t('admin_dashboard')}")
    with col2:
        st.write(f"{t('welcome')}, *Admin*!")
    with col3:
        if st.button(t('logout'), type="primary"):
            logout_user()
            st.rerun()
    
    st.markdown(f"{t('system_overview')}")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📊 {t('system_overview')}",
        f"👥 {t('all_patients')}", 
        f"📋 {t('patient_details')}",
        f"⚙️ {t('admin_tools')}"
    ])
    
    with tab1:
        st.subheader(f"📊 {t('system_overview')}")
        try:
            stats = user_db.get_database_stats()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t('total_patients'), stats.get('users_count', 0))
            with col2:
                st.metric(t('total_searches'), stats.get('symptom_history_count', 0))
            with col3:
                st.metric(t('profiles_created'), stats.get('user_profiles_count', 0))
            with col4:
                st.metric(t('recent_searches'), stats.get('recent_searches', 0))
        except Exception as e:
            st.error(f"Error loading statistics: {e}")

    with tab2:
        st.subheader(f"👥 {t('all_patients')}")
        try:
            all_users = user_db.get_all_users()
            if all_users:
                users_df = pd.DataFrame(all_users, columns=['Username', 'Email', 'Registration Date'])
                
                # Search functionality
                col1, col2 = st.columns([2, 1])
                with col1:
                    search_term = st.text_input(f"🔍 {t('search_patients')}:")
                with col2:
                    sort_by = st.selectbox("Sort by:", ["Registration Date", "Username"])
                
                # Filter data
                if search_term:
                    filtered_df = users_df[
                        users_df['Username'].str.contains(search_term, case=False, na=False) |
                        users_df['Email'].str.contains(search_term, case=False, na=False)
                    ]
                else:
                    filtered_df = users_df
                
                # Sort data
                if sort_by == "Registration Date":
                    filtered_df = filtered_df.sort_values('Registration Date', ascending=False)
                else:
                    filtered_df = filtered_df.sort_values('Username')
                
                # Display results
                st.dataframe(filtered_df, use_container_width=True)
                
                # Export option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label=f"📥 {t('export_patients')}",
                    data=csv,
                    file_name="patients_list.csv",
                    mime="text/csv"
                )
            else:
                st.info("No patients registered yet.")
                
        except Exception as e:
            st.error(f"Error loading patients: {e}")

    with tab3:
        st.subheader(f"📋 {t('patient_details')}")
        try:
            all_users = user_db.get_all_users()
            if all_users:
                usernames = [user[0] for user in all_users]
                selected_patient = st.selectbox(f"{t('select_patient')}:", usernames)
                
                if selected_patient:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### 👤 {t('basic_information')}")
                        profile = user_db.get_user_profile(selected_patient)
                        if profile:
                            st.write(f"**Username:** {selected_patient}")
                            if profile[0]:
                                st.write(f"**{t('age')}:** {profile[0]}")
                            if profile[1] and profile[1] != t('unknown'):
                                st.write(f"**{t('blood_type')}:** {profile[1]}")
                            if profile[2]:
                                st.write(f"**{t('allergies')}:** {profile[2]}")
                            if profile[3]:
                                st.write(f"**{t('chronic_conditions')}:** {profile[3]}")
                            if profile[4]:
                                st.write(f"**{t('emergency_contact')}:** {profile[4]}")
                        else:
                            st.info("No profile information available.")
                    
                    with col2:
                        st.markdown(f"### 🩺 {t('symptom_history_details')}")
                        history = user_db.get_symptom_history(selected_patient)
                        if history:
                            for i, record in enumerate(history, 1):
                                with st.expander(f"Search {i} - {record[4][:16]}..."):
                                    st.write(f"**Symptoms:** {record[0]}")
                                    st.write(f"**Severity:** {record[1]}")
                                    st.write(f"**Location:** {record[3]}")
                                    st.write(f"**Date:** {record[4]}")
                                    st.markdown("**AI Analysis:**")
                                    st.write(record[2])
                        else:
                            st.info("No symptom history available.")
            else:
                st.info("No patients registered yet.")
                
        except Exception as e:
            st.error(f"Error loading patient details: {e}")

    with tab4:
        st.subheader(f"⚙️ {t('admin_tools')}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🗄️ {t('database_management')}")
            if st.button(f"🔄 {t('refresh_cache')}"):
                st.success("Database cache refreshed!")
            
            if st.button(f"📊 {t('generate_report')}"):
                try:
                    stats = user_db.get_database_stats()
                    st.success("System report generated!")
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error generating report: {e}")
        
        with col2:
            st.markdown(f"### 🔒 {t('data_management')}")
            all_users = user_db.get_all_users()
            if all_users:
                delete_user = st.selectbox(f"{t('select_delete')}:", [user[0] for user in all_users])
                if st.button(f"🗑️ {t('delete_patient')}", type="secondary"):
                    if delete_user:
                        success, message = user_db.delete_user_data(delete_user)
                        if success:
                            st.success(f"Patient '{delete_user}' data deleted successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error: {message}")

# --- REGULAR USER APP ---
def main_app():
    st.set_page_config(layout="wide", page_title=t('app_title'))
    
    # Language selector in sidebar
    with st.sidebar:
        lm.create_language_selector()
        st.markdown("---")
    
    # Header
    col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
    with col_header1:
        st.title(f"🏥 {t('app_title')}")
    with col_header2:
        st.write(f"{t('welcome')}, *{st.session_state.current_user}*!")
    with col_header3:
        if st.button(t('logout'), type="primary"):
            logout_user()
            st.rerun()
    
    st.markdown(f"{t('describe_symptoms')}")

    # UPDATED TABS - Added Emergency Services tab
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🔍 {t('symptom_analysis')}",
        f"📊 {t('your_history')}", 
        f"👤 {t('your_profile')}",
        f"🚑 Emergency Services"  # New Emergency Services tab
    ])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📍 {t('describe_symptoms')}")
            symptoms_input = st.text_area(
                f"{t('describe_symptoms')}:",
                placeholder=t('symptom_placeholder'),
                height=150
            )

            st.subheader(f"📍 {t('enter_location')}")
            location_input = st.text_input(
                f"{t('enter_location')}:",
                placeholder=t('location_placeholder')
            )

            analyze_button = st.button(f"🔍 {t('analyze_button')}", type="primary")

        with col2:
            st.subheader(f"📊 {t('results')}")

            if analyze_button:
                if not symptoms_input:
                    st.warning(t('enter_symptoms_warning'))
                elif not location_input:
                    st.warning(t('enter_location_warning'))
                else:
                    # --- SYMPTOM SEVERITY CHECK ---
                    severity_level, severity_message = assess_symptom_severity(symptoms_input)
                    
                    if severity_level == "HIGH":
                        st.error(severity_message)
                        st.markdown(f"### 🚨 {t('emergency_contacts')}")
                        emergency_contacts = get_emergency_contacts(location_input)
                        for contact in emergency_contacts:
                            st.write(f"**{contact['service']}**: `{contact['number']}`")
                        st.divider()
                    
                    elif severity_level == "MEDIUM":
                        st.warning(severity_message)
                        st.divider()

                    # --- GEMINI ANALYSIS ---
                    with st.spinner("🔍 Analyzing symptoms with AI..."):
                        st.markdown(f"### 🩺 {t('possible_conditions')}")
                        disease_info = get_disease_suggestion(symptoms_input)
                        st.markdown(disease_info)

                    # --- SAVE TO DATABASE ---
                    save_success = save_symptom_search(
                        st.session_state.current_user, 
                        symptoms_input, 
                        disease_info, 
                        location_input
                    )
                    
                    if save_success:
                        st.success(f"✅ {t('analysis_saved')}")
                    else:
                        st.warning("⚠️ Could not save to history")

                    st.divider()

                    # --- HOSPITAL SEARCH ---
                    with st.spinner(f"🏨 {t('hospitals_near')} {location_input}..."):
                        st.markdown(f"### 📍 {t('hospitals_near')} {location_input}")

                        hospital_data = get_nearby_hospitals(location_input)

                        if hospital_data["status"] == "OK":
                            hospital_list = hospital_data["results"]
                            st.markdown(f"**Found {len(hospital_list)} hospitals:**")
                            for i, h in enumerate(hospital_list, start=1):
                                st.markdown(f"{i}. **{h['name']}**")

                            st.markdown(f"### 🗺️ {t('hospital_locations')}")
                            map_points = [{"lat": h["lat"], "lon": h["lon"]} for h in hospital_list]
                            st.map(map_points)

                        elif hospital_data["status"] == "ZERO_RESULTS":
                            st.warning(t('no_hospitals'))
                        else:
                            st.error(f"Error: {hospital_data.get('error', 'Unknown error')}")

    with tab2:
        st.subheader(f"📊 {t('symptom_history')}")
        history = get_user_history(st.session_state.current_user)
        if history:
            st.info(f"{t('symptom_history')}:")
            for i, record in enumerate(history, 1):
                with st.expander(f"Analysis {i} - {record[4][:16]}..."):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Symptoms:** {record[0]}")
                        st.write(f"**Severity:** {record[1]}")
                    with col2:
                        st.write(f"**Location:** {record[3]}")
                        st.write(f"**Date:** {record[4]}")
                    st.markdown("**AI Suggestions:**")
                    st.write(record[2])
        else:
            st.info(f"📝 {t('no_history')}")

    with tab3:
        st.subheader(f"👤 {t('health_profile')}")
        current_profile = user_db.get_user_profile(st.session_state.current_user)
        
        st.markdown(f"### 📋 {t('basic_info')}")
        col1, col2 = st.columns(2)
        with col1:
            current_age = current_profile[0] if current_profile and current_profile[0] else 25
            current_blood_type = current_profile[1] if current_profile and current_profile[1] else t('unknown')
            
            age = st.number_input(t('age'), min_value=1, max_value=120, value=current_age)
            blood_type = st.selectbox(t('blood_type'), lm.get_blood_types())
        
        with col2:
            current_allergies = current_profile[2] if current_profile and current_profile[2] else ""
            current_emergency_contact = current_profile[4] if current_profile and current_profile[4] else ""
            
            allergies = st.text_input(t('allergies'), value=current_allergies)
            emergency_contact = st.text_input(t('emergency_contact'), value=current_emergency_contact)
        
        current_conditions = current_profile[3] if current_profile and current_profile[3] else ""
        chronic_conditions = st.text_area(t('chronic_conditions'), value=current_conditions, height=80)
        
        if st.button(f"💾 {t('save_profile')}", type="primary", use_container_width=True):
            if age and emergency_contact:
                success = user_db.update_user_profile(
                    st.session_state.current_user,
                    age=age,
                    blood_type=blood_type,
                    allergies=allergies,
                    chronic_conditions=chronic_conditions,
                    emergency_contact=emergency_contact
                )
                if success:
                    st.success(f"✅ {t('profile_saved')}")
                    st.rerun()
                else:
                    st.error("❌ Error saving profile")
            else:
                st.warning("⚠️ Please fill required fields")

    # NEW TAB: Emergency Services
    with tab4:
        emergency_services_page()

# --- LOGIN/SIGNUP PAGE ---
def login_signup_page():
    st.set_page_config(layout="centered", page_title=f"Login - {t('app_title')}")
    
    # Language selector at top
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🏥 {t('app_title')}")
    with col2:
        lm.create_language_selector("main")
    
    st.markdown(f"### {t('login_title')}")
    
    tab1, tab2, tab3 = st.tabs([
        f"🔑 {t('patient_login')}",
        f"📝 {t('create_account')}", 
        f"👨‍⚕️ {t('admin_login')}"
    ])
    
    with tab1:
        st.subheader(f"🔑 {t('patient_login')}")
        login_username = st.text_input(t('username'), key="login_username")
        login_password = st.text_input(t('password'), type="password", key="login_password")
        
        if st.button(t('login_button'), key="login_btn", type="primary"):
            if login_username and login_password:
                success, message = authenticate_user(login_username, login_password)
                if success:
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning(f"Please enter both {t('username')} and {t('password')}")
    
    with tab2:
        st.subheader(f"📝 {t('create_account')}")
        signup_username = st.text_input(t('username'), key="signup_username")
        signup_email = st.text_input(t('email'), key="signup_email")
        signup_password = st.text_input(t('password'), type="password", key="signup_password")
        signup_confirm = st.text_input(t('confirm_password'), type="password", key="signup_confirm")
        
        if st.button(t('create_account_button'), key="signup_btn", type="primary"):
            if not signup_username or not signup_password:
                st.warning(f"Please enter both {t('username')} and {t('password')}")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match")
            elif len(signup_password) < 4:
                st.warning("Password should be at least 4 characters long")
            else:
                success, message = create_user(signup_username, signup_password, signup_email)
                if success:
                    st.success("Account created successfully!")
                    st.rerun()
                else:
                    st.error(message)
    
    with tab3:
        st.subheader(f"👨‍⚕️ {t('admin_login')}")
        st.info("Use admin credentials to access the admin dashboard")
        admin_username = st.text_input(t('username'), key="admin_username")
        admin_password = st.text_input(t('password'), type="password", key="admin_password")
        
        if st.button(t('login_button'), key="admin_login_btn", type="primary"):
            if admin_username and admin_password:
                success, message = authenticate_user(admin_username, admin_password)
                if success:
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning(f"Please enter both {t('username')} and {t('password')}")

def logout_user():
    clear_session_persistence()
    st.rerun()

# --- INITIALIZE APP ---
init_session_state()

if st.session_state.logged_in:
    if st.session_state.is_admin:
        admin_dashboard()
    else:
        main_app()
else:
    login_signup_page()