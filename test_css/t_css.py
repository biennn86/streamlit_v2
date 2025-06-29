import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Cấu hình trang
st.set_page_config(
    page_title="Warehouse Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        padding: 10px;
        margin: 5px;
        border: 1px solid #333;
    }
    
    .metric-grid {
        background-color: burlywood;
        border-radius: 8px;
        padding: 5px;
        margin: 5px;
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
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* CSS cho các section khác nhau */
    .top-section {
        margin-bottom: 5px;
    }
    
    .middle-section {
        margin: 20px 0;
    }
    
    .bottom-section {
        margin-top: 20px;
    }
    
    /* CSS cho header */
    .main-header {
        background: linear-gradient(90deg, #1e2329 0%, #2d3748 100%);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 5px;
        border-left: 4px solid #00ff88;
    }
    
    .header-title {
        color: #00ff88;
        font-size: 14px;
        font-weight: bold;
        margin: 0;
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
            padding: 8px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Hàm tạo gauge chart
def create_gauge(value, max_value, title=None, color="red", height=170):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'color': '#00ff88', 'size': 20}},
        gauge = {
            'axis': {'range': [None, max_value], 'tickcolor': "white", 'tickfont': {'size': 16}},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, max_value*0.7], 'color': "rgba(255,0,0,0.2)"},
                {'range': [max_value*0.7, max_value], 'color': "rgba(255,255,0,0.2)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': max_value*0.9
            }
        },
        number={'font': {'color': 'white', 'size': 36}}
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'size': 16},
        height=height,
        margin=dict(l=5, r=5, t=60, b=5)
    )
    
    return fig

# Hàm tạo metric card custom
def create_metric_card(title, value, delta=None, key=None):
    delta_html = ""
    if delta:
        delta_color = "#00ff88" if delta >= 0 else "#ff4444"
        delta_symbol = "↗" if delta >= 0 else "↘"
        delta_html = f'<div style="color: {delta_color}; font-size: 12px;">{delta_symbol} {abs(delta)}</div>'
    
    card_html = f"""
    <div class="metric-grid" id="{key or title.lower().replace(' ', '-')}">
        <div style="color: #000066; font-size: 24px; font-weight: bold; margin-bottom: 5px; text-align: center;">{title}</div>
        <div style="color: #174C4F; font-size: 32px; font-weight: bold; text-align: center;">{value}</div>
        {delta_html}
    </div>
    """
    return card_html

# Load CSS
load_custom_css()

# Header với container có thể control
st.markdown("""
<div class="main-header" id="main-header">
    <div class="header-title">📦 Warehouse Inventory Management System</div>
    <div class="header-subtitle">INVENTORY BY SUB WAREHOUSE 10-MAY-2025 22:08:38</div>
</div>
""", unsafe_allow_html=True)

# Top section - Gauge charts
st.markdown('<div class="top-section" id="top-section">', unsafe_allow_html=True)

# Sử dụng columns để layout
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown('<div class="gauge-container" id="wh1-container">', unsafe_allow_html=True)
    fig1 = create_gauge(1172, 2000, "WH1 CU: 96%", "#ff4444")
    st.plotly_chart(fig1, use_container_width=True, key="gauge1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Thêm 4 gauge phụ cho WH1
    st.markdown('<div class="gauge-container" id="wh1-sub1">', unsafe_allow_html=True)
    fig1_1 = create_gauge(898, 1200, "", "#ff4444", 150)
    st.plotly_chart(fig1_1, use_container_width=True, key="gauge1_1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="wh1-sub2">', unsafe_allow_html=True)
    fig1_2 = create_gauge(187, 300, "187", "#ff4444", 150)
    st.plotly_chart(fig1_2, use_container_width=True, key="gauge1_2")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="wh1-sub3">', unsafe_allow_html=True)
    fig1_3 = create_gauge(87, 150, "87", "#ff4444", 150)
    st.plotly_chart(fig1_3, use_container_width=True, key="gauge1_3")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="gauge-container" id="wh2-container">', unsafe_allow_html=True)
    fig2 = create_gauge(5478, 7000, "WH2 CU: 109%", "#ff4444")
    st.plotly_chart(fig2, use_container_width=True, key="gauge2")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Thêm 4 gauge phụ cho WH2
    st.markdown('<div class="gauge-container" id="wh2-sub1">', unsafe_allow_html=True)
    fig2_1 = create_gauge(3604, 4000, "3604", "#ff4444", 150)
    st.plotly_chart(fig2_1, use_container_width=True, key="gauge2_1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="wh2-sub2">', unsafe_allow_html=True)
    fig2_2 = create_gauge(753, 1000, "753", "#ff4444", 150)
    st.plotly_chart(fig2_2, use_container_width=True, key="gauge2_2")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="wh2-sub3">', unsafe_allow_html=True)
    fig2_3 = create_gauge(831, 1200, "831", "#ff4444", 150)
    st.plotly_chart(fig2_3, use_container_width=True, key="gauge2_3")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="gauge-container" id="wh3-container">', unsafe_allow_html=True)
    fig3 = create_gauge(5478, 7000, "WH2 CU: 109%", "#ff4444")
    st.plotly_chart(fig3, use_container_width=True, key="gauge3")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Thêm 4 gauge phụ cho WH3
    st.markdown('<div class="gauge-container" id="wh3-sub1">', unsafe_allow_html=True)
    fig3_1 = create_gauge(1729, 2000, "1729", "#ffaa00", 150)
    st.plotly_chart(fig3_1, use_container_width=True, key="gauge3_1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="wh3-sub2">', unsafe_allow_html=True)
    fig3_2 = create_gauge(409, 600, "409", "#ff4444", 150)
    st.plotly_chart(fig3_2, use_container_width=True, key="gauge3_2")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="wh3-sub3">', unsafe_allow_html=True)
    fig3_3 = create_gauge(383, 500, "383", "#ff4444", 150)
    st.plotly_chart(fig3_3, use_container_width=True, key="gauge3_3")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="gauge-container" id="cooling-container">', unsafe_allow_html=True)
    fig4 = create_gauge(251, 400, "COOLING: 63%", "#ffaa00")
    st.plotly_chart(fig4, use_container_width=True, key="gauge4")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics cho Cooling section
    st.markdown('<div class="metric-grid" id="cooling-metrics1">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <div style="text-align: center;">
            <div style="color: #a0a0a0; font-size: 10px;">C1 - P6</div>
            <div style="color: white; font-size: 18px; font-weight: bold;">57</div>
        </div>
        <div style="text-align: center;">
            <div style="color: #a0a0a0; font-size: 10px;">C2 - P8</div>
            <div style="color: white; font-size: 18px; font-weight: bold;">128</div>
        </div>
    </div>
    <div style="display: flex; justify-content: space-between;">
        <div style="text-align: center;">
            <div style="color: #a0a0a0; font-size: 10px;">C3 - P9</div>
            <div style="color: white; font-size: 18px; font-weight: bold;">66</div>
        </div>
        <div style="text-align: center;">
            <div style="color: #a0a0a0; font-size: 10px;">Floor - P8</div>
            <div style="color: white; font-size: 18px; font-weight: bold;">0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gauge phụ cho Cooling
    st.markdown('<div class="gauge-container" id="cooling-sub1">', unsafe_allow_html=True)
    fig4_1 = create_gauge(295, 400, "295", "#ffaa00", 150)
    st.plotly_chart(fig4_1, use_container_width=True, key="gauge4_1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics grid cho các tầng
    st.markdown('<div class="metric-grid" id="cooling-metrics2">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center;">
        <div>
            <div style="color: #a0a0a0; font-size: 10px;">P1 - 52</div>
            <div style="color: white; font-size: 16px; font-weight: bold;">22</div>
        </div>
        <div>
            <div style="color: #a0a0a0; font-size: 10px;">P2 - 42</div>
            <div style="color: white; font-size: 16px; font-weight: bold;">31</div>
        </div>
        <div>
            <div style="color: #a0a0a0; font-size: 10px;">P3 - 36</div>
            <div style="color: white; font-size: 16px; font-weight: bold;">35</div>
        </div>
        <div>
            <div style="color: #a0a0a0; font-size: 10px;">P4 - 48</div>
            <div style="color: white; font-size: 16px; font-weight: bold;">45</div>
        </div>
        <div>
            <div style="color: #a0a0a0; font-size: 10px;">P5 - 108</div>
            <div style="color: white; font-size: 16px; font-weight: bold;">153</div>
        </div>
        <div>
            <div style="color: #a0a0a0; font-size: 10px;">Floor - 37</div>
            <div style="color: white; font-size: 16px; font-weight: bold;">7</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="gauge-container" id="bonded-container">', unsafe_allow_html=True)
    fig5 = create_gauge(5013, 7000, "BONDED FEI: 92%", "#ff4444")
    st.plotly_chart(fig5, use_container_width=True, key="gauge5")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gauge phụ cho Bonded
    st.markdown('<div class="gauge-container" id="bonded-sub1">', unsafe_allow_html=True)
    fig5_1 = create_gauge(926, 1200, "WH LABEL: 90%", "#ffaa00", 150)
    st.plotly_chart(fig5_1, use_container_width=True, key="gauge5_1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gauge-container" id="bonded-sub2">', unsafe_allow_html=True)
    fig5_2 = create_gauge(442, 700, "EQ & CONE: 63%", "#ffaa00", 150)
    st.plotly_chart(fig5_2, use_container_width=True, key="gauge5_2")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Middle section - Metrics grid
st.markdown('<div class="middle-section" id="middle-section">', unsafe_allow_html=True)

# Tạo layout cho metrics
metrics_col1, metrics_col2 = st.columns([2, 1])

with metrics_col1:
    # Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_metric_card("PALLET/BBG", "5010"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("NORMAL BBG", "355"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("SHIPPER", "855"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("BOTTLE", "889"), unsafe_allow_html=True)
    with col5:
        st.markdown(create_metric_card("POUCH", "1138"), unsafe_allow_html=True)
    
    # Row 2
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_metric_card("DRUM", "3232"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("PP DRUM", "2661"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("FIBER", "304"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("PP WOVEN", "563"), unsafe_allow_html=True)
    with col5:
        st.markdown(create_metric_card("PI FIBER", "55"), unsafe_allow_html=True)

with metrics_col2:
    # Các metric khac
    st.markdown(create_metric_card("WH LABEL: 90%", "926"), unsafe_allow_html=True)
    st.markdown(create_metric_card("EQ & CONE: 63%", "442"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Bottom section
st.markdown('<div class="bottom-section" id="bottom-section">', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_metric_card("OTHER", "2241"), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card("PI LOT", "86"), unsafe_allow_html=True)
with col3:
    st.markdown(create_metric_card("LOT FIB", "115"), unsafe_allow_html=True)
with col4:
    st.markdown(create_metric_card("LOT SW", "17"), unsafe_allow_html=True)
with col5:
    st.markdown(create_metric_card("LIST", "15"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# JavaScript để control dynamic (nếu cần)
st.markdown("""
<script>
// Thêm các function JavaScript để control elements
function updateElementStyle(elementId, styles) {
    const element = document.getElementById(elementId);
    if (element) {
        Object.assign(element.style, styles);
    }
}

// Example: Thay đổi màu background của một container
// updateElementStyle('top-section', {backgroundColor: '#2d3748'});
</script>
""", unsafe_allow_html=True)

# Sidebar để control real-time (optional)
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    # Color controls
    primary_color = st.color_picker("Primary Color", "#00ff88")
    background_color = st.color_picker("Background Color", "#0e1117")
    
    # Layout controls
    gauge_height = st.slider("Gauge Height", 150, 300, 200)
    container_padding = st.slider("Container Padding", 5, 30, 15)
    
    # Apply changes button
    if st.button("Apply Changes"):
        # Update CSS với JavaScript
        st.markdown(f"""
        <script>
        document.documentElement.style.setProperty('--primary-color', '{primary_color}');
        document.documentElement.style.setProperty('--bg-color', '{background_color}');
        </script>
        """, unsafe_allow_html=True)
        st.success("Styles updated!")

# Cách sử dụng để control từng element:
st.markdown("""
---
### 🎯 Cách Control Từng Element:

1. **CSS Classes**: Mỗi container có class và ID riêng để target
2. **JavaScript**: Sử dụng `updateElementStyle()` function
3. **Sidebar Controls**: Real-time control panel
4. **Custom CSS**: Inject CSS trực tiếp vào từng element

**Example để thay đổi style:**
```python
# Thay đổi background color của gauge container
st.markdown('''
<style>
#wh1-container {
    background: linear-gradient(45deg, #1e2329, #2d3748) !important;
}
</style>
''', unsafe_allow_html=True)
```
""")