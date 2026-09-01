import streamlit as st
from datetime import datetime
from models import get_session, Booking, Customer
import pandas as pd
import config


def show_admin_login():
    """Show admin login page"""
    st.title("🔐 Admin Login")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if st.button("Login"):
        if password == config.ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Invalid password")


def show_admin_dashboard():
    """Show admin dashboard"""
    st.title("📊 Admin Dashboard - Bookings Management")
    
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()
    
    # Get bookings from database
    session = get_session()
    bookings = session.query(Booking).all()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Bookings", "🔍 Search & Filter", "📊 Statistics"])
    
    with tab1:
        show_all_bookings(bookings, session)
    
    with tab2:
        show_search_filter(session)
    
    with tab3:
        show_statistics(bookings)
    
    session.close()


def show_all_bookings(bookings, session):
    """Display all bookings in a table"""
    st.subheader("All Bookings")
    
    if not bookings:
        st.info("No bookings found")
        return
    
    # Prepare data for display
    data = []
    for booking in bookings:
        customer = session.query(Customer).filter_by(customer_id=booking.customer_id).first()
        data.append({
            "Booking ID": booking.booking_id,
            "Customer Name": customer.name if customer else "Unknown",
            "Email": customer.email if customer else "N/A",
            "Phone": customer.phone if customer else "N/A",
            "Service Type": booking.booking_type,
            "Date": booking.booking_date,
            "Time": booking.booking_time,
            "Status": booking.status,
            "Email Sent": "✅" if booking.email_sent else "❌",
            "Created": booking.created_at.strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(data)
    
    # Display dataframe
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def show_search_filter(session):
    """Show search and filter options"""
    st.subheader("Search & Filter Bookings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_type = st.radio("Search by:", ["Name/Email", "Date", "Booking Type", "Status"])
    
    with col2:
        if search_type == "Name/Email":
            search_value = st.text_input("Enter customer name or email:")
            if search_value:
                customers = session.query(Customer).filter(
                    (Customer.name.ilike(f"%{search_value}%")) |
                    (Customer.email.ilike(f"%{search_value}%"))
                ).all()
                
                if customers:
                    bookings = []
                    for customer in customers:
                        customer_bookings = session.query(Booking).filter_by(
                            customer_id=customer.customer_id
                        ).all()
                        bookings.extend(customer_bookings)
                    
                    show_all_bookings(bookings, session)
                else:
                    st.info("No customers found")
        
        elif search_type == "Date":
            selected_date = st.date_input("Select date:")
            date_str = selected_date.strftime("%Y-%m-%d")
            bookings = session.query(Booking).filter_by(booking_date=date_str).all()
            show_all_bookings(bookings, session)
        
        elif search_type == "Booking Type":
            booking_type = st.selectbox(
                "Select booking type:",
                ["doctor", "salon", "hotel", "events", "classes", "restaurant", "gym", "spa"]
            )
            bookings = session.query(Booking).filter_by(booking_type=booking_type).all()
            show_all_bookings(bookings, session)
        
        elif search_type == "Status":
            status = st.selectbox("Select status:", ["confirmed", "pending", "cancelled"])
            bookings = session.query(Booking).filter_by(status=status).all()
            show_all_bookings(bookings, session)


def show_statistics(bookings):
    """Show booking statistics"""
    st.subheader("📈 Booking Statistics")
    
    if not bookings:
        st.info("No bookings to display")
        return
    
    # Create columns for KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bookings", len(bookings))
    
    with col2:
        confirmed = len([b for b in bookings if b.status == "confirmed"])
        st.metric("Confirmed", confirmed)
    
    with col3:
        pending = len([b for b in bookings if b.status == "pending"])
        st.metric("Pending", pending)
    
    with col4:
        emails_sent = len([b for b in bookings if b.email_sent])
        st.metric("Emails Sent", emails_sent)
    
    # Booking type distribution
    st.write("#### Bookings by Type")
    type_counts = {}
    for booking in bookings:
        booking_type = booking.booking_type
        type_counts[booking_type] = type_counts.get(booking_type, 0) + 1
    
    if type_counts:
        type_df = pd.DataFrame(list(type_counts.items()), columns=["Type", "Count"])
        st.bar_chart(type_df.set_index("Type"))
    
    # Status distribution
    st.write("#### Bookings by Status")
    status_counts = {}
    for booking in bookings:
        status = booking.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        status_df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
        st.pie_chart(status_df.set_index("Status")["Count"])


def admin_dashboard():
    """Main admin dashboard entry point"""
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        show_admin_login()
    else:
        show_admin_dashboard()
