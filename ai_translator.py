# ai_translator.py
import google.generativeai as genai
import streamlit as st

class AITranslator:
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
    
    def get_multi_lingual_suggestion(self, symptoms, language):
        """Get disease suggestions in the specified language with smart prompting"""
        
        language_prompts = {
            'en': f"""
            As a medical information assistant, analyze these symptoms: "{symptoms}"
            
            Provide 3-5 possible medical conditions with brief, clear descriptions.
            Format with bullet points for easy reading.
            Maintain professional medical tone.
            
            End with this exact disclaimer:
            "*Disclaimer:* I am an AI assistant and not a medical professional. This information is not a diagnosis. Please consult a qualified healthcare provider for medical advice."
            """,
            
            'hi': f"""
            एक चिकित्सा सूचना सहायक के रूप में, इन लक्षणों का विश्लेषण करें: "{symptoms}"
            
            3-5 संभावित चिकित्सा स्थितियाँ संक्षिप्त, स्पष्ट विवरण के साथ प्रदान करें।
            आसान पठन के लिए बुलेट पॉइंट्स में प्रारूपित करें।
            पेशेवर चिकित्सा स्वर बनाए रखें।
            
            इस सटीक अस्वीकरण के साथ समाप्त करें:
            "*Disclaimer:* I am an AI assistant and not a medical professional. This information is not a diagnosis. Please consult a qualified healthcare provider for medical advice."
            """,
            
            'pa': f"""
            ਇੱਕ ਮੈਡੀਕਲ ਜਾਣਕਾਰੀ ਸਹਾਇਕ ਦੇ ਰੂਪ ਵਿੱਚ, ਇਹਨਾਂ ਲੱਛਣਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ: "{symptoms}"
            
            3-5 ਸੰਭਾਵਿਤ ਡਾਕਟਰੀ ਸਥਿਤੀਆਂ ਸੰਖੇਪ, ਸਾਫ਼ ਵਰਣਨਾਂ ਨਾਲ ਪ੍ਰਦਾਨ ਕਰੋ।
            ਆਸਾਨ ਪੜ੍ਹਨ ਲਈ ਬੁਲੇਟ ਪੁਆਇੰਟਾਂ ਵਿੱਚ ਫਾਰਮੈਟ ਕਰੋ।
            ਪੇਸ਼ੇਵਰ ਡਾਕਟਰੀ ਟੋਨ ਬਣਾਈ ਰੱਖੋ।
            
            ਇਸ ਸਹੀ ਇਨਕਾਰ ਨਾਲ ਖਤਮ ਕਰੋ:
            "*Disclaimer:* I am an AI assistant and not a medical professional. This information is not a diagnosis. Please consult a qualified healthcare provider for medical advice."
            """
        }
        
        prompt = language_prompts.get(language, language_prompts['en'])
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_messages = {
                'en': f"Error analyzing symptoms: {str(e)}",
                'hi': f"लक्षणों का विश्लेषण करने में त्रुटि: {str(e)}",
                'pa': f"ਲੱਛਣਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰਨ ਵਿੱਚ ਤਰੁਟੀ: {str(e)}"
            }
            return error_messages.get(language, error_messages['en'])