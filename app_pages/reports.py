import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_invoices, get_invoice_items, get_db_connection

def render_reports_page():
    """Render the reports and analytics page"""
    st.header("📊 Sales Reports & Analytics")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=7),
            max_value=datetime.now().date()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
    
    if start_date > end_date:
        st.error("Start date cannot be after end date")
        return
    
    # Tabs for different report types
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Overview", "📋 Invoice List", "🏆 Top Products", "📊 Analytics"])
    
    with tab1:
        render_sales_overview(start_date, end_date)
    
    with tab2:
        render_invoice_list(start_date, end_date)
    
    with tab3:
        render_top_products(start_date, end_date)
    
    with tab4:
        render_analytics(start_date, end_date)

def render_sales_overview(start_date, end_date):
    """Render sales overview metrics"""
    st.subheader("Sales Overview")
    
    # Get sales data for the period
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Daily sales query
    cursor.execute("""
        SELECT DATE(created_at) as sale_date, 
               COUNT(*) as invoice_count,
               SUM(total_amount) as daily_total
        FROM invoices
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY DATE(created_at)
        ORDER BY sale_date
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    daily_sales = cursor.fetchall()
    
    # Overall metrics
    cursor.execute("""
        SELECT COUNT(*) as total_invoices,
               SUM(total_amount) as total_revenue,
               AVG(total_amount) as avg_invoice_value
        FROM invoices
        WHERE DATE(created_at) BETWEEN ? AND ?
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    overall_stats = cursor.fetchone()
    conn.close()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Invoices",
            overall_stats[0] if overall_stats[0] else 0
        )
    
    with col2:
        st.metric(
            "Total Revenue",
            f"${overall_stats[1]:.2f}" if overall_stats[1] else "$0.00"
        )
    
    with col3:
        st.metric(
            "Average Invoice",
            f"${overall_stats[2]:.2f}" if overall_stats[2] else "$0.00"
        )
    
    with col4:
        days_in_period = (end_date - start_date).days + 1
        daily_avg = (overall_stats[1] / days_in_period) if overall_stats[1] and days_in_period > 0 else 0
        st.metric(
            "Daily Average",
            f"${daily_avg:.2f}"
        )
    
    # Daily sales chart
    if daily_sales:
        df_daily = pd.DataFrame(daily_sales, columns=['Date', 'Invoices', 'Revenue'])
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        
        st.subheader("Daily Sales Trend")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_daily['Date'],
            y=df_daily['Revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Daily Revenue Trend",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Invoice count chart
        fig2 = px.bar(
            df_daily,
            x='Date',
            y='Invoices',
            title="Daily Invoice Count",
            color='Invoices',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    else:
        st.info("No sales data found for the selected period.")

def render_invoice_list(start_date, end_date):
    """Render list of invoices"""
    st.subheader("Invoice List")
    
    # Get invoices for the period
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, invoice_number, customer_name, customer_phone,
               total_amount, payment_method, created_at
        FROM invoices
        WHERE DATE(created_at) BETWEEN ? AND ?
        ORDER BY created_at DESC
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    invoices = cursor.fetchall()
    conn.close()
    
    if not invoices:
        st.info("No invoices found for the selected period.")
        return
    
    # Convert to DataFrame
    df_invoices = pd.DataFrame(invoices, columns=[
        'ID', 'Invoice Number', 'Customer Name', 'Phone',
        'Total Amount', 'Payment Method', 'Created At'
    ])
    
    # Format data for display
    df_invoices['Total Amount'] = df_invoices['Total Amount'].apply(lambda x: f"${x:.2f}")
    df_invoices['Payment Method'] = df_invoices['Payment Method'].str.title()
    df_invoices['Customer Name'] = df_invoices['Customer Name'].fillna('Walk-in Customer')
    df_invoices['Phone'] = df_invoices['Phone'].fillna('N/A')
    
    # Search functionality
    search_term = st.text_input("🔍 Search invoices", placeholder="Search by invoice number, customer name...")
    
    if search_term:
        mask = (
            df_invoices['Invoice Number'].str.contains(search_term, case=False, na=False) |
            df_invoices['Customer Name'].str.contains(search_term, case=False, na=False)
        )
        df_invoices = df_invoices[mask]
    
    # Display invoices
    st.dataframe(
        df_invoices.drop('ID', axis=1),
        use_container_width=True,
        hide_index=True
    )
    
    # Invoice details expander
    if len(df_invoices) > 0:
        st.subheader("Invoice Details")
        
        invoice_options = {
            f"{row['Invoice Number']} - {row['Customer Name']} (${row['Total Amount']})": row['ID']
            for _, row in df_invoices.iterrows()
        }
        
        selected_invoice = st.selectbox("Select Invoice to View Details", list(invoice_options.keys()))
        
        if selected_invoice:
            invoice_id = invoice_options[selected_invoice]
            show_invoice_details(invoice_id)

def show_invoice_details(invoice_id):
    """Show detailed view of a specific invoice"""
    items = get_invoice_items(invoice_id)
    
    if items:
        st.write("**Invoice Items:**")
        
        items_df = pd.DataFrame(items, columns=['Product', 'Weight (kg)', 'Price/kg', 'Total'])
        items_df['Weight (kg)'] = items_df['Weight (kg)'].apply(lambda x: f"{x:.3f}")
        items_df['Price/kg'] = items_df['Price/kg'].apply(lambda x: f"${x:.2f}")
        items_df['Total'] = items_df['Total'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(items_df, use_container_width=True, hide_index=True)

def render_top_products(start_date, end_date):
    """Render top selling products"""
    st.subheader("Top Selling Products")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Top products by quantity
    cursor.execute("""
        SELECT ii.product_name,
               SUM(ii.weight_kg) as total_weight,
               COUNT(ii.id) as times_sold,
               SUM(ii.total_price) as total_revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        WHERE DATE(i.created_at) BETWEEN ? AND ?
        GROUP BY ii.product_name
        ORDER BY total_weight DESC
        LIMIT 10
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    top_products = cursor.fetchall()
    conn.close()
    
    if not top_products:
        st.info("No product sales data found for the selected period.")
        return
    
    # Create DataFrame
    df_products = pd.DataFrame(top_products, columns=[
        'Product', 'Total Weight (kg)', 'Times Sold', 'Total Revenue'
    ])
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top Products by Weight Sold**")
        
        fig = px.bar(
            df_products.head(5),
            x='Total Weight (kg)',
            y='Product',
            orientation='h',
            title="Top 5 Products by Weight",
            color='Total Weight (kg)',
            color_continuous_scale='Blues'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Top Products by Revenue**")
        
        fig2 = px.pie(
            df_products.head(5),
            values='Total Revenue',
            names='Product',
            title="Revenue Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed table
    st.write("**Detailed Product Performance**")
    
    # Format the DataFrame for display
    df_display = df_products.copy()
    df_display['Total Weight (kg)'] = df_display['Total Weight (kg)'].apply(lambda x: f"{x:.2f}")
    df_display['Total Revenue'] = df_display['Total Revenue'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

def render_analytics(start_date, end_date):
    """Render advanced analytics"""
    st.subheader("Advanced Analytics")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Payment method distribution
    cursor.execute("""
        SELECT payment_method, COUNT(*) as count, SUM(total_amount) as total
        FROM invoices
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY payment_method
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    payment_methods = cursor.fetchall()
    
    # Hourly sales pattern
    cursor.execute("""
        SELECT strftime('%H', created_at) as hour, 
               COUNT(*) as invoice_count,
               SUM(total_amount) as hourly_revenue
        FROM invoices
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY strftime('%H', created_at)
        ORDER BY hour
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    hourly_sales = cursor.fetchall()
    conn.close()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if payment_methods:
            st.write("**Payment Method Distribution**")
            
            df_payment = pd.DataFrame(payment_methods, columns=['Payment Method', 'Count', 'Total'])
            df_payment['Payment Method'] = df_payment['Payment Method'].str.title()
            
            fig = px.pie(
                df_payment,
                values='Count',
                names='Payment Method',
                title="Payment Methods Used"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if hourly_sales:
            st.write("**Hourly Sales Pattern**")
            
            df_hourly = pd.DataFrame(hourly_sales, columns=['Hour', 'Invoice Count', 'Revenue'])
            df_hourly['Hour'] = df_hourly['Hour'].astype(int)
            
            fig = px.line(
                df_hourly,
                x='Hour',
                y='Invoice Count',
                title="Sales by Hour of Day",
                markers=True
            )
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    if payment_methods or hourly_sales:
        st.subheader("Summary Statistics")
        
        if payment_methods:
            st.write("**Payment Methods:**")
            df_payment_display = pd.DataFrame(payment_methods, columns=['Payment Method', 'Count', 'Total Revenue'])
            df_payment_display['Payment Method'] = df_payment_display['Payment Method'].str.title()
            df_payment_display['Total Revenue'] = df_payment_display['Total Revenue'].apply(lambda x: f"${x:.2f}")
            st.dataframe(df_payment_display, use_container_width=True, hide_index=True)
        
        if hourly_sales:
            st.write("**Peak Hours:**")
            df_hourly_display = pd.DataFrame(hourly_sales, columns=['Hour', 'Invoice Count', 'Revenue'])
            df_hourly_display['Hour'] = df_hourly_display['Hour'].apply(lambda x: f"{int(x):02d}:00")
            df_hourly_display['Revenue'] = df_hourly_display['Revenue'].apply(lambda x: f"${x:.2f}")
            df_hourly_display = df_hourly_display.sort_values('Invoice Count', ascending=False)
            st.dataframe(df_hourly_display, use_container_width=True, hide_index=True) 