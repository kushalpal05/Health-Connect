# language_manager.py
import json
import streamlit as st
from typing import Dict, Any

class LanguageManager:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'हिन्दी (Hindi)', 
            'pa': 'ਪੰਜਾਬੀ (Punjabi)'
        }
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all language files"""
        try:
            for lang_code in self.supported_languages.keys():
                with open(f'locales/{lang_code}.json', 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
        except Exception as e:
            st.error(f"Error loading translations: {e}")
    
    def get_current_language(self):
        """Get current language from session state"""
        if 'current_language' not in st.session_state:
            st.session_state.current_language = 'en'
        return st.session_state.current_language
    
    def set_language(self, lang_code):
        """Set current language"""
        if lang_code in self.supported_languages:
            st.session_state.current_language = lang_code
    
    def t(self, key: str, default: str = None) -> str:
        """Get translation for key in current language"""
        lang = self.get_current_language()
        
        # Fallback chain: current language -> English -> default
        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]
        elif 'en' in self.translations and key in self.translations['en']:
            return self.translations['en'][key]
        else:
            return default or key
    
    def get_blood_types(self):
        """Get blood types in current language"""
        return self.t('blood_types', ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    
    def create_language_selector(self, position="sidebar"):
        """Create language selector widget"""
        current_lang = self.get_current_language()
        
        if position == "sidebar":
            with st.sidebar:
                st.markdown("---")
                selected_lang = st.selectbox(
                    "🌍 Language / भाषा / ਭਾਸ਼ਾ",
                    options=list(self.supported_languages.keys()),
                    format_func=lambda x: self.supported_languages[x],
                    index=list(self.supported_languages.keys()).index(current_lang)
                )
        else:
            selected_lang = st.selectbox(
                "🌍 Language",
                options=list(self.supported_languages.keys()),
                format_func=lambda x: self.supported_languages[x],
                index=list(self.supported_languages.keys()).index(current_lang)
            )
        
        if selected_lang != current_lang:
            self.set_language(selected_lang)
            st.rerun()

# Create global instance
language_manager = LanguageManager()

# Shortcut function
def t(key: str, default: str = None) -> str:
    return language_manager.t(key, default)
