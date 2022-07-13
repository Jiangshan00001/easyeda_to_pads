# easyeda_to_pads
this is a project for easyeda pcb-lib format to pads pcb-lib format convert


if you do some pcb and smt here:https://www.jlc.com/.
then, their are some footprint created by easyeda that could match the smt.
but, if you use pads for pcb. then the footprint need to converted to pads in order to use it.

this is a convert program.
their also contains the converted files.

how to conver the decl from easyeda to pads format?


```
1 install requirements.txt using command:
pip3 install -r requirements.txt
2 run the script szlc_to_pads.py
the 'CAP-SMD_L7.3-W4.3-R-RD' will be saved to out.d & out.p.
change the decl in :
if __name__ == '__main__':
    szlc_to_pads_decl_list(['CAP-SMD_L7.3-W4.3-R-RD'])
    sys.exit(0)

the decl will change.
'CAP-SMD_L7.3-W4.3-R-RD' is the decl name in easyeda.


 
```



how to use the converted files:

```
1 in pads, click File-library select a library.
2 select Decals and click import button. select the files with .d.
3 select Parts and click import button. select the files with .p.
```

NOTE:import one file to one library file. do not import all file into one library as the library has a component limit.


more info see:
https://zhuanlan.zhihu.com/p/382101712

