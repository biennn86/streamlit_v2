# import plotly.express as px
import plotly.graph_objects as go
# import matplotlib.pyplot as plt

class CreateGauge():
    def __init__(self, title, value, capa=1):
        self.title = title
        self.value = value
        self.capa = capa
        self.color_bar = None
       
    def create_gauge(self):
         #Tính CU
        self.cu = self.value/self.capa
        if self.cu <= 0.4:
            self.color_bar = '#33FFFF'
        elif 0.4 < self.cu < 0.9:
            self.color_bar = '#FFFF00'
        else:
            self.color_bar = '#EE0000'

        #draw fig
        fig = go.Figure(go.Indicator(
        domain = {'x': [0.1, 0.289], 'y': [0, 0]},
        value = self.value,
        mode = "gauge+number",
        # delta = {'reference': 100},
        number = {'valueformat': '.0f'},
        title = {'text': self.title},
        gauge = {'axis': {'range': [0, self.capa], 'tickvals': [0, self.capa], 'ticktext': ['0', self.capa], 'tickfont': {'size': 12}}, 
        'bar': {'color': self.color_bar, 'thickness': 1.0},
        'bordercolor': '#0E1117',
        'bgcolor': 'lightgray',
        }))

        fig.update_layout(margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
                          height=70, width=600, #57; 500
                          
                          )

        return fig
    
class StMetric:
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

    def dict_metric(self):
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
        return dict_metric

    def update_value(self, new_value):
        self.value = new_value
        self.delta = new_value - self.value_old
        self.value_old = new_value