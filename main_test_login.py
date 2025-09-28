import streamlit as st
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


from utils.constants import PAGE_CONFIG
from core.app_manager import AppManager
from controllers.user_controller import UserController
from views.pages.dashboard import DashboardView
from views.pages.login import render_login
from views.pages.profile import render_profile
from views.pages.registry_user import render_registry_user
from views.components.sidebar_root import render_sidebar



def main():
    st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        page_icon=PAGE_CONFIG["page_icon"],
        layout=PAGE_CONFIG["layout"],
        initial_sidebar_state=PAGE_CONFIG["initial_sidebar_state"],
        menu_items=PAGE_CONFIG["menu_items"]
        )

    # Khởi tạo app manager
    app_manager = AppManager()
    user_controller = app_manager.get_controller(UserController)

    if not user_controller.is_authenticated():
        render_login()
    else:
        page = render_sidebar()
        
        if page == "Dashboard":
            DashboardView().render()
        elif page == "Profile":
            render_profile()
        elif page == "Registry User":
            render_registry_user()
        elif page == "Settings":
            # render_setting()
            st.markdown("---")
            st.write(vars(user_controller))
            st.markdown("---") 
            st.write(vars(user_controller.state)['_state'])
            st.markdown("---")
            st.write(vars(user_controller.user_model))

if __name__ == "__main__":
    main()
    #======================
    #lấy file requirements.xtx
    #pip freeze > requirements.txt
    #cài module thông qua requirements.txt
    #pip install -r requirements.txt
    #=====================
    #cài menu tạo biến môi trường ảo trước
     # pip install virtualenv
    #tạo biến môi trường ảo
    #python -m venv myproject_env
    #truy cap bien moi truong ao
    #.\myproject_env\Scripts\activate
    #====config git==========
    #git config --global user.name "Your Name"
    #git config --global user.email "your.email@example.com"
    #git init
    #git remote add https://github.com/biennn86/my_repository
    #==========một máy khác lấy repository để sủ dụng===========
    #git clone https://github.com/biennn86/streamlit_v2.git
    #git pull origin master

    #=====config ngrok=============
    #1.tải ngrok về chép vào biến môi trường path. Cách kiểm tra biến môi trường path trong win
    #Lưu ý phải mở cmd bằng chuột phải trên màn hình desktop
    #$env:Path
    #2. tạo tài khoản và lấy authtoken trên trang chủ ngrok
    #https://dashboard.ngrok.com/
    #3. kết nối với ngrok thông qua authtoken
    #ngrok authtoken 33JWi624uby1xwd7chKORZB6qgU_2ok7K7My6RGE7BMaCUzHi
    #4. sử dụng
    #mỏ cmd gõ
    #ngrok http [cổng cần kết nối với internet: streamlit đang dùng cổng 8501]
    #5. Note
    #Địa chỉ lưu ngrok trên máy tính của tôi
    #C:\Users\Admin\AppData\Local\Programs\Python\Python311
    #địa chỉ lưu token
    # Authtoken saved to configuration file: C:\Users\Admin\AppData\Local/ngrok/ngrok.yml
