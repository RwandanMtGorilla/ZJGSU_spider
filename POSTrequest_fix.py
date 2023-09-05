import requests
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
def load_config():
    with open('config.test.json', 'r') as f:
        return json.load(f)
config = load_config()

cookies = config["cookies"]
headers = config["headers"]
classes = config["classes"]

#############

def task(conf_data):
    print("Task started with data:", conf_data)
    data = conf_data
    #jxb_id kch_id xkkz_id
    while True:  # 无限循环，直到请求成功为止
        response = requests.post(
            'http://124.160.64.163/jwglxt/xsxk/zzxkyzb_xkBcZyZzxkYzb.html',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )
        print(response.text)
        res = json.loads(response.text)
        flag = res['flag']
        localtime= time.asctime(time.localtime(time.time()))
        if flag == "-1":
            print(localtime,data,"fulled")
        if flag == "0":
            print(localtime,data, res["msg"])
        if flag == "1":
            print(localtime,data, "mission accomplished")
            break
        #time.sleep(1)
        wait_time = random.uniform(0.9, 1.3)
        time.sleep(wait_time)

def run():
    with ThreadPoolExecutor(5) as t:
        print("Thread pool created.")
        for k in classes:
            confdata = k[0]
            print(f"Submitting task for data: {confdata}")
            t.submit(task,confdata)


if __name__ == '__main__':
    run()