import os
import shutil
import subprocess
import logging
from pathlib import Path

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip

from povideo.lib.tencent.audio2txt_service import audio2txt_service

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量：缓存 FFmpeg 可用性检测结果
_ffmpeg_available = None


def _check_ffmpeg_available() -> bool:
    """
    检测本地是否安装了 FFmpeg
    :return: True 如果 FFmpeg 可用，否则 False
    """
    global _ffmpeg_available
    
    # 如果已经检测过，直接返回缓存结果
    if _ffmpeg_available is not None:
        return _ffmpeg_available
    
    # 方法1：检查 ffmpeg 是否在 PATH 中
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        try:
            # 验证 ffmpeg 可以正常执行
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                _ffmpeg_available = True
                logger.info(f"检测到 FFmpeg: {ffmpeg_path}")
                return True
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            pass
    
    # 方法2：尝试导入 ffmpeg-python 并执行简单命令
    try:
        import ffmpeg
        # 尝试获取 ffmpeg 版本信息
        ffmpeg.probe('nonexistent_file_for_test.mp4')
    except Exception as e:
        # 如果错误是 "ffmpeg not found" 类型，说明 ffmpeg 未安装
        error_str = str(e).lower()
        if 'ffmpeg' in error_str and ('not found' in error_str or 'no such file' in error_str or 'FileNotFoundError' in str(type(e).__name__)):
            _ffmpeg_available = False
            logger.warning("未检测到 FFmpeg，将使用 moviepy 作为回退方案")
            return False
    
    # 默认假设可用（ffmpeg-python 可能会在实际调用时失败）
    _ffmpeg_available = True
    return True


class MainVideo():

    # 从视频里提取音频
    def video2mp3(self, path, mp3_name, output_path):
        """
        :param path: 视频文件的路径
        :param mp3_name: mp3的名字，可以为空
        :return:
        """
        # specify the mp4 file here(mention the file path if it is in different directory)
        clip = VideoFileClip(filename=path)
        if not Path(output_path).exists():
            os.makedirs(name=output_path)
        if mp3_name:
            if not str(mp3_name).endswith('.mp3'):
                mp3_name = str(mp3_name) + '.mp3'
        else:
            mp3_name = 'Audio.mp3'
        clip.audio.write_audiofile(filename=Path(output_path) / mp3_name)

    def audio2txt(self, audio_path, appid, secret_id, secret_key):
        a2ts = audio2txt_service(appid=appid, secret_id=secret_id, secret_key=secret_key)
        requestId = a2ts.get_requestId(audio_file_path=audio_path)
        a2ts.get_recognition_result(requestId=requestId)

    def mark2video(self, input_file, output_file, watermark_content=None, watermark_type='text', position='center',
                   font=None, font_size=50, color='white', opacity=1, image_watermark_path=None):
        """
        给视频添加水印
        默认使用 FFmpeg（比 moviepy 快 5-10 倍），如果 FFmpeg 不可用则自动回退到 moviepy
        
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
        
        # 检测 FFmpeg 是否可用
        use_ffmpeg = _check_ffmpeg_available()
        
        if use_ffmpeg:
            try:
                self._mark2video_ffmpeg(
                    input_file=input_file,
                    output_file=output_file,
                    watermark_content=watermark_content,
                    watermark_type=watermark_type,
                    position=position,
                    font=font,
                    font_size=font_size,
                    color=color,
                    opacity=opacity,
                    image_watermark_path=image_watermark_path
                )
                logger.info(f"使用 FFmpeg 处理完成: {output_file}")
                return
            except Exception as e:
                logger.warning(f"FFmpeg 处理失败: {e}，正在切换到 moviepy...")
                # FFmpeg 失败时回退到 moviepy
        
        # 使用 moviepy 作为回退方案
        logger.info("使用 moviepy 处理视频水印...")
        self._mark2video_moviepy(
            input_file=input_file,
            output_file=output_file,
            watermark_content=watermark_content,
            watermark_type=watermark_type,
            position=position,
            font=font,
            font_size=font_size,
            color=color,
            opacity=opacity,
            image_watermark_path=image_watermark_path
        )
        logger.info(f"使用 moviepy 处理完成: {output_file}")
    
    def _mark2video_ffmpeg(self, input_file, output_file, watermark_content=None, watermark_type='text', position='center',
                           font=None, font_size=50, color='white', opacity=1, image_watermark_path=None):
        """
        使用 FFmpeg 添加水印（内部方法）
        """
        import ffmpeg
        
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
            stream = ffmpeg.input(filename=input_file)
            stream = ffmpeg.drawtext(stream=stream, **drawtext_params)
            stream = ffmpeg.output(
                stream,
                ffmpeg.input(filename=input_file).audio,  # 直接复制音频流
                output_file,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='copy'  # 音频直接复制，不重新编码
            )
            ffmpeg.run(stream_spec=stream, overwrite_output=True, quiet=True)
            
        elif watermark_type == 'image':
            if not image_watermark_path:
                raise ValueError("需要提供图片水印文件路径")
            
            if not os.path.exists(path=image_watermark_path):
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
            main_video = ffmpeg.input(filename=input_file)
            watermark = ffmpeg.input(filename=image_watermark_path)
            
            # 缩放水印图片为视频宽度的1/5
            watermark = ffmpeg.filter(stream_spec=watermark, filter_name='scale', w='iw/5', h='ih/5')
            
            # 设置透明度
            if opacity < 1:
                watermark = ffmpeg.filter(stream_spec=watermark, filter_name='format', pix_fmts='rgba')
                watermark = ffmpeg.filter(stream_spec=watermark, filter_name='colorchannelmixer', aa=opacity)
            
            # 叠加水印
            stream = ffmpeg.overlay(main=main_video, overlay=watermark, x=overlay_pos.split(':')[0], y=overlay_pos.split(':')[1])
            
            stream = ffmpeg.output(
                stream,
                ffmpeg.input(filename=input_file).audio,
                output_file,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='copy'
            )
            ffmpeg.run(stream_spec=stream, overwrite_output=True, quiet=True)
            
        else:
            raise ValueError("无效的水印类型，只能是 'text' 或 'image'")
    
    def _mark2video_moviepy(self, input_file, output_file, watermark_content=None, watermark_type='text', position='center',
                            font=None, font_size=50, color='white', opacity=1, image_watermark_path=None):
        """
        使用 moviepy 添加水印（回退方案，内部方法）
        """
        if watermark_type == 'text':
            if not watermark_content:
                raise ValueError("需要提供文字水印内容")
            
            # 加载视频
            video = VideoFileClip(filename=input_file)
            
            # 创建文字水印
            txt_clip = TextClip(
                text=watermark_content,
                font_size=font_size,
                color=color,
                font=font
            )
            
            # 设置透明度
            if opacity < 1:
                txt_clip = txt_clip.with_opacity(opacity)
            
            # 位置映射（moviepy 格式）
            position_map = {
                'center': 'center',
                'top_left': ('left', 'top'),
                'top_right': ('right', 'top'),
                'bottom_left': ('left', 'bottom'),
                'bottom_right': ('right', 'bottom'),
            }
            
            # 处理位置参数
            if isinstance(position, tuple):
                pos = position
            else:
                pos = position_map.get(position, 'center')
            
            # 设置水印位置和持续时间
            txt_clip = txt_clip.with_position(pos).with_duration(video.duration)
            
            # 合成视频
            final = CompositeVideoClip(clips=[video, txt_clip])
            
            # 写入输出文件
            final.write_videofile(
                filename=output_file,
                codec='libx264',
                preset='fast',
                threads=4,
                audio_codec='aac',
                logger=None  # 禁用 moviepy 的进度日志
            )
            
            # 释放资源
            video.close()
            final.close()
            
        elif watermark_type == 'image':
            if not image_watermark_path:
                raise ValueError("需要提供图片水印文件路径")
            
            if not os.path.exists(path=image_watermark_path):
                raise FileNotFoundError(f"图片水印文件 {image_watermark_path} 不存在")
            
            # 加载视频和水印图片
            video = VideoFileClip(filename=input_file)
            watermark = ImageClip(image_watermark_path)
            
            # 缩放水印图片为视频宽度的1/5
            watermark = watermark.resized(width=video.w // 5)
            
            # 设置透明度
            if opacity < 1:
                watermark = watermark.with_opacity(opacity)
            
            # 位置映射（moviepy 格式）
            position_map = {
                'center': 'center',
                'top_left': ('left', 'top'),
                'top_right': ('right', 'top'),
                'bottom_left': ('left', 'bottom'),
                'bottom_right': ('right', 'bottom'),
            }
            
            # 处理位置参数
            if isinstance(position, tuple):
                pos = position
            else:
                pos = position_map.get(position, 'center')
            
            # 设置水印位置和持续时间
            watermark = watermark.with_position(pos).with_duration(video.duration)
            
            # 合成视频
            final = CompositeVideoClip(clips=[video, watermark])
            
            # 写入输出文件
            final.write_videofile(
                filename=output_file,
                codec='libx264',
                preset='fast',
                threads=4,
                audio_codec='aac',
                logger=None
            )
            
            # 释放资源
            video.close()
            watermark.close()
            final.close()
            
        else:
            raise ValueError("无效的水印类型，只能是 'text' 或 'image'")
