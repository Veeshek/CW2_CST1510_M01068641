
"""
UI helpers shared across all Streamlit pages (Week 9/10 polish).

Goal:
- One place for CSS + navigation bar (topbar)
- Consistent look across pages
- Avoid repeating code everywhere (cleaner + easier to maintain)
"""

import streamlit as st


def inject_global_css() -> None:
    """
    Inject global CSS for the whole app.

    What this does:
    - Hides Streamlit sidebar + hamburger menu (because we use our own top nav)
    - Hides Streamlit default header
    - Adds cleaner padding / spacing
    - Adds a small 'badge' component for the user info
    """
    st.markdown(
        """
        <style>
        /* Hide Streamlit sidebar + nav */
        [data-testid="stSidebarNav"] {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}

        /* Hide Streamlit header (top bar) */
        header[data-testid="stHeader"] {display: none !important;}

        /* Cleaner spacing */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2.2rem !important;
        }

        /* Simple badge style (user info on the right) */
        .badge{
            padding:7px 12px;
            border-radius:999px;
            border:1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.04);
            font-size: 13px;
        }

        /* Nice topbar buttons spacing */
        .topbar-wrap { margin-bottom: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def topbar(active: str) -> None:
    """
    Custom navigation bar (Week 9/10).

    active: name of the current page to highlight the correct button.

    Pages used:
    - Dashboard (02)
    - Analytics (03)
    - Manage (04)
    - AI (06)
    - Settings (05)

    Also shows the logged-in user badge + logout button.
    """
    user = st.session_state.get("user_info", {"username": "User", "role": "user"})

    st.markdown('<div class="topbar-wrap"></div>', unsafe_allow_html=True)

    left, right = st.columns([7, 3])

    # LEFT: navigation buttons
    with left:
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            if st.button(
                "🛡️ Dashboard",
                use_container_width=True,
                type="primary" if active == "Dashboard" else "secondary",
            ):
                st.switch_page("pages/02_Dashboard.py")

        with c2:
            if st.button(
                "📊 Analytics",
                use_container_width=True,
                type="primary" if active == "Analytics" else "secondary",
            ):
                st.switch_page("pages/03_Analytics.py")

        with c3:
            if st.button(
                "📝 Manage",
                use_container_width=True,
                type="primary" if active == "Manage" else "secondary",
            ):
                st.switch_page("pages/04_Manage_Data.py")

        with c4:
            if st.button(
                "🤖 AI",
                use_container_width=True,
                type="primary" if active == "AI" else "secondary",
            ):
                st.switch_page("pages/06_AI_Assistant.py")

        with c5:
            if st.button(
                "⚙️ Settings",
                use_container_width=True,
                type="primary" if active == "Settings" else "secondary",
            ):
                st.switch_page("pages/05_Settings.py")

    # RIGHT: user badge + logout
    with right:
        r1, r2 = st.columns([2, 1])

        with r1:
            st.markdown(
                f'<div class="badge">👤 {user["username"]} · {user["role"]}</div>',
                unsafe_allow_html=True,
            )

        with r2:
            if st.button("🚪", help="Logout", use_container_width=True):
                # Clear auth session state
                st.session_state.logged_in = False
                st.session_state.user_info = None

                # After logout, go back to main entry point
                st.switch_page("main.py")


def auth_guard() -> None:
    """
    Standard auth guard (Week 9 requirement).

    Why st.stop()?
    - If not logged in, we must block the page completely.
    """
    if not st.session_state.get("logged_in"):
        st.warning("⚠️ Please login first.")
        st.switch_page("pages/01_Login.py")
        st.stop()
