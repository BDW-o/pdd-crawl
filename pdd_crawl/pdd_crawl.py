import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
import logging

import time
import json
import yaml
import re
from os import path
import tkinter as tk
import openpyxl
from tkinter import messagebox

# 设置日志等级
logger = logging.getLogger("uc")
logger.setLevel(logging.getLogger().getEffectiveLevel())

goodslist = []  # 全局变量，用于存储商品信息
item_nums = 0  # 全局变量，代表要存储的商品个数
_user_data_dir = ''  # 全局变量，用户缓存文件夹


# 过滤器
def filter_type(_type: str):
    types = [
        'application/javascript', 'application/x-javascript', 'text/css', 'webp', 'image/png', 'image/gif',
        'image/jpeg', 'image/x-icon', 'application/octet-stream'
        , 'image/webp', 'application/x-font-ttf'
    ]
    useful_type = ['text/html', 'application/json']
    # if _type not in types:
    #     return True
    if _type in useful_type:
        return True
    return False


def get_logs(browser):
    performance_log = browser.get_log('performance')  # 获取名称为 performance 的日志
    # 存储类型和响应内容
    resps = []
    for packet in performance_log:
        message = json.loads(packet.get('message')).get('message')  # 获取message的数据
        if message.get('method') != 'Network.responseReceived':  # 如果method 不是 responseReceived 类型就不往下执行
            continue
        packet_type = message.get('params').get('response').get('mimeType')  # 获取该请求返回的type
        if not filter_type(_type=packet_type):  # 过滤type
            continue
        requestId = message.get('params').get('requestId')  # 唯一的请求标识符。相当于该请求的身份证
        url = message.get('params').get('response').get('url')  # 获取 该请求  url
        if 'search' not in url:
            continue
        try:
            resp = browser.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})  # selenium调用 cdp
            # print(f'type: {packet_type} url: {url}')
            # print(f'response: {resp}')
            # print()
            resps.append((packet_type, resp))
        except WebDriverException:  # 忽略异常
            pass
    return resps


# 传入保存浏览器缓存的路径
def parse(root, user_data):
    global _user_data_dir
    try:
        _user_data_dir = str(user_data.get())
        if not re.match("[A-Z]:\\\\.+", _user_data_dir):
            raise SyntaxError
        root.destroy()
    except SyntaxError:
        messagebox.showerror(title='错误', message='输入的路径不合法!')


# 解析数据
def parse2(browser, text_box, item_num):  # network日志记录尝试
    global item_nums
    # 删除原有文本框
    text_box.delete('1.0', 'end')
    # text_box.update()  # 手动触发更新
    item_num = int(item_num.get())
    item_nums = item_num

    pages = int(item_num/20)
    for page in range(0, pages):
        js_down = f"window.scrollTo(0,{(page+1)*10000})"
        browser.execute_script(js_down)
        time.sleep(2)
    time.sleep(2)

    # 声明全局变量
    global goodslist
    # 商品详情页前缀
    search_url = 'https://mobile.yangkeduo.com/goods.html?goods_id='
    # text前缀
    text = '商品名称' + ' ' * 15 + '价格' + ' ' * 15 + '详情网址\n'
    # 下面是数据解析保存
    resps = get_logs(browser)
    for num, resp in enumerate(resps):
        if num == 0:
            html = resp[1]['body']
            scripts = re.findall(r'</script></div><script>(.*)</script>', html)
            origin_data = scripts[-1].replace('window.__SSR__=1;window.__CHUNK_DATA__={};window.rawData=', '').replace(
                r";document.dispatchEvent(new Event('XRenderInitialPropsLoaded'));", '')
            _goodslist = json.loads(origin_data)['stores']['store']['data']['ssrListData']['list']

            goodslist = []
            for goods in _goodslist:
                goodsName = goods['goodsName']
                priceInfo = goods['priceInfo']
                goodsID = goods['goodsID']
                goodslist.append((goodsName, priceInfo, search_url + str(goodsID)))

        else:
            jsons = resps[1][1]['body']
            print(jsons)
            odata = json.loads(jsons)
            _goodslist = odata['items']

            for goods in _goodslist:
                goods_name = goods['item_data']['goods_model']['goods_name']
                price_info = goods['item_data']['goods_model']['price_info']
                goods_id = goods['item_data']['goods_model']['goods_id']
                goodslist.append((goods_name, price_info, search_url + str(goods_id)))

    for number, goods in enumerate(goodslist):
        text += str(number+1) + '.\n' + goods[0] + '\n' + goods[1] + '\n' + goods[2] + '\n' * 2

    print(text)
    text_box.insert('1.0', text)

    print('go work!')


# 刷新浏览器界面
def parse3(browser):
    # 刷新
    browser.refresh()


# 保存到excel
def save():
    global item_nums
    # 生成工作簿
    if not path.exists('商品信息.xlsx'):
        wb = openpyxl.Workbook()
    else:
        wb = openpyxl.load_workbook('商品信息.xlsx')

    # 添加类目名称
    sheet = wb.active
    cell = sheet['A1']
    print(sheet['A1'], type(sheet['A1']))
    if not sheet['A1'].value:
        sheet['A1'] = '商品名称'
        sheet['B1'] = '价格'
        sheet['C1'] = '详情网址'

    global goodslist  # 声明全局变量
    for num, goods in enumerate(goodslist):
        if num < item_nums:
            sheet.append(list(goods))
        else:
            break

    wb.save('商品信息.xlsx')


# 关闭窗口
def exit_app(root):
    root.destroy()


# 获取配置信息
def get_configs():
    with open('set.yaml', 'r', encoding='utf-8') as f:
        sets = yaml.full_load(f)
    user_data_dir = sets['user_data_dir']
    driver_executable_path = sets['driver_executable_path']
    browser_executable_path = sets['browser_executable_path']
    return user_data_dir, driver_executable_path, browser_executable_path


# 获取浏览器缓存路径
def get_path(user_data_dir):
    # 创建一个tk对象
    root = tk.Tk(className='盗将行')
    root.geometry('400x150')

    # 创建一个菜单对象并将其绑定到窗口对象上
    menu = tk.Menu(root)
    root.config(menu=menu)

    # 设置变量
    path_ = tk.StringVar()

    # 定义frame空间
    fsetup = tk.Frame(root)

    # 设置控件
    tip = tk.Label(fsetup, text=r'请输入浏览器缓存路径(例:F:\default2):', padx=10, pady=10)
    path_entry = tk.Entry(fsetup, textvariable=path_)
    start_button = tk.Button(root, text="启动浏览器", command=lambda: parse(root, path_entry))

    # 布局
    fsetup.grid(row=15, column=1)
    tip.grid(row=0, column=0)
    path_entry.grid(row=0, column=1)
    start_button.grid(row=16, column=1)
    path_entry.insert('end', f'{user_data_dir}')
    root.mainloop()


# 定义一个窗口传参
def window(browser):
    # 创建一个tk对象
    root = tk.Tk(className='树深时见鹿')
    root.geometry('500x450')

    # 创建一个菜单对象并将其绑定到窗口对象上
    menu = tk.Menu(root)
    root.config(menu=menu)

    # 设置变量
    page_num = tk.IntVar()

    # 定义frame空间
    page_input = tk.Frame(root)

    # 设置控件
    text_box = tk.Text(root, width=65, height=22)
    tip = tk.Label(page_input, text='请输入爬取数量：', padx=10, pady=10)
    item_num_entry = tk.Entry(page_input, textvariable=page_num)
    setup = tk.Button(root, text="爬取", command=lambda: parse2(browser, text_box, item_num_entry))
    test = tk.Button(root, text="刷新网页", command=lambda: parse3(browser))
    save_button = tk.Button(root, text="保存", command=lambda: save())
    exit_button = tk.Button(root, text="退出", command=lambda: exit_app(root))

    page_input.grid(row=0, column=1)
    tip.grid(row=0, column=0)
    item_num_entry.grid(row=0, column=1)
    setup.grid(row=1, column=1)
    test.grid(row=2, column=1)
    text_box.grid(row=3, column=1)
    save_button.grid(row=50, column=1)
    exit_button.grid(row=51, column=1)

    root.mainloop()


if __name__ == '__main__':
    options = uc.ChromeOptions()
    # 获取配置信息
    sets = get_configs()
    driver_executable_path = sets[1]
    browser_executable_path = sets[2]
    # 获取浏览器缓存路径
    get_path(sets[0])
    if not re.match("[A-Z]:\\\\.+", _user_data_dir):
        exit()

    # 开启日志性能监听
    caps = {
        "browserName": "chrome",
        'goog:loggingPrefs': {'performance': 'ALL'}
    }
    # 将caps添加到options中
    for key, value in caps.items():
        options.set_capability(key, value)
    options.add_argument(f'--user-data-dir={_user_data_dir}')

    driver = uc.Chrome(options=options
                       , driver_executable_path=driver_executable_path
                       , browser_executable_path=browser_executable_path
                       , headless=False
                       )

    # https://www.nmpa.gov.cn/datasearch/search-result.html
    driver.get("https://mobile.yangkeduo.com/")

    window(browser=driver)
