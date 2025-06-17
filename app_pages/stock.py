import streamlit as st
import pandas as pd
import os
from PIL import Image
from utils.database import get_products, add_product, update_stock, get_low_stock_products

def render_stock_page():
    """Render the stock management page"""
    st.header("📦 Stock Management")
    
    # Tabs for different stock operations
    tab1, tab2, tab3 = st.tabs(["📊 Current Stock", "➕ Add Product", "⚠️ Low Stock Alerts"])
    
    with tab1:
        render_current_stock()
    
    with tab2:
        render_add_product()
    
    with tab3:
        render_low_stock_alerts()

def render_current_stock():
    """Render current stock levels"""
    st.subheader("📦 Current Stock Levels")
    
    # Get all products
    products = get_products()
    
    if not products:
        st.info("No products found. Add some products to get started.")
        return
    
    # Convert to DataFrame for better display
    stock_data = []
    for product in products:
        # SQLite with Row factory returns dictionary-like objects
        product_id = product['id']
        name = product['name']
        price_per_kg = product['price_per_kg']
        stock_kg = product['stock_kg']
        category = product['category']
        description = product['description']
        image_path = product['image_path'] if product['image_path'] else ''
        
        # Set a default minimum threshold for display
        min_threshold = 5.0  # Default threshold
        
        # Determine stock status
        if stock_kg <= min_threshold:
            status = "🔴 Low"
        elif stock_kg <= min_threshold * 2:
            status = "🟡 Medium"
        else:
            status = "🟢 Good"
        
        # Check if image exists
        has_image = "📷 Yes" if image_path and os.path.exists(image_path) else "❌ No"
        
        stock_data.append({
            'ID': product_id,
            'Product Name': name,
            'Category': category,
            'Current Stock (kg)': f"{stock_kg:.2f}",
            'Min Threshold (kg)': f"{min_threshold:.2f}",
            'Price/kg': f"${price_per_kg:.2f}",
            'Status': status,
            'Has Image': has_image
        })
    
    df = pd.DataFrame(stock_data)
    
    # Display with search and filter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search products", placeholder="Enter product name or category")
    
    with col2:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(df['Category'].unique())
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Product Name'].str.contains(search_term, case=False) |
            filtered_df['Category'].str.contains(search_term, case=False)
        ]
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['Category'] == category_filter]
    
    # Display the table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Product details section
    st.subheader("📋 Product Details")
    if products:
        product_names = [f"{p['name']} (ID: {p['id']})" for p in products]
        selected_product_detail = st.selectbox(
            "Select product to view details",
            options=product_names,
            key="product_detail_select"
        )
        
        if selected_product_detail:
            # Find the selected product
            selected_id = int(selected_product_detail.split("ID: ")[1].rstrip(")"))
            selected_prod = next((p for p in products if p['id'] == selected_id), None)
            
            if selected_prod:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Display product image
                    image_path = selected_prod['image_path'] if selected_prod['image_path'] else ''
                    if image_path and os.path.exists(image_path):
                        st.image(image_path, caption="Product Image", width=200)
                    else:
                        st.markdown(
                            """
                            <div style="
                                background-color: #f0f0f0;
                                height: 150px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                border-radius: 5px;
                                margin-bottom: 10px;
                            ">
                                <span style="color: #666; font-size: 24px;">📦 No Image</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                with col2:
                    # Display product information
                    st.markdown(f"**Product Name:** {selected_prod['name']}")
                    st.markdown(f"**Category:** {selected_prod['category']}")
                    st.markdown(f"**Price per kg:** ${selected_prod['price_per_kg']:.2f}")
                    st.markdown(f"**Current Stock:** {selected_prod['stock_kg']:.2f} kg")
                    if selected_prod['description']:
                        st.markdown(f"**Description:** {selected_prod['description']}")
                    else:
                        st.markdown("**Description:** No description available")
    
    st.divider()
    
    # Stock update section
    st.subheader("Update Stock")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Product selection for stock update - using dictionary access
        product_options = {f"{p['name']} (Current: {p['stock_kg']:.2f} kg)": p['id'] for p in products}
        selected_product = st.selectbox(
            "Select Product to Update",
            options=list(product_options.keys())
        )
    
    with col2:
        new_quantity = st.number_input(
            "New Quantity (kg)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f"
        )
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        update_button = st.button("🔄 Update Stock", use_container_width=True)
    
    if update_button and selected_product:
        product_id = product_options[selected_product]
        success = update_stock(product_id, new_quantity)
        
        if success:
            st.success(f"✅ Stock updated successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to update stock")

def render_add_product():
    """Render add new product form"""
    st.subheader("Add New Product")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name *", placeholder="e.g., Premium Beef Cut")
            category = st.selectbox(
                "Category *",
                ["Beef", "Chicken", "Pork", "Fish", "Lamb", "Turkey", "Other"]
            )
            price_per_kg = st.number_input(
                "Price per kg ($) *",
                min_value=0.01,
                value=10.00,
                step=0.01,
                format="%.2f"
            )
        
        with col2:
            unit = st.selectbox("Unit", ["kg", "lb", "piece"], index=0)
            initial_stock = st.number_input(
                "Initial Stock Quantity",
                min_value=0.0,
                value=0.0,
                step=0.1,
                format="%.2f"
            )
            min_threshold = st.number_input(
                "Minimum Stock Threshold",
                min_value=0.0,
                value=5.0,
                step=0.1,
                format="%.2f"
            )
        
        description = st.text_area("Description (Optional)", placeholder="Product description...")
        
        # Image upload section
        st.subheader("📷 Product Image")
        uploaded_file = st.file_uploader(
            "Upload Product Image (Optional)",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image for this product. Recommended size: 300x200 pixels"
        )
        
        # Show image preview if uploaded
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            # Resize image to standard size for consistency
            image = image.resize((300, 200), Image.Resampling.LANCZOS)
            st.image(image, caption="Product Image Preview", width=200)
        
        submitted = st.form_submit_button("➕ Add Product", use_container_width=True)
        
        if submitted:
            if not product_name or not category or price_per_kg <= 0:
                st.error("Please fill in all required fields with valid values.")
            else:
                try:
                    # Handle image upload
                    image_path = ""
                    if uploaded_file is not None:
                        # Create products_images directory if it doesn't exist
                        os.makedirs('products_images', exist_ok=True)
                        
                        # Generate filename based on product name
                        safe_name = product_name.lower().replace(' ', '_').replace('/', '_')
                        image_filename = f"{safe_name}.jpg"
                        image_path = f"products_images/{image_filename}"
                        
                        # Save the uploaded image
                        image = Image.open(uploaded_file)
                        # Resize to standard size and save as JPEG
                        image = image.resize((300, 200), Image.Resampling.LANCZOS)
                        # Convert to RGB if it's RGBA (PNG with transparency)
                        if image.mode == 'RGBA':
                            image = image.convert('RGB')
                        image.save(image_path, 'JPEG', quality=95)
                    
                    # Add product to database
                    product_id = add_product(
                        product_name,
                        price_per_kg,
                        initial_stock,
                        category,
                        description,
                        image_path
                    )
                    st.success(f"✅ Product '{product_name}' added successfully!")
                    if image_path:
                        st.success(f"📷 Product image saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add product: {str(e)}")

def render_low_stock_alerts():
    """Render low stock alerts"""
    st.subheader("⚠️ Low Stock Alerts")
    
    low_stock_products = get_low_stock_products()
    
    if not low_stock_products:
        st.success("🎉 All products are well stocked!")
        return
    
    st.warning(f"⚠️ {len(low_stock_products)} product(s) need restocking")
    
    # Display low stock products
    for product in low_stock_products:
        # SQLite with Row factory returns dictionary-like objects
        product_name = product['name']
        current_qty = product['stock_kg']
        min_threshold = 5.0  # Default threshold since we don't store this in DB
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{product_name}**")
            
            with col2:
                st.metric("Current", f"{current_qty:.2f} kg")
            
            with col3:
                st.metric("Minimum", f"{min_threshold:.2f} kg")
            
            # Progress bar showing stock level
            progress = min(current_qty / min_threshold, 1.0) if min_threshold > 0 else 0
            st.progress(progress)
            
            if current_qty == 0:
                st.error("🚨 OUT OF STOCK")
            elif current_qty < min_threshold * 0.5:
                st.error("🔴 CRITICALLY LOW")
            else:
                st.warning("🟡 LOW STOCK")
            
            st.divider()
    
    # Quick restock section
    st.subheader("Quick Restock")
    
    if low_stock_products:
        product_names = [p['name'] for p in low_stock_products]
        selected_product_name = st.selectbox("Select Product to Restock", product_names)
        
        col1, col2 = st.columns(2)
        
        with col1:
            restock_qty = st.number_input(
                "Restock Quantity (kg)",
                min_value=0.1,
                value=10.0,
                step=0.1,
                format="%.2f"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("📦 Restock Now", use_container_width=True):
                # Find product ID
                products = get_products()
                product_id = None
                current_stock = 0
                
                for product in products:
                    if product['name'] == selected_product_name:
                        product_id = product['id']
                        current_stock = product['stock_kg']
                        break
                
                if product_id:
                    new_quantity = current_stock + restock_qty
                    success = update_stock(product_id, new_quantity)
                    
                    if success:
                        st.success(f"✅ Restocked {selected_product_name} with {restock_qty:.2f} kg")
                        st.rerun()
                    else:
                        st.error("❌ Failed to restock product") 