import os
from pathlib import Path

from moviepy import CompositeVideoClip, ImageClip, TextClip, VideoFileClip

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
        clip = VideoFileClip(path)
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

    def mark2video(self, input_file, output_file, watermark_content=None, watermark_type='text', position=(500, 500),
                   font=None, font_size=50, color='black', opacity=1, image_watermark_path=None):

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
        
        # 保留原视频的音频轨道
        video_with_watermark = video_with_watermark.with_audio(video.audio)

        # 写出最终视频
        video_with_watermark.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=video.fps, threads=os.cpu_count(), preset='ultrafast')

        # 释放资源
        video.close()
        video_with_watermark.close()
