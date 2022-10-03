import sys

from PyQt6.QtCore import QUrl, QEventLoop
from PyQt6.QtGui import QAction
from PyQt6.QtNetwork import QNetworkRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo, QWebEngineUrlRequestJob, \
    QWebEngineProfile, QWebEnginePage

import json
#https://www.pythonguis.com/faq/qwebengineview-open-links-new-window/
# 记录某个页面访问的url
from easyeda import EasyEdaRead
from pads_ascii import PadsPcbAsciiWrite, PadsLibAsciiWrite


class MyInterceptor(QWebEngineUrlRequestInterceptor):

    def interceptRequest(self,info):#QWebEngineUrlRequestInfo):
        if info.resourceType()==QWebEngineUrlRequestInfo.ResourceType.ResourceTypeXhr:#ResourceType.ResourceTypeXhr:
            print(info)
            print(info.resourceType())
            print(info.requestUrl())
            self.mywin.get_one_url_callback(info.requestUrl())

    def receivers(self,*args, **kwargs):
        print(args, kwargs)

# chrome页面引擎
class WebEngineView(QWebEngineView):

    def __init__(self,parent=None):
        super(WebEngineView, self).__init__(parent)
        # self.settings().setAttribute()

    def createWindow(self, QWebEnginePage_WebWindowType):
        #self.page().setUrlRequestInterceptor(MyInterceptor())
        return self


class ExportGui(QMainWindow):
    def __init__(self):
        super(ExportGui, self).__init__()



# 主页面gui
class WebGui(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setupUi(self)
        # 设置menu
        self.resize(800, 600)
        self.HOME_URL='https://lceda.cn/'

        self.easy_pcb_list=[]
        self.easy_pcb_lib_list=[]

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # 菜单：
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")

        # 菜单项：2项
        self.action_export = self.menubar.addAction('&Export')
        self.acion_home = self.menubar.addAction('&Home')

        self.setMenuBar(self.menubar)



        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)


        self.verticalLayout1 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout2 = QtWidgets.QVBoxLayout()
        self.verticalLayout1.addLayout(self.verticalLayout2)

        # 内部widget
        self.address_text = QtWidgets.QLineEdit(self)
        self.address_text.setDisabled(True)

        self.web = WebEngineView()
        web_profile = QWebEngineProfile(self.web)
        self.interceptor = MyInterceptor()
        self.interceptor.mywin = self
        web_profile.setUrlRequestInterceptor(self.interceptor)
        self.web.setPage(QWebEnginePage(web_profile, self.web))
        # self.web.page().set
        # self.web.page().setUrlRequestInterceptor(self.interceptor)
        self.verticalLayout2.addWidget(self.address_text)
        self.verticalLayout2.addWidget(self.web)

        #connect signal
        self.acion_home.triggered.connect(self.go_home)
        self.web.urlChanged.connect(self.renew_urlbar)
        self.web.loadFinished.connect(self.on_load_finish)
        self.web.loadStarted.connect(self.on_load_start)
        self.action_export.triggered.connect(self.on_export)

        # init url address
        self.go_home()

    def get_one_url_callback(self, qurl):

        if qurl.host()!='lceda.cn':
            return
        if '/api/documents/' in qurl.path():
            #self.export_one_pcb(i)
            # export pcb
            dat = self.get_one_url_resp(qurl)
            dat = dat.data()
            dec1 = json.loads(dat)

            easy = EasyEdaRead()
            easy.parse_json(dec1)
            if easy.doc_type != 'PCB':
                return

            easy.org_to_zero()
            easy.y_mirror()
            easy.pin_renumber_all()
            self.statusbar.showMessage('找到一个pcb:'+easy.easy_data['title'])
            self.easy_pcb_list.append(easy)
        elif '/api/components/' in qurl.path():
            qurl=qurl

            dat = self.get_one_url_resp(qurl)
            dat = dat.data()
            try:
                dec1 = json.loads(dat)
            except Exception as e:
                print('not json. decode error')
                return

            easy = EasyEdaRead()
            easy.parse_json(dec1)
            if easy.doc_type!='SCHLIB':
                return
            easy.org_to_zero()
            easy.y_mirror()
            easy.pin_renumber_all()

            self.easy_pcb_lib_list.append(easy)
            self.statusbar.showMessage('找到一个元件:'+easy.easy_data['title']+' 封装:' + easy.package_detail.easy_data['title'])



    def on_export(self):
        # PCB document:
        #https://lceda.cn/api/documents/8e002e4e89e54220b6a86befd9036596?version=6.5.15&uuid=8e002e4e89e54220b6a86befd9036596

        # 'https://lceda.cn/api/documents/a9e9aa2b4732464083749469050b2e8a?version=6.5.15&uuid=a9e9aa2b4732464083749469050b2e8a'
        for i in self.easy_pcb_list:
            # 导出pcb文件
            self.export_one_pcb(i)

        if len(self.easy_pcb_lib_list)>0:
            self.export_pcb_lib(self.easy_pcb_lib_list)

        self.easy_pcb_lib_list.clear()
        self.easy_pcb_list.clear()


    def renew_urlbar(self, q):
        self.address_text.setText(q.toString())

    def go_home(self):
        self.address_text.setText(self.HOME_URL)
        self.web.load(QUrl(self.address_text.text()))

    def on_load_finish(self):
        print('on_load_finish')
    def on_load_start(self):
        print('on_load_start')

    def get_one_url_resp(self, url):
        Request = QNetworkRequest(url)
        net = QtNetwork.QNetworkAccessManager()

        #Request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        reply = net.get(Request)


        eventLoop=QEventLoop()
        reply.finished.connect(eventLoop.quit)

        eventLoop.exec()#QEventLoop.ExcludeUserInputEvents

        return reply.readAll()

    def export_pcb_lib(self, easy_list):
        pads = PadsLibAsciiWrite()
        decals, parts = pads.easyeda_to_pads_ascii(easy_list)

        file_name = QFileDialog.getSaveFileName(self, "保存的decals文件(pads ascii v9格式)", 'default.d')
        if len(file_name[0]) > 0:
            f = open(file_name[0], 'w')
            f.write(decals)
            f.close()
        file_name = QFileDialog.getSaveFileName(self, "保存的parts文件(pads ascii v9格式)", 'default.p')
        if len(file_name[0]) > 0:
            f = open(file_name[0], 'w')
            f.write(decals)
            f.close()

        QMessageBox.information(self, 'OK!','lib export finish!')


def export_one_pcb(self, easy):

        pads = PadsPcbAsciiWrite()
        pads_pcb_text = pads.easyeda_to_pads_ascii(easy)
        file_name = QFileDialog.getSaveFileName(self, "保存的pcb文件(pads ascii v9.4格式)", easy.easy_data['title']+'.asc')
        if len(file_name[0])>0:
            f = open(file_name[0], 'w')
            f.write(pads_pcb_text)
            f.close()
            QMessageBox.information(self, 'OK!','save file:'+file_name[0]+' finish!')



if __name__=='__main__':
    app = QApplication(sys.argv)

    gui = WebGui()
    gui.show()
    # view = WebEngineView()
    # view.load(QUrl("http://www.baidu.com/"))
    # view.show()
    sys.exit(app.exec())

