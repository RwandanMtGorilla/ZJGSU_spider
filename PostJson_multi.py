import os
import json
import requests
from glob import glob
import random
import time
from multiprocessing import Process, freeze_support

def load_json_files(folder_path):
    """ 加载指定文件夹中的所有JSON文件 """
    file_paths = glob(os.path.join(folder_path, '*.json'))
    json_data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data.append(json.load(file))
    return json_data

def send_requests_until_success(request_info):
    """ 发送请求直到flag为1 """
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

        wait_time = random.uniform(0.3, 0.6)
        time.sleep(wait_time)

def start_processes(json_requests):
    """ 为每个请求启动一个进程 """
    processes = []
    for request_info in json_requests:
        process = Process(target=send_requests_until_success, args=(request_info,))
        process.start()
        processes.append(process)

    # 等待所有进程完成
    for process in processes:
        process.join()

if __name__ == '__main__':
    # 这行在Windows上是必要的，用于多进程在Windows上运行时避免无限递归
    freeze_support()

    # 指定JSONs文件夹的路径
    folder_path = 'JSONs'
    json_requests = load_json_files(folder_path)
    start_processes(json_requests)
