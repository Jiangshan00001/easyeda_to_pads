import sys


from PyQt6.QtCore import QUrl, QEventLoop
from PyQt6.QtCore import QUrlQuery
from PyQt6.QtGui import QAction
from PyQt6.QtNetwork import QNetworkRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo, QWebEngineUrlRequestJob, \
    QWebEngineProfile, QWebEnginePage

import json
# https://www.pythonguis.com/faq/qwebengineview-open-links-new-window/
# 记录某个页面访问的url
from easyeda import EasyEdaRead
from pads_ascii import PadsPcbAsciiWrite, PadsLibAsciiWrite
from easyeda_search import get_decal_data, write_cfg, read_cfg


class MyInterceptor(QWebEngineUrlRequestInterceptor):

    def interceptRequest(self, info):  # QWebEngineUrlRequestInfo):
        if info.resourceType() == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeXhr:  # ResourceType.ResourceTypeXhr:
            print(info)
            print(info.resourceType())
            print(info.requestUrl())
            self.mywin.get_one_url_callback(info)

    def receivers(self, *args, **kwargs):
        print(args, kwargs)


# chrome页面引擎
class WebEngineView(QWebEngineView):

    def __init__(self, parent=None):
        super(WebEngineView, self).__init__(parent)
        # self.settings().setAttribute()

    def createWindow(self, QWebEnginePage_WebWindowType):
        # self.page().setUrlRequestInterceptor(MyInterceptor())
        return self


class ExportGui(QMainWindow):
    def __init__(self):
        super(ExportGui, self).__init__()


# 主页面gui
class WebGui(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setupUi(self)
        # 设置menu
        self.resize(800, 600)
        self.HOME_URL = 'https://lceda.cn/'

        self.easy_pcb_list = []
        self.easy_pcb_lib_list = []

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # 菜单：
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")

        # 菜单项：2+1项
        self.action_export = self.menubar.addAction('&Export')
        self.action_home = self.menubar.addAction('&Home')
        self.action_batch = self.menubar.addAction('&Batch')
        self.action_batch.setToolTip('此功能如果要启动，需要用户登录并点击元件库查询页面')

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

        # qputenv('QTWEBENGINE_REMOTE_DEBUGGING',9223)
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

        # connect signal
        self.action_home.triggered.connect(self.go_home)
        self.web.urlChanged.connect(self.renew_urlbar)
        self.web.loadFinished.connect(self.on_load_finish)
        self.web.loadStarted.connect(self.on_load_start)
        self.action_export.triggered.connect(self.on_export)
        self.action_batch.triggered.connect(self.on_batch)

        try:
            cfg = read_cfg()
            if 'uid' in cfg:
                self.uid = cfg['uid']
                self.ver = cfg['version']
            else:
                self.uid = None
                self.ver = None
        except Exception as e:
            self.uid = None
            self.ver = None

        if self.uid is None:
            self.action_batch.setEnabled(0)

        # init url address
        self.go_home()

    def on_batch(self):
        """
        导出指定封装
        将需要导出的封装名称写到一个文本文件中，每行一个封装，可以有空行
        从弹出的对话框中选择输入文件，输出文件
        """
        file_name = QFileDialog.getOpenFileName(self, "选择每行为1个封装的txt文本", './db/SMD_RCLD.txt')
        if len(file_name[0]) == 0:
            return

        f = open(file_name[0], 'r')
        decals = f.read()
        f.close()

        decals_list = decals.split('\n')

        self.easy_pcb_list.clear()
        self.easy_pcb_lib_list.clear()
        for index, i in enumerate(decals_list) :
            i = i.strip()
            if len(i) == 0:
                continue
            curr_decal = i
            print(curr_decal)
            decal_json_data = get_decal_data(curr_decal)
            try:
                if type(decal_json_data)==type(''):
                    dec1 = json.loads(decal_json_data)
                else:
                    dec1 = decal_json_data
            except Exception as e:
                print('decal error:', i)
                continue

            easy = EasyEdaRead()
            easy.parse_json(dec1)
            if (easy.doc_type != 'SCHLIB') and (easy.doc_type != 'PCBLIB'):
                continue

            if easy.package_detail is None:
                continue

            easy.org_to_zero()
            easy.y_mirror()
            easy.pin_renumber_all()
            self.easy_pcb_lib_list.append(easy)
            self.statusbar.showMessage( str(index)+'/'+str(len(decals_list))+
                '个元件:' + easy.easy_data['title'] + ' 封装:' + easy.package_detail.easy_data['title'])
            QApplication.processEvents()
        self.on_export()

    def get_one_url_callback(self, info):

        # get uid:
        # https://easyeda.com/api/components?version=6.5.15&docType=2&uid=0819f05c4eef4c71ace90d822a990e88&type=3

        qurl = info.requestUrl()
        if qurl.host() != 'lceda.cn':
            return
        print(qurl)

        if qurl.path() == '/api/components':
            # 将uid记录下来，方便后期直接进行查询操作
            qq = QUrlQuery(qurl.query())
            ver = None
            uid = None
            for i in qq.queryItems():
                if i[0] == 'version':
                    ver = i[1]
                if i[0] == 'uid':
                    uid = i[1]
            if uid is not None:
                self.uid = uid
                self.ver = ver
                write_cfg({'version': ver, 'uid': uid})

                self.action_batch.setEnabled(1)

        if '/api/documents/' in qurl.path():
            # self.export_one_pcb(i)
            # export pcb
            dat = self.get_one_url_resp(qurl)
            dat = dat.data()
            dec1 = json.loads(dat)

            easy = EasyEdaRead()
            try:
                easy.parse_json(dec1)
            except Exception as e:
                print('get_one_url_callback not json. decode error')

                return
            if easy.doc_type != 'PCB':
                return

            easy.org_to_zero()
            easy.y_mirror()
            easy.pin_renumber_all()
            self.statusbar.showMessage('找到一个pcb:' + easy.easy_data['title']+'. 点击export菜单按钮可以导出')
            self.easy_pcb_list.append(easy)
        elif '/api/components/' in qurl.path():
            qurl = qurl

            dat = self.get_one_url_resp(qurl)
            dat = dat.data()
            try:
                dec1 = json.loads(dat)
            except Exception as e:
                print('not json. decode error')
                return

            easy = EasyEdaRead()
            easy.parse_json(dec1)
            if easy.doc_type != 'SCHLIB':
                return
            easy.org_to_zero()
            easy.y_mirror()
            easy.pin_renumber_all()

            self.easy_pcb_lib_list.append(easy)
            self.statusbar.showMessage(
                '找到一个元件:' + easy.easy_data['title'] + ' 封装:' + easy.package_detail.easy_data['title']+'. 点击export菜单按钮可以导出')

    def on_export(self):

        if (len(self.easy_pcb_list) == 0) and (len(self.easy_pcb_lib_list) == 0):
            QMessageBox.information(self, '没有可以导出的内容.', '请先浏览相关内容，pcb和pcb封装会被自动抓取，之后再点击此导出按钮!')

        # PCB document:
        # https://lceda.cn/api/documents/8e002e4e89e54220b6a86befd9036596?version=6.5.15&uuid=8e002e4e89e54220b6a86befd9036596

        # 'https://lceda.cn/api/documents/a9e9aa2b4732464083749469050b2e8a?version=6.5.15&uuid=a9e9aa2b4732464083749469050b2e8a'
        for i in self.easy_pcb_list:
            # 导出pcb文件
            self.export_one_pcb(i)

        if len(self.easy_pcb_lib_list) > 0:
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

        # Request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        reply = net.get(Request)

        eventLoop = QEventLoop()
        reply.finished.connect(eventLoop.quit)

        eventLoop.exec()  # QEventLoop.ExcludeUserInputEvents

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
            f.write(parts)
            f.close()

        QMessageBox.information(self, 'OK!', 'lib export finish!')


    def export_one_pcb(self, easy):
        pads = PadsPcbAsciiWrite()
        pads_pcb_text = pads.easyeda_to_pads_ascii(easy)
        file_name = QFileDialog.getSaveFileName(self, "保存的pcb文件(pads ascii v9.4格式)", easy.easy_data['title'] + '.asc')
        if len(file_name[0]) > 0:
            f = open(file_name[0], 'w')
            f.write(pads_pcb_text)
            f.close()
            QMessageBox.information(self, 'OK!', 'save file:' + file_name[0] + ' finish!')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    gui = WebGui()
    gui.show()
    sys.exit(app.exec())
