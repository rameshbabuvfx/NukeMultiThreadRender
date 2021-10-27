import os
import platform
import sys
import time
import subprocess
import json

try:
    import nuke
except:
    pass

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from UI.RenderPanel import Ui_Form

PACKAGE_PATH = os.path.dirname(__file__)


class MultiThreadRender(Ui_Form, QWidget):
    def __init__(self):
        super(MultiThreadRender, self).__init__()
        self.setupUi(self)
        self.thread = QThreadPool()
        self.render_tableWidget.setColumnWidth(1, 250)
        self.clear_json_cache()

    @staticmethod
    def clear_json_cache():
        empty_data = {}
        with open(r"{}\subprocessCache\ProcessID.json".format(PACKAGE_PATH), "w+") as json_file:
            json.dump(empty_data, json_file, indent=4)


class UpdateRenderWidget:

    def __init__(self, render_panel, node):
        self.node = node
        self.worker = None
        self.render_path = self.node['file'].value()
        self.progress_bar = QProgressBar()
        self.control_widget = QWidget()
        self.control_layout = QHBoxLayout()
        self.open_button = QPushButton()
        self.stop_button = QPushButton()
        self.status_label = QLabel()

        self.multi_render_obj = render_panel.customKnob.getObject().widget
        self.row_count = self.multi_render_obj.render_tableWidget.rowCount()

        running_tasks = []
        for row in range(self.row_count):
            item_node_name = self.multi_render_obj.render_tableWidget.item(row, 0)
            running_tasks.append(item_node_name.text())

        if self.node.name() not in running_tasks:
            self.multi_render_obj.render_tableWidget.setRowCount(self.row_count + 1)
            self.update_render_ui()
        else:
            nuke.message("Already Task is Running")

    def update_render_ui(self):
        self.progress_bar.setStyleSheet(
            open(r"{}\UI\progressBarStart.qss".format(PACKAGE_PATH), "r+").read()
        )
        self.progress_bar.setMinimumWidth(250)
        self.progress_bar.setMaximumHeight(27)
        self.progress_bar.setRange(1, 100)

        name_item = QTableWidgetItem(self.node.name())
        range_item = QTableWidgetItem(str(self.node.frameRange()))
        file_path_item = QTableWidgetItem(self.render_path)

        self.control_layout.setContentsMargins(3, 0, 3, 0)
        self.open_button.setIcon(QIcon(r"{}\icons\open-folder.png".format(PACKAGE_PATH)))
        self.stop_button.setIcon(QIcon(r"{}\icons\stop.png".format(PACKAGE_PATH)))
        self.control_layout.addWidget(self.open_button)
        self.control_layout.addWidget(self.stop_button)
        self.control_widget.setLayout(self.control_layout)

        self.status_label.setText("Running")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: rgb(242, 156, 54)")

        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 0, name_item)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 1, self.progress_bar)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 2, self.status_label)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 3, self.control_widget)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 5, range_item)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 6, file_path_item)
        nuke_exec_path = sys.executable

        nuke_render_cmd = r'"{}" -X "{}" "{}" "{}"'.format(
            nuke_exec_path,
            self.node.name(),
            nuke.scriptName(),
            self.node.frameRange()
        )
        self.worker = RenderThread(
            cmd=nuke_render_cmd,
            last_frame=str(self.node.frameRange()).split("-")[1],
            node_name=self.node.name()
        )
        self.connect_ui()
        self.multi_render_obj.thread.start(self.worker)

    def connect_ui(self):
        self.multi_render_obj.queue_checkBox.stateChanged.connect(lambda: self.set_render_queue())
        # self.stop_button.clicked.connect(lambda: self.kill_subprocess())
        self.stop_button.clicked.connect(lambda: self.delete_row())
        self.open_button.clicked.connect(self.open_folder)
        self.worker.signal.progress_value.connect(self.update_progress_bar)
        self.worker.signal.time_left.connect(self.update_remaining_time)

    def delete_row(self):
        self.multi_render_obj.render_tableWidget.removeRow(self.current_row)

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
            self.progress_bar.setStyleSheet(
                open(r"{}\UI\progressBarEnd.qss".format(PACKAGE_PATH), "r+").read()
            )
        self.progress_bar.setValue(val)

    def update_remaining_time(self, val):
        time_item = QTableWidgetItem(val)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 4, time_item)

    def set_render_queue(self):
        if self.multi_render_obj.queue_checkBox.isChecked():
            self.multi_render_obj.thread.setMaxThreadCount(1)

    def kill_subprocess(self):
        selected_node_name = self.multi_render_obj.render_tableWidget.item(self.current_row + 1, 0).text()
        with open(r"{}\subprocessCache\ProcessID.json".format(PACKAGE_PATH), "r+") as json_file:
            json_data = json.load(json_file)
        process_pid = json_data[str(selected_node_name)]
        os.kill(int(process_pid), 9)


class WorkerSignals(QObject):
    progress_value = Signal(int)
    time_left = Signal(str)


class RenderThread(QRunnable):
    def __init__(self, cmd=None, last_frame=None, node_name=None):
        super(RenderThread, self).__init__()
        self.cmd = cmd
        self.total = last_frame
        self.node_name = node_name
        self.signal = WorkerSignals()
        self.start_time = time.time()

    def run(self):
        render_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        with open(r"{}\subprocessCache\ProcessID.json".format(PACKAGE_PATH), "r+") as json_file:
            json_data = json.load(json_file)

        json_data.update({self.node_name: render_process.pid})

        with open(r"{}\subprocessCache\ProcessID.json".format(PACKAGE_PATH), "w+") as json_file:
            json.dump(json_data, json_file, indent=4)

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

                remaining_time = sec_to_hours(int(left_seconds))
                self.signal.progress_value.emit(int(percent))
                self.signal.time_left.emit(str(remaining_time))
            if render_log == "":
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    render = MultiThreadRender()
    render.show()
    sys.exit(app.exec_())

