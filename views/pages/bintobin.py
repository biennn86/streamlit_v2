import streamlit as st
import pandas as pd
from utils.constants import StatusBorder
from views.components.sidebat_menu_btb import *
from views.pages.base_streamlit_view import *
from models.inventory_model import InventoryModel
from models.bintobin_model import BintobinModel
from controllers.bintobin_controller import BintobinController

from config.settings import AppConfig
from views.style.style_css import load_custom_css

class BintobinView(BaseStreamlitView):
    def __init__(self):
        inventory_model = InventoryModel()
        bintobin_model = BintobinModel(inventory_model)
        self.bintobin_controller = BintobinController(bintobin_model)

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

    def render(self):
        tab_btb, tab_demand = st.tabs(["Bin To Bin", "Demand"])

        with tab_btb:
            self.render_tab_btb()

        with tab_demand:
            self.render_tab_demand()

    def get_df_btb_report(self):
        DEFAULT_ITEM_NOT_BTB = ['80833958', '80833957', '80833959', '80841643',
                                '80842234', '80842233', '80861956', '80863602',
                                '80863601', '80883966', '80883983', '80883980',
                                '80892777', '80892794', '80831266', '80831265',
                                '83907572', '83907573', '83907574', '83907575',
                                '83907576', '83907577', '83907578', '83907579',
                                '83907580', '83907581', '83907582']
        
        try:
            # Đọc file no_bin_to_bin_log.txt đưa content vào state
            self.item_not_btb_from_txt = self.bintobin_controller.bintobin_model.read_item_not_btb()
            self.bintobin_controller.state.set(AppConfig.StateKeys.ITEM_NOT_BTB, [int(item) for x in self.item_not_btb_from_txt.split(",") if (item := x.strip()).isdigit()])
            self.item_not_btb_from_state = self.bintobin_controller.state.get(AppConfig.StateKeys.ITEM_NOT_BTB, [])

            # Lấy data đã xử lý trong model từ state. Data này được set vào state từ ControllerBtB
            self.df_btb_from_state = self.bintobin_controller.state.get(AppConfig.StateKeys.DF_BTB)
            # Tạo cột qty_total_need_move để remove bin duplicate
            if (not self.df_btb_from_state is None) and isinstance(self.df_btb_from_state, pd.DataFrame):
                self.df_btb_from_state["qty_total_need_move"] = self.df_btb_from_state.groupby(["gcas", "location"])["qty_need_move"].transform("sum")
                self.df_btb_from_state["pallet_count"] = self.df_btb_from_state.groupby(["gcas", "location"])["pallet"].transform("count")
                self.df_btb_from_state["qty_total"] = self.df_btb_from_state.groupby(["gcas", "location"])["qty"].transform("sum")
                self.df_btb_to_view = self.df_btb_from_state.drop_duplicates(subset=["location", "gcas"], keep="first").copy()

                if self.item_not_btb_from_state:
                    mask_item_not_btb = pd.Series(True, self.df_btb_to_view.index)
                    mask_item_not_btb &= self.df_btb_to_view['gcas'].isin(self.item_not_btb_from_state)
                    self.df_btb_to_view = self.df_btb_to_view[~mask_item_not_btb].copy()
                else:
                    self.df_btb_to_view = self.df_btb_to_view
                # Lọc ra df_rack và df_ww
                mask = pd.Series(True, self.df_btb_to_view.index)
                mask_is_rack = mask & self.df_btb_to_view['location_system_type'].isin(["PF"])
                mask_is_rack &= self.df_btb_to_view['name_warehouse'].isin(["WH2"])
                mask_is_ww = mask & self.df_btb_to_view['location_system_type'].isin(["WW"])

                self.df_btb_report_rack = self.df_btb_to_view[mask_is_rack].copy()
                self.df_btb_report_rack["gcas"] = pd.to_numeric(self.df_btb_report_rack["gcas"],downcast="integer")
                self.df_btb_report_rack["gcas"] = self.df_btb_report_rack["gcas"].astype(str)
                self.df_btb_report_rack = self.df_btb_report_rack.sort_values(by=["location"])
                self.df_btb_report_rack.index = range(1, len(self.df_btb_report_rack)+1)
                self.num_bin_rack = self.df_btb_report_rack["location"].nunique()
                self.num_pallet_rack = self.df_btb_report_rack["pallet_count"].sum()

                self.df_btb_report_ww = self.df_btb_to_view[mask_is_ww].copy()
                self.df_btb_report_ww["gcas"] = pd.to_numeric(self.df_btb_report_ww["gcas"],downcast="integer")
                self.df_btb_report_ww["gcas"] = self.df_btb_report_ww["gcas"].astype(str)
                self.df_btb_report_ww = self.df_btb_report_ww.sort_values(by=["location"])
                self.df_btb_report_ww.index = range(1, len(self.df_btb_report_ww)+1)
                self.num_bin_ww = self.df_btb_report_ww["location"].nunique()
                self.num_pallet_ww = self.df_btb_report_ww["pallet_count"].sum()

                # Lọc ra cột cần hiển thị
                name_col_view_rack = ["location", "gcas", "batch", "status", "pallet_count", "qty_total_need_move", "note_btb"]
                name_col_view_ww = ["location", "gcas", "batch", "status", "pallet_count", "qty_total", "note_btb"]
                name_col_report_rack = ["Location", "Item", "Batch", "Status", "Pallet Count", "Qty Need Move", "Note"]
                name_col_report_ww = ["Location", "Item", "Batch", "Status", "Pallet Count", "Total Qty", "Note"]
                dict_rename_rack = dict(zip(name_col_view_rack, name_col_report_rack))
                dict_rename_ww = dict(zip(name_col_view_ww, name_col_report_ww))
                self.df_btb_report_rack = self.df_btb_report_rack[name_col_view_rack]
                self.df_btb_report_rack = self.df_btb_report_rack.rename(columns=dict_rename_rack)
                self.df_btb_report_ww = self.df_btb_report_ww[name_col_view_ww]
                self.df_btb_report_ww = self.df_btb_report_ww.rename(columns=dict_rename_ww)
                # self.df_btb_report_rack = self.df_btb_report_rack
            else:
                self.num_bin_rack = 0
                self.num_bin_ww = 0
                self.num_pallet_rack = 0
                self.num_pallet_ww = 0
                self.df_btb_report_rack = pd.DataFrame()
                self.df_btb_report_ww = pd.DataFrame()
        except FileNotFoundError as e:
            self.show_error(e)
        except ValueError as e:
            self.show_error(e)
        except Exception as e:
            self.show_error(e)

    def render_tab_demand(self):
        dict_demand = self.bintobin_controller.state.get(AppConfig.StateKeys.DEMAND_DATA, {})
        is_valid, meesage = self.bintobin_controller.get_demand_export_view(dict_demand=dict_demand)
        if is_valid:
            # self.show_success(message=meesage)
            df_demand_report = self.bintobin_controller.state.get(AppConfig.StateKeys.DF_DEMAND_EXPORT_VIEW, pd.DataFrame)
            cont_demand = st.container(border=StatusBorder.BORDER.value)
            with cont_demand:
                title_demand = st.container(border=StatusBorder.BORDER.value)

                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                with col1:
                    search_query = st.text_input("Search (e.g., by Gcas, Market)", "")
                if search_query:
                    df_final = self.search_df(df_demand_report, search_query=search_query)
                else:
                    df_final = df_demand_report

                df_final["gcas"] = pd.to_numeric(df_final["gcas"],downcast="integer")
                df_final["gcas"] = df_final["gcas"].astype(str)
                df_final.index = range(1, len(df_final)+1)

                demand = st.container(border=StatusBorder.BORDER.value)
                with title_demand:
                    # Header với container có thể control
                    header_html  = f"""
                    <div class="main-header" id="main-header">
                        <div class="header-title">DEMAND EXPORT</div>
                    </div>
                    """
                    st.markdown(header_html, unsafe_allow_html=True)
    
                with demand:
                    st.html(f"<span class='df_demand'</span>")
                    st.dataframe(df_final, hide_index=False, height=500, use_container_width=True)

                self.download_data_display(df_final, key="download_demand_report")
        else:
            header_html  = f"""
                <div class="main-header" id="main-header">
                    <div class="header-title">Chưa có file demand nào được tải lên!</div>
                </div>
                """
            st.markdown(header_html, unsafe_allow_html=True)
            # st.subheader("Chưa có file demand nào được tải lên!")
            # self.show_error(message=meesage)
            # st.stop()

    def render_tab_btb(self):
        self.run_bintobin()
        self.import_inv_prime_csv()
        self.import_file_demand()
        self.get_df_btb_report()
        load_custom_css()

        # Header với container có thể control
        header_html  = f"""
        <div class="main-header" id="main-header">
            <div class="header-title">RUN BIN TO BIN WAREHOUSE P&G</div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        # st.subheader("RUN BIN TO BIN WAREHOUSE P&G")
        
        #Create layout bin to bin
        cont_bintobin = st.container(border=StatusBorder.BORDER.value)
        with cont_bintobin:
            form_btb = st.container(border=StatusBorder.BORDER.value)

            title_btb_rack = st.container(border=StatusBorder.BORDER.value)
            btb_rack = st.container(border=StatusBorder.BORDER.value)

            title_btb_ww = st.container(border=StatusBorder.BORDER.value)
            btb_ww = st.container(border=StatusBorder.BORDER.value)

            # Hiển thị msg khi button Update Config được click. Sẽ rerun và hiện thông báo này cho người dùng
            # Nếu không đưa vào state thì khi vừa click button xong chương trình sẽ rerun lại và người dùng không kịp thấy thông báo
            MESSAGE_BUTTON_UPDATE_CONFIG = "success_msg"
            if MESSAGE_BUTTON_UPDATE_CONFIG in self.bintobin_controller.state:
                # Hiển thị lại tin nhắn đã lưu ở lượt chạy trước
                self.show_success(st.session_state.success_msg)
                # Hiển thị xong thì xóa ngay trong state để không bị lặp lại ở lần sau
                del self.bintobin_controller.state.success_msg
            
            with form_btb:
                with st.form(key="form_btb"):
                    col1, col2 = st.columns(2, gap="medium") #st.columns([3, 1])
                    with col1:
                        item_not_btb = st.text_area(
                            label="Items Excluded from Bin-to-Bin",
                            value = self.item_not_btb_from_txt,
                            # key="text_buffer",
                            placeholder="Điền những Items không cần bin to bin vào đây. Các Items cách nhau bằng dấu phẩy. Ví dụ: 80833958, 80833957, 80833959, 80892777, 80883983",
                            height=None)
                    
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
            # Hàm này trả về True nếu người dùng CLICK vào button
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
                # self.show_success(message="Configuration updated successfully") #Update completed
                self.bintobin_controller.state.success_msg = f"Configuration updated successfully"
                st.rerun()
                

            with title_btb_rack:
                # Header với container có thể control
                header_html  = f"""
                <div class="main-header" id="main-header">
                    <div class="header-title">BIN TO BIN MOVEMENT FOR RACK {self.num_bin_rack} LOCATIONS</div>
                </div>
                """
                st.markdown(header_html, unsafe_allow_html=True)

            with btb_rack:
                st.html(f"<span class='df_btb'</span>")
                st.dataframe(self.df_btb_report_rack, hide_index=False, height=500, use_container_width=True)
                title_text = f"BIN TO BIN MOVEMENT FOR RACK {self.num_bin_rack} LOCATIONS - {self.num_pallet_rack} PALLETS"
                self.download_data_excel_format_display(self.df_btb_report_rack, key="download_btb_rack_report", title_text=title_text)

            with title_btb_ww:
                # Header với container có thể control
                header_html  = f"""
                <div class="main-header" id="main-header">
                    <div class="header-title">BIN TO BIN MOVEMENT FOR WORKWAY {self.num_bin_ww} LOCATIONS</div>
                </div>
                """
                st.markdown(header_html, unsafe_allow_html=True)

            with btb_ww:
                st.html(f"<span class='df_btb'</span>")
                st.dataframe(self.df_btb_report_ww, hide_index=False, height=250, use_container_width=True)
                title_text = f"BIN TO BIN MOVEMENT FOR WORKWAY {self.num_bin_ww} LOCATIONS - {self.num_pallet_ww} PALLETS"
                self.download_data_excel_format_display(self.df_btb_report_ww, key="download_btb_ww_report", title_text=title_text)
    

    