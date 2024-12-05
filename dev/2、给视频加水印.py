# -*- coding: UTF-8 -*-
'''
@作者  ：B站/抖音/微博/小红书/公众号，都叫：程序员晚枫，微信：CoderWanFeng
@读者群     ：http://www.python4office.cn/wechat-group/
@学习网站      ：https://www.python-office.com
@代码日期    ：2023/8/13 23:18 
@本段代码的视频说明     ：https://blog.csdn.net/kd_2015/article/details/80157713
'''

from moviepy.editor import *

clip = VideoFileClip(r"D:\software\obs\vedio\2023-08-13_23-17-46.mp4", audio=True)
width, height = clip.size
text = TextClip("vx:CoderWanFeng", font='Arial', color='white', fontsize=28)  # 水印内容
set_color = text.on_color(size=(clip.w + text.w, text.h - 10), color=(0, 0, 0), pos=(6, 'center'), col_opacity=0.6)
set_textPos = set_color.set_pos(
    lambda pos: (max(width / 30, int(width - 0.5 * width * pos)), max(5 * height / 6, int(100 * pos))))
Output = CompositeVideoClip([clip, set_textPos])
Output.duration = clip.duration
Output.write_videofile("output.mp4", fps=30, codec='libx264')
