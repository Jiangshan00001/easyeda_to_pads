# easyeda_to_pads
this is a project for easyeda pcb-lib format to pads pcb-lib format convert


if you do some pcb and smt here:https://www.jlc.com/.
then, their are some footprint created by easyeda that could match the smt.
but, if you use pads for pcb. then the footprint need to converted to pads in order to use it.



20220925：

```
1 install requirements.txt using command:
pip3 install -r requirements.txt

2 run web_qt.py
3 open the pcb project in the browser.
4 click export menu.
5 save to one asc/d/p file.
  
```


```
1 安装依赖包:
pip3 install -r requirements.txt

2 运行脚本  web_qt.py
3 打开对应pcb项目，状态栏会看到有提示。登录并查找元件，点击元件，会看到提示可导出的元件.
4 点击 导出 按钮.
5 保存相应的pcb项目，元件封装d/p 文件.
  
```
```
如果登录过，并查找过元件库，则：
1 batch功能，点击 batch按钮，选择文件 db/SMD_RCLD.txt，系统会自动将文件中的封装下载转换，并导出。
  自动弹出保存对话框，保存问 .d /.p 文件。
2 可以自行编辑txt文件，格式是每个封装一行

  
```


![web-qt](/doc/web_qt2.png)



![web-qt](/doc/web_qt_use.gif.gif)

















more info see:
https://zhuanlan.zhihu.com/p/382101712

