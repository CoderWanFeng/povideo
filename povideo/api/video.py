from pathlib import Path

import pyttsx3

from povideo.core.VideoType import MainVideo

mainVideo = MainVideo()


# 从视频里提取音频
def video2mp3(path, mp3_name=None, output_path=r'./'):
    mainVideo.video2mp3(path, mp3_name, output_path)


# 从音频里，提取文字
# 本地语音文件不能大于5MB
def audio2txt(audio_path, appid, secret_id, secret_key):
    mainVideo.audio2txt(audio_path, appid, secret_id, secret_key)


def mark2video(video_path, output_path=r'./', output_name=r'mark2video.mp4', mark_str: str = "www.python-office.com",
               font_size=28,
               font_type=r'C:\Windows\Fonts\arial.ttf', font_color='white'):
    """
    给视频添加水印
    :param video_path: 必填，视频地址
    :param output_path: 输出地址
    :param output_name: 输出名称，记得带‘.mp4’
    :param mark_str: 水印内容，只支持英文
    :param font_size: 水印字体大小
    :param font_color: 水印颜色
    :param font_type: 水印字体类型
    :return:
    """
    mainVideo.mark2video(video_path, output_path, output_name, mark_str, font_size, font_type, font_color)


def txt2mp3(content='程序员晚枫', file=None, mp3=r'./程序员晚枫.mp3', speak=True) -> str:
    """
    文字转为语音
    :param content: 需要转换的文字
    :param file: 需要转换的文件，可以不填，优先级最高
    :param mp3: 是否保存为mp3
    :param speak: 是否朗读
    :return:
    """
    # 是否读文件
    if file:
        with open(file, encoding='utf-8', mode='r') as f_c:
            content = f_c.read()
    # 是否朗读
    if speak:
        pyttsx3.speak(content)
    # 是否存为mp3
    if mp3 != None:
        engine = pyttsx3.init()
        engine.save_to_file(content, mp3)
        engine.runAndWait()
        return Path(mp3).absolute()
    return None


if __name__ == '__main__':
    mark2video(video_path=r'D:\software\obs\vedio\2024-12-02_22-36-41.mp4', output_path=r'./map3_path')
