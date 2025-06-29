import streamlit as st
from utils.constants import StatusBorder
from views.stylee.style_css import load_custom_css
from controllers.analytics_controller import AnalyticsController

class TabDashboardView:
    def __init__(self, analytics_controller: AnalyticsController):
        self.analytics_controller = analytics_controller

    def render(self):
        # self._init_style()
        load_custom_css()

        #get_all_chart() phải được chạy trước để lấy datafrme. Khi có df mới có date_time
        obj_chart = self.analytics_controller.get_all_chart()
        date_time = self.analytics_controller.get_datetime_current()

        container_inv = st.container(border=StatusBorder.BORDER.value)
        cont_title = container_inv.container(border=StatusBorder.BORDER.value)
        cont_dashboard = container_inv.container(border=StatusBorder.BORDER.value)
        col_wh1, col_wh2, col_wh3, col_pf_cl, col_lable_total = cont_dashboard.columns([1, 1, 1, 1, 1])
        cont_metric = cont_dashboard.container(border=StatusBorder.BORDER.value)
        cont_wh1 = col_wh1.container(border=StatusBorder.BORDER.value)
        cont_wh2 = col_wh2.container(border=StatusBorder.BORDER.value)
        cont_wh3 = col_wh3.container(border=StatusBorder.BORDER.value)
        cont_pf_cl = col_pf_cl.container(border=StatusBorder.BORDER.value)
        cont_label_total = col_lable_total.container(border=StatusBorder.BORDER.value)

        with cont_title:
           # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">INVENTORY BY SUB WAREHOUSE {date_time}</div>
            </div>
            """
            #header-subtitle
            st.markdown(header_html, unsafe_allow_html=True)
            # col1, col2, col3 = cont_title.columns([1, 10, 1])
            # with col2:
            #     # st.html(f"<span class='title_dashboard'</span>")
            #     st.subheader(f"INVENTOTY BY SUB WAREHOUSE {date_time}")

        with cont_dashboard:
            # Top section - Gauge charts
            st.markdown('<div class="top-section" id="top-section">', unsafe_allow_html=True)
            with cont_wh1:
                #WH1 Total
                st.markdown('<div class="gauge-container" id="wh1-total">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh1_total, use_container_width=True, key="wh1_total")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH1 hight rack
                st.markdown('<div class="gauge-container" id="wh1-hr">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh1_hr, use_container_width=True, key="wh1_hr")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH1 pick face
                st.markdown('<div class="gauge-container" id="wh1-pf">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh1_pf, use_container_width=True, key="wh1_pf")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH1 floor
                st.markdown('<div class="gauge-container" id="wh1-floor">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh1_floor, use_container_width=True, key="wh1_floor")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with cont_wh2:
                #WH2 total
                st.markdown('<div class="gauge-container" id="wh2-total">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh2_total, use_container_width=True, key="wh2_total")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH2 hight rack
                st.markdown('<div class="gauge-container" id="wh2-hr">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh2_hr, use_container_width=True, key="wh2_hr")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH2 pick face
                st.markdown('<div class="gauge-container" id="wh2-pf">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh2_pf, use_container_width=True, key="wh2_pf")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH2 floor
                st.markdown('<div class="gauge-container" id="wh2-floor">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh2_floor, use_container_width=True, key="wh2_floor")
                st.markdown('</div>', unsafe_allow_html=True)

            with cont_wh3:
                #WH3 total
                st.markdown('<div class="gauge-container" id="wh3-total">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh3_total, use_container_width=True, key="wh3_total")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH3 hight rack
                st.markdown('<div class="gauge-container" id="wh3-hr">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh3_hr, use_container_width=True, key="wh3_hr")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH3 pick face
                st.markdown('<div class="gauge-container" id="wh3-pf">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh3_pf, use_container_width=True, key="wh3_pf")
                st.markdown('</div>', unsafe_allow_html=True)
                #WH3 floor
                st.markdown('<div class="gauge-container" id="wh3-floor">', unsafe_allow_html=True)
                st.plotly_chart(obj_chart.wh3_floor, use_container_width=True, key="wh3_floor")
                st.markdown('</div>', unsafe_allow_html=True)

            with cont_pf_cl:
                # Set Layout Kho cooling
                cont_cl = cont_pf_cl.container(border=StatusBorder.BORDER.value)
                cont_cl_fig = cont_cl.container(border=StatusBorder.BORDER.value)
                cont_cl_metric = cont_cl.container(border=StatusBorder.BORDER.value)
        
                with cont_cl_fig:
                    # with st.container(border=StatusBorder.BORDER.value):
                    st.markdown('<div class="gauge-container" id="gauge-cool">', unsafe_allow_html=True)
                    st.plotly_chart(obj_chart.cool_total, use_container_width=True, key="gauge_cool")
                    st.markdown('</div>', unsafe_allow_html=True)
                with cont_cl_metric:
                    c1, c2 = st.columns([1, 1])
                    c3, c4 = st.columns([1, 1])
                    with c1:
                        st.markdown(obj_chart.cool1_mk, unsafe_allow_html=True)
                    with c2:
                        st.markdown(obj_chart.cool2_mk, unsafe_allow_html=True)
                    with c3:
                        st.markdown(obj_chart.cool3_mk, unsafe_allow_html=True)
                    with c4:
                        st.markdown(obj_chart.cool_floor, unsafe_allow_html=True)
                
                # Set Layout Kho Perfume
                cont_pf = cont_pf_cl.container(border=StatusBorder.BORDER.value)
                cont_pf_fig = cont_pf.container(border=StatusBorder.BORDER.value)
                cont_pf_metric = cont_pf.container(border=StatusBorder.BORDER.value)
                

                with cont_pf:
                    with cont_pf_fig:
                        st.markdown('<div class="gauge-container" id="gauge-pf">', unsafe_allow_html=True)
                        st.plotly_chart(obj_chart.pf_total, use_container_width=True, key="gauge_pf")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with cont_pf_metric:
                        p1, p2, p3 = st.columns([1, 1, 1])
                        p4, p5, p6 = st.columns([1, 1, 1])
                        with p1:
                            p1.markdown(obj_chart.pf1_mk, unsafe_allow_html=True)
                        with p2:
                            p2.markdown(obj_chart.pf2_mk, unsafe_allow_html=True)
                        with p3:
                            p3.markdown(obj_chart.pf3_mk, unsafe_allow_html=True)
                        with p4:
                            p4.markdown(obj_chart.pf4_mk, unsafe_allow_html=True)
                        with p5:
                            p5.markdown(obj_chart.pf5_mk, unsafe_allow_html=True)
                        with p6:
                            p6.markdown(obj_chart.pf_floor, unsafe_allow_html=True)

            with cont_label_total:
                #=========BDWH===================
                cont_bdwh = cont_label_total.container(border=StatusBorder.BORDER.value)
                with cont_bdwh:
                    st.markdown('<div class="gauge-container" id="wh3-bdwh">', unsafe_allow_html=True)
                    st.plotly_chart(obj_chart.wh_total, use_container_width=True, key="wh3_bdwh")
                    st.markdown('</div>', unsafe_allow_html=True)

                #=========Label==================
                cont_label = cont_label_total.container(border=StatusBorder.BORDER.value)
                with cont_label:
                    st.markdown('<div class="gauge-container" id="wh-lb">', unsafe_allow_html=True)
                    st.plotly_chart(obj_chart.lb_total, use_container_width=True, key="wh_lb")
                    st.markdown('</div>', unsafe_allow_html=True)

                 #==============EO===================
                cont_eo = cont_label_total.container(border=StatusBorder.BORDER.value)
                with cont_eo:
                    st.markdown('<div class="gauge-container" id="wh-eocons">', unsafe_allow_html=True)
                    st.plotly_chart(obj_chart.eo_total, use_container_width=True, key="wh_eocons")
                    st.markdown('</div>', unsafe_allow_html=True)
            #Top section
            st.markdown('</div>', unsafe_allow_html=True)

            # Middle section - Metrics grid
            st.markdown('<div class="middle-section" id="middle-section">', unsafe_allow_html=True)
            with cont_metric:
                with st.container(border=StatusBorder.BORDER.value):
                    a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    with a1:
                        a1.markdown(obj_chart.pmbd_total, unsafe_allow_html=True)
                    with a2:
                        a2.markdown(obj_chart.rm_total, unsafe_allow_html=True)
                    with a3:
                        a3.markdown(obj_chart.pm_shipper, unsafe_allow_html=True)
                    with a4:
                        a4.markdown(obj_chart.pm_bottle, unsafe_allow_html=True)
                    with a5:
                        a5.markdown(obj_chart.pm_pouch, unsafe_allow_html=True)
                    with a6:
                        a6.markdown(obj_chart.pm_other, unsafe_allow_html=True)
                    with a7:
                        a7.markdown(obj_chart.lsl_in, unsafe_allow_html=True)
                    with a8:
                        a8.markdown(obj_chart.lsl_lslpm, unsafe_allow_html=True)
                    with a9:
                        a9.markdown(obj_chart.lsl_lslrm, unsafe_allow_html=True)
                    with a10:
                        a10.markdown(obj_chart.lsl_lrt, unsafe_allow_html=True)

                with st.container(border=StatusBorder.BORDER.value):
                    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    with b1:
                        b1.markdown(obj_chart.fgbd_total, unsafe_allow_html=True)
                    with b2:
                        b2.markdown(obj_chart.fg_dwn, unsafe_allow_html=True)
                    with b3:
                        b3.markdown(obj_chart.fg_febz, unsafe_allow_html=True)
                    with b4:
                        b4.markdown(obj_chart.fg_hdl, unsafe_allow_html=True)
                    with b5:
                        b5.markdown(obj_chart.fg_other, unsafe_allow_html=True)
                    with b6:
                        b6.markdown(obj_chart.pallet_scanout, unsafe_allow_html=True)
                    with b7:
                        b7.markdown(obj_chart.pallet_fgls, unsafe_allow_html=True)
                    with b8:
                        b8.markdown(obj_chart.pallet_fgdm, unsafe_allow_html=True)
                    with b9:
                        b9.markdown(obj_chart.pallet_matdm, unsafe_allow_html=True)
                    with b10:
                        b10.markdown(obj_chart.pallet_lost, unsafe_allow_html=True)
                    # with b11:
                    #     b11.markdown(obj_chart.pallet_steam, unsafe_allow_html=True)

                with st.container(border=StatusBorder.BORDER.value):
                    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    with c1:
                        c1.markdown(obj_chart.fg_total, unsafe_allow_html=True)
                    with c2:
                        c2.markdown(obj_chart.pm_total, unsafe_allow_html=True)
                    with c3:
                        c3.markdown(obj_chart.block_total, unsafe_allow_html=True)
                    with c4:
                        c4.markdown(obj_chart.block_fg, unsafe_allow_html=True)
                    with c5:
                        c5.markdown(obj_chart.block_rpm, unsafe_allow_html=True)
                    with c6:
                        c6.markdown(obj_chart.block_lb, unsafe_allow_html=True)
                    with c7:
                        c7.markdown(obj_chart.pallet_jit, unsafe_allow_html=True)
                    with c8:
                        c8.markdown(obj_chart.pallet_emptybin, unsafe_allow_html=True)
                    with c9:
                        c9.markdown(obj_chart.pallet_combinebin, unsafe_allow_html=True)
                    with c10:
                        c10.markdown(obj_chart.pallet_mixup, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Bottom section
            st.markdown('<div class="bottom-section" id="bottom-section">', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    def _init_style(self):
        st.html("./views/style/style_wh123.html")
        # st.html("./views/style/style_pf_cool.html")
        # st.html("./views/style/style_bdwh_label_eo.html")
        # st.html("./views/style/style_mt_row1.html")
        # st.html("./views/style/style_mt_row2.html")
        # st.html("./views/style/style_mt_row3.html")
        # #tab empty loc
        # st.html("./views/style/style_emptyloc.html")
        # #tab combinebin
        # st.html("./views/style/style_combinebin.html")
        # #tab mixup
        # st.html("./views/style/style_mixup.html")

