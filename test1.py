from tkinter import *
import winsound

winsound.Beep(600, 1000)
winsound.Beep(900, 1000)
winsound.Beep(1200, 1000)
winsound.Beep(600, 1000)

root = Tk()

text1 = Text(root,width=30,height=5)
text1.pack()

text1.insert(INSERT,'I Love FishC.com!')
#第一个参数为自定义标签的名字
#第二个参数为设置的起始位置，第三个参数为结束位置
#第四个参数为另一个位置
text1.tag_add('tag1','1.7','1.12','1.14')
#用tag_config函数来设置标签的属性
text1.tag_config('tag1',background='yellow',foreground='red')
#新的tag会覆盖旧的tag
mainloop()