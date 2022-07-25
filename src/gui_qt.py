import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from gui_easyeda_to_pads import Ui_MainWindow
from szlc_read import pull_and_save, create_comp_db
from szlc_read_list import pull_comp_index, szlc_read_comp_search, szlc_product_search
from szlc_to_pads import szlc_to_pads_decl_list


class GuiEasyedaToPads(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.actionread_comp_list.triggered.connect(self.pull_comp_list)
        self.actionto_pads.triggered.connect(self.to_pads)

        self.pushButtonSearch.clicked.connect(self.on_search)
        self.listWidget.itemClicked.connect(self.on_item_show)

        #self.listWidget.setSelectionMode()
        self.search_ret=None

        create_comp_db('comp_20210612_gz.db', 1, 0)
        create_comp_db('decl_20210612_gz.db', 0, 1)


    def on_search(self):

        word_to_s = self.lineEditSearch.text()

        self.search_ret = szlc_read_comp_search(word_to_s)
        self.listWidget.clear()
        for index in range(len(self.search_ret)):
            i = self.search_ret[index]
            self.listWidget.addItem(str(index)+":"+ i['title']+'/'+i['dataStr']['head']['c_para']['package'])


    def to_pads(self):
        package_list=[]
        for i in self.listWidget.selectedItems():
            item_text = i.text()
            tarray = item_text.split(":")
            if len(tarray)<2:
                #不认识
                continue
            index = int(tarray[0])
            comp_t_save = self.search_ret[index]
            pull_and_save(None, comp_t_save['uuid'])
            package_list.append(comp_t_save['dataStr']['head']['c_para']['package'])

        szlc_to_pads_decl_list(package_list, out_d='out.d', out_p='out.p')





    def on_item_show(self):
        for i in self.listWidget.selectedItems():
            item_text = i.text()
            tarray = item_text.split(":")
            if len(tarray) < 2:
                # 不认识
                continue
            index = int(tarray[0])
            comp_t_show = self.search_ret[index]
            if 'lcsc' not in comp_t_show:
                self.labelPic.setText(item_text+"没有图片")
                break
            if 'number' not in comp_t_show['lcsc']:
                self.labelPic.setText(item_text+"没有图片")
                break
            number = comp_t_show['lcsc']['number']
            product = szlc_product_search(number)
            if len(product)==0:
                self.labelPic.setText(item_text+"没有图片")
                break

            image_list = product[0]['image'].split('<$>')
            print(image_list)
            if len(image_list)==0:
                self.labelPic.setText(item_text+"没有图片")
                break

            req = requests.get(image_list[0])
            photo = QPixmap()
            photo.loadFromData(req.content)
            self.labelPic.setPixmap(photo)


            break




    def pull_comp_list(self):
        pull_comp_index()

if __name__=='__main__':
    app = QApplication(sys.argv)

    gui = GuiEasyedaToPads()
    gui.show()
    sys.exit(app.exec_())






