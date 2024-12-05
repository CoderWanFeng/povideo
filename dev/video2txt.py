# -*- coding: UTF-8 -*-
'''
@学习网站      ：https://www.python-office.com
@读者群     ：http://www.python4office.cn/wechat-group/
@作者  ：B站/抖音/微博/小红书/公众号，都叫：程序员晚枫，微信：CoderWanFeng
@代码日期    ：2024/12/3 21:41 
@本段代码的视频说明     ：
'''
import torch
from faster_whisper import WhisperModel


def transcribe_audio(audio_path, model_path):
    # 加载模型
    model = WhisperModel(model_path)
    model.eval()

    # 加载音频文件
    waveform, sample_rate = torchaudio.load(audio_path)

    # 对音频进行处理（如需要）
    # ...

    # 进行语音识别
    with torch.no_grad():
        transcripts = model(waveform.unsqueeze(0), sample_rate=sample_rate)

    # 获取最可能的转录文本
    text = transcripts[0].text
    return text


text = transcribe_audio('output_audio.wav', 'path_to_faster_whisper_model')
print(text)
