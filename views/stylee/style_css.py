import streamlit as st

# Custom CSS để control từng phần tử
def load_custom_css():
    st.markdown("""
    <style>
    /* Ẩn header và footer mặc định */
    MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom CSS cho toàn bộ app */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    /* Container chứa toàn bộ nội dung chính của ứng dụng */
    /* Tất cả nội dung Streamlit của bạn (titles, charts, widgets, etc.) */
    /* Toàn bộ layout columns */
    /* Các components như st.write(), st.plotly_chart(), etc. */
    .block-container {
        width: 100% !important; /* Chiếm toàn bộ chiều rộng */
        padding: 1rem 2rem 1rem !important; /* Padding: top=2rem, left/right=1rem, bottom=5rem */
        max-width: initial !important;  /* Không giới hạn chiều rộng tối đa */
        min-width: auto !important; /* Chiều rộng tối thiểu tự động */
    }
                
    /* Điều chỉnh khoảng cách giữa các gauge streamlit */
    .stPlotlyChart {
        margin-bottom: -30px !important;
        margin-top: -18px !important;
    }
                
    /* CSS cho metric cards */
    [data-testid="metric-container"] {
        background-color: #1e2329;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* CSS cho từng container có thể customize riêng */
    .gauge-container {
        background-color: #1e2329;
        border-radius: 8px;
        padding: 2px;
        margin: 2px;
        border: 1px solid #333;
    }
    
    .metric-grid {
        background-color: burlywood;
        border: 2px solid #CCCCCC;
        border-left: 6px solid #00ff88;
        border-radius: 8px;
        padding: 2px;
        margin: 2px; #(theo thứ tự kim đồng hồ: trên, phải, dưới, trái)
    }
    
    /* CSS cho gauge charts */
    .gauge-title {
        color: #00ff88;
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* CSS cho gauge nhỏ hơn */
    .gauge-container {
        # min-height: 0px;
        display: none;
    }
    
    /* CSS cho metric grid nhỏ gọn */
    .metric-grid {
        min-height: 0px;
        display: flex;
        flex-direction: column;
        justify-content: center; 
    }
    
    /* CSS cho các section khác nhau */
    .top-section {
        margin-bottom: 20px;
    }
    
    .middle-section {
        margin: 20px 0;
    }
    
    .bottom-section {
        margin-top: 20px;
    }
    
    /* CSS cho header */
    .main-header {
        # background: linear-gradient(90deg, #1e2329 0%, #2d3748 100%);
        padding: 2px;
        # border: 1px solid #CCCCCC;
        border-radius: 12px;
        margin-bottom: 2px;
        # border-left: 4px solid #00ff88;
        text-align: center;
        box-shadow: 10px 0px 20px rgba(4, 12, 226, 0.2);
    }
    
    .header-title {
        color: #39FF14; /*#00ff88*/
        font-size: 36px;
        font-weight: bold;
        margin: 0px;
    }
    
    .header-subtitle {
        color: #a0a0a0;
        font-size: 14px;
        margin: 5px 0 0 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .gauge-container {
            margin: 2px;
            padding: 2px;
        }
    }
                
    @media (max-width: 480px) {
    .gauge-container {
        grid-template-columns: 1fr;
        grid-gap: 5px;
        }
    }
                
    /*-------------Căn giữa data trong df---------------*/
    .stDataFrame th {
        text-align: center !important;
    }
    
    .stDataFrame td {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)


#-----------------------------------------------
# def load_custom_css():
#     st.markdown("""
#     <style>
#     /* Ẩn header và footer mặc định */
#     MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
    
#     /* Custom CSS cho toàn bộ app */
#     .stApp {
#         background-color: #0e1117;
#         color: white;
#     }
    
#     /* LOẠI BỎ HOÀN TOÀN SPACING CỦA STREAMLIT */
#     .block-container {
#         padding: 0 !important;
#         margin: 0 !important;
#         max-width: 100% !important;
#     }
    
#     /* Loại bỏ margin/padding của tất cả elements */
#     .element-container {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     /* Loại bỏ spacing giữa columns */
#     .stColumn {
#         padding: 0 !important;
#         margin: 0 !important;
#     }
    
#     /* Loại bỏ gap giữa columns */
#     .stHorizontal {
#         gap: 0 !important;
#     }
    
#     .stVertical {
#         gap: 0 !important;
#     }
    
#     /* Loại bỏ spacing của vertical blocks */
#     div[data-testid="stVerticalBlock"] {
#         gap: 0 !important;
#     }
    
#     div[data-testid="stVerticalBlock"] > div {
#         gap: 0 !important;
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     /* CSS cho metric cards - SIÊU COMPACT */
#     [data-testid="metric-container"] {
#         background-color: #1e2329;
#         border: 1px solid #333;
#         border-radius: 4px;
#         padding: 2px !important;
#         margin: 0 !important;
#         box-shadow: 0 1px 2px rgba(0,0,0,0.3);
#         min-height: auto !important;
#         height: auto !important;
#     }
    
#     /* Thu nhỏ metric text */
#     [data-testid="metric-container"] [data-testid="metric-value"] {
#         font-size: 18px !important;
#         line-height: 1 !important;
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     [data-testid="metric-container"] [data-testid="metric-label"] {
#         font-size: 10px !important;
#         margin: 0 !important;
#         padding: 0 !important;
#         line-height: 1 !important;
#     }
    
#     /* CSS cho gauge container - ZERO SPACING */
#     .gauge-container {
#         background-color: #1e2329;
#         border-radius: 4px;
#         padding: 0 !important;
#         margin: 0 !important;
#         border: 1px solid #333;
#         min-height: auto !important;
#         height: auto !important;
#         display: none;
#     }
    
#     /* CSS cho metric grid - ZERO SPACING */
#     .metric-grid {
#         background-color: burlywood;
#         border: 1px solid #CCCCCC;
#         border-left: 2px solid #00ff88;
#         border-radius: 4px;
#         padding: 1px !important;
#         margin: 2px !important;
#         min-height: 10px !important;
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         align-items: center;
#     }
    
#     /* LOẠI BỎ HOÀN TOÀN MARGIN/PADDING CỦA PLOTLY */
#     .js-plotly-plot {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     .plotly-graph-div {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     /* CSS cho gauge charts */
#     .gauge-title {
#         color: #00ff88;
#         font-size: 10px;
#         font-weight: bold;
#         text-align: center;
#         margin: 0 !important;
#         padding: 0 !important;
#         line-height: 1;
#     }
    
#     /* LOẠI BỎ TẤT CẢ SPACING */
#     .stMarkdown {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     .stMetric {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     /* CSS cho header - COMPACT HOÀN TOÀN */
#     .main-header {
#         background: linear-gradient(90deg, #1e2329 0%, #2d3748 100%);
#         padding: 5px;
#         border-radius: 4px;
#         margin: 2px !important;
#         border-left: 2px solid #00ff88;
#         text-align: center;
#     }
    
#     .header-title {
#         color: #00ff88;
#         font-size: 20px;
#         font-weight: bold;
#         margin: 2px !important;
#         padding: 0 !important;
#         line-height: 1;
#     }
    
#     .header-subtitle {
#         color: #a0a0a0;
#         font-size: 10px;
#         margin: 0 !important;
#         padding: 0 !important;
#         line-height: 1;
#     }
    
#     /* OVERRIDE TẤT CẢ CSS MẶC ĐỊNH CỦA STREAMLIT */
#     .css-1d391kg, .css-1inwz65, .css-1y4p8pa {
#         padding: 0 !important;
#         margin: 0 !important;
#     }
    
#     /* Loại bỏ spacing của containers */
#     .css-ocqkz7, .css-1kyxreq {
#         margin: 0 !important;
#         padding: 0 !important;
#         gap: 0 !important;
#     }
    
#     /* CSS cho sections - ZERO MARGIN */
#     .top-section, .middle-section, .bottom-section {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     /* FORCE ZERO SPACING cho tất cả divs */
#     div {
#         margin: 0;
#         padding: 0;
#     }
    
#     /* Exceptions cho specific elements cần padding */
#     .main-header, .gauge-title {
#         margin: 2px !important;
#         padding: 2px !important;
#     }
    
#     /* Thu nhỏ font cho compact hơn */
#     html, body, .stApp {
#         font-size: 12px !important;
#     }
    
#     /* DENSE LAYOUT - spacing = 0 */
#     .dense-layout {
#         display: grid !important;
#         grid-gap: 0 !important;
#         gap: 0 !important;
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     .dense-layout > div {
#         margin: 0 !important;
#         padding: 0 !important;
#     }
    
#     /* CUSTOM GRID cho gauges */
#     .gauge-grid {
#         display: grid;
#         grid-template-columns: repeat(5, 1fr);
#         grid-gap: 1px;
#         gap: 1px;
#         margin: 0;
#         padding: 0;
#     }
    
#     .metric-grid-bottom {
#         display: grid;
#         grid-template-columns: repeat(10, 1fr);
#         grid-gap: 1px;
#         gap: 1px;
#         margin: 0;
#         padding: 0;
#     }
    
#     /* Mobile responsive - vẫn giữ zero spacing */
#     @media (max-width: 768px) {
#         .gauge-grid {
#             grid-template-columns: repeat(3, 1fr);
#         }
#         .metric-grid-bottom {
#             grid-template-columns: repeat(5, 1fr);
#         }
#     }
    
#     @media (max-width: 480px) {
#         .gauge-grid {
#             grid-template-columns: repeat(2, 1fr);
#         }
#         .metric-grid-bottom {
#             grid-template-columns: repeat(3, 1fr);
#         }
#     }
    
#     /* OVERRIDE tất cả margin/padding có thể */
#     * {
#         margin: 2px !important;
#         padding: 2px !important;
#         box-sizing: border-box !important;
#     }
    
#     /* Exceptions cho text content */
#     .main-header *, .gauge-title, [data-testid="metric-value"], [data-testid="metric-label"] {
#         margin: 1px !important;
#         padding: 1px !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)