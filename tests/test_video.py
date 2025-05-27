import unittest

from povideo.api.video import *


class TestImage(unittest.TestCase):
    def test_wc(self):
        video2mp3(path=r'D:\software\obs\vedio\2-功能介绍.mp4', output_path=r'./map3_path')
    def test_mark(self):
        mark2video(video_path=r'D:\BaiduNetdiskDownload\Pandas-玩转-Excel\视频\Pandas VS Excel', output_path=r'./map4_path')

    def test_txt2mp3_all(self):
        # 测试全部功能
        content = "Hello, world!"
        mp3 = Path(__file__).absolute() / "test.mp3"
        result = txt2mp3(content=content, mp3=mp3, speak=True)
        assert result is not None
        assert isinstance(result, Path)
        assert result.exists()
    # def test_2txt(self):
    #     audio2txt(audio_path=r"D:\software\obs\vedio\2022-09-28_23-51-28.mp4", appid, secret_id, secret_key)
