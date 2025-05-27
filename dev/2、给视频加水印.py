# -*- coding: UTF-8 -*-
'''
@作者  ：B站/抖音/微博/小红书/公众号，都叫：程序员晚枫，微信：python-office
@读者群     ：http://www.python4office.cn/wechat-group/
@学习网站      ：https://www.python-office.com
@代码日期    ：2023/8/13 23:18 
@本段代码的视频说明     ：https://blog.csdn.net/kd_2015/article/details/80157713
'''

import os

from moviepy import VideoFileClip, TextClip, ImageClip, CompositeVideoClip


def add_watermark_to_video(input_file, output_file, watermark_content=None, watermark_type='text', position=(500, 500),
                           font=None, font_size=50, color='black', opacity=1, image_watermark_path=None):
    """
    给视频添加水印

    参数:
    input_file -- 输入视频文件路径
    output_file -- 输出视频文件路径
    watermark_type -- 水印类型，'text' 或 'image'
    watermark_content -- 文字水印内容
    position -- 水印位置 (x, y)
    font -- 字体名称
    font_size -- 字体大小
    color -- 文字颜色
    opacity -- 透明度 (0.0-1.0)
    image_watermark_path -- 图片水印文件路径
    """
    # 加载视频
    video = VideoFileClip(input_file)

    # 创建水印
    if watermark_type == 'text':
        if not watermark_content:
            raise ValueError("需要提供文字水印内容")
        watermark = (
            TextClip(text=watermark_content, font=font, font_size=font_size, color=color,
                     margin=(video.size[0] / 2, video.size[1] / 2),
                     duration=video.duration)
        )
    elif watermark_type == 'image':
        if not image_watermark_path:
            raise ValueError("需要提供图片水印文件路径")
        # 确保图片水印路径存在
        if not os.path.exists(image_watermark_path):
            raise FileNotFoundError(f"图片水印文件 {image_watermark_path} 不存在")

        # 加载图片水印并调整大小
        image_watermark = ImageClip(image_watermark_path)
        # 调整图片水印大小为原图的1/5
        image_watermark = image_watermark.resize(0.2)
        watermark = (image_watermark
                     .set_position(position)
                     .set_opacity(opacity)
                     .set_duration(video.duration))
    else:
        raise ValueError("无效的水印类型，只能是 'text' 或 'image'")

    # 合并视频和水印
    video_with_watermark = CompositeVideoClip([video, watermark])

    # 写出最终视频
    video_with_watermark.write_videofile(output_file, codec='libx264', fps=video.fps)

    # 释放资源
    video.close()
    video_with_watermark.close()


if __name__ == "__main__":
    add_watermark_to_video(
        input_file=r'D:\BaiduNetdiskDownload\给非程序员的python入门课\视频\第0讲：这个课程是为谁准备的.mp4',
        output_file=r'./ou.mp4',
        watermark_content="python-office")
