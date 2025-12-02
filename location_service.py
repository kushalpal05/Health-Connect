# location_service.py
import streamlit as st
import requests
import json

def get_current_location():
    """
    Get user's current location using browser geolocation or IP-based fallback
    """
    # Method 1: Browser Geolocation (requires user permission)
    st.markdown("""
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        }
                    }, '*');
                },
                function(error) {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue', 
                        value: null
                    }, '*');
                }
            );
        } else {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: null
            }, '*');
        }
    }
    getLocation();
    </script>
    """, unsafe_allow_html=True)
    
    # This will be populated by the JavaScript
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None
    
    return st.session_state.user_location

def get_location_by_ip():
    """
    Fallback method: Get approximate location by IP address
    """
    try:
        response = requests.get('http://ipinfo.io/json', timeout=5)
        data = response.json()
        loc = data.get('loc', '').split(',')
        if len(loc) == 2:
            return {
                'lat': float(loc[0]),
                'lon': float(loc[1]),
                'city': data.get('city', ''),
                'country': data.get('country', ''),
                'method': 'ip'
            }
    except:
        pass
    return None

def create_location_selector():
    """
    Create location input with current location option
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location_input = st.text_input(
            "Enter Location:",
            placeholder="City, address, or use current location →",
            key="location_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_current = st.button("📍 Use Current Location", use_container_width=True)
    
    current_location = None
    
    if use_current:
        with st.spinner("Detecting your location..."):
            # Try IP-based location first (more reliable in Streamlit)
            current_location = get_location_by_ip()
            
            if current_location:
                st.success(f"📍 Found: {current_location.get('city', 'Your location')}")
                # Store in session state
                st.session_state.current_location = current_location
                location_input = f"{current_location.get('city', 'Current location')}"
            else:
                st.warning("Could not detect location automatically. Please enter your location manually.")
    
    return location_input, current_location