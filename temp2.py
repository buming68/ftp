from ftplib import FTP
import sys, getpass, os.path
import configparser

import tkinter as Tkinter
from tkinter import ttk, filedialog

# from mttkinter import mtTkinter as tk

import time
import threading
import socket

# from tkinter import filedialog



# HOST = '192.100.30.227'  # ftp地址
#
# USER_NAME = 'CCLK'  # ftp账号
# PASS_WORD = 'CCLK'  # ftp密码

# global HOST, USER_NAME, PASS_WORD

PORT = 21
TIMEOUT = 30  # 超时时间
BLOCK_SIZE = 8192  # 每帧上传的数据大小

file_name = ''  # 上传的文件名，ui部分显示用
file_size = 0  # 文件总大小，计算进度时用
upload_size = 0  # 已上传的数据大小，计算进度时用
bar = None  # 进度条对象

def read_config():
    global HOST, USER_NAME, PASS_WORD

    # 当前文件路径
    curpath = os.path.dirname(os.path.realpath(__file__))
    # config.ini的路径
    cfgpath = os.path.join(curpath, "config.ini")
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")  # python3


    # 获取user host 信息
    USER_NAME = conf.get('USER', 'username')
    PASS_WORD = conf.get('USER', 'password')
    HOST = conf.get('HOSTCONFIG', 'host')
    # print(USER_NAME, PASS_WORD)  # list里面对象
    # print(HOST)

class PopupProgressBar:
    def __init__(self, title):
        self.title = title
        self.root = None
        self.bar = None
        self.bar_lock = threading.Lock()
        self.thread = None
        self.thread_upd = None
        self.is_stop_thread_upd = False
        self.value = 0
        self.text = ""
        self.labelText = None  # Tkinter.StringVar()
        if not self.title:
            self.title = "PopupProgressBar"

    def start(self):
        # print("start")
        self.thread = threading.Thread(target=PopupProgressBar._run_, args=(self,))
        self.thread.daemon = True
        self.thread.start()

    def _run_(self):
        root = Tkinter.Tk()
        root.geometry('500x80+500+200')
        root.title(self.title)

        self.labelText = Tkinter.StringVar()
        self.labelText.set(self.text)

        ft = ttk.Frame()
        ft.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)

        label1 = Tkinter.Label(ft, textvariable=self.labelText)
        label1.pack(fill=Tkinter.X, side=Tkinter.TOP)

        pb_hD = ttk.Progressbar(ft, orient='horizontal', length=300, mode='determinate')
        pb_hD.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)

        self.root = root
        self.bar = pb_hD
        self.bar["maximum"] = 100
        self.bar["value"] = 0

        self.thread_upd = threading.Thread(target=PopupProgressBar._update_, args=(self,))
        # self.thread_upd11.daemon = True
        self.thread_upd.start()

        self.root.mainloop()

    def _update_(self):
        while not self.is_stop_thread_upd:
            self.update_data(self.value)
            self.labelText.set(self.text)
            time.sleep(0.01)

    def update_data(self, value):
        if not self.bar:
            return
        if self.bar_lock.acquire():
            self.bar["value"] = value
            self.bar_lock.release()

    def stop(self):
        if self.thread_upd:
            self.is_stop_thread_upd = True

        self.thread_upd.join()
        self.root.quit()


# localfile 本机要上传的文件与路径
# remotepath ftp服务器的路径 (ftp://192.168.1.8/xxx)
def upload_file(localfile, remotepath):
    global file_size
    global bar
    bar = PopupProgressBar('ftp upload file: ' + localfile)
    bar.start()

    cur_ftp = FTP()
    cur_ftp.encoding = "GB2312"
    # print(HOST, USER_NAME)
    pass

    try:
        cur_ftp.connect(HOST, PORT, TIMEOUT)  # 连接ftp服务器
        cur_ftp.login(USER_NAME, PASS_WORD)  # 登录ftp服务器
        print(cur_ftp.getwelcome())  # 打印欢迎信息
        print("connected OK! ")

        cur_ftp.cwd(remotepath)  # 设置ftp服务器端的路径
        cur_file = open(localfile, 'rb')  # 打开本地文件
        file_size = os.path.getsize(localfile)
        cur_ftp.storbinary('STOR %s' % os.path.basename(localfile), cur_file, blocksize=BLOCK_SIZE,
                           callback=upload_file_cb)  # 上传文件到ftp服务器

        cur_file.close()  # 关闭本地文件

        destname = remotepath + '/' + os.path.basename(localfile).split('.')[0] + '.ok'
        sourcename = remotepath + '/' + os.path.basename(localfile)

        cur_ftp.rename(sourcename, destname)

        print('upload_file done!, rename filen name OK!')

    except(socket.error, socket.gaierror):  # ftp 连接错误
        print("ERROR: cannot connect [{}:{}]".format(HOST, PORT))
        return None
    # except error_perm:  # 用户登录认证错误
    #     print("ERROR: user Authentication failed ")
    #     return None


    cur_ftp.quit()  # 退出


def upload_file_cb(block):
    global upload_size
    upload_size = upload_size + len(block)
    bar.value = upload_size / file_size * 100
    bar.text = format(upload_size / file_size * 100, '.2f') + '%'
    if bar.value >= 100:
        time.sleep(0.2)
        bar.stop()


if '__main__' == __name__:
    read_config()

    source_filename = filedialog.askopenfilename()
    #
    # print(source_filename)

    upload_file('e:/test.mxf', '/高清')

