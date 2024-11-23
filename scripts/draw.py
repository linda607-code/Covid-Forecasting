import operator
import json
import random
import string

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from models.PolynomialRegressionModel import PolynomialRegressionModel

DATA_PATH = "../data/"
OUTPUT_PATH = "../output/"


def get_model(x, y):
    regression_model = PolynomialRegressionModel("model", 5)
    regression_model.train(x, y)
    return regression_model


def plot_graph(model_name, x, y, y_pred, pname):
    plt.scatter(x, y, s=10)
    sort_axis = operator.itemgetter(0)
    sorted_zip = sorted(zip(x, y_pred), key=sort_axis)
    x, y_pred = zip(*sorted_zip)

    plt.plot(x, y_pred, color='m')
    plt.title(pname+"疫情拟合曲线")
    plt.xlabel("Day")
    plt.ylabel(model_name)

    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    path = OUTPUT_PATH + ran_str + ".png"
    plt.savefig(path)
    img = Image.open(path)
    img.show()


def print_forecast(model_name, model, beginning_day=0, limit=10):
    next_days_x = np.array(range(beginning_day, beginning_day + limit)).reshape(-1, 1)
    next_days_pred = model.get_predictions(next_days_x)

    print("The forecast for " + model_name + " in the following " + str(limit) + " days is:")

    for i in range(0, limit):
        print("Day " + str(i + 1) + ": " + str(next_days_pred[i]))


def print_stats(x, y, model, pname):
    y_pred = model.get_predictions(x)

    print_forecast("", model, beginning_day=len(x), limit=5)

    if isinstance(model, PolynomialRegressionModel):
        print("The " + "" + " model function is: f(X) = " + model.get_model_polynomial_str())

    plot_graph("xx", x, y, y_pred, pname)
    print("")


def draw(pname):
    plt.clf()
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
    plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题
    training_set = np.genfromtxt(DATA_PATH + "data_fordraw.csv", delimiter=',').astype(np.int32)
    x = training_set[:, 0].reshape(-1, 1)
    y = training_set[:, 1]
    model = get_model(x, y)
    print_stats(x, y, model, pname)
