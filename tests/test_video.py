import unittest

from povideo.api.video import *


class TestImage(unittest.TestCase):
    def test_wc(self):
        video2mp3(path=r'D:\迅雷下载\9月27日\9月27日.mp4')

    # def test_2txt(self):
    #     audio2txt(audio_path=r"D:\software\obs\vedio\2022-09-28_23-51-28.mp4", appid, secret_id, secret_key)
