import streamlit as st
from core.app_manager import AppManager
from controllers.user_controller import UserController
from views.components.header import render_header

def render_registry_user():
    '''Render trang registry_user'''
    app_manager = AppManager()
    user_controller = app_manager.get_controller(UserController)

    # Check authentication
    if not user_controller.is_authenticated():
        st.error("❌ Vui lòng đăng nhập trước")
        st.stop()

    # Header
    render_header("👤 Tạo mới user")

    # User info
    user_profile = app_manager.state.user_profile

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        st.markdown("### Nhập thông tin user cần đăng ký")

        with st.form('registry_user'):
            username = st.text_input(
                label='Username',
                value='',
                placeholder='Enter username'
            )

            password = st.text_input(
                label='Password',
                value='',
                placeholder='Enter password'
            )

            email = st.text_input(
                label='Email',
                value='',
                placeholder='Enter email'
            )

            fullname = st.text_input(
                label='Họ Và Tên',
                value='',
                placeholder='Enter fullname'
            )

            position = st.text_input(
                label='Vị Trí Làm Việc',
                value='',
                placeholder='Enter position'
            )

            address = st.text_input(
                label='Địa Chỉ Làm Việc',
                value='',
                placeholder='Enter address'
            )

            phone_number = st.text_input(
                label='Số Điện Thoại',
                value='',
                placeholder='Enter phone number'
            )

            role = st.text_input(
                label='Role',
                value='',
                placeholder='Enter role'
            )

            is_active = st.number_input(
                label='Active',
                min_value=0,
                max_value=1,
                placeholder='Enter activate (0|1)'
            )

            udf1 = st.text_area(
                label='Giới thiệu',
                value='',
                placeholder='Viết vài dòng về bạn...',
                height=100
            )

            submitted = st.form_submit_button('Đăng Ký', type='primary')

            if submitted:
                profile_data = {
                    'username': username.lower(),
                    'password_hash': password,
                    'email': email,
                    'fullname': fullname,
                    'position': position,
                    'address': address,
                    'phone_number': phone_number,
                    'role': role,
                    'udf1': udf1,
                    'is_active': is_active
                }

                if user_controller.register_user(profile_data):
                    # st.success("✅ Cập nhật thông tin thành công!")
                    st.toast("✅ Đăng ký thông tin user thành công!")
                    st.rerun()
                else:
                    st.error("❌ Lỗi khi đăng ký usser!")