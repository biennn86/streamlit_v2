import streamlit as st
from core.app_manager import AppManager
from controllers.user_controller import UserController

def render_login():
    '''Render trang đăng nhập'''
    app_manager = AppManager()
    user_controller = app_manager.get_controller(UserController)

    # Center the login form
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        # st.title("🔐 Đăng nhập")
        st.header("🔐 Login")
        # st.markdown("---")

        # Login form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter password")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_btn = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            with col_btn2:
                demo_btn = st.form_submit_button("🎯 Demo", use_container_width=True)

        # Handle login
        if login_btn and username and password:
            if user_controller.login(username, password):
                st.success("✅ Đăng nhập thành công!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Sai thông tin đăng nhập!")
                attempts = user_controller.get_login_attempts()
                if attempts >= 3:
                    st.warning(f"⚠️ Bạn đã thử {attempts} lần. Vui lòng thử lại sau.")

        # Handle demo login
        if demo_btn:
            if user_controller.login("demo", "demo123"):
                st.success("✅ Đăng nhập demo thành công!")
                st.rerun()
