# coding=utf-8
from flask import Flask
from potime import RunTime  # 导入时间计算模块

# 创建flask应用程序
app = Flask(__name__)


# 写一个函数来处理浏览器发送过来的请求
@app.route("/")  # 当访问网址时，默认执行下面函数
@RunTime  # 计算当前接口的运行时间
def index():
    a = 0
    for i in range(1000000):
        a = a + i
    return 'weclome to python-office'


if __name__ == "__main__":
    app.run(debug=True)  # 启动应用程序
