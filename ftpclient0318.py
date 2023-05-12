from ftplib import FTP
import configparser
from tkinter import filedialog
import tkinter as tk
import tkinter.messagebox

import socket
import os
import winsound

'''
#host  ftp server  地址
#ftpencoding  ftp服务器端的编码格式 GB2312 或 utf-8
#username	用户名
#password	密码
#dirs		服务器段最终文件目录，多个目录用;分开（注意小写;）
#suffix		最终成品文件的后缀，如果为空，则文件名的后缀不变
#temp_dir	在服务器端临时目录名
'''

PORT = 21
TIMEOUT = 20  # 超时时间
BLOCK_SIZE = 65536  # 每帧上传的数据大小
file_size = 0  # 文件总大小，计算进度时用

def read_config():
    global HOST, USER_NAME, PASS_WORD, DIRS, SUFFIX, ENCODING, TEMP_DIR
    # 当前文件路径
    curpath = os.path.dirname(os.path.realpath(__file__))
    # config.ini的路径
    cfgpath = os.path.join(curpath, "config.ini")
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding='GB2312')  # python3
    # 获取user host 信息
    USER_NAME = conf.get('USER', 'username')
    PASS_WORD = conf.get('USER', 'password')
    HOST = conf.get('HOSTCONFIG', 'host')
    DIRS = conf.get('DIRECTORY', 'dirs')
    TEMP_DIR = conf.get('DIRECTORY', 'temp_dir')
    SUFFIX = conf.get('DIRECTORY', 'suffix')
    ENCODING = conf.get('HOSTCONFIG', 'ftpencoding')

def button_clicked():
    source_filename = filedialog.askopenfilename(title='选择视频文件')
    if not source_filename:         #未选择文件，返回
        return
    m_text.delete(1.0, tk.END)
    m_text.insert(tk.END, '待上传文件'+source_filename+'\n')
    m_text.pack()
    directoys = DIRS.split(';')         #依次选择多个目标传送目录
    for dir1 in directoys:
        m_text.insert(tk.END, '将传输至：  '+dir1+ '\n')
        m_text.pack()
        m_text.update()
        upload_file(source_filename, dir1)

def upload_file(localfile, remotepath):
    global file_size, upload_size
    upload_size = 0
    cur_ftp = connect_ftp()                  #connect ftp server ,return ftp handle
    if cur_ftp:
        local_name = os.path.basename(localfile).split('.')[0]
        csremote_ok = check_samename(local_name, remotepath, cur_ftp)
        cstemp_ok = check_samename(local_name, TEMP_DIR, cur_ftp)
        if csremote_ok and cstemp_ok:
            try:
                cur_file = open(localfile, 'rb')  # 打开本地文件
                file_size = os.path.getsize(localfile)
                cur_ftp.storbinary('STOR %s' % os.path.basename(localfile), cur_file, blocksize=BLOCK_SIZE,
                                   callback=upload_file_cb)  # 上传文件到ftp服务器
                cur_file.close()  # 关闭本地文件
                if SUFFIX:                                          #确认是否更改临时文件的后缀名
                    destname = remotepath + '/' + os.path.basename(localfile).split('.')[0] + '.'+ SUFFIX
                else:
                    destname = remotepath + '/' + os.path.basename(localfile)
                srcname = TEMP_DIR + os.path.basename(localfile)
                tempfile_size = cur_ftp.size(srcname)
                if file_size == tempfile_size:                      #比较ftp服务器上的文件与源文件大小是否一致？
                    cur_ftp.rename(srcname, destname)               #更改文件名后缀，或者不变，并移动文件至目标目录
                    m_text.insert(tk.END, '\n 文件上传成功!, 移动至目标目录成功! \n')
            except(socket.error, socket.gaierror):  # ftp 连接错误
                alarm("上传异常出错")
        else:
            return False
        cur_ftp.quit()  # 退出

def connect_ftp():
    cur_ftp = FTP()
    cur_ftp.encoding = ENCODING
    try:
        cur_ftp.connect(HOST, PORT, TIMEOUT)  # 连接ftp服务器
        cur_ftp.login(USER_NAME, PASS_WORD)  # 登录ftp服务器
        m_text.insert(tk.END, cur_ftp.getwelcome()+'      连接FTPd服务器成功 !  \n')
        m_text.pack()
        m_text.update()
        return cur_ftp
    except(socket.error, socket.gaierror):  # ftp 连接错误
        alarm_string = '服务器连接错误' +HOST+':'+str(PORT)
        alarm(alarm_string)
        return 0

def upload_file_cb(block):      #上传回调函数，同时输出进度
    global upload_size, location
    upload_size = upload_size + len(block)
    if upload_size == len(block):
        location = m_text.index("insert")
    process1 = int(upload_size / file_size *100)
    if process1> int((upload_size-len(block)) / file_size *100):        #百分比数字变化时，才刷新进度比例
        begin_location = location.split('.')[0] + '.0'
        end_location = location.split('.')[0] + '.80'
        m_text.delete(begin_location, end_location)
        process_str = '正在上传，进度: '+str(process1)+'%'+int(upload_size / file_size * 40)*chr(0x2588) + 2*chr(0x25BA)
        m_text.insert(begin_location, process_str)
        m_text.update()

def alarm(str1):
    winsound.Beep(600, 1000)
    winsound.Beep(900, 1000)
    winsound.Beep(1200, 1000)
    winsound.Beep(600, 1000)
    tk.messagebox.showinfo(title='告警提示', message=str1)

def check_samename(l_name, r_name, c_ftp):
    c_ftp.cwd(r_name)  # 设置ftp服务器端目标的路径
    ftp_name = c_ftp.nlst()
    for fn1 in ftp_name:
        if l_name == fn1.split('.')[0]:
            alarm1 = "服务器目标目录" + r_name + "有重名文件"
            alarm(alarm1)
            return False
        else:
            pass
    return True


if '__main__' == __name__:
    read_config()

    root_window = tk.Tk()                                                       # 初始化form
    root_window.title('备播文件上传  ftp client copyright ver1.0 by zjjohn')
    root_window.geometry('1024x768')
    m_text = tk.Text(root_window,fg='green',font=32,width=130, height=42)       #设置text
    m_text.insert(tk.END, '请选择待上传的备播视频文件 \n')
    m_text.pack()
    m_button = tk.Button(root_window, text='选择文件',bg='green', font=32, command=button_clicked, width=25, height=2)#按键
    m_button.pack()

    root_window.mainloop()

