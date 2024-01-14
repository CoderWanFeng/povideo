import os
from pathlib import Path

import moviepy.editor as mp
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from pofile import mkdir

from povideo.lib.tencent.audio2txt_service import audio2txt_service


class MainVideo():

    # 从视频里提取音频
    def video2mp3(self, path, mp3_name, output_path):
        """
        :param path: 视频文件的路径
        :param mp3_name: mp3的名字，可以为空
        :return:
        """
        # specify the mp4 file here(mention the file path if it is in different directory)
        clip = mp.VideoFileClip(path)
        if not Path(output_path).exists():
            os.makedirs(output_path)
        if mp3_name:
            if not str(mp3_name).endswith('.mp3'):
                mp3_name = str(mp3_name) + '.mp3'
        else:
            mp3_name = 'Audio.mp3'
        clip.audio.write_audiofile(Path(output_path) / mp3_name)

    def audio2txt(self, audio_path, appid, secret_id, secret_key):
        a2ts = audio2txt_service(appid, secret_id, secret_key)
        requestId = a2ts.get_requestId(audio_path)
        a2ts.get_recognition_result(requestId)

    def mark2video(self, video_path, output_path, output_name, mark_str, font_size, font_type, font_color):
        # 获取视频路径
        abs_video_path = Path(video_path).absolute()
        # 读取视频文件，并获取视频宽度和高度
        clip = VideoFileClip(str(abs_video_path), audio=True)
        width, height = clip.size
        # 创建带有水印内容的文本动画对象
        text = TextClip(mark_str, font=font_type, color=font_color, fontsize=font_size)
        # 设置水印颜色，并调整大小、位置和透明度
        set_color = text.on_color(size=(clip.w + text.w, text.h - 10), color=(0, 0, 0), pos=(6, 'center'), col_opacity=0.6)
        # 设置水印文本的位置
        set_textPos = set_color.set_pos(lambda pos: (max(width / 30, int(width - 0.5 * width * pos)), max(5 * height / 6, int(100 * pos))))
        set_duration = set_textPos.set_duration(clip.duration)
        # 合并视频和水印
        Output = CompositeVideoClip([clip, set_duration])
        # 设置输出视频的时长
        Output.duration = clip.duration
        # 创建输出路径
        mkdir(output_path)
        # 获取输出路径绝对路径
        abs_output_path = Path(os.path.join(output_path, output_name)).absolute()
        # 将合成后的视频保存为文件
        Output.write_videofile(str(abs_output_path), fps=30, codec='libx264')

