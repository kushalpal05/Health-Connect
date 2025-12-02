# emergency_services.py
import streamlit as st

class EmergencyServices:
    def __init__(self):
        self.emergency_numbers = {
            "Police": "100",
            "Fire Department": "101", 
            "Ambulance": "102",
            "Disaster Management": "108",
            "Women Helpline": "1091",
            "Child Abuse Hotline": "1098",
            "Emergency Medical": "108",
            "Suicide Prevention": "9152987821",
            "Poison Control": "1066",
            "Road Accident Emergency": "1073"
        }
        
        self.hospital_contacts = {
            "AIIMS Emergency": "+91-11-26588500",
            "Apollo Hospitals": "+91-11-29871090",
            "Max Healthcare": "+91-11-40554055",
            "Fortis Emergency": "+91-11-42776222",
            "Local Government Hospital": "102"
        }
    
    def display_emergency_contacts(self):
        """Display emergency contact numbers"""
        st.subheader("🚨 Emergency Contact Numbers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            for service, number in list(self.emergency_numbers.items())[:5]:
                st.metric(label=service, value=number)
        
        with col2:
            for service, number in list(self.emergency_numbers.items())[5:]:
                st.metric(label=service, value=number)
    
    def display_hospital_contacts(self):
        """Display hospital emergency contacts"""
        st.subheader("🏥 Hospital Emergency Contacts")
        
        for hospital, number in self.hospital_contacts.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{hospital}**")
            with col2:
                st.code(number, language="text")
    
    def display_emergency_guidance(self):
        """Display emergency guidance and instructions"""
        st.subheader("🆘 Emergency Guidance")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Medical Emergency", "Accident", "Mental Health", "First Aid Tips"])
        
        with tab1:
            st.write("**For Medical Emergencies:**")
            st.write("""
            1. 🚨 **Call Ambulance (102/108)** immediately
            2. 🩹 **Check responsiveness** - tap and shout
            3. 📍 **Clear the area** around the person
            4. 💊 **Check for medical ID** or medications
            5. 📋 **Keep medical records** ready
            6. 🕒 **Note the time** symptoms started
            """)
            
        with tab2:
            st.write("**In Case of Accident:**")
            st.write("""
            1. 🚗 **Ensure safety** - move to safe location if possible
            2. 📞 **Call Police (100)** and **Ambulance (102)**
            3. 👤 **Check for injuries** - don't move seriously injured
            4. 📸 **Document the scene** if safe to do so
            5. 🆘 **Provide first aid** for bleeding or breathing issues
            6. 🏥 **Seek medical attention** even for minor injuries
            """)
            
        with tab3:
            st.write("**Mental Health Crisis:**")
            st.write("""
            1. 📞 **Call suicide prevention**: 9152987821
            2. 👥 **Reach out** to trusted friends/family
            3. 🏥 **Visit nearest hospital** emergency room
            4. 💬 **Talk** to a mental health professional
            5. 🎯 **Remove means** of self-harm if possible
            6. 🆘 **Remember**: It's okay to ask for help
            """)
            
        with tab4:
            st.write("**Basic First Aid Tips:**")
            st.write("""
            • **Bleeding**: Apply direct pressure with clean cloth
            • **Burns**: Cool with running water for 10-20 minutes
            • **Choking**: Perform Heimlich maneuver
            • **CPR**: 30 chest compressions + 2 rescue breaths
            • **Seizure**: Clear area, don't restrain, place on side
            • **Stroke**: Remember FAST (Face, Arms, Speech, Time)
            """)
    
    def display_quick_actions(self):
        """Display quick action buttons"""
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚑 Call Ambulance", use_container_width=True, type="primary"):
                st.success("**Dialing 102/108...** Describe: Location, Condition, Number of people, Any hazards")
                st.info("💡 **Speak clearly**: Provide exact location and describe the emergency")
                
        with col2:
            if st.button("👮‍♂️ Call Police", use_container_width=True):
                st.success("**Dialing 100...** Describe: Location, Type of emergency, Suspect description if any")
                st.info("💡 **Stay calm**: Provide your location first, then details")
                
        with col3:
            if st.button("🧠 Mental Health Help", use_container_width=True):
                st.success("**Calling Suicide Prevention: 9152987821**")
                st.info("💡 **You're not alone**: Professional help is available 24/7")
        
        # Additional quick actions
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("🔥 Fire Department", use_container_width=True):
                st.success("**Dialing 101...** Describe: Location, Type of fire, People trapped")
                
        with col5:
            if st.button("👩 Women Helpline", use_container_width=True):
                st.success("**Dialing 1091...** Help is available for harassment, violence, or abuse")
                
        with col6:
            if st.button("🚗 Road Accident", use_container_width=True):
                st.success("**Dialing 1073...** Provide: Location, Vehicles involved, Injuries")
    
    def display_crisis_resources(self):
        """Display additional crisis resources"""
        st.subheader("📞 Additional Crisis Resources")
        
        resources = {
            "National Emergency Number": "112",
            "COVID-19 Helpline": "1075",
            "Senior Citizen Helpline": "14567",
            "Drug Abuse Helpline": "1800-11-0031",
            "Ambulance Service (Private)": "1029",
            "Blood Bank Emergency": "1910"
        }
        
        for resource, number in resources.items():
            st.write(f"**{resource}**: `{number}`")

def emergency_services_page():
    """Main function for the emergency services page"""
    st.title("🚑 Emergency Services Hub")
    st.markdown("---")
    
    # Initialize the emergency services app
    emergency_app = EmergencyServices()
    
    # Display emergency contacts
    emergency_app.display_emergency_contacts()
    
    st.markdown("---")
    
    # Display hospital contacts
    emergency_app.display_hospital_contacts()
    
    st.markdown("---")
    
    # Display quick actions
    emergency_app.display_quick_actions()
    
    st.markdown("---")
    
    # Display emergency guidance
    emergency_app.display_emergency_guidance()
    
    st.markdown("---")
    
    # Display additional resources
    emergency_app.display_crisis_resources()
    
    # Footer with important note
    st.markdown("---")
    st.warning("""
    ⚠️ **Important**: 
    - In life-threatening emergencies, call your local emergency number immediately
    - This information is for guidance only
    - Always follow instructions from emergency professionals
    - Keep your phone charged and accessible
    """)

if __name__ == "__main__":
    emergency_services_page()