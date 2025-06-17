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

def inject_custom_css():
    """Inject beautiful custom CSS for the entire application"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        padding-top: 0rem;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #5a6fd8, #6a4190);
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2d3748;
    }
    
    p, div, span {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -2rem 3rem -2rem;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Login Container */
    .login-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.1),
            0 8px 25px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.8);
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Credentials Card */
    .credentials-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        position: relative;
    }
    
    .credentials-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
        border-radius: 15px;
        pointer-events: none;
    }
    
    /* Role Cards */
    .role-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.08),
            0 2px 4px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .role-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.6) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .role-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 28px rgba(0, 0, 0, 0.12),
            0 6px 12px rgba(0, 0, 0, 0.08);
    }
    
    .role-card:hover::before {
        opacity: 1;
    }
    
    .admin-card { 
        border-left-color: #e53e3e;
        background: linear-gradient(135deg, #ffffff 0%, #fed7d7 100%);
    }
    .manager-card { 
        border-left-color: #dd6b20;
        background: linear-gradient(135deg, #ffffff 0%, #feebc8 100%);
    }
    .cashier-card { 
        border-left-color: #38a169;
        background: linear-gradient(135deg, #ffffff 0%, #c6f6d5 100%);
    }
    
    /* Feature Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 
            0 6px 20px rgba(0, 0, 0, 0.08),
            0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.8);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 25px rgba(102, 126, 234, 0.12),
            0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .feature-card h3 {
        color: #2d3748;
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.3;
    }
    
    .feature-card p {
        color: #718096;
        line-height: 1.4;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Welcome Text */
    .welcome-text {
        text-align: center;
        color: #2d3748;
        margin: 3rem 0;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .welcome-text h2 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .welcome-text p {
        font-size: 1.2rem;
        color: #718096;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    /* Sidebar Enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    /* Metrics */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        background: white;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border-radius: 10px;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        border-radius: 10px;
        border: none;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
        border-radius: 10px;
        border: none;
    }
    
    /* Navigation */
    .nav-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        margin: -1rem -1rem 1rem -1rem;
        border-radius: 0 0 15px 15px;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.6s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.8s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .feature-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8rem;
        }
        
        .feature-card {
            padding: 1rem 0.8rem;
            min-height: 100px;
        }
        
        .feature-card h3 {
            font-size: 0.9rem;
        }
        
        .feature-icon {
            font-size: 2rem;
        }
        
        .login-container {
            padding: 2rem;
        }
    }
    
    @media (max-width: 480px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def login_page():
    """Beautiful login interface with enhanced styling"""
    inject_custom_css()
    
    # Main header with animation
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🥩 Alwalima POS System</h1>
        <p>Professional Point of Sale Solution for Modern Businesses</p>
    </div>
    """, unsafe_allow_html=True)
    

    
    # Enhanced features showcase
    st.markdown("""
    <div class="feature-grid fade-in">
        <div class="feature-card">
            <div class="feature-icon">🧮</div>
            <h3>Lightning-Fast Sales</h3>
            <p>Process transactions with speed and precision using our intuitive visual interface designed for efficiency</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📦</div>
            <h3>Intelligent Inventory</h3>
            <p>Advanced stock management with real-time tracking, automated alerts, and predictive analytics</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Advanced Analytics</h3>
            <p>Comprehensive business intelligence with interactive dashboards and actionable insights</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>Enterprise Security</h3>
            <p>Military-grade security with role-based access control and audit trails for compliance</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        #st.markdown('<div class="login-container slide-in">', unsafe_allow_html=True)
        
        st.markdown("### 🔐 Sign In to Your Account")
        st.markdown("---")
        
        username = st.text_input(
            "👤 Username", 
            placeholder="Enter your username",
            help="Use one of the demo accounts below",
            key="username_input"
        )
        password = st.text_input(
            "🔑 Password", 
            type="password", 
            placeholder="Enter your password",
            help="Check the demo credentials below",
            key="password_input"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Sign In", use_container_width=True, type="primary"):
            if username and password:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = get_user_role(username)
                    st.success(f"✅ Welcome back, {username}! Redirecting to your dashboard...")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please verify your username and password.")
            else:
                st.warning("⚠️ Please fill in both username and password fields.")
        


def main_interface():
    """Enhanced main application interface"""
    inject_custom_css()
    
    # Enhanced header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1.5rem; margin: -1rem -2rem 2rem -2rem; 
                border-radius: 0 0 20px 20px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
        <h1 style="margin: 0; text-align: center; font-size: 2.5rem;">🥩 Meat Shop POS System</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced user info display
    if st.session_state.username:
        role_colors = {
            'admin': '#e53e3e',
            'manager': '#dd6b20', 
            'cashier': '#38a169'
        }
        role_color = role_colors.get(st.session_state.user_role, '#667eea')
        
        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 10px; 
                    margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    border-left: 4px solid {role_color};">
            <strong>👤 Logged in as:</strong> {st.session_state.username} 
            <span style="color: {role_color}; font-weight: 600;">({st.session_state.user_role.title()})</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced sidebar navigation
    with st.sidebar:
        st.markdown('<div class="nav-header">🧭 Navigation</div>', unsafe_allow_html=True)
        
        # Define available pages based on user role
        user_role = st.session_state.user_role
        
        if user_role == "cashier":
            available_pages = ["🧮 New Sale"]
        elif user_role == "manager":
            available_pages = [
                "🧮 New Sale",
                "📦 Stock Management", 
                "📊 Reports & Analytics"
            ]
        elif user_role == "admin":
            available_pages = [
                "🧮 New Sale",
                "📦 Stock Management", 
                "📊 Reports & Analytics",
                "⚙️ Settings"
            ]
        else:
            available_pages = ["🧮 New Sale"]
        
        page = st.selectbox("Select Page", available_pages, key="nav_select")
        
        st.markdown("---")
        
        # Enhanced quick stats
        st.markdown("### 📈 Today's Overview")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                FROM invoices 
                WHERE DATE(created_at) = ?
            """, (today,))
            
            result = cursor.fetchone()
            count = result[0]
            total = result[1]
            
            # Enhanced metrics display
            st.markdown(f"""
            <div class="metric-container">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; color: #667eea; margin-bottom: 0.5rem;">🛒</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #2d3748;">{count}</div>
                    <div style="color: #718096; font-size: 0.9rem;">Sales Today</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-container">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; color: #38a169; margin-bottom: 0.5rem;">💰</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #2d3748;">${total:.2f}</div>
                    <div style="color: #718096; font-size: 0.9rem;">Revenue Today</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"❌ Error loading statistics: {e}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.success("👋 Logged out successfully!")
            st.rerun()
    
    # Enhanced main content area with access control
    user_role = st.session_state.user_role
    
    if page == "🧮 New Sale":
        sale.render_sale_page()
    elif page == "📦 Stock Management":
        if user_role in ["manager", "admin"]:
            stock.render_stock_page()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%); 
                        border-radius: 15px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚫</div>
                <h2 style="color: #e53e3e; margin-bottom: 1rem;">Access Denied</h2>
                <p style="color: #c53030; font-size: 1.1rem;">You don't have permission to access Stock Management</p>
                <p style="color: #9c2828;">💡 Contact your administrator for access</p>
            </div>
            """, unsafe_allow_html=True)
    elif page == "📊 Reports & Analytics":
        if user_role in ["manager", "admin"]:
            reports.render_reports_page()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%); 
                        border-radius: 15px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚫</div>
                <h2 style="color: #e53e3e; margin-bottom: 1rem;">Access Denied</h2>
                <p style="color: #c53030; font-size: 1.1rem;">You don't have permission to access Reports & Analytics</p>
                <p style="color: #9c2828;">💡 Contact your administrator for access</p>
            </div>
            """, unsafe_allow_html=True)
    elif page == "⚙️ Settings":
        if user_role == "admin":
            settings.render_settings_page()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%); 
                        border-radius: 15px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚫</div>
                <h2 style="color: #e53e3e; margin-bottom: 1rem;">Access Denied</h2>
                <p style="color: #c53030; font-size: 1.1rem;">You don't have permission to access Settings</p>
                <p style="color: #9c2828;">💡 Contact your administrator for access</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_interface()

if __name__ == "__main__":
    main()