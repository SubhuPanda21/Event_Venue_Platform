import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import time

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="🎪 Event Venue Platform",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com",
        'About': "# Event Venue Platform\nYour one-stop solution for event booking!"
    }
)

# ==================== API CONFIG ====================
API_BASE_URL = "http://localhost:5000/api"

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Headers */
    h1, h2, h3 {
        color: white !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Card Styling */
    .venue-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 15px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid #667eea;
    }
    
    .venue-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .metric-card h2 {
        color: #667eea !important;
        font-size: 2.5rem;
        margin: 10px 0;
    }
    
    .metric-card p {
        color: #666;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 15px;
        font-weight: 500;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Badge Styling */
    .badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 5px;
    }
    
    .badge-success {
        background: #10b981;
        color: white;
    }
    
    .badge-warning {
        background: #f59e0b;
        color: white;
    }
    
    .badge-info {
        background: #3b82f6;
        color: white;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 40px 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        margin: 20px 0;
    }
    
    .hero-section h1 {
        font-size: 3.5rem;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-section p {
        font-size: 1.5rem;
        color: white;
        margin-bottom: 30px;
    }
    
    /* Loading Animation */
    .loading-spinner {
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top: 4px solid white;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: white;
        margin-top: 50px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'refresh' not in st.session_state:
    st.session_state.refresh = 0

# ==================== HELPER FUNCTIONS ====================
def make_request(endpoint, method="GET", data=None, auth_required=False):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth_required and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"⚠️ Connection Error: {str(e)}")
        return None

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:,.2f}"

def format_date(date_string):
    """Format date string"""
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime("%B %d, %Y at %I:%M %p")
    except:
        return date_string

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 3rem; margin: 0;'>🎪</h1>
        <h2 style='margin: 10px 0;'>Event Platform</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Authentication Section
    if st.session_state.token is None:
        st.subheader("🔐 Authentication")
        
        auth_tab = st.radio("", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
        
        if auth_tab == "Login":
            with st.form("login_form", clear_on_submit=False):
                st.markdown("##### Login to Your Account")
                email = st.text_input("📧 Email", placeholder="your@email.com")
                password = st.text_input("🔒 Password", type="password", placeholder="••••••••")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Login", use_container_width=True)
                with col2:
                    demo = st.form_submit_button("Demo Login", use_container_width=True)
                
                if submit or demo:
                    if demo:
                        email = "admin@eventplatform.com"
                        password = "admin123"
                    
                    with st.spinner("Logging in..."):
                        data = {"email": email, "password": password}
                        response = make_request("/auth/login", "POST", data)
                        
                        if response and "token" in response:
                            st.session_state.token = response["token"]
                            st.session_state.user = response["user"]
                            st.success(f"✅ Welcome {response['user']['name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials!")
            
            st.info("💡 **Demo Accounts:**\n\n"
                   "👨‍💼 Admin: admin@eventplatform.com / admin123\n\n"
                   "🏢 Venue Owner: john@venues.com / password123")
        
        else:  # Register
            with st.form("register_form"):
                st.markdown("##### Create New Account")
                name = st.text_input("👤 Full Name", placeholder="John Doe")
                email = st.text_input("📧 Email", placeholder="your@email.com")
                password = st.text_input("🔒 Password", type="password", placeholder="••••••••")
                phone = st.text_input("📱 Phone", placeholder="+1-555-0000")
                role = st.selectbox("👔 Role", ["user", "venue_owner"])
                
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    with st.spinner("Creating account..."):
                        data = {
                            "name": name,
                            "email": email,
                            "password": password,
                            "phone": phone,
                            "role": role
                        }
                        response = make_request("/auth/register", "POST", data)
                        
                        if response and "token" in response:
                            st.session_state.token = response["token"]
                            st.session_state.user = response["user"]
                            st.success("✅ Registration successful!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Registration failed!")
    
    else:
        # User Info
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <div style='text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 10px;'>👤</div>
                <h3 style='margin: 5px 0;'>{st.session_state.user['name']}</h3>
                <p style='margin: 5px 0; opacity: 0.9;'>{st.session_state.user['email']}</p>
                <span class='badge badge-info'>{st.session_state.user['role'].upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.success("👋 Logged out successfully!")
            time.sleep(1)
            st.rerun()
        
        st.markdown("---")
        
        # Navigation Menu
        selected = option_menu(
            menu_title="Navigation",
            options=["🏠 Home", "🏢 Venues", "🎉 Events", "📅 My Bookings", "➕ Create Venue", "📊 Analytics"],
            icons=['house', 'building', 'calendar-event', 'calendar-check', 'plus-circle', 'graph-up'],
            menu_icon="cast",
            default_index=0,
        )

# ==================== MAIN CONTENT ====================

# Landing Page (Not Logged In)
if st.session_state.token is None:
    # Hero Section
    st.markdown("""
    <div class='hero-section'>
        <h1>🎪 Event Venue Platform</h1>
        <p>Find and book the perfect venue for your events!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    venues_data = make_request("/venues")
    events_data = make_request("/events")
    
    total_venues = venues_data.get("pagination", {}).get("total", 0) if venues_data else 0
    total_events = events_data.get("pagination", {}).get("total", 0) if events_data else 0
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <p>AVAILABLE VENUES</p>
            <h2>{total_venues}+</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <p>EVENTS HOSTED</p>
            <h2>{total_events}+</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <p>HAPPY CUSTOMERS</p>
            <h2>50K+</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Featured Venues
    st.markdown("<h2 style='text-align: center; margin: 30px 0;'>🌟 Featured Venues</h2>", unsafe_allow_html=True)
    
    if venues_data and "venues" in venues_data:
        cols = st.columns(3)
        for idx, venue in enumerate(venues_data["venues"][:6]):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class='venue-card'>
                    <h3>🏢 {venue['name']}</h3>
                    <p>📍 {venue['location']['city']}, {venue['location']['state']}</p>
                    <p>👥 Capacity: <strong>{venue['capacity']}</strong> people</p>
                    <p>💰 <strong>{format_currency(venue['pricePerHour'])}</strong>/hour</p>
                    <p>⭐ Rating: <strong>{venue['rating']}</strong>/5.0</p>
                    <span class='badge badge-info'>{venue['venueType'].upper()}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.info("👈 Please login or register in the sidebar to book venues and create events!")

# Authenticated User Content
else:
    if 'selected' not in locals():
        selected = "🏠 Home"
    
    # HOME PAGE
    if selected == "🏠 Home":
        st.markdown(f"<h1 style='text-align: center;'>Welcome back, {st.session_state.user['name']}! 👋</h1>", unsafe_allow_html=True)
        
        # Dashboard Stats
        col1, col2, col3, col4 = st.columns(4)
        
        venues_data = make_request("/venues")
        events_data = make_request("/events")
        bookings_data = make_request("/bookings", auth_required=True)
        
        total_venues = venues_data.get("pagination", {}).get("total", 0) if venues_data else 0
        total_events = events_data.get("pagination", {}).get("total", 0) if events_data else 0
        total_bookings = bookings_data.get("pagination", {}).get("total", 0) if bookings_data else 0
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <p>TOTAL VENUES</p>
                <h2>🏢 {total_venues}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <p>TOTAL EVENTS</p>
                <h2>🎉 {total_events}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <p>MY BOOKINGS</p>
                <h2>📅 {total_bookings}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <p>USER ROLE</p>
                <h2>⭐</h2>
                <span class='badge badge-success'>{st.session_state.user['role'].upper()}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recent Activity
        st.subheader("📊 Quick Overview")
        
        tab1, tab2 = st.tabs(["📈 Recent Venues", "🎪 Upcoming Events"])
        
        with tab1:
            if venues_data and "venues" in venues_data:
                for venue in venues_data["venues"][:5]:
                    with st.expander(f"🏢 {venue['name']} - {venue['location']['city']}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Description:** {venue['description']}")
                            st.write(f"**Location:** {venue['location']['address']}, {venue['location']['city']}")
                        with col2:
                            st.metric("Capacity", f"{venue['capacity']} 👥")
                            st.metric("Price/Hour", format_currency(venue['pricePerHour']))
        
        with tab2:
            if events_data and "events" in events_data:
                for event in events_data["events"][:5]:
                    with st.expander(f"🎉 {event['title']}", expanded=False):
                        st.write(f"**Type:** {event['eventType']}")
                        st.write(f"**Start:** {format_date(event['startDate'])}")
                        st.write(f"**Attendees:** {event['expectedAttendees']} people")
                        st.write(f"**Ticket Price:** {format_currency(event['ticketPrice'])}")
    
    # VENUES PAGE
    elif selected == "🏢 Venues":
        st.markdown("<h1 style='text-align: center;'>🏢 Browse Venues</h1>", unsafe_allow_html=True)
        
        # Filters
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                city_filter = st.text_input("🏙️ Filter by City", placeholder="e.g., New York")
            with col2:
                venue_type = st.selectbox("🎭 Venue Type", 
                    ["All", "conference", "wedding", "concert", "party", "corporate"])
            with col3:
                max_price = st.number_input("💰 Max Price/Hour", min_value=0, value=1000, step=50)
            with col4:
                min_capacity = st.number_input("👥 Min Capacity", min_value=0, value=0, step=10)
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (Real-time)", value=False)
        
        if auto_refresh:
            st.info("⚡ Real-time mode active - Updates every 5 seconds")
            time.sleep(5)
            st.rerun()
        
        # Build query
        query_params = "?limit=50"
        if city_filter:
            query_params += f"&city={city_filter}"
        if venue_type != "All":
            query_params += f"&venueType={venue_type}"
        if max_price:
            query_params += f"&maxPrice={max_price}"
        if min_capacity:
            query_params += f"&minCapacity={min_capacity}"
        
        # Fetch venues
        with st.spinner("Loading venues..."):
            venues_data = make_request(f"/venues{query_params}")
        
        if venues_data and "venues" in venues_data:
            st.success(f"✅ Found **{len(venues_data['venues'])}** venues")
            
            # Display venues in grid
            cols = st.columns(2)
            for idx, venue in enumerate(venues_data["venues"]):
                with cols[idx % 2]:
                    with st.container():
                        st.markdown(f"""
                        <div class='venue-card'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <h3>🏢 {venue['name']}</h3>
                                <span class='badge badge-info'>{venue['venueType'].upper()}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("View Details", expanded=False):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown(f"**📝 Description:**")
                                st.write(venue['description'])
                                st.markdown(f"**📍 Address:**")
                                st.write(f"{venue['location']['address']}, {venue['location']['city']}, {venue['location']['state']} {venue['location']['zipCode']}")
                                
                                if venue.get('amenities'):
                                    st.markdown(f"**✨ Amenities:**")
                                    amenities_html = " ".join([f"<span class='badge badge-success'>{a}</span>" for a in venue['amenities']])
                                    st.markdown(amenities_html, unsafe_allow_html=True)
                            
                            with col2:
                                st.metric("👥 Capacity", f"{venue['capacity']} people")
                                st.metric("💰 Price", f"{format_currency(venue['pricePerHour'])}/hr")
                                st.metric("⭐ Rating", f"{venue['rating']}/5.0")
                                st.metric("📊 Reviews", venue['reviewCount'])
                                
                                if st.button(f"📅 Book Now", key=f"book_{venue['_id']}", use_container_width=True):
                                    st.session_state.selected_venue_id = venue['_id']
                                    st.session_state.selected_venue_name = venue['name']
                                    
                                    # Booking Form in Modal
                                    with st.form(f"booking_form_{venue['_id']}"):
                                        st.subheader(f"Book {venue['name']}")
                                        
                                        start_date = st.date_input("Start Date", min_value=datetime.today())
                                        start_time = st.time_input("Start Time")
                                        
                                        end_date = st.date_input("End Date", min_value=datetime.today())
                                        end_time = st.time_input("End Time")
                                        
                                        guests = st.number_input("Number of Guests", min_value=1, max_value=venue['capacity'], value=10)
                                        special_requests = st.text_area("Special Requests", placeholder="Any special requirements...")
                                        
                                        submit_booking = st.form_submit_button("Confirm Booking", use_container_width=True)
                                        
                                        if submit_booking:
                                            booking_data = {
                                                "venue": venue['_id'],
                                                "startDate": f"{start_date}T{start_time}",
                                                "endDate": f"{end_date}T{end_time}",
                                                "guests": guests,
                                                "specialRequests": special_requests
                                            }
                                            
                                            response = make_request("/bookings", "POST", booking_data, auth_required=True)
                                            
                                            if response:
                                                st.success("✅ Booking created successfully!")
                                                st.balloons()
                                            else:
                                                st.error("❌ Failed to create booking. Please check availability.")
        else:
            st.warning("😔 No venues found matching your criteria.")
    
    # EVENTS PAGE
    elif selected == "🎉 Events":
        st.markdown("<h1 style='text-align: center;'>🎉 Upcoming Events</h1>", unsafe_allow_html=True)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            event_type_filter = st.selectbox("🎭 Event Type", 
                ["All", "conference", "wedding", "concert", "workshop", "seminar", "party"])
        with col2:
            status_filter = st.selectbox("📊 Status", 
                ["All", "pending", "confirmed", "cancelled", "completed"])
        
        # Build query
        query_params = "?limit=50"
        if event_type_filter != "All":
            query_params += f"&eventType={event_type_filter}"
        if status_filter != "All":
            query_params += f"&status={status_filter}"
        
        # Fetch events
        with st.spinner("Loading events..."):
            events_data = make_request(f"/events{query_params}")
        
        if events_data and "events" in events_data:
            st.success(f"✅ Found **{len(events_data['events'])}** events")
            
            # Timeline view
            for event in events_data["events"]:
                with st.container():
                    st.markdown(f"""
                    <div class='venue-card'>
                        <div style='display: flex; justify-content: space-between; align-items: start;'>
                            <div>
                                <h3>🎉 {event['title']}</h3>
                                <p style='color: #666; margin: 5px 0;'>{event['description'][:100]}...</p>
                            </div>
                            <div>
                                <span class='badge badge-info'>{event['eventType'].upper()}</span>
                                <span class='badge badge-{"success" if event["status"] == "confirmed" else "warning"}'>{event['status'].upper()}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📋 Event Details", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**📝 Description:**")
                            st.write(event['description'])
                            
                            st.markdown(f"**📅 Schedule:**")
                            st.write(f"Start: {format_date(event['startDate'])}")
                            st.write(f"End: {format_date(event['endDate'])}")
                            
                            if event.get('tags'):
                                st.markdown(f"**🏷️ Tags:**")
                                tags_html = " ".join([f"<span class='badge badge-info'>{tag}</span>" for tag in event['tags']])
                                st.markdown(tags_html, unsafe_allow_html=True)
                        
                        with col2:
                            st.metric("👥 Expected Attendees", event['expectedAttendees'])
                            st.metric("🎫 Ticket Price", format_currency(event['ticketPrice']))
                            st.metric("💰 Total Cost", format_currency(event['totalCost']))
                            st.metric("📊 Status", event['status'].upper())
                            
                            if event['isPublic']:
                                st.success("🌐 Public Event")
                            else:
                                st.info("🔒 Private Event")
        else:
            st.warning("😔 No events found.")
    
    # MY BOOKINGS PAGE
    elif selected == "📅 My Bookings":
        st.markdown("<h1 style='text-align: center;'>📅 My Bookings</h1>", unsafe_allow_html=True)
        
        # Tabs for different booking statuses
        tab1, tab2, tab3, tab4 = st.tabs(["📋 All", "⏳ Pending", "✅ Confirmed", "❌ Cancelled"])
        
        bookings_data = make_request("/bookings", auth_required=True)
        
        def display_bookings(bookings):
            if not bookings:
                st.warning("No bookings found.")
                return
            
            for booking in bookings:
                with st.container():
                    st.markdown(f"""
                    <div class='venue-card'>
                        <div style='display: flex; justify-content: space-between; align-items: start;'>
                            <div>
                                <h3>📅 Booking #{booking['_id'][:8].upper()}</h3>
                            </div>
                            <div>
                                <span class='badge badge-{"success" if booking["status"] == "confirmed" else "warning" if booking["status"] == "pending" else "info"}'>{booking['status'].upper()}</span>
                                <span class='badge badge-{"success" if booking["paymentStatus"] == "paid" else "warning"}'>{booking['paymentStatus'].upper()}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("View Booking Details", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            venue_name = booking.get('venue', {}).get('name', 'N/A') if isinstance(booking.get('venue'), dict) else 'N/A'
                            st.write(f"**🏢 Venue:** {venue_name}")
                            st.write(f"**📅 Start:** {format_date(booking['startDate'])}")
                            st.write(f"**📅 End:** {format_date(booking['endDate'])}")
                            st.write(f"**⏱️ Duration:** {booking['duration']} hours")
                            
                            if booking.get('specialRequests'):
                                st.write(f"**📝 Special Requests:** {booking['specialRequests']}")
                        
                        with col2:
                            st.metric("👥 Guests", booking['guests'])
                            st.metric("💰 Total Amount", format_currency(booking['totalAmount']))
                            st.metric("📊 Status", booking['status'].upper())
                            st.metric("💳 Payment", booking['paymentStatus'].upper())
                            
                            if booking['status'] == 'pending':
                                if st.button(f"❌ Cancel Booking", key=f"cancel_{booking['_id']}", use_container_width=True):
                                    st.warning("Cancellation feature coming soon!")
        
        if bookings_data and "bookings" in bookings_data:
            bookings = bookings_data["bookings"]
            
            with tab1:
                display_bookings(bookings)
            
            with tab2:
                pending = [b for b in bookings if b['status'] == 'pending']
                display_bookings(pending)
            
            with tab3:
                confirmed = [b for b in bookings if b['status'] == 'confirmed']
                display_bookings(confirmed)
            
            with tab4:
                cancelled = [b for b in bookings if b['status'] == 'cancelled']
                display_bookings(cancelled)
        else:
            st.info("📭 You don't have any bookings yet!")
            st.markdown("👉 Go to **Venues** to make your first booking!")
    
# CREATE VENUE PAGE
    elif selected == "➕ Create Venue":
     st.markdown("<h1 style='text-align: center;'>➕ Create New Venue</h1>", unsafe_allow_html=True)

    # Check user role
    if st.session_state.user['role'] not in ['venue_owner', 'admin']:
        st.error("🚫 Only venue owners and admins can create venues!")
        st.info("💡 Change your role to 'venue_owner' when registering to create venues.")
    else:
        with st.form("create_venue_form", clear_on_submit=True):
            st.subheader("📝 Venue Information")

            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("🏢 Venue Name *", placeholder="e.g., Grand Convention Center")
            with col2:
                venue_type = st.selectbox("🎭 Venue Type *", 
                    ["conference", "wedding", "concert", "party", "corporate", "other"])

            description = st.text_area("📝 Description *", 
                placeholder="Describe your venue...", height=100)

            st.subheader("📍 Location Details")
            col1, col2 = st.columns(2)
            with col1:
                address = st.text_input("🏠 Street Address *", placeholder="123 Main Street")
                city = st.text_input("🏙️ City *", placeholder="New York")
            with col2:
                state = st.text_input("🗺️ State *", placeholder="NY")
                zipcode = st.text_input("📮 Zip Code *", placeholder="10001")

            st.subheader("💰 Pricing & Capacity")
            col1, col2 = st.columns(2)
            with col1:
                capacity = st.number_input("👥 Capacity *", min_value=1, value=100, step=10)
            with col2:
                price = st.number_input("💵 Price per Hour *", min_value=0, value=200, step=10)

            st.subheader("✨ Amenities")
            amenities = st.multiselect(
                "Select Available Amenities",
                ["WiFi", "Parking", "Catering", "AV Equipment", "Accessibility", 
                 "Air Conditioning", "Security", "Kitchen", "Stage", "Dance Floor"]
            )

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button("🎉 Create Venue", use_container_width=True)

            if submitted:
                if not all([name, description, address, city, state, zipcode]):
                    st.error("❌ Please fill in all required fields!")
                else:
                    venue_data = {
                        "name": name,
                        "description": description,
                        "location": {
                            "address": address,
                            "city": city,
                            "state": state,
                            "zipCode": zipcode
                        },
                        "capacity": capacity,
                        "pricePerHour": price,
                        "venueType": venue_type,
                        "amenities": amenities
                    }

                    with st.spinner("Creating venue..."):
                        response = make_request("/venues", "POST", venue_data, auth_required=True)

                    if response:
                        st.success("✅ Venue created successfully!")
                        st.balloons()
                        st.json(response['venue'])
                    else:
                        st.error("❌ Failed to create venue. Please try again.")

# ANALYTICS PAGE
            elif selected == "📊 Analytics":
             st.markdown("<h1 style='text-align: center;'>📊 Analytics Dashboard</h1>", unsafe_allow_html=True)
        
        # Fetch data
        venues_data = make_request("/venues?limit=100")
        events_data = make_request("/events?limit=100")
        
        if venues_data and events_data:
            venues = venues_data.get("venues", [])
            events = events_data.get("events", [])
            
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <p>TOTAL VENUES</p>
                    <h2>{len(venues)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_price = sum([v['pricePerHour'] for v in venues]) / len(venues) if venues else 0
                st.markdown(f"""
                <div class='metric-card'>
                    <p>AVG PRICE/HOUR</p>
                    <h2>{format_currency(avg_price)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_capacity = sum([v['capacity'] for v in venues]) if venues else 0
                st.markdown(f"""
                <div class='metric-card'>
                    <p>TOTAL CAPACITY</p>
                    <h2>{total_capacity:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_rating = sum([v['rating'] for v in venues]) / len(venues) if venues else 0
                st.markdown(f"""
                <div class='metric-card'>
                    <p>AVG RATING</p>
                    <h2>{avg_rating:.1f} ⭐</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Venues by City
                city_counts = {}
                for venue in venues:
                    city = venue['location']['city']
                    city_counts[city] = city_counts.get(city, 0) + 1
                
                df_cities = pd.DataFrame(list(city_counts.items()), columns=['City', 'Count'])
                df_cities = df_cities.sort_values('Count', ascending=False).head(10)
                
                fig1 = px.bar(df_cities, x='City', y='Count', 
                             title='📍 Top 10 Cities by Venue Count',
                             color='Count',
                             color_continuous_scale='Viridis')
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Venues by Type
                type_counts = {}
                for venue in venues:
                    vtype = venue['venueType']
                    type_counts[vtype] = type_counts.get(vtype, 0) + 1
                
                fig2 = go.Figure(data=[go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=.4,
                    marker=dict(colors=px.colors.qualitative.Set3)
                )])
                fig2.update_layout(
                    title='🎭 Venues by Type',
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Price Distribution
            st.subheader("💰 Price Distribution")
            df_prices = pd.DataFrame([{'Venue': v['name'], 'Price': v['pricePerHour'], 'Capacity': v['capacity']} for v in venues])
            
            fig3 = px.scatter(df_prices, x='Capacity', y='Price', 
                            size='Price', color='Price',
                            hover_data=['Venue'],
                            title='Price vs Capacity Analysis',
                            color_continuous_scale='Sunset')
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.9)',
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Events Timeline
            if events:
                st.subheader("📅 Events Timeline")
                
                event_counts = {}
                for event in events:
                    try:
                        date = datetime.fromisoformat(event['startDate'].replace('Z', '+00:00')).date()
                        month = date.strftime('%Y-%m')
                        event_counts[month] = event_counts.get(month, 0) + 1
                    except:
                        pass
                
                df_timeline = pd.DataFrame(list(event_counts.items()), columns=['Month', 'Events'])
                df_timeline = df_timeline.sort_values('Month')
                
                fig4 = px.line(df_timeline, x='Month', y='Events',
                              title='📈 Events Over Time',
                              markers=True)
                fig4.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.9)',
                )
                st.plotly_chart(fig4, use_container_width=True)

# Helper function for displaying bookings
import streamlit as st

def display_bookings(bookings):
    st.subheader("Your Bookings")

    if not bookings:
        st.warning("No bookings found.")
        return

    for booking in bookings:
        st.write(f"Event: {booking['event_name']}")
        st.write(f"Date: {booking['date']}")
        st.write(f"Tickets: {booking['tickets']}")
        st.markdown("---")

    display_bookings(bookings)

    
    for booking in bookings:
        with st.container():
            st.markdown(f"""
            <div class='venue-card'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <h3>📅 Booking #{booking['_id'][:8].upper()}</h3>
                    </div>
                    <div>
                        <span class='badge badge-{"success" if booking["status"] == "confirmed" else "warning" if booking["status"] == "pending" else "info"}'>{booking['status'].upper()}</span>
                        <span class='badge badge-{"success" if booking["paymentStatus"] == "paid" else "warning"}'>{booking['paymentStatus'].upper()}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View Booking Details", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    venue_name = booking.get('venue', {}).get('name', 'N/A') if isinstance(booking.get('venue'), dict) else 'N/A'
                    st.write(f"**🏢 Venue:** {venue_name}")
                    st.write(f"**📅 Start:** {format_date(booking['startDate'])}")
                    st.write(f"**📅 End:** {format_date(booking['endDate'])}")
                    st.write(f"**⏱️ Duration:** {booking['duration']} hours")
                    
                    if booking.get('specialRequests'):
                        st.write(f"**📝 Special Requests:** {booking['specialRequests']}")
                
                with col2:
                    st.metric("👥 Guests", booking['guests'])
                    st.metric("💰 Total Amount", format_currency(booking['totalAmount']))
                    st.metric("📊 Status", booking['status'].upper())
                    st.metric("💳 Payment", booking['paymentStatus'].upper())
                    
                    if booking['status'] == 'pending':
                        if st.button(f"❌ Cancel Booking", key=f"cancel_{booking['_id']}", use_container_width=True):
                            # Cancel booking logic
                            st.warning("Cancellation feature coming soon!")

# Footer
st.markdown("""
<div class='footer'>
    <h3>🎪 Event Venue Platform</h3>
    <p>Made with ❤️ using Streamlit & Node.js</p>
    <p>© 2026 Event Venue Platform. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)