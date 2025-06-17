import hashlib
import streamlit as st

def hash_password(password):
    """Hash a password using SHA256 (simplified for demo)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(password, hashed):
    """Check if password matches the hash"""
    return hash_password(password) == hashed

def authenticate_user(username, password):
    """Simple authentication - in production, use proper user management"""
    # Pre-computed SHA256 hashes for consistent authentication
    # admin123, cashier123, manager123
    default_users = {
        "admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",      # admin123
        "cashier": "b4c94003c562bb0d89535eca77f07284fe560fd48a7cc1ed99f0a56263d616ba",    # cashier123  
        "manager": "866485796cfa8d7c0cf7111640205b83076433547577511d81f8030ae99ecea5"     # manager123
    }
    
    if username in default_users:
        return check_password(password, default_users[username])
    
    return False

def get_user_role(username):
    """Get user role - simplified for demo"""
    roles = {
        "admin": "admin",
        "cashier": "cashier", 
        "manager": "manager"
    }
    
    return roles.get(username, "cashier") 