import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.database import get_products, create_invoice, get_db_connection
from utils.invoice_gen import generate_invoice_pdf, generate_receipt_text

def render_sale_page():
    """Render the main sales/invoice page"""
    st.header("🧮 New Sale")
    
    # Initialize session state for current sale
    if 'current_invoice_items' not in st.session_state:
        st.session_state.current_invoice_items = []
    
    # Customer information section
    st.subheader("Customer Information (Optional)")
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
    
    with col2:
        customer_phone = st.text_input("Phone Number", placeholder="Enter phone number")
    
    st.divider()
    
    # Add items section
    st.subheader("Add Items to Sale")
    
    # Get products for display
    products = get_products()
    if not products:
        st.error("No products available. Please add products in Stock Management.")
        return
    
    # Initialize session state for product selection
    if 'selected_product_id' not in st.session_state:
        st.session_state.selected_product_id = None
    if 'show_product_picker' not in st.session_state:
        st.session_state.show_product_picker = False
    
    # Compact product selection interface
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Show current selection or button to open picker
        if st.session_state.selected_product_id:
            selected_product = next((p for p in products if p['id'] == st.session_state.selected_product_id), None)
            if selected_product:
                st.info(f"Selected: {selected_product['name']} - ${selected_product['price_per_kg']:.2f}/kg")
        
        if st.button("🖼️ Choose Product with Images", use_container_width=True):
            st.session_state.show_product_picker = True
            st.rerun()
    
    with col2:
        # Weight input
        if st.session_state.selected_product_id:
            selected_product = next((p for p in products if p['id'] == st.session_state.selected_product_id), None)
            if selected_product:
                weight = st.number_input(
                    "Weight (kg)",
                    min_value=0.001,
                    max_value=float(selected_product['stock_kg']),
                    value=1.0,
                    step=0.1,
                    format="%.3f",
                    key="weight_input"
                )
            else:
                weight = 1.0
        else:
            st.info("Select a product first")
            weight = 1.0
    
    with col3:
        # Add item button
        if st.session_state.selected_product_id:
            selected_product = next((p for p in products if p['id'] == st.session_state.selected_product_id), None)
            if selected_product and st.button("➕ Add Item", use_container_width=True, type="primary"):
                # Check stock availability
                if selected_product['stock_kg'] < weight:
                    st.error(f"Insufficient stock! Available: {selected_product['stock_kg']:.2f} kg")
                else:
                    total_price = weight * selected_product['price_per_kg']
                    item = {
                        'product_id': selected_product['id'],
                        'product_name': selected_product['name'],
                        'weight_kg': weight,
                        'price_per_kg': selected_product['price_per_kg'],
                        'total_price': total_price
                    }
                    
                    st.session_state.current_invoice_items.append(item)
                    st.success(f"Added {weight:.2f} kg of {selected_product['name']} to sale")
                    st.rerun()
        else:
            st.button("➕ Add Item", use_container_width=True, disabled=True)
    
    # Show product picker popup
    if st.session_state.show_product_picker:
        render_product_picker_popup(products)
    
    st.divider()
    
    # Current invoice items
    if st.session_state.current_invoice_items:
        st.subheader("Current Sale Items")
        
        # Create DataFrame for display
        items_data = []
        total_amount = 0
        
        for i, item in enumerate(st.session_state.current_invoice_items):
            items_data.append({
                'Product': item['product_name'],
                'Weight (kg)': f"{item['weight_kg']:.3f}",
                'Price/kg': f"${item['price_per_kg']:.2f}",
                'Total': f"${item['total_price']:.2f}",
                'Action': i  # For remove button
            })
            total_amount += item['total_price']
        
        df = pd.DataFrame(items_data)
        
        # Display items with remove buttons
        for i, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(row['Product'])
            with col2:
                st.write(row['Weight (kg)'])
            with col3:
                st.write(row['Price/kg'])
            with col4:
                st.write(row['Total'])
            with col5:
                if st.button("🗑️", key=f"remove_{i}", help="Remove item"):
                    st.session_state.current_invoice_items.pop(i)
                    st.rerun()
        
        st.divider()
        
        # Total and payment section
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            payment_method = st.selectbox(
                "Payment Method",
                ["cash", "card", "mobile_payment", "check"],
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        with col2:
            st.metric("Total Amount", f"${total_amount:.2f}")
        
        with col3:
            st.write("")  # Spacing
            complete_sale = st.button("💰 Complete Sale", use_container_width=True, type="primary")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Items", use_container_width=True):
                st.session_state.current_invoice_items = []
                st.rerun()
        
        with col2:
            if st.button("📄 Preview Receipt", use_container_width=True):
                preview_receipt(customer_name, customer_phone, payment_method)
        
        # Complete sale
        if complete_sale:
            success, result, invoice_id = create_invoice(
                customer_name or None,
                customer_phone or None,
                st.session_state.current_invoice_items,
                payment_method
            )
            
            if success:
                invoice_number = result
                st.success(f"✅ Sale completed! Invoice: {invoice_number}")
                
                # Generate PDF invoice
                try:
                    invoice_data = {
                        'invoice_number': invoice_number,
                        'customer_name': customer_name,
                        'customer_phone': customer_phone,
                        'payment_method': payment_method
                    }
                    
                    pdf_path = generate_invoice_pdf(invoice_data, st.session_state.current_invoice_items)
                    
                    # Provide download link
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download Invoice PDF",
                            data=pdf_file.read(),
                            file_name=f"invoice_{invoice_number}.pdf",
                            mime="application/pdf"
                        )
                
                except Exception as e:
                    st.warning(f"Invoice PDF generation failed: {e}")
                
                # Clear current sale
                st.session_state.current_invoice_items = []
                
                # Auto-refresh after 3 seconds
                st.balloons()
                
            else:
                st.error(f"❌ Sale failed: {result}")
    
    else:
        st.info("No items in current sale. Add items above to get started.")

def preview_receipt(customer_name, customer_phone, payment_method):
    """Show receipt preview in modal"""
    if not st.session_state.current_invoice_items:
        return
    
    invoice_data = {
        'invoice_number': 'PREVIEW',
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'payment_method': payment_method
    }
    
    receipt_text = generate_receipt_text(invoice_data, st.session_state.current_invoice_items)
    
    with st.expander("📄 Receipt Preview", expanded=True):
        st.code(receipt_text, language=None)

def render_product_picker_popup(products):
    """Render product picker popup with images"""
    st.markdown("---")
    
    # Header with close button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("🖼️ Choose Product")
    with col2:
        if st.button("❌ Close", key="close_picker"):
            st.session_state.show_product_picker = False
            st.rerun()
    
    # Group products by category
    categories = {}
    for product in products:
        category = product['category'] or 'Other'
        if category not in categories:
            categories[category] = []
        categories[category].append(product)
    
    # Display products by category in a more compact grid
    for category, category_products in categories.items():
        st.markdown(f"**{category}**")
        
        # Create columns for grid layout (3 products per row for better visibility)
        cols_per_row = 3
        for i in range(0, len(category_products), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(category_products):
                    product = category_products[i + j]
                    with col:
                        # Product image
                        image_path = product['image_path'] if product['image_path'] else ''
                        if image_path and os.path.exists(image_path):
                            st.image(image_path, use_column_width=True)
                        else:
                            # Placeholder if no image
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #f0f0f0;
                                    height: 120px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    border-radius: 5px;
                                    margin-bottom: 10px;
                                ">
                                    <span style="color: #666; font-size: 24px;">📦</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        
                        # Product details
                        st.markdown(f"**{product['name']}**")
                        st.markdown(f"💰 ${product['price_per_kg']:.2f}/kg")
                        st.markdown(f"📦 {product['stock_kg']:.1f} kg available")
                        
                        # Select button
                        if st.button(
                            "✅ Select This Product", 
                            key=f"pick_{product['id']}",
                            use_container_width=True,
                            type="primary"
                        ):
                            st.session_state.selected_product_id = product['id']
                            st.session_state.show_product_picker = False
                            st.success(f"Selected: {product['name']}")
                            st.rerun()
                else:
                    # Empty column for alignment
                    col.empty()
        
        st.markdown("---") 