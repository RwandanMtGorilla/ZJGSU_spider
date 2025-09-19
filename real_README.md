
## 环境准备
```shell
# 下载uv

# 克隆项目
git clone https://github.com/RwandanMtGorilla/ZJGSU_spider.git

# 创建虚拟环境
uv venv --python 3.9
uv init

# 启动虚拟环境
.venv\Scripts\activate

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 


```

## 启动
```shell
uv run ui.py

```

## 打包
```shell
pyinstaller --onefile --noconsole ui.py
```
