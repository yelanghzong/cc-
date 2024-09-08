import re
import time
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt, QSize, QThread, Signal,QSettings,QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QTextEdit, QWidget, QFileDialog, QTableWidget, \
    QTableWidgetItem, QHBoxLayout, QListWidget, QStackedWidget, QVBoxLayout
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
import subprocess

import os
from lxml import etree
import requests

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(800, 500)
        self.main_layout = QHBoxLayout(Widget)  # 主布局

        self.sidebar = QListWidget(Widget)  #侧边栏
        self.sidebar.setFixedWidth(100)  # 设置侧边栏固定宽度
        self.sidebar.addItem("获取下载")
        self.sidebar.addItem("下载任务")

        # 设置侧边栏样式
        self.sidebar.setStyleSheet("""
            QListWidget {
                border: 2px solid black;  # 侧边栏边框
                padding: 10px;  # 内容与边框之间的间隔
                font-size: 14px;  # 字体大小
            }
            QListWidget::item {
                margin-bottom: 5px;  # 每项之间的间隔
            }
        """)
        self.main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget(Widget) #页面切换控件

        self.stack.setStyleSheet("""
            QStackedWidget {
                border: 2px solid blue;  # 页面切换控件边框
            }
        """)

        self.main_layout.addWidget(self.stack)

        #创建页面1

        self.page1 = QWidget(Widget)
        self.page1_layout = QVBoxLayout(self.page1)

        self.label = QLabel(self.page1)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 90, 91, 19))
        self.label_2 = QLabel(self.page1)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 170, 91, 19))
        self.label_3 = QLabel(self.page1)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(0, 380, 200, 31))

        self.textEdit = QTextEdit(self.page1)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(150, 80, 131, 31))
        self.textEdit_2 = QTextEdit(self.page1)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(150, 170, 371, 131))
        self.pushButton = QPushButton(self.page1)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(150, 120, 131, 31))
        self.pushButton.setText(QCoreApplication.translate("Widget", u"获取数据", None))

        self.pushButton_2 = QPushButton(self.page1)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(180, 310, 131, 31))
        self.pushButton_2.setText(QCoreApplication.translate("Widget", u"复制直播源", None))

        self.pushButton_3 = QPushButton(self.page1)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(340, 310, 131, 31))
        self.pushButton_3.setText(QCoreApplication.translate("Widget", u"下载直播源", None))

        self.pushButton_4 = QPushButton(self.page1)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(360, 380, 131, 31))
        self.pushButton_4.setText(QCoreApplication.translate("Widget",u"选择存放路径",None))

        # 将获取信息页面添加到StackedWidget中
        self.stack.addWidget(self.page1)

        #创建页面2
        self.page2=QWidget(Widget)
        self.page2_layout = QVBoxLayout(self.page2)

        self.tableWidget = QTableWidget(self.page2)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(20, 60, 640, 380))  # 设置位置和大小
        self.tableWidget.setRowCount(20)  # 设置行数
        self.tableWidget.setColumnCount(5)  # 设置列数
        self.tableWidget.setHorizontalHeaderLabels(["房间号", "名字", "下载速度", "下载内存","停止"])
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(4,100)

        self.stack.addWidget(self.page2)  # 将下载管理页面添加到StackedWidget中
        # 绑定侧边栏选择的事件
        self.sidebar.currentRowChanged.connect(self.switch_page)

        self.page1.setStyleSheet("""
            QWidget {
                border: 2px solid green;  # 页面1边框
            }
        """)

        self.page2.setStyleSheet("""
            QWidget {
                border: 2px solid red;  # 页面2边框
            }
        """)

        self.retranslateUi(Widget)
        QMetaObject.connectSlotsByName(Widget)

    def retranslateUi(self, Widget):
        self.setWindowIcon(QIcon('./cc.icon'))
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"cc直播源获取", None))
        self.label.setText(QCoreApplication.translate("Widget", u"输入房间号", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"直播源地址", None))

    def switch_page(self, index):
        """根据侧边栏选择切换页面"""
        self.stack.setCurrentIndex(index)

class DownloadThread(QThread):
    update_signal = Signal(str, str, str,str)
    finished_signal = Signal(str) #结束信号
    def __init__(self, room_number, name, url, output_file_path):
        super().__init__()
        self.room_number = room_number
        self.name = name
        self.url = url
        self.output_file_path = output_file_path

        self.last_size = 0  # 上一次的下载大小
        self.last_time = 0  # 上一次的时间

        self._stop_flag = False  # 停止标志位

    def run(self):
        ffmpeg_command = [
            'ffmpeg',
            '-i', self.url,
            '-c', 'copy',
            self.output_file_path
        ]

        self.process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW ) # 防止弹出黑色窗口)

        while True:
            output = self.process.stderr.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                size_match = re.search(r'size=\s*([\d.]+[kMG]B)', output)
                time_match = re.search(r'time=\s*([\d:.]+)', output)
                if size_match:

                    download_size = size_match.group(1)
                    time_str = time_match.group(1)

                    h, m, s = map(float, time_str.split(":"))
                    elapsed_time = h * 3600 + m * 60 + s  # 计算当前时间点（秒）

                    # 计算下载速度
                    size_in_kb = self.convert_size_to_kb(download_size)
                    speed = (size_in_kb - self.last_size) / (
                                elapsed_time - self.last_time) if elapsed_time > self.last_time else 0
                    speed_str = f"{speed:.2f} KB/s"

                    # 更新上一轮的数据
                    self.last_size = size_in_kb
                    self.last_time = elapsed_time
                    self.update_signal.emit(self.room_number, self.name, download_size,speed_str)
        self.finished_signal.emit(self.room_number)

    def convert_size_to_kb(self, size_str):#转换下载速度的函数
        """将 '1.2MB', '2048kB' 等转换为 kB 的值"""
        size_value = float(size_str[:-2])
        unit = size_str[-2:]
        if unit == 'MB':
            return size_value * 1024
        elif unit == 'kB':
            return size_value
        elif unit == 'GB':
            return size_value * 1024 * 1024
        return 0

    def stop(self):
        if self.process is not None:
            self.process.terminate()  # 停止 ffmpeg 进程
            self._stop_flag = True  # 设置停止标志位
            while self.process.poll() is None:
                time.sleep(0.1)  # 定期检查，避免阻塞主线程
class MyWidget(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.get_data)
        self.pushButton_2.clicked.connect(self.copytext)
        self.pushButton_3.clicked.connect(self.download_video_url)
        self.pushButton_4.clicked.connect(self.choose_folder_path)
        self.download_threads = {}  # 保存下载线程的字典
        self.selected_folder_path = None  # 用于存储用户选择的文件夹路径
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        self.load_folder_path()  # 启动时加载存储路径

        self.label.setStyleSheet("""  
            QLabel {  
                font-size: 14px;  
                color: black;  
            }  
        """)
        self.label_2.setStyleSheet("""
           QLabel {  
                font-size: 14px;  
                color: black;  
            } 
        """)
        self.label_3.setStyleSheet("""
                   QLabel {  
                        font-size: 14px;  
                        color: black;  
                        border: 1px solid black;
                    } 
                """)

        self.textEdit.setStyleSheet("""
            QTextEdit {
            background-color: white;
            border: 1px solid grey;
            }
        """)
        self.textEdit_2.setStyleSheet("""
               QTextEdit {
               border: 1px solid grey;
               }
           """)
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d3d3d3; /* 表格边框 */
                gridline-color: #d3d3d3; /* 网格线颜色 */
            }
            QTableWidget QTableCornerButton::section {
                background: #f0f0f0; /* 左上角按钮的背景色 */
            }
            QTableWidget::item {
                border: 1px solid black; /* 单元格边框 */
            }
            QTableWidget::item:hover {
                background-color: grey; /* 鼠标悬停时单元格的背景色 */
            }
        """)

    def load_folder_path(self):
        """从 INI 文件中加载存放路径"""
        self.selected_folder_path = self.settings.value('folder_path', None)  # 获取存储的路径
        if self.selected_folder_path:
            self.label_3.setText(f"存放路径: {self.selected_folder_path}")
        else:
            self.label_3.setText("存放路径: 未选择")

    def save_folder_path(self):
        """将选择的存放路径保存到 INI 文件"""
        self.settings.setValue('folder_path', self.selected_folder_path)

    def choose_folder_path(self):
        folder_path = QFileDialog.getExistingDirectory(self,"请选择文件存放路径")
        if folder_path:
            self.selected_folder_path = folder_path
            self.label_3.setText(f"存放路径:{self.selected_folder_path}")#更新标签显示
            self.save_folder_path()  # 保存路径到 INI 文件
        else:
            self.selected_folder_path = None

    def add_table_row(self, row_data):
        # 找到第一个空行
        for row in range(self.tableWidget.rowCount()):
            if not self.tableWidget.item(row, 0):  # 如果第一列为空，表示这一行是空的
                break
        else:
            # 如果没有空行，则新增一行
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)

        # 填充数据
        for col, data in enumerate(row_data):
            item = QTableWidgetItem(str(data))
            self.tableWidget.setItem(row, col, item)
        stop_button = QPushButton("停止")
        stop_button.clicked.connect(lambda: self.stop_download(row_data[0]))  # 传递房间号
        self.tableWidget.setCellWidget(row, 4, stop_button)

    def stop_download(self, room_number):
        # 停止下载线程
        if room_number in self.download_threads:
            self.download_threads[room_number].stop()  # 停止对应的 ffmpeg 进程
            del self.download_threads[room_number]  # 从字典中移除线程

        # 移除表格中的对应行
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0) and self.tableWidget.item(row, 0).text() == room_number:
                self.tableWidget.removeRow(row)
                return
    def update_table_row(self, room_number, name, download_size,download_speed):
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0) and self.tableWidget.item(row, 0).text() == room_number:
                self.tableWidget.setItem(row, 3, QTableWidgetItem(download_size)) #更新下载内存
                self.tableWidget.setItem(row, 2, QTableWidgetItem(download_speed))  # 更新下载速度
                return
        self.add_table_row([room_number, name, download_speed, download_size])
    def remove_table_row(self,room_number):
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row,0) and self.tableWidget.item(row,0).text() == room_number:
                self.tableWidget.removeRow(row)
                return
    def get_data(self):
        room_number = self.textEdit.toPlainText().strip()
        if not room_number:
            QMessageBox.warning(self, "提示", "请先输入房间号！")
            return
        url = f"https://vapi.cc.163.com/video_play_url/{room_number}"
        response = requests.get(url)
        res1 = response.json()
        if 'videourl' in res1:
            rtmp = res1['videourl']
        else:
            QMessageBox.warning(self, "提示", "该主播还未开播")
            return

        self.textEdit_2.setPlainText(str(rtmp))

        # 获取主播名字
        name = self.get_name(room_number)



    def get_name(self, room_number):
        url1 = f"https://cc.163.com/{room_number}"
        res2 = requests.get(url1)
        tree = etree.HTML(res2.text)
        name = tree.xpath('//*[@id="__next"]/div[2]/div[4]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/h1/div/text()')[0]
        return name

    def copytext(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.textEdit_2.toPlainText())

    def download_video_url(self):
        room_number = self.textEdit.toPlainText().strip()
        name = self.get_name(room_number)
        if not self.selected_folder_path:
                QMessageBox.warning(self, "提示", "请先选择文件存放路径！")
                return
        if self.selected_folder_path is not None:
            person_folder_path=os.path.join(self.selected_folder_path,name)
            #如果文件夹不存家 则创建文件夹
            if not os.path.exists(person_folder_path):
                os.makedirs(person_folder_path)

            formatted_time = time.strftime("%Y-%m-%d")
            timestamp = int(time.time())
            output_file_path = os.path.join(person_folder_path, f"{name}-{formatted_time}-{timestamp}.ts")
            url = self.textEdit_2.toPlainText()

            # 创建并启动下载线程
            download_thread = DownloadThread(room_number, name, url, output_file_path)
            download_thread.update_signal.connect(self.update_table_row)
            download_thread.finished_signal.connect(self.remove_table_row)
            download_thread.start()

            # 保存下载线程到字典
            self.download_threads[room_number] = download_thread

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())