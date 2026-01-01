import os
from pathlib import Path

import ffmpeg
from moviepy import VideoFileClip

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

    def mark2video(self, input_file, output_file, watermark_content=None, watermark_type='text', position='center',
                   font=None, font_size=50, color='white', opacity=1, image_watermark_path=None):
        """
        给视频添加水印（使用 FFmpeg，比 moviepy 快 5-10 倍）
        
        :param input_file: 输入视频文件路径
        :param output_file: 输出视频文件路径
        :param watermark_content: 文字水印内容
        :param watermark_type: 水印类型，'text' 或 'image'
        :param position: 水印位置，可选 'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right'
        :param font: 字体文件路径
        :param font_size: 字体大小
        :param color: 文字颜色
        :param opacity: 透明度 (0.0-1.0)
        :param image_watermark_path: 图片水印文件路径
        """
        
        if watermark_type == 'text':
            if not watermark_content:
                raise ValueError("需要提供文字水印内容")
            
            # 位置映射
            position_map = {
                'center': {'x': '(w-text_w)/2', 'y': '(h-text_h)/2'},
                'top_left': {'x': '10', 'y': '10'},
                'top_right': {'x': 'w-text_w-10', 'y': '10'},
                'bottom_left': {'x': '10', 'y': 'h-text_h-10'},
                'bottom_right': {'x': 'w-text_w-10', 'y': 'h-text_h-10'},
            }
            
            # 处理元组位置参数（兼容旧版本）
            if isinstance(position, tuple):
                pos_x, pos_y = str(position[0]), str(position[1])
            else:
                pos = position_map.get(position, position_map['center'])
                pos_x, pos_y = pos['x'], pos['y']
            
            # 构建 drawtext 参数
            drawtext_params = {
                'text': watermark_content,
                'fontsize': font_size,
                'fontcolor': f'{color}@{opacity}',  # 支持透明度
                'x': pos_x,
                'y': pos_y,
            }
            
            # 如果指定了字体文件
            if font:
                drawtext_params['fontfile'] = font
            
            # 使用 ffmpeg-python 添加文字水印
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.drawtext(stream, **drawtext_params)
            stream = ffmpeg.output(
                stream,
                ffmpeg.input(input_file).audio,  # 直接复制音频流
                output_file,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='copy'  # 音频直接复制，不重新编码
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        elif watermark_type == 'image':
            if not image_watermark_path:
                raise ValueError("需要提供图片水印文件路径")
            
            if not os.path.exists(image_watermark_path):
                raise FileNotFoundError(f"图片水印文件 {image_watermark_path} 不存在")
            
            # 位置映射
            position_map = {
                'center': 'main_w/2-overlay_w/2:main_h/2-overlay_h/2',
                'top_left': '10:10',
                'top_right': 'main_w-overlay_w-10:10',
                'bottom_left': '10:main_h-overlay_h-10',
                'bottom_right': 'main_w-overlay_w-10:main_h-overlay_h-10',
            }
            
            # 处理元组位置参数（兼容旧版本）
            if isinstance(position, tuple):
                overlay_pos = f"{position[0]}:{position[1]}"
            else:
                overlay_pos = position_map.get(position, position_map['center'])
            
            # 使用 ffmpeg-python 添加图片水印
            main_video = ffmpeg.input(input_file)
            watermark = ffmpeg.input(image_watermark_path)
            
            # 缩放水印图片为视频宽度的1/5
            watermark = ffmpeg.filter(watermark, 'scale', 'iw/5', 'ih/5')
            
            # 设置透明度
            if opacity < 1:
                watermark = ffmpeg.filter(watermark, 'format', 'rgba')
                watermark = ffmpeg.filter(watermark, 'colorchannelmixer', aa=opacity)
            
            # 叠加水印
            stream = ffmpeg.overlay(main_video, watermark, x=overlay_pos.split(':')[0], y=overlay_pos.split(':')[1])
            
            stream = ffmpeg.output(
                stream,
                ffmpeg.input(input_file).audio,
                output_file,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='copy'
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        else:
            raise ValueError("无效的水印类型，只能是 'text' 或 'image'")
