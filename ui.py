import os
import json
import requests
from glob import glob
import random
import time
from multiprocessing import Process, Manager, freeze_support
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Canvas, Scrollbar, Listbox, Frame
from collections import defaultdict


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
            localtime = time.strftime("%H:%M:%S", time.localtime(time.time()))
        except Exception as e:
            localtime = time.strftime("%H:%M:%S", time.localtime(time.time()))
            log_queue.put(f"请求失败，返回: {e}||{localtime}")
            continue

        try:
            response_json = response.json()
            if response_json.get("flag") == "1":
                log_queue.put(f"成功: {response.text}||{localtime}")
                time.sleep(1)
                break
            elif response_json.get("flag") == "0":
                log_queue.put(f"响应: {response.text} 请先退选当前时段。||{localtime}")
                time.sleep(1)
                break
            else:
                log_queue.put(f"尝试中, 响应: {response.text}||{localtime}")
        except json.JSONDecodeError:
            log_queue.put(f"无法解析JSON响应: {response.text}||{localtime}")

        time.sleep(random.uniform(wait_time, wait_time + 0.3))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON 请求多进程管理器")
        self.root.geometry('2000x800')
        self.root.resizable(False, False)

        self.folder_path = './JSONs'  # 默认的JSON文件夹路径
        self.json_requests = []
        self.file_names = []  # 保存每个 JSON 文件的文件名
        self.processes = []
        self.log_queues = []
        self.log_counts = []  # 存储每个日志框的响应计数
        self.log_times = []  # 存储每个日志的最新时间
        self.listboxes = []  # 存储Listbox组件

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
        main_frame.add(log_frame, weight=4)

        # 创建一个容器框架来包含Canvas和滚动条
        canvas_container = ttk.Frame(log_frame)
        canvas_container.pack(fill=BOTH, expand=True)

        # 创建垂直滚动条
        self.main_scrollbar = ttk.Scrollbar(canvas_container, orient=VERTICAL)
        self.main_scrollbar.pack(side=RIGHT, fill=Y)

        # 创建Canvas
        self.canvas = Canvas(canvas_container, yscrollcommand=self.main_scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # 配置滚动条
        self.main_scrollbar.configure(command=self.canvas.yview)

        # 创建可滚动的框架
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 将scrollable_frame添加到canvas中
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 路径选择
        path_label = ttk.Label(control_frame, text="选择 JSON 文件夹路径:")
        path_label.pack(anchor="w", pady=5)

        self.path_entry = ttk.Entry(control_frame, width=25)
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
        self.listboxes.clear()
        self.log_counts.clear()
        self.log_times.clear()  # 清除时间记录
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 动态调整每个日志框的高度
        num_logs = len(self.file_names)
        base_height = 8
        adjusted_height = max(5, int(base_height * (1 / (num_logs * 0.3 + 1))))

        # 绑定Canvas大小变化事件
        def configure_canvas(event):
            # 获取Canvas的实际宽度
            canvas_width = event.width
            # 更新scrollable_frame的宽度以匹配Canvas宽度
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            # 强制更新scrollable_frame的布局
            self.scrollable_frame.update_idletasks()
            # 更新滚动区域
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind('<Configure>', configure_canvas)

        # 使用鼠标滚轮滚动
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

        for i, file_name in enumerate(self.file_names):
            log_queue = Manager().Queue()
            self.log_queues.append(log_queue)
            self.log_counts.append(defaultdict(int))
            self.log_times.append(defaultdict(str))  # 添加时间记录

            # 创建日志框架，使用ttk.Frame以保持一致的样式
            log_frame = ttk.Frame(self.scrollable_frame, relief="ridge", borderwidth=1)
            log_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

            log_label = ttk.Label(log_frame, text=file_name)
            log_label.pack(anchor="w", padx=5, pady=2)

            # 创建Listbox容器，关键修改：使用BOTH fill和expand=True
            listbox_frame = ttk.Frame(log_frame)
            listbox_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

            # 创建Listbox，关键修改：去掉固定宽度限制
            listbox = Listbox(listbox_frame, height=adjusted_height, font=("Arial", 9))
            scrollbar_listbox = ttk.Scrollbar(listbox_frame, orient=VERTICAL, command=listbox.yview)

            listbox.configure(yscrollcommand=scrollbar_listbox.set)
            # 关键修改：确保Listbox完全填充其容器
            listbox.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar_listbox.pack(side=RIGHT, fill=Y)

            self.listboxes.append(listbox)

        # 强制更新布局
        self.root.update_idletasks()
        # 更新Canvas配置
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # 确保Canvas窗口宽度正确设置
        def update_canvas_width():
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 1:  # 确保Canvas已经被渲染
                self.canvas.itemconfig(self.canvas_window, width=canvas_width)

        # 延迟执行宽度更新，确保所有组件都已完成初始化
        self.root.after(100, update_canvas_width)

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
            log_with_time = self.log_queues[index].get_nowait()

            # 分离日志内容和时间
            if "||" in log_with_time:
                log, current_time = log_with_time.rsplit("||", 1)
            else:
                log = log_with_time
                current_time = time.strftime("%H:%M:%S", time.localtime(time.time()))

            # 更新计数和时间
            self.log_counts[index][log] += 1
            self.log_times[index][log] = current_time  # 更新为最新时间
            count = self.log_counts[index][log]
            latest_time = self.log_times[index][log]

            # 在列表中查找是否已存在该日志
            found = False
            for i in range(self.listboxes[index].size()):
                item = self.listboxes[index].get(i)
                # 提取原始日志内容（去掉计数和时间部分）
                if ' (×' in item:
                    original_log = item.split(' (×')[0]
                elif '[' in item and ']' in item:
                    # 处理只有时间没有计数的情况
                    original_log = item.split(' [')[0]
                else:
                    original_log = item

                if original_log == log:
                    # 更新现有项目
                    self.listboxes[index].delete(i)
                    if count > 1:
                        display_text = f"{log} (×{count}) [{latest_time}]"
                    else:
                        display_text = f"{log} [{latest_time}]"
                    self.listboxes[index].insert(i, display_text)
                    found = True
                    break

            if not found:
                # 添加新项目
                if count > 1:
                    display_text = f"{log} (×{count}) [{latest_time}]"
                else:
                    display_text = f"{log} [{latest_time}]"
                self.listboxes[index].insert('end', display_text)
                self.listboxes[index].see('end')

        except:
            pass
        self.root.after(500, lambda: self.update_log(index))


if __name__ == '__main__':
    freeze_support()
    root = ttk.Window(themename="litera")
    app = App(root)
    root.mainloop()
