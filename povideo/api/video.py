from pathlib import Path

import pyttsx3

from povideo.core.VideoType import MainVideo

mainVideo = MainVideo()


# 从视频里提取音频
def video2mp3(path, mp3_name=None, output_path=r'./'):
    mainVideo.video2mp3(path=path, mp3_name=mp3_name, output_path=output_path)


# 从音频里，提取文字
# 本地语音文件不能大于5MB
def audio2txt(audio_path, appid, secret_id, secret_key):
    mainVideo.audio2txt(audio_path=audio_path, appid=appid, secret_id=secret_id, secret_key=secret_key)


def mark2video(video_path, output_path=None, output_name=None, watermark_content: str = "白开水AI",
               font_size=28,
               font_type=r'C:\Windows\Fonts\arial.ttf', font_color='black'):
    """
    给视频添加水印
    :param video_path: 必填，视频地址
    :param output_path: 输出地址，默认为输入视频所在目录
    :param output_name: 输出名称，默认为原文件名添加'-水印版'后缀
    :param mark_str: 水印内容，只支持英文
    :param font_size: 水印字体大小
    :param font_color: 水印颜色
    :param font_type: 水印字体类型
    :return:
    """
    video_file = Path(video_path)
    
    # 默认输出路径为输入视频所在目录
    if output_path is None:
        output_path = video_file.parent
    
    # 默认输出文件名为原文件名添加'-水印版'后缀
    if output_name is None:
        output_name = f"{video_file.stem}-水印版{video_file.suffix}"
    
    mainVideo.mark2video(input_file=video_path, output_file=str(Path(output_path) / output_name), watermark_content=watermark_content, font=font_type, font_size=font_size, color=font_color)


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
