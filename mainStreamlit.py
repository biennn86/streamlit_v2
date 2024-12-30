import streamlit as st
from dashboard.dashboardTonkho import *

#https://pfw.youtube.com/watch?v=pWxDxhWXJos&t=5744s

#Tồn kho
st.set_page_config(page_title='Dashboard P&G', page_icon='📊', layout='wide')
st.html("./dashboard/style_wh123.html")
st.html("./dashboard/style_mt_row1.html")
st.html("./dashboard/style_mt_row2.html")
st.html("./dashboard/style_bdwh_label_eo.html")
st.html("./dashboard/style_pf_cool.html")
#tab empty loc
st.html("./dashboard/style_emptyloc.html")
#tab combinebin
st.html("./dashboard/style_combinebin.html")
#tab mixup
st.html("./dashboard/style_mixup.html")
#=========================================================================================================================
#1. set layout
border = False
tab_dashboard, tab_emptyloc, tab_combine, tab_mixup, tab_tonkho = st.tabs(['DashBoard', 'Empty Loc', 'Combine Bin', 'Mixup', 'Inventory'])

#set tabs
container_inv = tab_dashboard.container(border=border)
cont_dashboard = container_inv.container(border=border)
cont_title = cont_dashboard.container(border=border)
col_wh1, col_wh2, col_wh3, col_pf_cl, col_lable_total = cont_dashboard.columns([1, 1, 1, 1, 1])
cont_metric = cont_dashboard.container(border=border)
cont_wh1 = col_wh1.container(border=border)
cont_wh2 = col_wh2.container(border=border)
cont_wh3 = col_wh3.container(border=border)
cont_pf_cl = col_pf_cl.container(border=border)
cont_label_total = col_lable_total.container(border=border)
obj_getpl_3wh =  CoutPlDetailLoc()
if obj_getpl_3wh.dfInv is None:
    st.stop()

with cont_title:
    st.html(f"<span class='title_dashboard'</span>")
    st.subheader('INVENTOTY BY SUB WAREHOUSE {}'.format(obj_getpl_3wh.StringDataTime))

with cont_dashboard:
    cont_dashboard.html(f"<span class='dashboard_control'</span>")
    with cont_wh1:
        figwh1 = obj_getpl_3wh.GetPl_Wh1()
        st.html(f"<span class='control_wh1'</span>")
        with st.container(border=border):
            st.html(f"<span class='info_wh1'</span>")
            st.write('WH3 CU: {}'.format(figwh1['cu']))
            # st.info('WH3 CU: {}'.format(figwh1['cu']), icon='🏚️')
        with st.container(border=border):
            st.html(f"<span class='fig_wh1'</span>")
            st.plotly_chart(figwh1['total'])
            st.plotly_chart(figwh1['hr'])
            st.plotly_chart(figwh1['pf'])
            st.plotly_chart(figwh1['fl'])
    with cont_wh2:
        figwh2 = obj_getpl_3wh.GetPl_Wh2()
        st.html(f"<span class='control_wh2'</span>")
        with st.container(border=border):
            st.html(f"<span class='info_wh2'</span>")
            st.write('WH2 CU: {}'.format(figwh2['cu']))
            # st.info('WH2 CU: {}'.format(figwh2['cu']), icon='🏚️')
        with st.container(border=border):
            st.html(f"<span class='fig_wh2'</span>")
            st.plotly_chart(figwh2['total'])
            st.plotly_chart(figwh2['hr'])
            st.plotly_chart(figwh2['pf'])
            st.plotly_chart(figwh2['fl'])
    with cont_wh3:
        figwh3 = obj_getpl_3wh.GetPl_Wh3()
        cont_wh3.html(f"<span class='control_wh3'</span>")
        with st.container(border=border):
            st.html(f"<span class='info_wh3'</span>")
            st.write('WH3 CU: {}'.format(figwh3['cu']))
            # st.info('WH3 CU: {}'.format(figwh3['cu']), icon='🏚️')
        with st.container(border=border):
            st.html(f"<span class='fig_wh3'</span>")
            st.plotly_chart(figwh3['total'])
            st.plotly_chart(figwh3['hr'])
            st.plotly_chart(figwh3['pf'])
            st.plotly_chart(figwh3['fl'])
    with cont_pf_cl:
        #title
        title_pf_cl= cont_pf_cl.columns([1])
        # Set Layout Kho cooling
        coo = obj_getpl_3wh.GetPl_Cooling()
        cont_cl = cont_pf_cl.container(border=border)
        cool_fig = cont_cl.columns([1])
        c1, c2 = cont_cl.columns([1, 1])
        c3, c4 = cont_cl.columns([1, 1])
        # Set Layout Kho Perfume
        pf = obj_getpl_3wh.GetPl_Perfume()
        cont_pf = cont_pf_cl.container(border=border)
        pf_fig = cont_pf.columns([1])
        p1, p2, p3 = cont_pf.columns([1, 1, 1])
        p4, p5, p6 = cont_pf.columns([1, 1, 1])

        with title_pf_cl[0].container(border=border):
            st.html(f"<span class='title_pf_cl'</span>")
            st.write('COOLING {} & PERFUME {}'.format(coo['cu'], pf['cu']))

        with cont_cl:
            cont_cl.html(f"<span class='cool'</span>")
            with st.container(border=border):
                cool_fig[0].html(f"<span class='fig_cool'</span>")
                cool_fig[0].plotly_chart(coo['cool_total'])
            with st.container(border=border):
                c1.html(f"<span class='cl_c1'</span>")
                c1.metric(**coo['cool1'].dict_metric())
                c2.html(f"<span class='cl_c2'</span>")
                c2.metric(**coo['cool2'].dict_metric())
                c3.html(f"<span class='cl_c3'</span>")
                c3.metric(**coo['cool3'].dict_metric())
                c4.html(f"<span class='cl_c4'</span>")
                c4.metric(**coo['cool_ww'].dict_metric())

        with cont_pf:
            cont_pf.html(f"<span class='perfume'</span>")
            with st.container(border=border):
                pf_fig[0].html(f"<span class='fig_perfume'</span>")
                pf_fig[0].plotly_chart(pf['pf_total'])
            with st.container(border=border):
                p1.html(f"<span class='pf_p1'</span>")
                p1.metric(**pf['pf1'].dict_metric())
                p2.html(f"<span class='pf_p2'</span>")
                p2.metric(**pf['pf2'].dict_metric())
                p3.html(f"<span class='pf_p3'</span>")
                p3.metric(**pf['pf3'].dict_metric())
                p4.html(f"<span class='pf_p4'</span>")
                p4.metric(**pf['pf4'].dict_metric())
                p5.html(f"<span class='pf_p5'</span>")
                p5.metric(**pf['pf5'].dict_metric())
                p6.html(f"<span class='pf_p6'</span>")
                p6.metric(**pf['pf_ww'].dict_metric())
        
    with cont_label_total:
        #=========BDWH===================
        cont_bdwh = cont_label_total.container(border=border)
        bdwh = obj_getpl_3wh.GetPl_Total()
        with cont_bdwh:
            cont_bdwh.html(f"<span class='bdwh'</span>")
            with st.container(border=border):
                st.html(f"<span class='title_bdwh'</span>")
                st.write('BDWH#123 (Ex EO, Cons) {}'.format(bdwh['cu']))
            with st.container(border=border):
                st.html(f"<span class='fig_bdwh'</span>")
                st.plotly_chart(bdwh['total_pl'])

        #=========Label==================
        cont_label = cont_label_total.container(border=border)
        figlb = obj_getpl_3wh.GetPl_LB()
        with cont_label:
            cont_label.html(f"<span class='label'</span>")
            with st.container(border=border):
                st.html(f"<span class='title_label'</span>")
                st.write('WH LABEL {}'.format(figlb['cu']))
            with st.container(border=border):
                st.html(f"<span class='fig_label'</span>")
                st.plotly_chart(figlb['total'])
        #==============EO===================
        cont_eo = cont_label_total.container(border=border)
        figeo = obj_getpl_3wh.GetPl_Eo()
        with cont_eo:
            cont_eo.html(f"<span class='eo'</span>")
            with st.container(border=border):
                st.html(f"<span class='title_eo'</span>")
                st.write('EO & CONS {}'.format(figeo['cu']))
            with st.container(border=border):
                st.html(f"<span class='fig_eo'</span>")
                st.plotly_chart(figeo['total'])

    with cont_metric:
        mt_steam = obj_getpl_3wh.GetPl_Steam()
        mt_scanout = obj_getpl_3wh.GetPl_Scanout()
        mt_fgls = obj_getpl_3wh.GetPl_Fgls()
        mt_fgdm = obj_getpl_3wh.GetPl_Fgdm()
        mt_matdm = obj_getpl_3wh.GetPl_Matdm()
        mt_lost = obj_getpl_3wh.GetPl_Lost()
        mt_pm_cat = obj_getpl_3wh.GetPl_PmWithCat()
        mt_fg_cat = obj_getpl_3wh.GetPl_FgWithCat()
        mt_lsl = obj_getpl_3wh.GetPl_Lsl()
        #chuyển tính fg, pm, rm xuống dưới cùng
        #vì khi tính fg, pm, rm cần chạy các method trên để lấy số trước
        mt_fg = obj_getpl_3wh.GetPl_Fg()
        mt_pm = obj_getpl_3wh.GetPl_Pm()
        mt_rm = obj_getpl_3wh.GetPl_Rm()

        # 'pleol': self.obj_lsl_in,
        # 'lslpm': self.obj_lsl_pm,
        # 'lslrm': self.obj_lsl_rm,
        # 'lrt': self.lsl_lrt
        with st.container(border=border):
            a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            a1.html(f"<span class='pm'</span>")
            a2.html(f"<span class='rm'</span>")
            a3.html(f"<span class='shipper'</span>")
            a4.html(f"<span class='bottle'</span>")
            a5.html(f"<span class='pouch'</span>")
            a6.html(f"<span class='other'</span>")
            a7.html(f"<span class='pleol'</span>")
            a8.html(f"<span class='lslpm'</span>")
            a9.html(f"<span class='lslrm'</span>")
            a10.html(f"<span class='lrt'</span>")

            
            a1.metric(**mt_pm['pm'].dict_metric())
            a2.metric(**mt_rm['rm'].dict_metric())
            a3.metric(**mt_pm_cat['shipper'].dict_metric())
            a4.metric(**mt_pm_cat['bottle'].dict_metric())
            a5.metric(**mt_pm_cat['pouch'].dict_metric())
            a6.metric(**mt_pm_cat['other'].dict_metric())
            a7.metric(**mt_lsl['pleol'].dict_metric())
            a8.metric(**mt_lsl['lslpm'].dict_metric())
            a9.metric(**mt_lsl['lslrm'].dict_metric())
            a10.metric(**mt_lsl['lrt'].dict_metric())

        with st.container(border=border):
            b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            b1.html(f"<span class='fg'</span>")
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

            b1.metric(**mt_fg['fg'].dict_metric())
            b2.metric(**mt_fg_cat['fgdwn'].dict_metric())
            b3.metric(**mt_fg_cat['fgfebz'].dict_metric())
            b4.metric(**mt_fg_cat['fghdl'].dict_metric())
            b5.metric(**mt_fg_cat['fgother'].dict_metric())
            b6.metric(**mt_scanout['scanout'].dict_metric())
            b7.metric(**mt_fgls['fgls'].dict_metric())
            b8.metric(**mt_fgdm['fgdm'].dict_metric())
            b9.metric(**mt_matdm['matdm'].dict_metric())
            b10.metric(**mt_lost['lost'].dict_metric())
            b11.metric(**mt_steam['steam'].dict_metric())
#=============================================TAB_EMPTYLOC===============================================
container_emploc = tab_emptyloc.container(border=border)
title_emp = container_emploc.container(border=border)
cont_emp = container_emploc.container(border=border)
with title_emp:
    st.html(f"<span class='title_emp'</span>")
    st.subheader('EMPTY LOCATION {}'.format(obj_getpl_3wh.StringDataTime))
with cont_emp:
    st.html(f"<span class='df_emp'</span>")
    st.dataframe(obj_getpl_3wh.GetEmptyLoc(), width=1000, height=1000, hide_index=True)
# obj_Empty = TabOther()
# oo = obj_Empty.Empty_Loc()
#=============================================COMBINE_BIN===============================================
cont_combine_bin = tab_combine.container(border=border)
title_combinebin = cont_combine_bin.container(border=border)
combinebin = cont_combine_bin.container(border=border)
with title_combinebin:
    st.html(f"<span class='title_commbinebin'</span>")
    st.subheader('COMBINE BIN {}'.format(obj_getpl_3wh.StringDataTime))
with combinebin:
    st.html(f"<span class='df_combinebin'</span>")
    st.dataframe(obj_getpl_3wh.GetCombinebin(), width=1000, height=None, hide_index=True)
#=============================================MIXUP===============================================
cont_mixup = tab_mixup.container(border=border)
title_mixup = cont_mixup.container(border=border)
mixup = cont_mixup.container(border=border)
with title_mixup:
    st.html(f"<span class='title_mixup'</span>")
    st.subheader('BIN MIXUP {}'.format(obj_getpl_3wh.StringDataTime))
with mixup:
    st.html(f"<span class='df_mixup'</span>")
    st.dataframe(obj_getpl_3wh.GetMixup(), width=1000, height=None, hide_index=True)
#=============================================TỒN KHO===============================================
cont_inv = tab_tonkho.container(border=border)
title_inv = cont_inv.container(border=border)
all_inv = cont_inv.container(border=border)
df_inventory_from_db = obj_getpl_3wh.GetInventory()
row_no = df_inventory_from_db.shape[0]
row_no = '{:,.0f}'.format(row_no)
with title_inv:
    st.html(f"<span class='title_inv'</span>")
    st.subheader('INVENTORY BALANCES. TOTAL ROWS DATA {}'.format(row_no))
with all_inv:
    st.html(f"<span class='df_inv'</span>")
    st.dataframe(df_inventory_from_db, width=1500, height=700, hide_index=True)


















