import streamlit as st
from core.app_manager import AppManager
from controllers.user_controller import UserController
from views.components.header import render_header

def render_profile():
    '''Render trang profile'''
    app_manager = AppManager()
    user_controller = app_manager.get_controller(UserController)


    # Check authentication
    if not user_controller.is_authenticated():
        st.error("❌ Vui lòng đăng nhập trước")
        st.stop()

    # Header
    render_header("👤 Thông tin cá nhân")

    # User info
    user_profile = app_manager.state.user_profile
    # st.write(user_profile)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📋 Thông tin hiện tại")
        st.info(f"**Username:** {user_profile.get('username', app_manager.state.username)}")
        st.info(f"**Full Name:** {user_profile.get('fullname', 'Chưa cập nhật')}")
        st.info(f"**Email:** {user_profile.get('email', 'Chưa cập nhật')}")
        st.info(f"**Role:** {user_profile.get('role', 'user')}")
        st.info(f"**Online:** {user_profile.get('is_online', '0')}")
        st.info(f"**Created at:** {user_profile.get('created_at', 'N/A')}")
        st.info(f"**Updated at:** {user_profile.get('updated_at', 'N/A')}")
        st.info(f"**Last login:** {user_profile.get('last_login_at', '')}")

    with col2:
        st.markdown("### ✏️ Cập nhật thông tin")

        with st.form("profile_form"):
            full_name = st.text_input(
                label="Họ và tên",
                value=user_profile.get('fullname', ''),
                placeholder="Nhập họ và tên đầy đủ"
            )

            email = st.text_input(
                label="Email",
                value=user_profile.get('email', ''),
                placeholder="example@email.com"
            )

            position = st.text_input(
                label="Vị trí",
                value=user_profile.get('position', ''),
                placeholder="Vị trí làm việc"
            )

            address = st.text_input(
                label="Địa chỉ",
                value=user_profile.get('address', ''),
                placeholder="Địa chỉ làm việc"
            )

            role = st.text_input(
                label="Role",
                value=user_profile.get('role', ''),
                placeholder="Role"
            )

            is_active = st.number_input(
                label="Active",
                min_value=0,
                max_value=1,
                value=int(user_profile.get('is_active', '')),
                placeholder="Activate"
            )

            phone = st.text_input(
                label="Số điện thoại",
                value=user_profile.get('phone_number', ''),
                placeholder="0901234567"
            )

            bio = st.text_area(
                label="Giới thiệu",
                value=user_profile.get('udf1', ''),
                placeholder="Viết vài dòng về bạn...",
                height=100
            )

            submitted = st.form_submit_button("💾 Cập nhật", type="primary")

            if submitted:
                profile_data = {
                    'fullname': full_name,
                    'email': email,
                    'position': position,
                    'address': address,
                    'phone_number': phone,
                    'role': role,
                    'udf1': bio,
                    'is_active': is_active
                }

                if user_controller.update_profile(profile_data):
                    # st.success("✅ Cập nhật thông tin thành công!")
                    st.toast("✅ Cập nhật thông tin thành công!")
                    st.rerun()
                else:
                    st.error("❌ Lỗi khi cập nhật thông tin!")