import moviepy.editor as mp

from povideo.lib.tencent.audio2txt_service import audio2txt_service


class MainVideo():

    # 从视频里提取音频
    def video2mp3(self, path, mp3_name):
        """
        :param path: 视频文件的路径
        :param mp3_name: mp3的名字，可以为空
        :return:
        """
        # specify the mp4 file here(mention the file path if it is in different directory)
        clip = mp.VideoFileClip(path)
        if mp3_name:
            clip.audio.write_audiofile(str(mp3_name) + '.mp3')
        else:
            # specify the name for mp3 extracted
            clip.audio.write_audiofile('Audio.mp3')
            # you will notice mp3 file will be created at the specified location.

    def audio2txt(self, audio_path, appid, secret_id, secret_key):
        a2ts = audio2txt_service(appid, secret_id, secret_key)
        requestId = a2ts.get_requestId(audio_path)
        a2ts.get_recognition_result(requestId)
