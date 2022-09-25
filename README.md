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
5 save to one asc file.
  
```

![web-qt](/doc/web_qt_use.gif.gif)

















----------------------
the gui_qt.py is not functional for this version.
if you need it, use the prev version or next version.

this is a convert program.
their also contains the converted files.

how to conver the decl from easyeda to pads format?


```
1 install requirements.txt using command:
pip3 install -r requirements.txt

2 run gui_qt.py
3 input the footprint name, click search.
4 click one of the compoment list
5 click operation-to_pads. their will be one out.d file in the current directory.
  
```

![gui-qt](/doc/gui_qt.png)

how to use the converted files:

```
1 in pads, click File-library select a library.
2 select Decals and click import button. select the files with .d.
3 select Parts and click import button. select the files with .p.
```

NOTE:import one file to one library file. do not import all file into one library as the library has a component limit.


more info see:
https://zhuanlan.zhihu.com/p/382101712

