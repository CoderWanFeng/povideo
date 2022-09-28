from povideo.core.VideoType import MainVideo

mainVideo = MainVideo()


# 从视频里提取音频
def video2mp3(path, mp3_name=None):
    mainVideo.video2mp3(path, mp3_name)


# 从音频里，提取文字
# 本地语音文件不能大于5MB
def audio2txt(audio_path, appid, secret_id, secret_key):
    mainVideo.audio2txt(audio_path, appid, secret_id, secret_key)
