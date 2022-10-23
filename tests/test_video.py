import unittest

from povideo.api.video import *


class TestImage(unittest.TestCase):
    def test_wc(self):
        video2mp3(path=r'D:\迅雷下载\10月21日 (1)\10月21日 (1).mp4',output_path=r'./map3_path')

    # def test_2txt(self):
    #     audio2txt(audio_path=r"D:\software\obs\vedio\2022-09-28_23-51-28.mp4", appid, secret_id, secret_key)
