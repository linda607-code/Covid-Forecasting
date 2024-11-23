import time
import paho.mqtt.client as mqtt
import pandas as pd

# 服务器地址
SERVER_IP = "127.0.0.1"
# SERVER_IP = "150.158.80.33"
# 服务器端口
SERVER_PORT = 1883
# 消息主题
TOPIC = "/covid"
# 输出数据
DATA_PATH = r"../data/data_converted.csv"
# 发生间隔
SEND_INTERVAL = 0.5


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(SERVER_IP, SERVER_PORT)
    return client


if __name__ == '__main__':
    # 初始数据处理
    c_data = pd.read_csv(DATA_PATH, encoding='gbk')
    dates = c_data['updateTime'].unique()  # 获取所有日期
    dates = dates[::-1]  # 反转
    # 连接mqtt
    client = connect_mqtt()
    client.loop_start()
    for date in dates:
        # if date == "2020/4/1":
        #     break
        time.sleep(SEND_INTERVAL)  # 先挂起
        df = c_data[c_data['updateTime'] == date]
        json_str = df.to_json()
        res = client.publish(TOPIC, json_str)
        print("已发送"+date+"状态"+str(res[0]))
