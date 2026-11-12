
import streamlit as st
import pandas as pd

from sqlalchemy import select, func, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database import SessionLocal
from models import Product, Customer


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Product & Customer Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }

    div.stButton > button {
        border-radius: 8px;
        min-height: 40px;
    }

    div[data-testid="stForm"] {
        border-radius: 12px;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- DATABASE HELPERS ----------------

def get_dashboard_data():
    with SessionLocal() as db:
        products = db.scalars(select(Product)).all()
        customers = db.scalars(select(Customer)).all()

        return {
            "total_products": len(products),
            "active_products": sum(p.is_active for p in products),
            "total_customers": len(customers),
            "active_customers": sum(c.is_active for c in customers),
            "inventory_value": sum(
                (p.price or 0) * (p.stock_quantity or 0)
                for p in products
            ),
            "low_stock": sum(
                p.stock_quantity <= 5
                for p in products
                if p.is_active
            ),
        }


def get_records(model):
    with SessionLocal() as db:
        return db.scalars(
            select(model).order_by(model.id.desc())
        ).all()


def save_record(record):
    try:
        with SessionLocal() as db:
            db.add(record)
            db.commit()
        return True

    except IntegrityError:
        st.error(
            "Duplicate value detected. Check the SKU or email "
            "and try again."
        )
    except SQLAlchemyError:
        st.error(
            "Database operation failed. Check your database "
            "connection and table schema."
        )

    return False


def update_record(model, record_id, values):
    try:
        with SessionLocal() as db:
            record = db.get(model, record_id)

            if record is None:
                st.error("Record not found.")
                return False

            for field, value in values.items():
                setattr(record, field, value)

            db.commit()
        return True

    except IntegrityError:
        st.error("SKU or email already exists.")
    except SQLAlchemyError:
        st.error("Unable to update the record. Check the database.")

    return False


def delete_record(model, record_id):
    try:
        with SessionLocal() as db:
            record = db.get(model, record_id)

            if record is None:
                st.error("Record not found.")
                return False

            db.delete(record)
            db.commit()

        return True

    except SQLAlchemyError:
        st.error("Unable to delete this record.")
        return False


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("📊 Admin Panel")
    st.caption("Product & Customer Management")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Products", "Customers"],
        label_visibility="visible",
    )

    st.divider()
    st.caption("Python • Streamlit • PostgreSQL")


# ---------------- DASHBOARD ----------------

if page == "Dashboard":
    st.title("Dashboard")
    st.caption("Overview of your business records")

    try:
        data = get_dashboard_data()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Products", data["total_products"])
        c2.metric("Active Products", data["active_products"])
        c3.metric("Total Customers", data["total_customers"])
        c4.metric("Active Customers", data["active_customers"])

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("Inventory Summary")
            st.metric(
                "Estimated Inventory Value",
                f"₹{data['inventory_value']:,.2f}",
            )
            st.metric("Low-stock Products", data["low_stock"])

        with right:
            st.subheader("Quick Actions")
            st.write("Manage your products and customer records.")

            if st.button("📦 Manage Products", use_container_width=True):
                st.session_state["page_redirect"] = "Products"
                st.rerun()

            if st.button("👥 Manage Customers", use_container_width=True):
                st.session_state["page_redirect"] = "Customers"
                st.rerun()

    except SQLAlchemyError:
        st.error(
            "Unable to load the dashboard. Verify your PostgreSQL "
            "connection and database schema."
        )


# ---------------- PRODUCTS ----------------

elif page == "Products":
    st.title("📦 Product Management")
    st.caption("Create, search, update and manage inventory")

    products = get_records(Product)

    tab1, tab2, tab3 = st.tabs([
        "📋 Product List",
        "➕ Add Product",
        "✏️ Edit / Delete",
    ])

    with tab1:
        search = st.text_input(
            "🔍 Search products",
            placeholder="Search name, SKU or category...",
        )

        active_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive"],
        )

        filtered = products

        if search:
            term = search.lower()
            filtered = [
                p for p in filtered
                if term in (p.name or "").lower()
                or term in (p.sku or "").lower()
                or term in (p.category or "").lower()
            ]

        if active_filter == "Active":
            filtered = [p for p in filtered if p.is_active]
        elif active_filter == "Inactive":
            filtered = [p for p in filtered if not p.is_active]

        product_rows = [
            {
                "ID": p.id,
                "Name": p.name,
                "SKU": p.sku,
                "Category": p.category,
                "Price (₹)": p.price,
                "Stock": p.stock_quantity,
                "Status": "Active" if p.is_active else "Inactive",
            }
            for p in filtered
        ]

        st.caption(f"{len(filtered)} product(s) found")

        if product_rows:
            st.dataframe(
                pd.DataFrame(product_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No products found.")

    with tab2:
        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("Product name")
            sku = st.text_input("SKU")
            category = st.text_input("Category")
            description = st.text_area("Description")
            col1, col2 = st.columns(2)

            with col1:
                price = st.number_input(
                    "Price (₹)", min_value=0.0, step=100.0
                )
            with col2:
                stock = st.number_input(
                    "Stock quantity", min_value=0, step=1
                )

            active = st.checkbox("Active product", value=True)

            submitted = st.form_submit_button(
                "➕ Create Product",
                use_container_width=True,
            )

            if submitted:
                if not all([name.strip(), sku.strip(), category.strip()]):
                    st.warning("Name, SKU and category are required.")
                elif price <= 0:
                    st.warning("Price must be greater than zero.")
                else:
                    record = Product(
                        name=name.strip(),
                        sku=sku.strip(),
                        category=category.strip(),
                        description=description.strip() or None,
                        price=price,
                        stock_quantity=int(stock),
                        is_active=active,
                    )

                    if save_record(record):
                        st.success("Product created successfully.")
                        st.rerun()

    with tab3:
        if not products:
            st.info("No products available to edit.")
        else:
            product_map = {
                f"{p.id} — {p.name} ({p.sku})": p.id
                for p in products
            }

            selected_label = st.selectbox(
                "Select product",
                list(product_map.keys()),
                key="edit_product_select",
            )
            selected_id = product_map[selected_label]
            selected = next(p for p in products if p.id == selected_id)

            with st.form("edit_product_form"):
                new_name = st.text_input(
                    "Name", value=selected.name
                )
                new_sku = st.text_input(
                    "SKU", value=selected.sku
                )
                new_category = st.text_input(
                    "Category", value=selected.category
                )
                new_description = st.text_area(
                    "Description", value=selected.description or ""
                )

                c1, c2 = st.columns(2)

                with c1:
                    new_price = st.number_input(
                        "Price (₹)",
                        min_value=0.0,
                        value=float(selected.price),
                        step=100.0,
                    )

                with c2:
                    new_stock = st.number_input(
                        "Stock quantity",
                        min_value=0,
                        value=int(selected.stock_quantity),
                        step=1,
                    )

                new_active = st.checkbox(
                    "Active",
                    value=selected.is_active,
                )

                update_clicked = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True,
                )

                if update_clicked:
                    if not all([
                        new_name.strip(),
                        new_sku.strip(),
                        new_category.strip(),
                    ]):
                        st.warning(
                            "Name, SKU and category are required."
                        )
                    elif new_price <= 0:
                        st.warning("Price must be greater than zero.")
                    else:
                        values = {
                            "name": new_name.strip(),
                            "sku": new_sku.strip(),
                            "category": new_category.strip(),
                            "description": new_description.strip() or None,
                            "price": new_price,
                            "stock_quantity": int(new_stock),
                            "is_active": new_active,
                        }

                        if update_record(Product, selected_id, values):
                            st.success("Product updated.")
                            st.rerun()

            st.divider()
            st.warning("Deleting a product permanently removes its record.")

            confirm_product_delete = st.checkbox(
                "I confirm that I want to delete this product.",
                key="confirm_product_delete",
            )

            if st.button(
                "🗑️ Delete Product",
                type="secondary",
                disabled=not confirm_product_delete,
            ):
                if delete_record(Product, selected_id):
                    st.success("Product deleted.")
                    st.rerun()


# ---------------- CUSTOMERS ----------------

elif page == "Customers":
    st.title("👥 Customer Management")
    st.caption("Manage customer information and account status")

    customers = get_records(Customer)

    tab1, tab2, tab3 = st.tabs([
        "📋 Customer List",
        "➕ Add Customer",
        "✏️ Edit / Delete",
    ])

    with tab1:
        search = st.text_input(
            "🔍 Search customers",
            placeholder="Search name, email, phone or city...",
        )

        status = st.selectbox(
            "Customer status",
            ["All", "Active", "Inactive"],
        )

        filtered = customers

        if search:
            term = search.lower()
            filtered = [
                c for c in filtered
                if any(
                    term in (value or "").lower()
                    for value in [
                        c.name, c.email, c.phone, c.city
                    ]
                )
            ]

        if status == "Active":
            filtered = [c for c in filtered if c.is_active]
        elif status == "Inactive":
            filtered = [c for c in filtered if not c.is_active]

        customer_rows = [
            {
                "ID": c.id,
                "Name": c.name,
                "Email": c.email,
                "Phone": c.phone,
                "City": c.city,
                "State": c.state,
                "Pincode": c.pincode,
                "Status": "Active" if c.is_active else "Inactive",
            }
            for c in filtered
        ]

        st.caption(f"{len(filtered)} customer(s) found")

        if customer_rows:
            st.dataframe(
                pd.DataFrame(customer_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No customers found.")

    with tab2:
        with st.form("add_customer_form", clear_on_submit=True):
            name = st.text_input("Full name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_input("Address")

            c1, c2, c3 = st.columns(3)

            with c1:
                city = st.text_input("City")
            with c2:
                state = st.text_input("State")
            with c3:
                pincode = st.text_input("Pincode")

            active = st.checkbox("Active customer", value=True)

            submitted = st.form_submit_button(
                "➕ Create Customer",
                use_container_width=True,
            )

            if submitted:
                required = [
                    name, email, phone, address,
                    city, state, pincode,
                ]

                if not all(value.strip() for value in required):
                    st.warning("Please fill in all customer fields.")
                elif "@" not in email or "." not in email.split("@")[-1]:
                    st.warning("Please enter a valid email address.")
                else:
                    record = Customer(
                        name=name.strip(),
                        email=email.strip().lower(),
                        phone=phone.strip(),
                        address=address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        pincode=pincode.strip(),
                        is_active=active,
                    )

                    if save_record(record):
                        st.success("Customer created successfully.")
                        st.rerun()

    with tab3:
        if not customers:
            st.info("No customers available to edit.")
        else:
            customer_map = {
                f"{c.id} — {c.name} ({c.email})": c.id
                for c in customers
            }

            selected_label = st.selectbox(
                "Select customer",
                list(customer_map.keys()),
                key="edit_customer_select",
            )
            selected_id = customer_map[selected_label]
            selected = next(
                c for c in customers if c.id == selected_id
            )

            with st.form("edit_customer_form"):
                new_name = st.text_input(
                    "Full name", value=selected.name
                )
                new_email = st.text_input(
                    "Email", value=selected.email
                )
                new_phone = st.text_input(
                    "Phone", value=selected.phone
                )
                new_address = st.text_input(
                    "Address", value=selected.address
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    new_city = st.text_input(
                        "City", value=selected.city
                    )
                with c2:
                    new_state = st.text_input(
                        "State", value=selected.state
                    )
                with c3:
                    new_pincode = st.text_input(
                        "Pincode", value=selected.pincode
                    )

                new_active = st.checkbox(
                    "Active",
                    value=selected.is_active,
                )

                update_clicked = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True,
                )

                if update_clicked:
                    required = [
                        new_name, new_email, new_phone, new_address,
                        new_city, new_state, new_pincode,
                    ]

                    if not all(value.strip() for value in required):
                        st.warning("Please fill in all customer fields.")
                    elif (
                        "@" not in new_email
                        or "." not in new_email.split("@")[-1]
                    ):
                        st.warning("Please enter a valid email.")
                    else:
                        values = {
                            "name": new_name.strip(),
                            "email": new_email.strip().lower(),
                            "phone": new_phone.strip(),
                            "address": new_address.strip(),
                            "city": new_city.strip(),
                            "state": new_state.strip(),
                            "pincode": new_pincode.strip(),
                            "is_active": new_active,
                        }

                        if update_record(Customer, selected_id, values):
                            st.success("Customer updated.")
                            st.rerun()

            st.divider()
            st.warning("Deleting a customer permanently removes the record.")

            confirm_customer_delete = st.checkbox(
                "I confirm that I want to delete this customer.",
                key="confirm_customer_delete",
            )

            if st.button(
                "🗑️ Delete Customer",
                disabled=not confirm_customer_delete,
            ):
                if delete_record(Customer, selected_id):
                    st.success("Customer deleted.")
                    st.rerun()
