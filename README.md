# zjgsu抢课脚本 保姆级使用教程（ 2023 - 2024 - 1 ）

## 观前提醒：

```
此项目仅用于社团内部python学习交流，请勿用于非法用途[doge]。
使用过程略有些复杂，请耐心按照以下教程逐步操作。
实在不会？wx：yzhdrinkT 远控帮你操作。
```
## 脚本原理：

### 脚本会模拟你不停刷新页面的操作，不停检查某一门（或多门）课程的余量情况，直到

### 发现余量并进行抢课后停止运行。

## 文件构成：

### 使用此脚本，必要的文件有两项：

```
Config.test.json （你需要手动配置的抢课信息）；
POSTrequest_fix.exe（信息配置完成后执行抢课程序的脚本）；
使用前请检查两项项文件是否完整。
```
## 如何使用：

## 1. 课程信息写入（在选课期间操作）

```
确认并记录（Ctrl+c）你要抢的课程名称，确保无课程时间冲突（如果有 将以最先
抢到的为准）
```
### 登录并进入选课界面

```
http://124.160.64.163/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N
2&layout=default （网址）
页面任意位置右键单击并下拉找到 *检查* 并点击（或按F 12 ）
```

在右侧弹出的开发者模式界面中找到 *network*（或*网络*）并点击

点击Fetch/XHR

### 在左侧选课界面找到 你想要的课 进行 *选课* （可以是满课的课程 只需要点击

### 一次 用以获取自己的账号信息）


### 完成上一步操作后，右侧将会出现数据包

右键单击 > Copy > Copy as cURL(bash)

进入网站https://curlconverter.com/ （转换curl请求为python）
将之前复制的curl内容复制入curl command，language选择Python + Requests


### （例图中信息已经过混淆处理）

```
在翻译后的内容中找到data字段
```
### 形如：

## data =

## 'jxb_ids=503e2f0f0b6582aaae1fe460b46db6797bdf99a7774c4ffd3b

## 8a80afe20b1e14f287315ed6cd58f18999a0d77e0a8746134cf7215f2dfbc

## f18ae55eb3bac90423488ca93775468827932c02faa088d3607fb1c3a

## 3a2b9f8a9b07a84fc8b69f85c8ba175b0eb22d094f36f5c59be97e03d7ec7d

## 4986dfbedcfdddf3f&kch_id=GENWCE030&kcmc=(GENWCE030)%E6%81%8B%E

## 7%88%B1%E5%BF%83%E7%90%86%E5%AD%A6+-

## +2.0+%E5%AD%A6%E5%88%86&rwlx=2&rlzlkz=1&sxbj=1&xxkbj=0&qz=0&cx

## bj=0&xkkz_id=0483F36B7276EC90E063CA8AA8C0182B&njdm_id=2022&kkl

## xdm=10&xklc=2&xkxnm=2023&xkxqm=3'

```
使用记事本(或代码编辑器)（右键打开方式中选择记事本）打开config.test.json 将
单引号内的内容 填入对应位置 (例图中内容有删减)
```

### 如果是多门课程，可以按相同格式添加（记得各段中间有英文逗号） 例如：

```
保存config.test.json 文件
```
## 2. 个人信息写入（在选课期间操作）（前半部分操作重复）

### 登录并进入选课界面（以下操作同上）

```
http://124.160.64.163/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N
2&layout=default （网址）
页面任意位置右键单击并下拉找到 *检查* 并点击（或按F 12 ）
```
```
在右侧弹出的开发者模式界面中找到 *network*（或*网络*）并点击
```

点击Fetch/XHR

### 在左侧选课界面找到任意一节课进行 *选课* （可以是满课的课程 只需要点击一次

### 用以获取自己的账号信息）

### 完成上一步操作后，右侧将会出现数据包

右键单击 > Copy > Copy as cURL(bash)


进入网站https://curlconverter.com/ （转换curl请求为python）（至此同上）
将之前复制的curl内容复制入curl command，language选择JSON


### （例图中信息已经过混淆处理）

```
使用记事本(或代码编辑器)打开config.test.json 将cookies以及 headers复制入
对应位置 形如下图
```
```
保存config.test.json 文件并退出
```
## 3. 脚本，启动！（请在config.test.json填写完整后进行）

```
双击 POSTrequest_fix.exe 文件开始进行抢课
如果出现命令行窗口，并不断显示课程选择信息，则代表脚本成功运行
```

