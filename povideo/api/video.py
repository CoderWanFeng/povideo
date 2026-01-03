import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, List, Dict

import pyttsx3
from pofile import mkdir, get_files

from povideo.core.VideoType import MainVideo

mainVideo = MainVideo()


def _format_time(seconds: float) -> str:
    """
    将秒数格式化为用户友好的时间格式
    :param seconds: 秒数
    :return: 格式化后的时间字符串，如 "1小时2分30秒" 或 "5分30秒"
    """
    if seconds < 0:
        return "计算中..."
    
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


def _get_default_chinese_font():
    """
    获取跨平台的中文默认字体路径
    :return: 字体文件路径，如果找不到则返回 None
    """
    system = platform.system()
    
    if system == 'Windows':
        # Windows 中文字体优先级：微软雅黑 > 黑体 > 宋体
        font_candidates = [
            r'C:\Windows\Fonts\msyh.ttc',      # 微软雅黑
            r'C:\Windows\Fonts\msyhbd.ttc',    # 微软雅黑粗体
            r'C:\Windows\Fonts\simhei.ttf',    # 黑体
            r'C:\Windows\Fonts\simsun.ttc',    # 宋体
        ]
    elif system == 'Darwin':  # macOS
        # macOS 中文字体优先级：苹方 > 华文黑体 > 华文细黑
        font_candidates = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
    else:  # Linux
        # Linux 中文字体优先级：文泉驿 > Noto Sans CJK
        font_candidates = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        ]
    
    for font_path in font_candidates:
        if Path(font_path).exists():
            return font_path
    
    return None


# 从视频里提取音频
def video2mp3(path, mp3_name=None, output_path=r'./'):
    mainVideo.video2mp3(path=path, mp3_name=mp3_name, output_path=output_path)


# 从音频里，提取文字
# 本地语音文件不能大于5MB
def audio2txt(audio_path, appid, secret_id, secret_key):
    mainVideo.audio2txt(audio_path=audio_path, appid=appid, secret_id=secret_id, secret_key=secret_key)


def _process_single_video(video_path: str, output_dir: str, output_name: str, 
                         watermark_content: str, font_size: int, 
                         font_type: Optional[str], font_color: str) -> Dict[str, any]:
    """
    处理单个视频的内部函数
    :return: 包含处理结果的字典 {'success': bool, 'video': str, 'message': str}
    """
    try:
        # 确保输出目录存在（包括所有子目录）
        output_dir_path = Path(output_dir)
        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True, exist_ok=True)
        
        output_file = str(output_dir_path / output_name)
        
        # 创建新的 MainVideo 实例（进程安全）
        video_handler = MainVideo()
        video_handler.mark2video(
            input_file=video_path, 
            output_file=output_file,
            watermark_content=watermark_content, 
            font=font_type, 
            font_size=font_size, 
            color=font_color
        )
        return {
            'success': True,
            'video': video_path,
            'output': output_file,
            'message': '处理成功'
        }
    except Exception as e:
        return {
            'success': False,
            'video': video_path,
            'output': None,
            'message': f'处理失败: {str(e)}'
        }


def mark2video(video_path: str,
               output_path: Optional[str] = None, output_name: Optional[str] = None, 
               watermark_content: str = "白开水AI社区",
               font_size: int = 28,
               font_type: Optional[str] = None, font_color: str = 'red',
               max_workers: Optional[int] = None) -> Optional[List[Dict[str, any]]]:
    """
    给视频添加水印，支持单个视频处理和批量处理
    
    :param video_path: 视频文件路径或视频文件夹路径（自动识别）
                      - 如果是文件：处理单个视频
                      - 如果是文件夹：批量处理该文件夹及其子文件夹下所有视频，保留目录结构
    :param output_path: 输出地址，默认为输入视频所在目录
    :param output_name: 输出名称（仅单个视频有效），默认为原文件名添加'-水印版'后缀
    :param watermark_content: 水印内容，支持中英文
    :param font_size: 水印字体大小
    :param font_color: 水印颜色
    :param font_type: 水印字体类型，默认自动选择系统中文字体
    :param max_workers: 批量处理时的最大并发数，默认为 CPU 核心数的一半（避免系统过载）
    :return: 批量处理时返回处理结果列表，单个视频处理时返回 None
    
    使用示例：
    # 单个视频处理
    mark2video(video_path='/path/to/video.mp4', output_path='./output')
    
    # 批量处理（指定文件夹路径，保留目录结构）
    # 例如: /videos/subfolder/video.mp4 -> /output/subfolder/video-水印版.mp4
    results = mark2video(video_path='/path/to/videos', output_path='./output')
    for result in results:
        if result['success']:
            print(f"✓ {result['video']} -> {result['output']}")
        else:
            print(f"✗ {result['video']}: {result['message']}")
    """
    # 参数校验
    if not video_path:
        raise ValueError("必须指定 video_path 参数")
    
    input_path = Path(video_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"路径不存在: {video_path}")
    
    # 如果未指定字体，自动选择系统中文字体
    if font_type is None:
        font_type = _get_default_chinese_font()
    
    # 判断是文件还是文件夹
    if input_path.is_file():
        # 单个视频处理模式
        video_file = input_path
        
        # 默认输出路径为输入视频所在目录
        if output_path is None:
            output_path = video_file.parent
        
        # 默认输出文件名为原文件名添加'-水印版'后缀
        if output_name is None:
            output_name = f"{video_file.stem}-水印版{video_file.suffix}"
        
        # 检查输出目录是否存在，不存在则创建
        if not Path(output_path).exists():
            mkdir(str(output_path))
        
        mainVideo.mark2video(
            input_file=str(video_file), 
            output_file=str(Path(output_path) / output_name),
            watermark_content=watermark_content, 
            font=font_type, 
            font_size=font_size, 
            color=font_color
        )
        return None
    
    elif input_path.is_dir():
        # 批量处理模式
        input_folder_path = input_path
        
        # 默认输出路径（批量处理时默认在输入文件夹同级创建 output 目录）
        if output_path is None:
            output_path = input_folder_path.parent / f'{input_folder_path.name}_output'
        
        output_base_path = Path(output_path)
        
        # 确保输出根目录存在
        if not output_base_path.exists():
            mkdir(str(output_base_path))
        
        # 递归获取所有视频文件（包括子文件夹，支持常见视频格式）
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.mpeg', '.mpg']
        video_files = []
        
        try:
            # 使用 pofile 的 get_files 获取文件列表（包括子文件夹）
            all_files = get_files(str(input_folder_path))
            video_files = [f for f in all_files if Path(f).suffix.lower() in video_extensions]
        except Exception:
            # 如果 get_files 失败，使用 pathlib 递归扫描（包括子文件夹）
            for ext in video_extensions:
                video_files.extend(input_folder_path.rglob(f'*{ext}'))
                video_files.extend(input_folder_path.rglob(f'*{ext.upper()}'))
            video_files = [str(f) for f in video_files]
        
        if not video_files:
            print(f"警告: 在 {input_folder_path} 中未找到视频文件")
            return []
        
        print(f"找到 {len(video_files)} 个视频文件（包括子文件夹），开始批量处理...")
        
        # 确定并发数：默认为 CPU 核心数的一半，避免系统过载
        if max_workers is None:
            cpu_count = os.cpu_count() or 2
            # 考虑到视频处理本身已经多线程，并发数设为核心数的一半
            max_workers = max(1, cpu_count // 2)
        
        print(f"使用 {max_workers} 个进程并发处理")
        print(f"正在启动处理，首个视频完成后将显示预估时间...\n")
        
        # 准备任务列表，计算每个视频的相对路径和输出目录
        tasks = []
        for video_file in video_files:
            video_path_obj = Path(video_file)
            
            # 计算相对于输入文件夹的相对路径
            try:
                relative_path = video_path_obj.relative_to(input_folder_path)
            except ValueError:
                # 如果无法计算相对路径，只使用文件名
                relative_path = Path(video_path_obj.name)
            
            # 计算输出目录（保留目录结构）
            output_dir = output_base_path / relative_path.parent
            
            # 生成输出文件名
            output_name_auto = f"{video_path_obj.stem}-水印版{video_path_obj.suffix}"
            
            tasks.append({
                'video_path': video_file,
                'output_dir': str(output_dir),
                'output_name': output_name_auto,
                'watermark_content': watermark_content,
                'font_size': font_size,
                'font_type': font_type,
                'font_color': font_color
            })
        
        # 使用进程池并发处理
        results = []
        start_time = time.time()  # 记录开始时间
        processing_times = []  # 记录每个视频的处理时间
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务，记录提交时间
            future_to_task = {}
            for task in tasks:
                future = executor.submit(
                    _process_single_video,
                    task['video_path'],
                    task['output_dir'],
                    task['output_name'],
                    task['watermark_content'],
                    task['font_size'],
                    task['font_type'],
                    task['font_color']
                )
                future_to_task[future] = {
                    'task': task,
                    'submit_time': time.time()
                }
            
            # 收集结果并实时更新进度
            for future in as_completed(future_to_task):
                result = future.result()
                results.append(result)
                
                # 计算当前视频的处理时间
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                # 记录单个视频的平均处理时间（考虑并发）
                avg_time_per_video = elapsed_time / len(results)
                
                # 计算剩余视频数量和预估剩余时间
                remaining_videos = len(video_files) - len(results)
                
                # 预估剩余时间（考虑并发处理）
                if remaining_videos > 0:
                    # 根据已完成的平均速度预估剩余时间
                    estimated_remaining = avg_time_per_video * remaining_videos
                else:
                    estimated_remaining = 0
                
                # 格式化时间
                elapsed_str = _format_time(elapsed_time)
                remaining_str = _format_time(estimated_remaining)
                
                # 计算进度百分比
                progress_pct = (len(results) / len(video_files)) * 100
                
                # 输出处理进度
                video_name = Path(result['video']).name
                if result['success']:
                    status_icon = "✓"
                    status_msg = "处理完成"
                else:
                    status_icon = "✗"
                    status_msg = f"处理失败: {result['message']}"
                
                # 显示进度信息
                print(f"{status_icon} [{len(results)}/{len(video_files)}] {video_name} {status_msg}")
                print(f"   进度: {progress_pct:.1f}% | 已用时间: {elapsed_str} | 预计剩余: {remaining_str}")
        
        # 计算总处理时间
        total_time = time.time() - start_time
        total_time_str = _format_time(total_time)
        
        # 输出统计信息
        success_count = sum(1 for r in results if r['success'])
        print(f"\n{'='*50}")
        print(f"批量处理完成!")
        print(f"成功: {success_count}/{len(video_files)} | 失败: {len(video_files) - success_count}")
        print(f"总耗时: {total_time_str}")
        if len(results) > 0:
            avg_time = total_time / len(results)
            print(f"平均每个视频: {_format_time(avg_time)}")
        print(f"{'='*50}")
        
        return results
    
    else:
        raise ValueError(f"路径既不是文件也不是文件夹: {video_path}")


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
        with open(file=file, encoding='utf-8', mode='r') as f_c:
            content = f_c.read()
    # 是否朗读
    if speak:
        pyttsx3.speak(text=content)
    # 是否存为mp3
    if mp3 != None:
        engine = pyttsx3.init()
        engine.save_to_file(text=content, filename=mp3)
        engine.runAndWait()
        return Path(mp3).absolute()
    return None


if __name__ == '__main__':
    mark2video(video_path=r'D:\software\obs\vedio\2024-12-02_22-36-41.mp4', output_path=r'./map3_path')
