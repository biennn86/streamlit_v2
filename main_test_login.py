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
    #lấy file requirements.xtx
    #pip freeze > requirements.txt
    #cài module thông qua requirements.txt
    #pip install -r requirements.txt
    #tạo biến môi trường ảo
    #python -m venv myproject_env
    #====config git==========
    #git config --global user.name "Your Name"
    #git config --global user.email "your.email@example.com"
    #git init
    #git remote add https://github.com/biennn86/my_repository
    #==========một máy khác lấy repository để sủ dụng===========
    #git clone htts của repository
    #git pull origin master
    