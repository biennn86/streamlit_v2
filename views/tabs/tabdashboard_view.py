import streamlit as st
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController

class TabDashboardView:
    def __init__(self, analytics_controller: AnalyticsController):
        self.analytics_controller = analytics_controller

    def render(self):
        self._init_style()
        #get_all_chart() phải được chạy trước để lấy datafrme. Khi có df mới có date_time
        obj_chart = self.analytics_controller.get_all_chart()
        date_time = self.analytics_controller.get_datetime_current()

        container_inv = st.container(border=StatusBorder.BORDER.value)
        cont_dashboard = container_inv.container(border=StatusBorder.BORDER.value)
        cont_title = cont_dashboard.container(border=StatusBorder.BORDER.value)
        col_wh1, col_wh2, col_wh3, col_pf_cl, col_lable_total = cont_dashboard.columns([1, 1, 1, 1, 1])
        cont_metric = cont_dashboard.container(border=StatusBorder.BORDER.value)
        cont_wh1 = col_wh1.container(border=StatusBorder.BORDER.value)
        cont_wh2 = col_wh2.container(border=StatusBorder.BORDER.value)
        cont_wh3 = col_wh3.container(border=StatusBorder.BORDER.value)
        cont_pf_cl = col_pf_cl.container(border=StatusBorder.BORDER.value)
        cont_label_total = col_lable_total.container(border=StatusBorder.BORDER.value)

        with cont_title:
            # CSS để căn giữa các thẻ h2 (là thẻ HTML tương ứng với st.subheader)
            # st.markdown("""
            # <style>
            # h3 {
            #     text-align: center;
            # }
            # </style>
            # """, unsafe_allow_html=True)
            col1, col2, col3 = cont_title.columns([1, 10, 1])
            with col2:
                st.html(f"<span class='title_dashboard'</span>")
                st.subheader(f"INVENTOTY BY SUB WAREHOUSE {date_time}")

        with cont_dashboard:
            cont_dashboard.html(f"<span class='dashboard_control'</span>")
            with cont_wh1:
                st.html(f"<span class='control_wh1'</span>")
                with st.container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='info_wh1'</span>")
                    st.write(f"WH1 CU: {obj_chart.cu_wh1}")
                    # st.info('WH1 CU: {}'.format(figwh1['cu']), icon='🏚️')
                with st.container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='fig_wh1'</span>")
                    st.plotly_chart(obj_chart.wh1_total)
                    st.plotly_chart(obj_chart.wh1_hr)
                    st.plotly_chart(obj_chart.wh1_pf)
                    st.plotly_chart(obj_chart.wh1_floor)
            
            with cont_wh2:
                st.html(f"<span class='control_wh2'</span>")
                with st.container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='info_wh2'</span>")
                    st.write(f"WH2 CU: {obj_chart.cu_wh2}")
                    # st.info('WH2 CU: {}'.format(figwh2['cu']), icon='🏚️')
                with st.container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='fig_wh2'</span>")
                    st.plotly_chart(obj_chart.wh2_total)
                    st.plotly_chart(obj_chart.wh2_hr)
                    st.plotly_chart(obj_chart.wh2_pf)
                    st.plotly_chart(obj_chart.wh2_floor)

            with cont_wh3:
                cont_wh3.html(f"<span class='control_wh3'</span>")
                with st.container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='info_wh3'</span>")
                    st.write(f"WH3 CU: {obj_chart.cu_wh3}")
                    # st.info('WH3 CU: {}'.format(figwh3['cu']), icon='🏚️')
                with st.container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='fig_wh3'</span>")
                    st.plotly_chart(obj_chart.wh3_total)
                    st.plotly_chart(obj_chart.wh3_hr)
                    st.plotly_chart(obj_chart.wh3_pf)
                    st.plotly_chart(obj_chart.wh3_floor)

            with cont_pf_cl:
                #title
                title_pf_cl= cont_pf_cl.columns([1])
                # Set Layout Kho cooling
                cont_cl = cont_pf_cl.container(border=StatusBorder.BORDER.value)
                cool_fig = cont_cl.columns([1])
                c1, c2 = cont_cl.columns([1, 1])
                c3, c4 = cont_cl.columns([1, 1])
                # Set Layout Kho Perfume
                cont_pf = cont_pf_cl.container(border=StatusBorder.BORDER.value)
                pf_fig = cont_pf.columns([1])
                p1, p2, p3 = cont_pf.columns([1, 1, 1])
                p4, p5, p6 = cont_pf.columns([1, 1, 1])

                with title_pf_cl[0].container(border=StatusBorder.BORDER.value):
                    st.html(f"<span class='title_pf_cl'</span>")
                    st.write(f"COOLING: {obj_chart.cu_cool} & PERFUME: {obj_chart.cu_pf}")
        
                with cont_cl:
                    cont_cl.html(f"<span class='cool'</span>")
                    with st.container(border=StatusBorder.BORDER.value):
                        cool_fig[0].html(f"<span class='fig_cool'</span>")
                        cool_fig[0].plotly_chart(obj_chart.cool_total)
                    with st.container(border=StatusBorder.BORDER.value):
                        c1.html(f"<span class='cl_c1'</span>")
                        c1.metric(**obj_chart.cool1_mk)
                        c2.html(f"<span class='cl_c2'</span>")
                        c2.metric(**obj_chart.cool2_mk)
                        c3.html(f"<span class='cl_c3'</span>")
                        c3.metric(**obj_chart.cool3_mk)
                        c4.html(f"<span class='cl_c4'</span>")
                        c4.metric(**obj_chart.cool_floor)

                with cont_pf:
                    cont_pf.html(f"<span class='perfume'</span>")
                    with st.container(border=StatusBorder.BORDER.value):
                        pf_fig[0].html(f"<span class='fig_perfume'</span>")
                        pf_fig[0].plotly_chart(obj_chart.pf_total)
                    with st.container(border=StatusBorder.BORDER.value):
                        p1.html(f"<span class='pf_p1'</span>")
                        p1.metric(**obj_chart.pf1_mk)
                        p2.html(f"<span class='pf_p2'</span>")
                        p2.metric(**obj_chart.pf2_mk)
                        p3.html(f"<span class='pf_p3'</span>")
                        p3.metric(**obj_chart.pf3_mk)
                        p4.html(f"<span class='pf_p4'</span>")
                        p4.metric(**obj_chart.pf4_mk)
                        p5.html(f"<span class='pf_p5'</span>")
                        p5.metric(**obj_chart.pf5_mk)
                        p6.html(f"<span class='pf_p6'</span>")
                        p6.metric(**obj_chart.pf_floor)

            with cont_label_total:
                #=========BDWH===================
                cont_bdwh = cont_label_total.container(border=StatusBorder.BORDER.value)
                with cont_bdwh:
                    cont_bdwh.html(f"<span class='bdwh'</span>")
                    with st.container(border=StatusBorder.BORDER.value):
                        st.html(f"<span class='title_bdwh'</span>")
                        st.write(f"BDWH#123 (Ex EO, Cons): {obj_chart.cu_wh}")
                    with st.container(border=StatusBorder.BORDER.value):
                        st.html(f"<span class='fig_bdwh'</span>")
                        st.plotly_chart(obj_chart.wh_total)

                #=========Label==================
                cont_label = cont_label_total.container(border=StatusBorder.BORDER.value)
                with cont_label:
                    cont_label.html(f"<span class='label'</span>")
                    with st.container(border=StatusBorder.BORDER.value):
                        st.html(f"<span class='title_label'</span>")
                        st.write(f"WH LABEL: {obj_chart.cu_lb}")
                    with st.container(border=StatusBorder.BORDER.value):
                        st.html(f"<span class='fig_label'</span>")
                        st.plotly_chart(obj_chart.lb_total)

                 #==============EO===================
                cont_eo = cont_label_total.container(border=StatusBorder.BORDER.value)
                with cont_eo:
                    cont_eo.html(f"<span class='eo'</span>")
                    with st.container(border=StatusBorder.BORDER.value):
                        st.html(f"<span class='title_eo'</span>")
                        st.write(f"EO & CONS: {obj_chart.cu_eo}")
                    with st.container(border=StatusBorder.BORDER.value):
                        st.html(f"<span class='fig_eo'</span>")
                        st.plotly_chart(obj_chart.eo_total)


            with cont_metric:
                with st.container(border=StatusBorder.BORDER.value):
                    a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    a1.html(f"<span class='pm_plt'</span>")
                    a2.html(f"<span class='rm'</span>")
                    a3.html(f"<span class='shipper'</span>")
                    a4.html(f"<span class='bottle'</span>")
                    a5.html(f"<span class='pouch'</span>")
                    a6.html(f"<span class='other'</span>")
                    a7.html(f"<span class='pleol'</span>")
                    a8.html(f"<span class='lslpm'</span>")
                    a9.html(f"<span class='lslrm'</span>")
                    a10.html(f"<span class='lrt'</span>")

                    a1.metric(**obj_chart.pmbd_total)
                    a2.metric(**obj_chart.rm_total)
                    a3.metric(**obj_chart.pm_shipper)
                    a4.metric(**obj_chart.pm_bottle)
                    a5.metric(**obj_chart.pm_pouch)
                    a6.metric(**obj_chart.pm_other)
                    a7.metric(**obj_chart.lsl_in)
                    a8.metric(**obj_chart.lsl_lslpm)
                    a9.metric(**obj_chart.lsl_lslrm)
                    a10.metric(**obj_chart.lsl_lrt)

                with st.container(border=StatusBorder.BORDER.value):
                    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    b1.html(f"<span class='fg_bd'</span>")
                    b2.html(f"<span class='fgdwn'</span>")
                    b3.html(f"<span class='fgfebz'</span>")
                    b4.html(f"<span class='fghdl'</span>")
                    b5.html(f"<span class='fgother'</span>")
                    b6.html(f"<span class='scanout'</span>")
                    b7.html(f"<span class='fgls'</span>")
                    b8.html(f"<span class='fgdm'</span>")
                    b9.html(f"<span class='matdm'</span>")
                    b10.html(f"<span class='lost'</span>")
                    b11.html(f"<span class='steam'</span>")

                    b1.metric(**obj_chart.fgbd_total)
                    b2.metric(**obj_chart.fg_dwn)
                    b3.metric(**obj_chart.fg_febz)
                    b4.metric(**obj_chart.fg_hdl)
                    b5.metric(**obj_chart.fg_other)
                    b6.metric(**obj_chart.pallet_scanout)
                    b7.metric(**obj_chart.pallet_fgls)
                    b8.metric(**obj_chart.pallet_fgdm)
                    b9.metric(**obj_chart.pallet_matdm)
                    b10.metric(**obj_chart.pallet_lost)
                    b11.metric(**obj_chart.pallet_steam)

                with st.container(border=StatusBorder.BORDER.value):
                    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    c1.html(f"<span class='total_fg'</span>")
                    c2.html(f"<span class='total_pm'</span>")
                    c3.html(f"<span class='total_block'</span>")
                    c4.html(f"<span class='fg_block'</span>")
                    c5.html(f"<span class='rpm_block'</span>")
                    c6.html(f"<span class='lb_block'</span>")
                    c7.html(f"<span class='jit'</span>")
                    c8.html(f"<span class='emploc_wh123'</span>")
                    c9.html(f"<span class='combinebin'</span>")
                    c10.html(f"<span class='mixup'</span>")

                    c1.metric(**obj_chart.fg_total)
                    c2.metric(**obj_chart.pm_total)
                    c3.metric(**obj_chart.block_total)
                    c4.metric(**obj_chart.block_fg)
                    c5.metric(**obj_chart.block_rpm)
                    c6.metric(**obj_chart.block_lb)
                    c7.metric(**obj_chart.pallet_jit)
                    # c8.metric()
                    # c9.metric()
                    # c10.metric()












































    def _init_style(self):
        st.html("./views/style/style_wh123.html")
        st.html("./views/style/style_pf_cool.html")
        st.html("./views/style/style_bdwh_label_eo.html")
        st.html("./views/style/style_mt_row1.html")
        st.html("./views/style/style_mt_row2.html")
        st.html("./views/style/style_mt_row3.html")
        # #tab empty loc
        # st.html("./views/style/style_emptyloc.html")
        # #tab combinebin
        # st.html("./views/style/style_combinebin.html")
        # #tab mixup
        # st.html("./views/style/style_mixup.html")