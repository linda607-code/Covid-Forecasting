import glob
import os

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import QUrl, pyqtProperty, QFile
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
import UI
import sys
from pyecharts import options as opts
from pyecharts.charts import Map
import pandas as pd
import paho.mqtt.client as mqtt
import draw

# 输入数据
DATA_PATH = r"../data/"
# 输出html路径
TMP_PATH = r"../output/"

SERVER_IP = "127.0.0.1"
# SERVER_IP = "150.158.80.33"
# 服务器端口
SERVER_PORT = 1883

# # 服务器地址
# SERVER_IP = "150.158.80.33"
# # 服务器端口
# SERVER_PORT = 1884
# 消息主题
TOPIC = "/covid"

# 全局变量
ui_components = None
date_text = ""
# total_df = pd.DataFrame()
total_df = None
last_df = None


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("已连接到mqtt服务器")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(SERVER_IP, SERVER_PORT)
    return client


# 刷新地图
def refresh_webview():
    wpath = os.path.abspath(os.path.dirname(os.getcwd()))
    furl = QUrl.fromLocalFile(os.path.join(wpath, "output", "render.html"))
    global ui_components
    ui_components.webview.load(furl)
    ui_components.dateLabel.setText("当前日期：" + date_text)


def on_message(client, userdata, msg):
    print(f"收到消息: {msg.payload.decode()}")
    json_str = msg.payload.decode()
    df = pd.read_json(json_str)
    # 重命名特殊省份
    df['provinceName'].replace("宁夏回族自治区", "宁夏", inplace=True)
    df['provinceName'].replace("广西壮族自治区", "广西", inplace=True)
    df['provinceName'].replace("内蒙古自治区", "内蒙古", inplace=True)
    df['provinceName'].replace("新疆维吾尔自治区", "新疆", inplace=True)
    df['provinceName'].replace("西藏自治区", "西藏", inplace=True)
    # 填补数据
    global last_df
    if last_df is not None:
        df = pd.concat([df, last_df])
        df = df.drop_duplicates(subset=['provinceName'], keep='first')
    last_df = df
    # 更新总表
    global total_df
    if total_df is None:
        total_df = df
    else:
        total_df = pd.concat([total_df, df])
    # 更新地图
    global date_text
    date_text = df['updateTime'].values[0].replace("/", "-")
    render_map(df, date_text)
    ui_components.testButton.clicked.emit()


# 渲染地图html
def render_map(org_data, date_str):
    # 读取并处理数据
    c_conv_data = org_data
    if len(c_conv_data) == 0:
        return
    c_list_data = list(zip(list(c_conv_data['provinceName']), list(c_conv_data['province_confirmedCount'])))
    # 配置地图参数
    mp = Map(
        init_opts=opts.InitOpts(
            chart_id="map",
            width=f"{ui_components.webview.width() - 10}px",
            height=f"{ui_components.webview.height() - 20}px"
        ),
    )

    mp.add_js_funcs(
        """
        document.addEventListener("DOMContentLoaded", function () {
            new QWebChannel( qt.webChannelTransport, function(channel) {
                window.con = channel.objects.con;
            });
        });
        chart_map.on('click', function(params){
            if ( window.con) {
                window.con.value = params.name;
            }
        });
        """
    )
    mp.add(
        series_name="各省市确诊人数",
        data_pair=c_list_data,
        maptype="china",
        zoom=1.2,
        # is_roam=False,
        itemstyle_opts={
            # 强调颜色
            "emphasis": {"areaColor": "#CEE5E8"}
        }
    )
    mp.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    mp.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=15000,
            range_color=['#FAD4D5', '#E50000', '#A30000']
        ),
    )
    # 渲染
    mp.render(path=TMP_PATH + "render.html")
    print(date_str + "地图已渲染")
    f = open(TMP_PATH + "render.html", 'r+')
    flist = f.readlines()
    f.close()
    flist[7] = '<script src="qrc:///qtwebchannel/qwebchannel.js"></script>\n'
    f = open(TMP_PATH + "render.html", 'w+')
    f.writelines(flist)
    f.close()



def forecast(name):
    df = total_df[total_df['provinceName'] == name]
    df = df.reset_index()
    if len(df) < 10:
        print("数据量不足")
        return
    tmp = 0
    with open(DATA_PATH + "data_fordraw.csv", 'w') as f:
        for idx, row in df.iterrows():
            total = int(row['province_confirmedCount'])
            f.write(str(idx) + "," + str(total) + '\n')
            tmp = total
    draw.draw(name)

# def forecast(name):
#     global total_df
#     # 检查 total_df 是否为空
#     if total_df is None or total_df.empty:
#         print("total_df 数据为空，无法进行预测")
#         return
#
#     # 按省份过滤数据
#     df = total_df[total_df['provinceName'] == name]
#     if df.empty:
#         print(f"没有关于 {name} 的数据")
#         return
#
#     df = df.reset_index()
#     if len(df) < 10:
#         print("数据量不足，无法进行预测")
#         return
#
#     # 写入预测数据
#     with open(DATA_PATH + "data_fordraw.csv", 'w') as f:
#         for idx, row in df.iterrows():
#             total = int(row['province_confirmedCount'])
#             f.write(f"{idx},{total}\n")
#
#     draw.draw(name)


# 共享对象类 用于js与qt通信
class WebShared(QWidget):
    def __init__(self):
        super().__init__()

    def get(self):
        pass

    def set(self, str):
        print("点击了" + str)
        forecast(str)

    value = pyqtProperty(str, fget=get, fset=set)


if __name__ == '__main__':
    # 清除图片缓存
    print("正在清除缓存")
    for infile in glob.glob(os.path.join(TMP_PATH, '*.png')):
        print("已删除"+infile)
        os.remove(infile)
    # 创建Qt应用
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    # 注册testUI中的窗口
    ui_components = UI.Ui_MainWindow()
    ui_components.setupUi(main_window)
    # 初始化webview
    map_view = ui_components.webview
    # 禁用滚动条
    map_view.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
    # 创建Channel对象 用于qt与js通信
    channel = QWebChannel()
    shared = WebShared()
    channel.registerObject("con", shared)
    map_view.page().setWebChannel(channel)
    # 绑定刷新事件
    ui_components.testButton.clicked.connect(refresh_webview)
    # 连接mqtt服务器
    client = connect_mqtt()
    client.subscribe(TOPIC)
    client.on_message = on_message
    # 打开接受进程
    client.loop_start()
    # 显示
    main_window.show()
    sys.exit(app.exec_())
