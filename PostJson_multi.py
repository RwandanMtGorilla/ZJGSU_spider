import os
import json
import requests
from glob import glob
import random
import time

def load_json_files(folder_path):
    """ 加载指定文件夹中的所有JSON文件 """
    file_paths = glob(os.path.join(folder_path, '*.json'))
    json_data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data.append(json.load(file))
    return json_data

def send_requests_until_success(json_requests):
    """ 发送请求直到flag为1 """
    for request_info in json_requests:
        url = request_info.get("url")
        method = request_info.get("method", 'get').lower()
        headers = request_info.get("headers")
        cookies = request_info.get("cookies")
        data = request_info.get("data")


        while True:
            response = requests.request(method, url, headers=headers, cookies=cookies, data=data)
            localtime = time.asctime(time.localtime(time.time()))
            try:
                response_json = response.json()
                if response_json.get("flag") == "1":
                    print(f"{localtime} 成功: {response.text}")
                    break
                else:
                    print(f"{localtime} 尝试中, 响应: {response.text}")
            except json.JSONDecodeError:
                print(f"{localtime} 无法解析JSON响应: {response.text}")
                break

            wait_time = random.uniform(0.9, 1.3)
            time.sleep(wait_time)

# 指定JSONs文件夹的路径
folder_path = 'JSONs'
json_requests = load_json_files(folder_path)
send_requests_until_success(json_requests)
