import os
import platform
import sys
import time
import subprocess

try:
    import nuke
except:
    pass

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from UI.RenderPanel import Ui_Form


class MultiThreadRender(Ui_Form, QWidget):
    def __init__(self):
        super(MultiThreadRender, self).__init__()
        self.setupUi(self)
        self.thread = QThreadPool()
        self.render_tableWidget.setColumnWidth(1, 250)


class UpdateRenderWidget:

    def __init__(self, render_panel, node):
        self.multi_render_obj = render_panel.customKnob.getObject().widget
        self.row_count = self.multi_render_obj.render_tableWidget.rowCount()
        self.multi_render_obj.render_tableWidget.setRowCount(self.row_count + 1)
        self.multi_render_obj.queue_checkBox.stateChanged.connect(lambda: self.set_render_queue())

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar{
            color: rgb(242, 156, 54);
            text-align: right; 
            margin-right: 12ex;
            }
            QProgressBar:chunk {
            background-color: qlineargradient(spread:pad, x1:0.487, y1:0, x2:0.481, y2:1, stop:0 rgba(255, 167, 64, 255), stop:1 rgba(205, 122, 24, 255));
            border-radius:3px;
            border-style: solid;
            border-width: 1px;
            border-left-color: rgb(240, 140, 50);
            border-bottom-color: rgb(240, 140, 50);
            }
        """)
        self.progress_bar.setMinimumWidth(250)
        self.progress_bar.setMaximumHeight(27)
        self.progress_bar.setRange(1, 100)

        name_item = QTableWidgetItem(node.name())
        range_item = QTableWidgetItem(str(node.frameRange()))
        self.render_path = node['file'].value()
        self.package_path = os.path.dirname(__file__)
        file_path_item = QTableWidgetItem(self.render_path)

        self.control_widget = QWidget()
        self.control_layout = QHBoxLayout()
        self.control_layout.setContentsMargins(3, 0, 3, 0)
        self.open_button = QPushButton()
        self.open_button.setIcon(QIcon(r"{}\icons\open-folder.png".format(self.package_path)))
        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(r"{}\icons\stop.png".format(self.package_path)))
        self.control_layout.addWidget(self.open_button)
        self.control_layout.addWidget(self.stop_button)
        self.control_widget.setLayout(self.control_layout)
        self.stop_button.clicked.connect(lambda: self.delete_row())
        self.open_button.clicked.connect(self.open_folder)

        self.status_label = QLabel()
        self.status_label.setText("Running")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: rgb(242, 156, 54)")

        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 0, name_item)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 1, self.progress_bar)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 2, self.status_label)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 3, self.control_widget)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 5, range_item)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 6, file_path_item)
        self.nuke_exec_path = sys.executable

        nuke_render_cmd = r'"{}" -X "{}" "{}" "{}"'.format(
            self.nuke_exec_path,
            node.name(),
            nuke.scriptName(),
            node.frameRange()
        )
        self.worker = RenderThread(cmd=nuke_render_cmd,
                                   last_frame=str(node.frameRange()).split("-")[1])
        self.worker.signal.progress_value.connect(self.update_progress_bar)
        self.worker.signal.time_left.connect(self.update_remaining_time)
        self.multi_render_obj.thread.start(self.worker)

    def delete_row(self):
        selected_row = self.multi_render_obj.render_tableWidget.currentRow()
        self.multi_render_obj.render_tableWidget.removeRow(selected_row)

    def open_folder(self):
        render_folder = os.path.dirname(self.render_path)
        if os.path.exists(render_folder):
            if (platform.system()).lower() == "linux":
                os.system("xdg-open '%s'" % render_folder)
            else:
                prj_path = render_folder.replace("/", "\\")
                os.startfile(prj_path)

    def update_progress_bar(self, val):
        if val == 100:
            self.status_label.setText("Completed")
            self.status_label.setStyleSheet("color: rgb(85, 255, 0)")
            self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 2, self.status_label)
            self.progress_bar.setStyleSheet("color: rgb(85, 255, 0)")
            self.progress_bar.setStyleSheet("""
                QProgressBar{
                color: rgb(85, 255, 0);
                text-align: right; 
                margin-right: 12ex;
                }
                QProgressBar:chunk {
                background-color: qlineargradient(spread:pad, x1:0.487, y1:0, x2:0.481, y2:1, stop:0 rgba(255, 167, 64, 255), stop:1 rgba(205, 122, 24, 255));
                border-radius:3px;
                }
            """)
        self.progress_bar.setValue(val)

    def update_remaining_time(self, val):
        time_item = QTableWidgetItem(val)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 4, time_item)

    def set_render_queue(self):
        if self.multi_render_obj.queue_checkBox.isChecked():
            self.multi_render_obj.thread.setMaxThreadCount(1)


class WorkerSignals(QObject):
    progress_value = Signal(int)
    time_left = Signal(str)


class RenderThread(QRunnable):
    def __init__(self, cmd=None, last_frame=None):
        super(RenderThread, self).__init__()
        self.cmd = cmd
        self.total = last_frame
        print(self.cmd)
        self.signal = WorkerSignals()
        self.start_time = time.time()

    def run(self):
        render_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        while True:
            render_log = render_process.stdout.readline().decode(encoding="utf-8")
            if render_log.startswith("Frame"):
                value = render_log.split(" ")[1]
                percent = (int(value) / int(self.total)) * 100
                current_time = time.time()
                elapsed_time = current_time - self.start_time
                left_seconds = 100 * elapsed_time / percent - elapsed_time

                def sec_to_hours(seconds):
                    a = str(seconds // 3600)
                    b = str((seconds % 3600) // 60)
                    c = str((seconds % 3600) % 60)
                    if a and b:
                        left = "{} seconds".format(c)
                    elif a:
                        left = "{} minutes".format(b)
                    else:
                        left = "{} hours".format(a)
                    return left

                def kill_subprocess():
                    pass

                remaining_time = sec_to_hours(int(left_seconds))
                self.signal.progress_value.emit(int(percent))
                self.signal.time_left.emit(str(remaining_time))
            if render_log == "":
                break

    # @staticmethod
    # def kill_subprocess():
    #     with open(r"{}\pid.log".format(package_path), "r+") as pid_file:
    #         pid_number = pid_file.readline()
    #         pid_file.close()
    #     os.kill(int(pid_number), 9)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    render = MultiThreadRender()
    render.show()
    sys.exit(app.exec_())
