# database.py
import sqlite3
import hashlib
import streamlit as st
from datetime import datetime

class UserDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('healthcare_app.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Symptoms history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptom_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symptoms TEXT,
                severity TEXT,
                suggested_conditions TEXT,
                location_searched TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                age INTEGER,
                blood_type TEXT,
                allergies TEXT,
                chronic_conditions TEXT,
                emergency_contact TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
        print("Database tables created/verified successfully")
    
    def create_user(self, username, password, email=""):
        """Create new user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, hashlib.sha256(password.encode()).hexdigest(), email)
            )
            self.conn.commit()
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM users WHERE username = ?", 
                (username,)
            )
            result = cursor.fetchone()
            
            if result and result[0] == hashlib.sha256(password.encode()).hexdigest():
                return True, "Login successful"
            return False, "Invalid username or password"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def save_symptom_history(self, username, symptoms, severity, conditions, location):
        """Save symptom search history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_result = cursor.fetchone()
            
            if user_result:
                user_id = user_result[0]
                cursor.execute('''
                    INSERT INTO symptom_history 
                    (user_id, symptoms, severity, suggested_conditions, location_searched) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, symptoms, severity, conditions, location))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            st.error(f"Error saving symptom history: {e}")
            return False
    
    def get_symptom_history(self, username):
        """Get user's symptom history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT sh.symptoms, sh.severity, sh.suggested_conditions, 
                       sh.location_searched, sh.created_at
                FROM symptom_history sh
                JOIN users u ON sh.user_id = u.id
                WHERE u.username = ?
                ORDER BY sh.created_at DESC
                LIMIT 10
            ''', (username,))
            return cursor.fetchall()
        except Exception as e:
            st.error(f"Error fetching history: {e}")
            return []
    
    def update_user_profile(self, username, age=None, blood_type=None, allergies=None, 
                          chronic_conditions=None, emergency_contact=None):
        """Update or create user profile"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_result = cursor.fetchone()
            
            if user_result:
                user_id = user_result[0]
                cursor.execute('''
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, age, blood_type, allergies, chronic_conditions, emergency_contact)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, age, blood_type, allergies, chronic_conditions, emergency_contact))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            st.error(f"Error updating profile: {e}")
            return False
    
    def get_user_profile(self, username):
        """Get user profile"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT up.age, up.blood_type, up.allergies, up.chronic_conditions, up.emergency_contact
                FROM user_profiles up
                JOIN users u ON up.user_id = u.id
                WHERE u.username = ?
            ''', (username,))
            return cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching profile: {e}")
            return None
    
    def user_exists(self, username):
        """Check if user exists"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
        except Exception as e:
            st.error(f"Error checking user: {e}")
            return False

    # --- NEW METHODS ADDED FOR DATABASE VERIFICATION ---

    def get_all_users(self):
        """Get all users (for admin purposes)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT username, email, created_at FROM users")
            return cursor.fetchall()
        except Exception as e:
            st.error(f"Error getting users: {e}")
            return []

    def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
            cursor = self.conn.cursor()
            stats = {}
            
            # Table counts
            tables = ['users', 'symptom_history', 'user_profiles']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Recent activity (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM symptom_history 
                WHERE datetime(created_at) >= datetime('now', '-1 day')
            ''')
            stats['recent_searches'] = cursor.fetchone()[0]
            
            # User registration trends (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE datetime(created_at) >= datetime('now', '-7 days')
            ''')
            stats['recent_users'] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            st.error(f"Error getting database stats: {e}")
            return {}

    def debug_database(self):
        """Debug function to check database state"""
        try:
            cursor = self.conn.cursor()
            
            print("=== DATABASE DEBUG INFO ===")
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables: {[table[0] for table in tables]}")
            
            # Count records
            for table in ['users', 'symptom_history', 'user_profiles']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} records")
            
            # Check recent users
            cursor.execute("SELECT username, created_at FROM users ORDER BY created_at DESC LIMIT 3")
            recent_users = cursor.fetchall()
            print(f"Recent users: {recent_users}")
            
            print("===========================")
            return True
        except Exception as e:
            print(f"Debug error: {e}")
            return False

    def export_user_data(self, username, format='json'):
        """Export all user data for GDPR compliance"""
        try:
            cursor = self.conn.cursor()
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_result = cursor.fetchone()
            
            if not user_result:
                return None
            
            user_id = user_result[0]
            
            # Get all user data
            user_data = {
                'user_info': {},
                'symptom_history': [],
                'user_profile': {}
            }
            
            # User basic info
            cursor.execute("SELECT username, email, created_at FROM users WHERE id = ?", (user_id,))
            user_info = cursor.fetchone()
            if user_info:
                user_data['user_info'] = {
                    'username': user_info[0],
                    'email': user_info[1],
                    'created_at': user_info[2]
                }
            
            # Symptom history
            cursor.execute('''
                SELECT symptoms, severity, suggested_conditions, location_searched, created_at
                FROM symptom_history WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            symptom_history = cursor.fetchall()
            for record in symptom_history:
                user_data['symptom_history'].append({
                    'symptoms': record[0],
                    'severity': record[1],
                    'suggested_conditions': record[2],
                    'location_searched': record[3],
                    'created_at': record[4]
                })
            
            # User profile
            cursor.execute('''
                SELECT age, blood_type, allergies, chronic_conditions, emergency_contact
                FROM user_profiles WHERE user_id = ?
            ''', (user_id,))
            profile = cursor.fetchone()
            if profile:
                user_data['user_profile'] = {
                    'age': profile[0],
                    'blood_type': profile[1],
                    'allergies': profile[2],
                    'chronic_conditions': profile[3],
                    'emergency_contact': profile[4]
                }
            
            if format == 'json':
                import json
                return json.dumps(user_data, indent=2, default=str)
            else:
                return user_data
                
        except Exception as e:
            st.error(f"Error exporting user data: {e}")
            return None

    def delete_user_data(self, username):
        """Delete all user data (GDPR compliance)"""
        try:
            cursor = self.conn.cursor()
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_result = cursor.fetchone()
            
            if not user_result:
                return False, "User not found"
            
            user_id = user_result[0]
            
            # Delete user data (in correct order due to foreign keys)
            cursor.execute("DELETE FROM symptom_history WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            self.conn.commit()
            return True, "User data deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting user data: {str(e)}"

# Create global database instance
user_db = UserDatabase()

# Optional: Run debug on import to verify database
if __name__ == "__main__":
    user_db.debug_database()
