# -*- coding: utf-8 -*-
"""
本地语音文件识别
参考：
    https://blog.csdn.net/TomorrowAndTuture/article/details/100100430
    https://github.com/TencentCloud/tencentcloud-sdk-python
"""
import requests
import hashlib
import time
import hmac
import urllib
import urllib.parse
import json
import base64

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


class audio2txt_service():

    def __init__(self, appid, secret_id, secret_key):
        self.req_url = "https://aai.qcloud.com/asr/v1/"
        self.callback_url = ""
        self.sign_url = "aai.qcloud.com/asr/v1/"

        self.appid = appid
        self.secret_id = secret_id
        self.secret_key = secret_key

    def task_process(self, audio_url):
        request_data = dict()
        request_data['channel_num'] = 1
        request_data['secretid'] = self.secret_id
        request_data['engine_model_type'] = "8k_6"
        request_data['timestamp'] = int(time.time())
        request_data['expired'] = int(time.time()) + 3600
        request_data['nonce'] = 1559
        request_data['projectid'] = 0
        request_data['callback_url'] = self.callback_url
        request_data['res_text_format'] = 0
        request_data['res_type'] = 1
        request_data['source_type'] = 1
        request_data['sub_service_type'] = 0
        with open(audio_url, 'rb') as f:
            body_data = f.read()
            body_len = str(len(body_data))
        authorization = self.generate_sign(request_data, self.appid)
        task_req_url = self.generate_request(request_data, self.appid)
        header = {
            "Authorization": authorization,
            "Content-Length": body_len
        }

        r = requests.post(task_req_url, headers=header, data=body_data)
        return r.text

    def generate_sign(self, request_data, appid):
        sign_str = "POST" + self.sign_url + str(appid) + "?"
        sort_dict = sorted(request_data.keys())
        for key in sort_dict:
            sign_str = sign_str + key + "=" + urllib.parse.unquote(str(request_data[key])) + '&'
        sign_str = sign_str[:-1]
        authorization = base64.b64encode(
            hmac.new(bytes(self.secret_key, 'utf-8'), bytes(sign_str, 'utf-8'), hashlib.sha1).digest())
        # authorization = base64.b64encode(hmac.new(secret_key, sign_str, hashlib.sha1).digest())
        return authorization

    def generate_request(self, request_data, appid):
        result_url = self.req_url + str(appid) + "?"
        for key in request_data:
            result_url = result_url + key + "=" + str(request_data[key]) + '&'
        result_url = result_url[:-1]
        return result_url

    def get_requestId(self, audio_file_path):
        request_result = self.task_process(audio_file_path)
        print(request_result)
        requestId = eval(request_result)["requestId"]
        return requestId

    def get_recognition_result(self, requestId):
        try:
            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = asr_client.AsrClient(cred, "ap-guangzhou", clientProfile)

            while True:
                req = models.DescribeTaskStatusRequest()
                # 537731632
                params = '{"TaskId":%s}' % requestId
                req.from_json_string(params)
                resp = client.DescribeTaskStatus(req)
                recognition_text = json.loads(resp.to_json_string())
                recognition_status = recognition_text['Data']['StatusStr']
                if recognition_status == "success":
                    print(recognition_text['Data']['TaskId'], "识别成功！")
                    break
                if recognition_status == "failed":
                    raise TencentCloudSDKException
                time.sleep(1)
                # print(recognition_text)
            recognition_text = recognition_text['Data']['Result']
            sentence_list = recognition_text.split('\n')[0:-1]  # 列表最后一个元素是空字符串
            for sentence in sentence_list:
                content = sentence.split('  ')[1]  # 获取单句通话内容
                # begin_time = sentence.split('  ')[0].split(',')[0][1:]  # 获取每句话的开始时间
                # begin_time = str(int(begin_time.split(":")[0]) * 60000 + int(begin_time.split(":")[1].replace(".", "")))
                # end_time = sentence.split('  ')[0].split(',')[1]  # 获取每句话的结束时间
                # end_time = str(int(end_time.split(":")[0]) * 60000 + int(end_time.split(":")[1].replace(".", "")))
                # speaker = sentence.split('  ')[0].split(',')[-1][:-1]  # 获取说话人
                # print(speaker + "\t" + content + '\t' + begin_time + '\t' + end_time)
                # print(speaker + "\t" + content + '\t' + filename + '\t' + begin_time + '\t' + end_time, file=doc)
                print(content + '\n')
        except TencentCloudSDKException as err:
            print(err)
