# database_admin.py
import sqlite3
import streamlit as st
from datetime import datetime

class DatabaseAdmin:
    def __init__(self, db_path='healthcare_app.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Table counts
        tables = ['users', 'symptom_history', 'user_profiles']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f'{table}_count'] = cursor.fetchone()[0]
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM symptom_history 
            WHERE date(created_at) = date('now')
        ''')
        stats['today_searches'] = cursor.fetchone()[0]
        
        # User registration trends
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE date(created_at) >= date('now', '-7 days')
        ''')
        stats['recent_users'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def get_all_data(self, table_name):
        """Get all data from a specific table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        
        conn.close()
        return columns, data
    
    def export_data(self, table_name, format='csv'):
        """Export table data to different formats"""
        columns, data = self.get_all_data(table_name)
        
        if format == 'csv':
            csv_content = ",".join(columns) + "\n"
            for row in data:
                csv_content += ",".join(str(cell) for cell in row) + "\n"
            return csv_content
        elif format == 'json':
            import json
            json_data = []
            for row in data:
                json_data.append(dict(zip(columns, row)))
            return json.dumps(json_data, indent=2, default=str)
    
    def backup_database(self):
        """Create a backup of the database"""
        import shutil
        from datetime import datetime
        
        backup_name = f"healthcare_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(self.db_path, backup_name)
        return backup_name

# Admin functions for the main app
def show_admin_panel():
    """Show admin panel in the main app"""
    st.markdown("---")
    st.subheader("🔧 Database Administration")
    
    admin = DatabaseAdmin()
    
    # Password protection for admin access
    admin_password = st.text_input("Admin Password", type="password", 
                                  placeholder="Enter admin password...")
    
    if admin_password == "admin123":  # Change this to a secure password
        st.success("🔓 Admin access granted")
        
        # Database Statistics
        st.markdown("### 📊 Database Statistics")
        stats = admin.get_database_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", stats['users_count'])
        with col2:
            st.metric("Symptom Searches", stats['symptom_history_count'])
        with col3:
            st.metric("Today's Searches", stats['today_searches'])
        with col4:
            st.metric("Recent Users (7d)", stats['recent_users'])
        
        # Data Explorer
        st.markdown("### 🔍 Data Explorer")
        table_to_view = st.selectbox("Select Table to View", 
                                   ['users', 'symptom_history', 'user_profiles'])
        
        if st.button("View Table Data"):
            columns, data = admin.get_all_data(table_to_view)
            
            st.markdown(f"**Table: {table_to_view}** ({len(data)} records)")
            
            # Display as table
            if data:
                # Create a DataFrame-like display
                display_data = []
                for row in data:
                    display_data.append(dict(zip(columns, row)))
                
                st.dataframe(display_data)
            else:
                st.info("No data found in this table")
        
        # Export Options
        st.markdown("### 📤 Export Data")
        export_table = st.selectbox("Select Table to Export", 
                                  ['users', 'symptom_history', 'user_profiles'])
        export_format = st.radio("Export Format", ['csv', 'json'])
        
        if st.button("Export Data"):
            exported_data = admin.export_data(export_table, export_format)
            st.download_button(
                label=f"Download {export_table}.{export_format}",
                data=exported_data,
                file_name=f"{export_table}.{export_format}",
                mime="text/csv" if export_format == 'csv' else "application/json"
            )
        
        # Backup Options
        st.markdown("### 💾 Backup Database")
        if st.button("Create Backup", type="primary"):
            backup_file = admin.backup_database()
            st.success(f"Backup created: {backup_file}")
    
    elif admin_password and admin_password != "admin123":
        st.error("❌ Incorrect admin password")