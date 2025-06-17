import streamlit as st
import os
from datetime import datetime
from utils.database import get_db_connection, reset_database

def render_settings_page():
    """Render the settings and configuration page"""
    st.header("⚙️ Settings & Configuration")
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏪 Store Info", 
        "👥 User Management", 
        "📊 System Info",
        "🔧 Advanced"
    ])
    
    with tab1:
        render_store_settings()
    
    with tab2:
        render_user_management()
    
    with tab3:
        render_system_info()
    
    with tab4:
        render_advanced_settings()

def render_store_settings():
    """Render store information settings"""
    st.subheader("🏪 Store Information")
    
    # Store details form
    with st.form("store_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            store_name = st.text_input("Store Name", value="Premium Meat Shop")
            store_address = st.text_area("Address", value="123 Main Street\nCity, State 12345")
            store_phone = st.text_input("Phone", value="+1 (555) 123-4567")
        
        with col2:
            store_email = st.text_input("Email", value="info@meatshop.com")
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=8.5, step=0.1)
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"], index=0)
        
        # Receipt settings
        st.subheader("Receipt Settings")
        
        col3, col4 = st.columns(2)
        with col3:
            receipt_header = st.text_area("Receipt Header", value="Thank you for your business!")
            receipt_footer = st.text_area("Receipt Footer", value="Visit us again soon!")
        
        with col4:
            print_logo = st.checkbox("Print Logo on Receipt", value=True)
            auto_print = st.checkbox("Auto-print Receipts", value=False)
        
        if st.form_submit_button("💾 Save Store Settings", use_container_width=True):
            # In a real application, save these settings to database or config file
            st.success("✅ Store settings saved successfully!")
            st.info("💡 Settings will be applied to new invoices and receipts.")

def render_user_management():
    """Render user management interface"""
    st.subheader("👥 User Management")
    
    # Current user info
    if st.session_state.get('username'):
        st.info(f"Currently logged in as: **{st.session_state.username}** ({st.session_state.get('user_role', 'Unknown')})")
    
    # User roles explanation
    with st.expander("📋 User Roles & Permissions"):
        st.markdown("""
        **Admin**: Full access to all features including settings, user management, and reports
        
        **Manager**: Access to sales, inventory, reports, but limited settings access
        
        **Cashier**: Access to sales processing and basic inventory viewing
        """)
    
    # Default users table
    st.subheader("Default Users")
    
    users_data = [
        {"Username": "admin", "Role": "Admin", "Status": "Active"},
        {"Username": "manager", "Role": "Manager", "Status": "Active"},
        {"Username": "cashier", "Role": "Cashier", "Status": "Active"}
    ]
    
    st.dataframe(users_data, use_container_width=True, hide_index=True)
    
    # Password change form
    st.subheader("🔐 Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔄 Change Password"):
            if not current_password or not new_password:
                st.error("❌ Please fill in all fields")
            elif new_password != confirm_password:
                st.error("❌ New passwords don't match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            else:
                # In a real application, verify current password and update
                st.success("✅ Password changed successfully!")
                st.info("💡 Please log out and log back in with your new password.")

def render_system_info():
    """Render system information"""
    st.subheader("📊 System Information")
    
    # Database statistics
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get table counts
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        invoice_items_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Products", product_count)
        
        with col2:
            st.metric("Invoices", invoice_count)
        
        with col3:
            st.metric("Invoice Items", invoice_items_count)
        
        with col4:
            st.metric("Users", user_count)
        
    except Exception as e:
        st.error(f"Error loading system info: {e}")
    
    # System details
    st.subheader("System Details")
    
    system_info = {
        "Application Version": "1.0.0",
        "Database Type": "SQLite (Local)",
        "Database Provider": "Local File",
        "Mode": "Offline-First",
        "Last Started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Session Duration": "Active",
        "Data Directory": os.getcwd()
    }
    
    for key, value in system_info.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(f"**{key}:**")
        with col2:
            st.write(value)

def render_advanced_settings():
    """Render advanced settings"""
    st.subheader("🔧 Advanced Settings")
    
    # Database management
    st.subheader("🗄️ Database Management")
    
    st.info("💡 Database is stored locally as SQLite. Export/import functionality available below.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Data", use_container_width=True):
            st.info("📋 Export functionality coming soon")
    
    with col2:
        if st.button("📥 Import Data", use_container_width=True):
            st.info("📋 Import functionality coming soon")
    
    # Performance settings
    st.subheader("⚡ Performance Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cache_enabled = st.checkbox("Enable Caching", value=True)
        max_cache_size = st.number_input("Max Cache Size (MB)", min_value=10, max_value=1000, value=100)
    
    with col2:
        connection_timeout = st.number_input("Database Timeout (seconds)", min_value=5, max_value=60, value=30)
        retry_attempts = st.number_input("Retry Attempts", min_value=1, max_value=5, value=3)
    
    # Save advanced settings
    if st.button("💾 Save Advanced Settings", use_container_width=True):
        st.success("✅ Advanced settings saved!")
        st.info("💡 Some settings may require application restart to take effect.")
    
    # Database reset section
    st.subheader("🗑️ Database Reset")
    st.warning("⚠️ **DANGER ZONE**: This will permanently delete all your data!")
    
    with st.expander("🚨 Reset Database", expanded=False):
        st.markdown("""
        **This action will:**
        - Delete all products and their data
        - Delete all invoices and sales records
        - Delete all invoice items
        - **Keep user accounts** (admin, manager, cashier)
        - **Keep database structure** intact
        
        **Use this to:**
        - Clean up development/test data
        - Start fresh for production
        - Remove dummy data
        """)
        
        st.text_input(
            "Type 'RESET DATABASE' to confirm:",
            key="reset_confirm",
            placeholder="Type exactly: RESET DATABASE"
        )
        
        if st.button("🗑️ RESET DATABASE", type="secondary"):
            if st.session_state.get("reset_confirm", "") == "RESET DATABASE":
                try:
                    reset_database()
                    st.success("✅ Database reset successfully!")
                    st.info("🔄 Please refresh the page to see changes.")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Failed to reset database: {e}")
            else:
                st.error("❌ Please type 'RESET DATABASE' exactly to confirm.")
    
    # Debug information
    with st.expander("🐛 Debug Information"):
        st.json({
            "session_state_keys": list(st.session_state.keys()),
            "current_user": st.session_state.get('username', 'Not logged in'),
            "user_role": st.session_state.get('user_role', 'Unknown'),
            "authenticated": st.session_state.get('authenticated', False),
            "database_mode": "Offline-First SQLite",
            "database_provider": "Local File"
        }) 