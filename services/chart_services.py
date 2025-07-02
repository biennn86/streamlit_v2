# import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
# import matplotlib.pyplot as plt

class GaugeChart():
    def __init__(self, title, value, capa=1, height=None):
        self.title = title
        self.value = value
        self.capa = capa
        self.height = height
        self.color_bar = None
       
    def create_fig(self):
         #Tính CU
        self.cu = self.value/self.capa
        if self.cu <= 0.4:
            self.color_bar = '#33FFFF'
        elif 0.4 < self.cu < 0.9:
            self.color_bar = '#FFFF00'
        else:
            self.color_bar = '#EE0000'

        #set height_chart
        if self.height is None:
            self.height = 100
        else:
            self.height = 110

        #draw fig
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = self.value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            # title = {
            #     'text': self.title,
            #     'font': {'color': '#00ff88', 'size': 20},
            #     'align': 'center', # Căn giữa tiêu đề
            #     },
            # delta = {'reference': 100},
            gauge = {
                'axis': {
                    'range': [0, self.capa], # Phạm vi từ 0 đến 2000
                    'tickvals': [0, self.capa], # Chỉ hiển thị số 0 và 2000
                    'ticktext': ['0', str(self.capa)], # Nhãn cho các tick
                    'tickfont': {'size': 12, 'weight': 'normal'} # Kích thước font cho số trên trục
                    }, 
                'bar': {
                    'color': self.color_bar, # Màu của thanh chỉ báo tiến trình
                    'thickness': 1.0}, # kích thước thanh tiến trình bằng với viền ngoài
                    # 'bgcolor': 'rgba(0,0,0,0)', # Nền của gauge trong suốt (quan trọng cho nền đen)
                    'bordercolor': '#0E1117', #Màu đường viền gauge
                    'bgcolor': 'lightgray', # Màu nền vòng cung trong gauge
                    },
                    
            number = {
                'valueformat': '.0f',
                'font': {
                    'color': 'white',
                    'size': 26
                    }
                    },
        ))

        # Danh sách chứa các annotations (chú thích)
        annotations = []
        # CHỈ THÊM ANNOTATION NẾU title_text KHÔNG RỖNG
        if self.title:
            annotations.append(
                go.layout.Annotation(
                   text=self.title,
                    xref='paper', # Tham chiếu theo tọa độ của toàn bộ giấy (figure)
                    yref='paper', # Tham chiếu theo tọa độ của toàn bộ giấy (figure)
                    x=0.5,        # Căn giữa theo chiều ngang (0.5 là chính giữa)
                    y=1.15,       # Đặt vị trí Y (0 là đáy, 1 là đỉnh của figure). 0.95 thường là trên cùng.
                    showarrow=False, # Không hiển thị mũi tên
                    font=dict(
                        family='Open Sans, sans-serif', # font chữ title
                        size=14,        # Kích thước font cho tiêu đề
                        color="#39FF14", # Màu xanh lá cho tiêu đề #39FF14
                        weight='bold' # chữ đậm
                    ),
                    xanchor='center', # Căn giữa văn bản theo trục x
                    yanchor='middle'  # Căn giữa văn bản theo trục y
                        )
                )

        fig.update_layout(
            height=self.height,
            margin=dict(l=2, r=2, t=24, b=5),
            # paper_bgcolor="black", # Đặt màu nền của toàn bộ biểu đồ là đen
            # plot_bgcolor="black", # Đặt màu nền của vùng vẽ là đen
            annotations=annotations # Gán danh sách annotations vào layout
                          )

        return fig
    
class Metric:
    def __init__(self, label, value, delta=None, delta_color="normal", help = None, **kwargs):
        """
        Tạo một đối tượng st.metric

        Args:
            label (str): Nhãn của metric.
            value (int or float): Giá trị của metric.
            delta (int or float, optional): Sự thay đổi so với giá trị trước đó. Defaults to None.
            delta_color (str, optional): Màu sắc của delta. Defaults to "normal".
            help_text (str, optional): Text giúp đỡ. Defaults to None.
            **kwargs: Các tham số tùy chọn khác truyền vào st.metric.
        """
        self.label = label
        self.value = value
        self.delta = delta
        self.delta_color = delta_color
        self.help = help
        self.kwargs = kwargs

        
    
    def get_info_metric(self):
        """
       Tạo dict nạp vào metric.
        """
        dict_metric = {
            'label' : self.label,
            'value' : self.value,
            'delta' : self.delta,
            'delta_color' : self.delta_color,
            'help' : self.help
            # **self.kwargs
            }
        
        # return dict_metric
    
    def update_value(self, new_value):
        self.value = new_value
        self.delta = new_value - self.value_old
        self.value_old = new_value

    # Hàm tạo metric card custom
    def create_metric_card(self):
        delta_html = ""
        if self.delta:
            delta_color = "#00ff88" if self.delta >= 0 else "#ff4444"
            delta_symbol = "↗" if self.delta >= 0 else "↘"
            delta_html = f'<div style="color: {delta_color}; font-size: 12px;">{delta_symbol} {abs(self.delta)}</div>'
        
        card_html = f"""
        <div class="metric-grid" id="{None or self.label.lower().replace(' ', '-')}">
            <div style="color: #000066; font-size: 10px; font-weight: bold; margin-bottom: 0px; text-align: center;">{self.label}</div>
            <div style="color: #174C4F; font-size: 18px; font-weight: bold; margin-bottom: 0px; text-align: center;">{self.value}</div>
            {delta_html}
        </div>
        """
        return card_html
        


#============================
# import plotly.graph_objects as go

# class GaugeChart:
#     """
#     Tạo một biểu đồ gauge (đồng hồ đo) tùy chỉnh bằng Plotly.

#     Biểu đồ sẽ hiển thị giá trị hiện tại so với một công suất tối đa
#     và thay đổi màu sắc của thanh đồng hồ dựa trên tỷ lệ sử dụng công suất (CU).
#     """

#     # Hằng số định nghĩa ngưỡng và màu sắc
#     _CU_LOW_THRESHOLD = 0.4
#     _CU_HIGH_THRESHOLD = 0.9

#     _COLOR_LOW_CU = '#33FFFF'  # Xanh lam nhạt (ví dụ: công suất thấp, an toàn)
#     _COLOR_MEDIUM_CU = '#FFFF00' # Vàng (ví dụ: công suất trung bình)
#     _COLOR_HIGH_CU = '#EE0000' # Đỏ (ví dụ: công suất cao, cảnh báo)

#     # Cấu hình mặc định cho layout và gauge
#     _DEFAULT_LAYOUT_HEIGHT = 70
#     _DEFAULT_LAYOUT_WIDTH = 600
#     _DEFAULT_GAUGE_THICKNESS = 1.0
#     _DEFAULT_GAUGE_BORDER_COLOR = '#0E1117'
#     _DEFAULT_GAUGE_BG_COLOR = 'lightgray'

#     def __init__(self, title: str, value: (int | float), capacity: (int | float) = 1):
#         """
#         Khởi tạo một đối tượng CreateGauge.

#         Args:
#             title (str): Tiêu đề sẽ hiển thị trên đồng hồ đo.
#             value (int | float): Giá trị hiện tại mà đồng hồ đo sẽ hiển thị.
#             capacity (int | float): Giá trị tối đa (giới hạn trên) của đồng hồ đo. Mặc định là 1.

#         Raises:
#             ValueError: Nếu 'capacity' nhỏ hơn hoặc bằng 0, hoặc 'value' âm.
#         """
#         # if not isinstance(title, str) or not title:
#         #     raise ValueError("Title must be a non-empty string.")
#         if not isinstance(value, (int, float)) or value < 0:
#             raise ValueError("Value must be a non-negative number.")
#         if not isinstance(capacity, (int, float)) or capacity <= 0:
#             raise ValueError("Capacity must be a positive number.")

#         self.title = title
#         self.value = value
#         self.capacity = capacity
#         self._color_bar = None # Thuộc tính nội bộ để lưu trữ màu thanh

#     def _calculate_color(self) -> str:
#         """
#         Tính toán và trả về mã màu cho thanh đồng hồ dựa trên tỷ lệ sử dụng công suất (CU).
#         """
#         if self.capacity == 0: # Đã xử lý ở __init__, nhưng an toàn hơn khi kiểm tra lại
#             return self._COLOR_LOW_CU # Hoặc một màu lỗi mặc định

#         cu = self.value / self.capacity

#         if cu <= self._CU_LOW_THRESHOLD:
#             return self._COLOR_LOW_CU
#         elif self._CU_LOW_THRESHOLD < cu < self._CU_HIGH_THRESHOLD:
#             return self._COLOR_MEDIUM_CU
#         else:
#             return self._COLOR_HIGH_CU

#     def create_fig(self) -> go.Figure:
#         """
#         Tạo và trả về đối tượng Plotly Figure cho biểu đồ gauge.

#         Returns:
#             plotly.graph_objects.Figure: Đối tượng Figure chứa biểu đồ gauge đã cấu hình.
#         """
#         self._color_bar = self._calculate_color() # Xác định màu sắc trước khi vẽ

#         # Cấu hình cho đồng hồ đo Plotly
#         gauge_config = {
#             'axis': {
#                 'range': [0, self.capacity],
#                 'tickvals': [0, self.capacity],
#                 'ticktext': ['0', str(self.capacity)], # Đảm bảo ticktext là string
#                 'tickfont': {'size': 12}
#             },
#             'bar': {
#                 'color': self._color_bar,
#                 'thickness': self._DEFAULT_GAUGE_THICKNESS
#             },
#             'bordercolor': self._DEFAULT_GAUGE_BORDER_COLOR,
#             'bgcolor': self._DEFAULT_GAUGE_BG_COLOR
#         }

#         # Tạo đối tượng Indicator
#         indicator = go.Indicator(
#             domain = {'x': [0.1, 0.289], 'y': [0, 0]},
#             value = self.value,
#             mode = "gauge+number",
#             number = {'valueformat': '.0f'},
#             title = {'text': self.title},
#             gauge = gauge_config
#         )

#         # Tạo Figure và cập nhật layout
#         fig = go.Figure(indicator)
#         fig.update_layout(
#             margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
#             height=self._DEFAULT_LAYOUT_HEIGHT,
#             width=self._DEFAULT_LAYOUT_WIDTH
#         )

#         return fig

# # --- Cách sử dụng ---
# if __name__ == "__main__":
#     # Ví dụ 1: Công suất thấp (màu xanh)
#     gauge_low_cu = CreateGauge(title="Sản lượng: Thấp", value=30, capacity=100)
#     fig_low = gauge_low_cu.create_gauge()
#     fig_low.show()

#     # Ví dụ 2: Công suất trung bình (màu vàng)
#     gauge_medium_cu = CreateGauge(title="Sản lượng: Trung bình", value=65, capacity=100)
#     fig_medium = gauge_medium_cu.create_gauge()
#     fig_medium.show()

#     # Ví dụ 3: Công suất cao (màu đỏ)
#     gauge_high_cu = CreateGauge(title="Sản lượng: Cao", value=92, capacity=100)
#     fig_high = gauge_high_cu.create_gauge()
#     fig_high.show()

#     # Ví dụ 4: Kiểm tra xử lý lỗi
#     try:
#         gauge_error = CreateGauge(title="Lỗi", value=50, capacity=0)
#         fig_error = gauge_error.create_gauge()
#         fig_error.show()
#     except ValueError as e:
#         print(f"\nLỗi khi khởi tạo gauge: {e}")