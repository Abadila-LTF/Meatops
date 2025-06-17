import streamlit as st
import os
from datetime import datetime
from utils.database import get_db_connection
from utils.auth import authenticate_user, get_user_role
from app_pages import sale, stock, reports, settings

# Page configuration
st.set_page_config(
    page_title="🥩 Meat Shop POS System",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'current_invoice_items' not in st.session_state:
        st.session_state.current_invoice_items = []

def login_page():
    """Beautiful login interface"""
    # Custom CSS for beautiful styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .login-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
    }
    
    .credentials-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .role-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .admin-card { border-left-color: #e74c3c; }
    .manager-card { border-left-color: #f39c12; }
    .cashier-card { border-left-color: #27ae60; }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 3px solid #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .welcome-text {
        text-align: center;
        color: #2c3e50;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🥩 Meat Shop POS System</h1>
        <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">Professional Point of Sale Solution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome section
    st.markdown("""
    <div class="welcome-text">
        <h2>Welcome to Your Business Dashboard</h2>
        <p>Sign in to access your personalized workspace and start managing your business efficiently.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features showcase
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🧮</div>
            <h3>Fast Sales Processing</h3>
            <p>Quick and efficient point of sale with visual product selection</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📦</div>
            <h3>Smart Inventory</h3>
            <p>Real-time stock management with low stock alerts</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Detailed Analytics</h3>
            <p>Comprehensive reports and business insights</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>Secure Access</h3>
            <p>Role-based permissions for team management</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("### 🔐 Sign In to Your Account")
        st.markdown("---")
        
        username = st.text_input(
            "👤 Username", 
            placeholder="Enter your username",
            help="Use one of the demo accounts below"
        )
        password = st.text_input(
            "🔑 Password", 
            type="password", 
            placeholder="Enter your password",
            help="Check the demo credentials below"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Sign In", use_container_width=True, type="primary"):
            if username and password:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = get_user_role(username)
                    st.success(f"✅ Welcome back, {username}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please check your username and password.")
            else:
                st.warning("⚠️ Please fill in both username and password fields.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Demo credentials section
        st.markdown('<div class="credentials-card">', unsafe_allow_html=True)
        st.markdown("### 🧪 Demo Accounts & Access Levels")
        st.markdown("*Use these credentials to explore different user roles:*")
        
        # Admin card
        st.markdown("""
        <div class="role-card admin-card">
            <h4>🔴 Administrator</h4>
            <strong>Username:</strong> admin | <strong>Password:</strong> admin123<br>
            <small>✅ Full system access including settings and user management</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Manager card
        st.markdown("""
        <div class="role-card manager-card">
            <h4>🟡 Manager</h4>
            <strong>Username:</strong> manager | <strong>Password:</strong> manager123<br>
            <small>✅ Sales, inventory management, and business reports</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Cashier card
        st.markdown("""
        <div class="role-card cashier-card">
            <h4>🟢 Cashier</h4>
            <strong>Username:</strong> cashier | <strong>Password:</strong> cashier123<br>
            <small>✅ Point of sale operations only</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main_interface():
    """Main application interface"""
    st.title("🥩 Meat Shop POS System")
    
    # Show current user info
    if st.session_state.username:
        st.markdown(f"**Logged in as:** {st.session_state.username} ({st.session_state.user_role})")
    
    # Sidebar navigation with role-based access control
    with st.sidebar:
        st.markdown("### Navigation")
        
        # Define available pages based on user role
        user_role = st.session_state.user_role
        
        if user_role == "cashier":
            # Cashiers only have access to New Sale
            available_pages = ["🧮 New Sale"]
        elif user_role == "manager":
            # Managers have access to sales, stock, and reports
            available_pages = [
                "🧮 New Sale",
                "📦 Stock Management", 
                "📊 Reports & Analytics"
            ]
        elif user_role == "admin":
            # Admins have access to everything
            available_pages = [
                "🧮 New Sale",
                "📦 Stock Management", 
                "📊 Reports & Analytics",
                "⚙️ Settings"
            ]
        else:
            # Default to cashier permissions for unknown roles
            available_pages = ["🧮 New Sale"]
        
        page = st.selectbox("Select Page", available_pages)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### Today's Summary")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get today's sales count and total
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                FROM invoices 
                WHERE DATE(created_at) = ?
            """, (today,))
            
            result = cursor.fetchone()
            count = result[0]
            total = result[1]
            
            st.metric("Sales Today", f"{count}")
            st.metric("Revenue Today", f"${total:.2f}")
            
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error loading stats: {e}")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.rerun()
    
    # Main content area with access control
    user_role = st.session_state.user_role
    
    if page == "🧮 New Sale":
        # All roles can access New Sale
        sale.render_sale_page()
    elif page == "📦 Stock Management":
        # Only managers and admins can access Stock Management
        if user_role in ["manager", "admin"]:
            stock.render_stock_page()
        else:
            st.error("🚫 Access Denied: You don't have permission to access Stock Management")
            st.info("💡 Contact your administrator for access")
    elif page == "📊 Reports & Analytics":
        # Only managers and admins can access Reports
        if user_role in ["manager", "admin"]:
            reports.render_reports_page()
        else:
            st.error("🚫 Access Denied: You don't have permission to access Reports & Analytics")
            st.info("💡 Contact your administrator for access")
    elif page == "⚙️ Settings":
        # Only admins can access Settings
        if user_role == "admin":
            settings.render_settings_page()
        else:
            st.error("🚫 Access Denied: You don't have permission to access Settings")
            st.info("💡 Contact your administrator for access")

def main():
    """Main application entry point"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_interface()

if __name__ == "__main__":
    main() 