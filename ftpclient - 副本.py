from ftplib import FTP
import configparser
from tkinter import filedialog
import socket
import sys, os
import winsound

'''
#host  ftp server  地址
#ftpencoding  ftp服务器端的编码格式 GB2312 或 utf-8
#username	用户名
#password	密布
#dirs		服务器段最终文件目录，多个目录用;分开（注意小写;）
#suffix		最终成品文件的后缀
#temp_dir	在服务器端临时目录名
'''

PORT = 21
TIMEOUT = 20  # 超时时间
BLOCK_SIZE = 8192  # 每帧上传的数据大小
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

def alarm():
    for i in range(3):
        winsound.Beep(600,1000)
        winsound.Beep(900, 1000)
    input("按回车键 enter 继续")

def connect_ftp():
    cur_ftp = FTP()
    cur_ftp.encoding = ENCODING
    try:
        cur_ftp.connect(HOST, PORT, TIMEOUT)  # 连接ftp服务器
        cur_ftp.login(USER_NAME, PASS_WORD)  # 登录ftp服务器
        print(cur_ftp.getwelcome())  # 打印欢迎信息
        print("连接FTPd服务器成功 ! ")
        return cur_ftp
    except(socket.error, socket.gaierror):  # ftp 连接错误
        print("服务器连接错误[{}:{}]".format(HOST, PORT))
        alarm()
        return 0

def check_samename(l_name, r_name, c_ftp):
    c_ftp.cwd(r_name)  # 设置ftp服务器端目标的路径
    ftp_name = c_ftp.nlst()
    for fn1 in ftp_name:
        if l_name == fn1.split('.')[0]:
            print("服务器目标目录",r_name,"有重名文件")
            alarm()
            return False
        else:
            pass
    return True

def upload_file(localfile, remotepath):
    global file_size, upload_size
    upload_size = 0
    cur_ftp = connect_ftp()         #connect ftp server ,return ftp handle
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
                destname = remotepath + '/' + os.path.basename(localfile).split('.')[0] + '.'+ SUFFIX
                srcname = TEMP_DIR + os.path.basename(localfile)
                cur_ftp.rename(srcname, destname)                       #更改文件名后缀，并移动文件至目标目录
                print('   文件上传成功!, 文件名后缀更改，移动至目标目录成功!')
            except(socket.error, socket.gaierror):  # ftp 连接错误
                print("上传异常出错")
                alarm()
        else:
            return False
        return False
        cur_ftp.quit()  # 退出


def upload_file_cb(block):      #上传回调函数，同时输出进度
    global upload_size
    upload_size = upload_size + len(block)
    sys.stdout.write('正在上传，进度: \r{}>{}%'.format('=' * int(upload_size / file_size *40), int(upload_size / file_size *100)))
    sys.stdout.flush()


if '__main__' == __name__:
    read_config()
    source_filename = filedialog.askopenfilename(title='选择视频文件')
    print('待上传文件   '+source_filename)
    directoys = DIRS.split(';')         #依次选择多个传送目录
    for dir1 in directoys:
        print('将传输至：  '+dir1)
        upload_file(source_filename, dir1)


