import streamlit as st
from core.app_manager import AppManager
from controllers.user_controller import UserController

def render_sidebar():
    '''Render sidebar navigation'''
    app_manager = AppManager()
    user_controller = app_manager.get_controller(UserController)


    with st.sidebar:
        # st.title("🚀 Navigation_Tui Them Vào")

        # User info
        if user_controller.is_authenticated():
            # st.markdown("---")
            st.write(f"👤 Wellcome: **{app_manager.state.username}**")
            # st.write(f"🏷️ Role: {app_manager.state.user_role}")

            # Logout button
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                user_controller.logout()
                st.rerun()

            st.markdown("---")

            # Phân quyền được vào page theo role
            role_user = user_controller.state.user_role
            if role_user in ['guest', 'viewer', 'edit']:
                pages = ["Dashboard"]
            elif role_user in ['admin']:
                pages = ["Dashboard", "Bintobin", "Profile", "Settings", "Registry User"]

            # Navigation menu
            if user_controller.has_role('admin'):
                pages.append("Admin")

            selected_page = st.selectbox(
                "Select Pages:",
                pages,
                key="sidebar_page_select"
            )

            st.markdown("---")


            return selected_page
        else:
            st.info("Vui lòng đăng nhập để sử dụng")
            return "Login"