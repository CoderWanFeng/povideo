# -*- coding: UTF-8 -*-
'''
@作者  ：B站/抖音/微博/小红书/公众号，都叫：程序员晚枫，微信：CoderWanFeng
@读者群     ：http://www.python4office.cn/wechat-group/
@学习网站      ：www.python-office.com
@代码日期    ：2023/8/1 21:38 
@本段代码的视频说明     ：
'''

import pyttsx3

engine = pyttsx3.init()  # 初始化语音引擎

engine.setProperty('rate', 100)  # 设置语速
engine.setProperty('volume', 0.6)  # 设置音量
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 设置第一个语音合成器
engine.say("程序员晚枫")
engine.runAndWait()
engine.stop()

# https://github.com/nateshmbhat/pyttsx3

import pyttsx3
#语音播放
pyttsx3.speak("程序员晚枫")
pyttsx3.speak("How are you?")
pyttsx3.speak("I am fine, thank you")
