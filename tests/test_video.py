import unittest

from povideo.api.video import video2mp3


class TestImage(unittest.TestCase):
    def test_wc(self):
        video2mp3(path=r'./8月14日.mp4')
