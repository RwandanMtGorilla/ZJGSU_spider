import os
import json
import requests
from glob import glob
import random
import time
from multiprocessing import Process, Manager, freeze_support
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext, Canvas, Scrollbar


def load_json_files(folder_path):
    """ 加载指定文件夹中的所有JSON文件 """
    file_paths = glob(os.path.join(folder_path, '*.json'))
    json_data = []
    file_names = []  # 存储文件名
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data.append(json.load(file))
            file_names.append(os.path.basename(file_path))
    return json_data, file_names


def send_requests_until_success(request_info, log_queue, wait_time):
    """ 发送请求直到flag为1 """
    url = request_info.get("raw_url")
    method = request_info.get("method", 'get').lower()
    headers = request_info.get("headers")
    cookies = request_info.get("cookies")
    data = request_info.get("data")

    while True:
        try:
            response = requests.request(method, url, headers=headers, cookies=cookies, data=data)
            localtime = time.asctime(time.localtime(time.time()))
        except Exception as e:
            log_queue.put(f"{localtime} 请求失败，返回: {e}")

        try:
            response_json = response.json()
            if response_json.get("flag") == "1":
                log_queue.put(f"{localtime} 成功: {response.text}")
                time.sleep(1)
                break
            elif response_json.get("flag") == "0":
                log_queue.put(f"{localtime} 响应: {response.text} 请先退选当前时段。")
                time.sleep(1)
                break
            else:
                log_queue.put(f"{localtime} 尝试中, 响应: {response.text}")
        except json.JSONDecodeError:
            log_queue.put(f"{localtime} 无法解析JSON响应: {response.text}")

        time.sleep(random.uniform(wait_time, wait_time + 0.3))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON 请求多进程管理器")
        self.root.geometry('1200x700')
        self.root.resizable(False, False)

        self.folder_path = './JSONs'  # 默认的JSON文件夹路径
        self.json_requests = []
        self.file_names = []  # 保存每个 JSON 文件的文件名
        self.processes = []
        self.log_queues = []

        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 左侧控制区
        control_frame = ttk.Frame(main_frame, padding=(10, 10), bootstyle=SECONDARY)
        main_frame.add(control_frame, weight=1)

        # 右侧日志区
        log_frame = ttk.Labelframe(main_frame, text="日志输出", padding=(10, 10), bootstyle=INFO)
        main_frame.add(log_frame, weight=3)

        # 滚动框架用于容纳日志框
        self.canvas = Canvas(log_frame)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 使用窗口创建可滚动的区域
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # 路径选择
        path_label = ttk.Label(control_frame, text="选择 JSON 文件夹路径:")
        path_label.pack(anchor="w", pady=5)

        self.path_entry = ttk.Entry(control_frame, width=30)
        self.path_entry.insert(0, self.folder_path)
        self.path_entry.pack(fill=X, pady=5)

        browse_button = ttk.Button(control_frame, text="浏览", command=self.browse_folder, bootstyle=PRIMARY)
        browse_button.pack(fill=X, pady=5)

        # 等待时间设置
        wait_time_label = ttk.Label(control_frame, text="设置等待时间 (秒，最少为0.3):")
        wait_time_label.pack(anchor="w", pady=5)

        self.wait_time_var = ttk.DoubleVar(value=0.5)
        self.wait_time_entry = ttk.Spinbox(control_frame, from_=0.3, to=10.0, increment=0.1,
                                           textvariable=self.wait_time_var, width=10)
        self.wait_time_entry.pack(fill=X, pady=5)

        # 控制按钮
        start_button = ttk.Button(control_frame, text="开始", command=self.start_processes, bootstyle=SUCCESS)
        start_button.pack(fill=X, pady=5)

        stop_button = ttk.Button(control_frame, text="停止", command=self.stop_processes, bootstyle=DANGER)
        stop_button.pack(fill=X, pady=5)

        info_button = ttk.Button(control_frame, text="信息", command=self.show_info, bootstyle=INFO)
        info_button.pack(fill=X, pady=5)

        self.scroll_texts = []

    def browse_folder(self):
        # 选择JSON文件夹
        selected_folder = filedialog.askdirectory(initialdir=self.folder_path, title="选择JSON文件夹")
        if selected_folder:
            self.folder_path = selected_folder
            self.path_entry.delete(0, ttk.END)
            self.path_entry.insert(0, self.folder_path)
            self.load_json_requests()

    def load_json_requests(self):
        # 加载JSON文件
        try:
            self.json_requests, self.file_names = load_json_files(self.folder_path)
            self.clear_logs()
            self.create_log_windows()
            messagebox.showinfo("加载成功", f"已加载 {len(self.json_requests)} 个请求")
        except Exception as e:
            messagebox.showerror("加载错误", f"无法加载JSON文件: {str(e)}")

    def create_log_windows(self):
        # 清除现有的日志框架
        self.scroll_texts.clear()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 动态调整每个日志框的宽度和高度
        num_logs = len(self.file_names)
        base_width = 45
        adjusted_width = base_width
        base_height = 5
        adjusted_height = max(5, int(base_height * (1/(num_logs+1))))  # 最小高度为1

        # 创建垂直滚动条并配置
        scrollbar = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定滚动事件
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # 使用鼠标滚轮滚动
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        for i, file_name in enumerate(self.file_names):
            log_queue = Manager().Queue()
            self.log_queues.append(log_queue)

            log_frame = ttk.Frame(self.scrollable_frame)
            log_frame.pack(fill=X, padx=5, pady=5)

            log_label = ttk.Label(log_frame, text=file_name)
            log_label.pack(anchor="w")

            # 设置日志框的宽度会根据日志数量自动收窄
            scroll_text = scrolledtext.ScrolledText(log_frame, width=adjusted_width, height=adjusted_height, wrap=ttk.WORD)
            scroll_text.pack(fill=X, padx=5, pady=5)
            self.scroll_texts.append(scroll_text)

    def clear_logs(self):
        # 清除所有日志队列
        self.log_queues.clear()

    def start_processes(self):
        # 启动所有进程
        if not self.json_requests:
            messagebox.showwarning("警告", "请先选择包含JSON文件的文件夹并加载请求")
            return

        wait_time = max(0.3, self.wait_time_var.get())
        for i, request_info in enumerate(self.json_requests):
            process = Process(target=send_requests_until_success, args=(request_info, self.log_queues[i], wait_time))
            process.start()
            self.processes.append(process)
            self.update_log(i)

    def stop_processes(self):
        # 停止所有进程
        for process in self.processes:
            process.terminate()
        self.processes = []
        messagebox.showinfo("停止", "所有进程已停止")

    def show_info(self):
        # 创建一个新的信息窗口
        info_window = ttk.Toplevel(self.root)
        info_window.title("信息")
        info_window.geometry("400x200")

        # 显示当前正在运行的进程数
        running_processes = len([p for p in self.processes if p.is_alive()])
        process_label = ttk.Label(info_window, text=f"当前正在运行的进程数: {running_processes}")
        process_label.pack(pady=10)

        # 创建一个可点击的 GitHub 链接
        github_link = ttk.Label(info_window, text="GitHub 链接", foreground="blue", cursor="hand2")
        github_link.pack(pady=10)

        # 绑定点击事件打开链接
        github_link.bind("<Button-1>", lambda e: self.open_github_link())

    def open_github_link(self):
        # 打开 GitHub 链接
        import webbrowser
        webbrowser.open("https://github.com/RwandanMtGorilla/ZJGSU_spider/tree/main")



    def update_log(self, index):
        # 更新日志显示
        if not self.processes or not self.processes[index].is_alive():
            return
        try:
            log = self.log_queues[index].get_nowait()
            self.scroll_texts[index].insert(ttk.END, log + '\n')
            self.scroll_texts[index].see(ttk.END)
        except:
            pass
        self.root.after(500, lambda: self.update_log(index))


if __name__ == '__main__':
    freeze_support()  # 这行在Windows上是必要的，用于多进程在Windows上运行时避免无限递归
    root = ttk.Window(themename="litera")  # 使用 ttkbootstrap 的主题
    app = App(root)
    root.mainloop()
