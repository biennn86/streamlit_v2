import streamlit as st
import pandas as pd
from utils.constants import StatusBorder
from views.components.sidebat_menu_btb import *
from models.inventory_model import InventoryModel
from models.bintobin_model import BintobinModel
from controllers.bintobin_controller import BintobinController

from config.settings import AppConfig
from views.style.style_css import load_custom_css

class BintobinView:
    def __init__(self):
        inventory_model = InventoryModel()
        bintobin_model = BintobinModel(inventory_model)
        self.bintobin_controller = BintobinController(bintobin_model)

    @staticmethod
    def show_error(message: str):
        # st.error(message)
        st.toast(message, icon="🚨")

    @staticmethod
    def show_warning(message: str):
        # st.warning(message)
        st.toast(message, icon="⚠️")

    @staticmethod
    def show_success(message: str):
        st.toast(message, icon="✔️")

    def import_inv_prime_csv(self):
        link_ton_kho_csv = import_inv_prime_csv_btb()
        status_file_uploader_inv_btb = self.bintobin_controller.state.get(AppConfig.StateKeys.FILE_UPLOADER_INV_BTB, False)
        if all([link_ton_kho_csv, status_file_uploader_inv_btb]):
            is_valid, meesage = self.bintobin_controller.import_file_tonkho_prime(link_ton_kho_csv)
            if is_valid:
                self.show_success(message=meesage)
            else:
                self.show_error(message=meesage)
                st.stop()

    def import_file_demand(self):
        link_file_demand = import_demand_excel_btb()
        status_file_uploader_demand = self.bintobin_controller.state.get(AppConfig.StateKeys.FILE_UPLOADER_DEMAND, False)
        if all([link_file_demand, status_file_uploader_demand]):
            is_valid, meesage = self.bintobin_controller.import_file_demand(link_file_demand)
            if is_valid:
                self.show_success(message=meesage)
            else:
                self.show_error(message=meesage)
                st.stop()
            

    def run_bintobin(self):
        button_btb = sidebar_button_btb()
       
        if button_btb:
            current_strategy = self.bintobin_controller.state.get(AppConfig.StateKeys.STRATEGY_BTB, "standard")
            df_inv_btb = self.bintobin_controller.state.get(AppConfig.StateKeys.INV_BTB, pd.DataFrame())
            dict_demand = self.bintobin_controller.state.get(AppConfig.StateKeys.DEMAND_DATA, {})
            if current_strategy == "standard":
                is_valid, meesage = self.bintobin_controller.run_bintobin_standard(df_inv_btb, dict_demand)
                if is_valid:
                    self.show_success(message=meesage)
                else:
                    self.show_error(message=meesage)
                    st.stop()
            elif current_strategy == "greedy":
                is_valid, meesage = self.bintobin_controller.run_bintobin_greedy(df_inv_btb, dict_demand)
                if is_valid:
                    self.show_success(message=meesage)
                else:
                    self.show_error(message=meesage)
                    st.stop()

    def render_page_btb(self):
        self.run_bintobin()
        self.import_inv_prime_csv()
        self.import_file_demand()
        load_custom_css()

        #Create layout bin to bin
        cont_bintobin = st.container(border=StatusBorder.BORDER.value)

        form_btb = cont_bintobin.container(border=StatusBorder.BORDER.value)

        title_btb_rack = cont_bintobin.container(border=StatusBorder.BORDER.value)
        btb_rack = cont_bintobin.container(border=StatusBorder.BORDER.value)

        title_btb_ww = cont_bintobin.container(border=StatusBorder.BORDER.value)
        btb_ww = cont_bintobin.container(border=StatusBorder.BORDER.value)


        #Lọc dataframe rack và ww
        try:
             # Đọc file no_bin_to_bin_log.txt đưa content vào state
            item_not_btb_save = self.bintobin_controller.bintobin_model.read_item_not_btb()
            self.bintobin_controller.state.set(AppConfig.StateKeys.ITEM_NOT_BTB, [int(item) for x in item_not_btb_save.split(",") if (item := x.strip()).isdigit()])
            # Lấy data đã xử lỹ tron model từ state
            df_btb_draft = self.bintobin_controller.state.get(AppConfig.StateKeys.DF_BTB)
            list_item_not_btb_in_state = self.bintobin_controller.state.get(AppConfig.StateKeys.ITEM_NOT_BTB, [])

            if list_item_not_btb_in_state:
                mask_item_not_btb = pd.Series(True, df_btb_draft.index)
                mask_item_not_btb &= df_btb_draft['gcas'].isin(list_item_not_btb_in_state)
                df_btb = df_btb_draft[~mask_item_not_btb]
            else:
                df_btb = df_btb_draft

            if isinstance(df_btb, pd.DataFrame):
                mask = pd.Series(True, df_btb.index)
                mask_is_rack = mask & df_btb['location_system_type'].isin(["PF"])
                mask_is_ww = mask & df_btb['location_system_type'].isin(["WW"])

                df_btb_rack = df_btb[mask_is_rack].copy()
                df_btb_rack["gcas"] = pd.to_numeric(df_btb_rack["gcas"],downcast="integer")
                df_btb_rack["gcas"] = df_btb_rack["gcas"].astype(str)
                df_btb_rack = df_btb_rack.sort_values(by=["location"])
                num_bin_rack = df_btb_rack["location"].nunique()

                df_btb_ww = df_btb[mask_is_ww].copy()
                df_btb_ww["gcas"] = pd.to_numeric(df_btb_ww["gcas"],downcast="integer")
                df_btb_ww["gcas"] = df_btb_ww["gcas"].astype(str)
                df_btb_ww = df_btb_ww.sort_values(by=["location"])
                num_bin_ww = df_btb_ww["location"].nunique()

            else:
                df_btb_rack = pd.DataFrame()
                df_btb_ww = pd.DataFrame()
                num_bin_rack = 0
                num_bin_ww = 0
        except:
            df_btb_rack = pd.DataFrame()
            df_btb_ww = pd.DataFrame()
            num_bin_rack = 0
            num_bin_ww = 0

        with form_btb:
            with st.form(key="form_btb"):
                col1, col2 = st.columns(2, gap="medium") #st.columns([3, 1])
                with col1:
                    # Đọc file no_bin_to_bin_log.txt lấy những items không btb đã lưu
                    item_not_btb_save = self.bintobin_controller.state.get(AppConfig.StateKeys.ITEM_NOT_BTB, [])
                    if not item_not_btb_save:
                        item_not_btb_save = None
                    else:
                        item_not_btb_save = ", ".join([str(item) for item in item_not_btb_save])

                    item_not_btb = st.text_area(
                        label="Items Excluded from Bin-to-Bin",
                        value = item_not_btb_save,
                        placeholder="Điền những Items không cần bin to bin vào đây. Các Items cách nhau bằng dấu phẩy. Ví dụ: 80883962, 80892777, 80833957",
                        height=68)
                    
                with col2:
                    strategy_options = {
                        "standard": "Standard Approach (Chiến thuật tiêu chuẩn / Mặc định)",
                        "greedy": "Greedy Approach (Chiến thuật tham lam)"
                    }
                    # Mặc định hiển thị theo chiều dọc, bạn có thể thêm horizontal=True để dàn hàng ngang
                    selected_strategy = st.radio(
                        label="Select Algorithm Strategy:",
                        options=list(strategy_options.keys()),
                        format_func=lambda x: strategy_options[x],
                        horizontal=True # Hiển thị hàng ngang cho gọn gàng (tùy chọn)
                    )
                    # selected_strategy = st.radio(
                    #     "Select Strategy Bin To Bin:",
                    #     ["Strategy 1", "Strategy 2"],
                    #     horizontal=True,
                    #     captions=["Lấy bin to bin tham lam", "Lấy bin to bin không tham lam"])
                    # chu_de = st.selectbox("Chọn chủ đề bài viết:", ["Công nghệ", "Kinh doanh", "Sức khỏe"])
                    # dong_y = st.checkbox("Tôi đồng ý với điều khoản sử dụng")
                    
                    text_content = f"{strategy_options[selected_strategy]}"
                    color_code = "red"  # Hoặc dùng mã HEX như "#800080"
                    font_size = "18px"
                    # Sử dụng f-string truyền biến vào HTML
                    st.markdown(
                        f"Strategy Current: <span style='color: {color_code}; font-size: {font_size}; font-weight: bold;'>{text_content}</span>", 
                        unsafe_allow_html=True
                    )
                    # 1. Thêm CSS để ép nút luôn căn sát lề phải và không được tràn viền
                    st.markdown(
                        """
                        <style>
                        /* Căn phải vùng chứa nút form */
                        div[data-testid="stFormSubmitButton"] {
                            display: flex;
                            justify-content: flex-end; /* Đẩy nút sát lề phải */
                            width: 100%;
                        }
                        /* Đảm bảo nút không tự động co giãn bậy hoặc tràn viền */
                        div[data-testid="stFormSubmitButton"] button {
                            white-space: nowrap !important; /* Không cho chữ xuống dòng */
                            width: auto !important;         /* Độ rộng tự động vừa khít chữ */
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    sub_col1, sub_col2, sub_col3 = st.columns([2, 1, 1])
                    with sub_col3:
                        submit_btn = st.form_submit_button(label="Update Configuration", type="primary", use_container_width=True)

        # 3. Xử lý logic khi bấm nút (nằm ngoài khối st.form)
        # Hàm này trả về True nếu người dùng CLICK vào nút
        if submit_btn:
            if item_not_btb:
                final_int_list = [int(item) for x in item_not_btb.split(",") if (item := x.strip()).isdigit()]
                #Ghi data item not bin to bin xuống file txt
                self.bintobin_controller.bintobin_model.write_item_not_btb(final_int_list)
                # Update data mới lên state nếu có
                self.bintobin_controller.state.set(AppConfig.StateKeys.ITEM_NOT_BTB, final_int_list)
            else:
                #Ghi data item not bin to bin xuống file txt
                #Ghi nếu người dùng xóa hết item trong text_area
                self.bintobin_controller.bintobin_model.write_item_not_btb(item_not_btb)

            # Update strategy btb mới nếu có
            self.bintobin_controller.state.set(AppConfig.StateKeys.STRATEGY_BTB, selected_strategy)
            

        with title_btb_rack:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">BIN TO BIN MOVEMENT FOR RACK {num_bin_rack} LOCATIONS</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

        with btb_rack:
            st.html(f"<span class='df_btb'</span>")
            st.dataframe(df_btb_rack, hide_index=True, height=500, use_container_width=True)

        with title_btb_ww:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">BIN TO BIN MOVEMENT FOR WORKWAY {num_bin_ww} LOCATIONS</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

        with btb_ww:
            st.html(f"<span class='df_btb'</span>")
            st.dataframe(df_btb_ww, hide_index=True, height=250, use_container_width=True)
