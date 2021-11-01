"""
Author      : Ramesh Babu
Date        : Oct 25 2021
Script Name : Nuke Multi Thread Render
"""
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
        """
        Main Render panel
        """
        super(MultiThreadRender, self).__init__()
        self.setupUi(self)
        self.thread = QThreadPool()
        self.render_tableWidget.setColumnWidth(1, 250)
        self.clear_json_cache()

    @staticmethod
    def clear_json_cache():
        """
        Clears subprocess JSON cache when nuke opens.

        :return: None
        """
        empty_data = {}
        with open(r"{}\subprocessCache\ProcessID.json".format(PACKAGE_PATH), "w+") as json_file:
            json.dump(empty_data, json_file, indent=4)


class UpdateRenderWidget:

    def __init__(self, render_panel, node):
        """
        Adds the items in main render panel.

        :param Obj render_panel: render panel object
        :param Dict node: Node data.
        """
        self.node = node
        self.worker = None
        self.render_path = self.node['file'].value()
        self.progress_bar = QProgressBar()
        self.control_widget = QWidget()
        self.control_layout = QHBoxLayout()
        self.open_button = QPushButton()
        self.stop_button = QPushButton()
        self.status_label = QLabel()
        self.frame_label = QLabel()
        self.last_frame = int(self.node["custom_last"].value())
        self.frame_range = self.frame_range_value()

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
        """
        Creates widgets add date in widgets.

        :return: None
        """
        self.progress_bar.setStyleSheet(
            open(r"{}\UI\progressBarStart.qss".format(PACKAGE_PATH), "r+").read()
        )
        self.progress_bar.setMinimumWidth(250)
        self.progress_bar.setMaximumHeight(27)
        self.progress_bar.setRange(1, 100)

        name_item = QTableWidgetItem(self.node.name())
        range_item = QTableWidgetItem(str(self.frame_range))
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
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 0, name_item)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 1, self.progress_bar)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 3, self.status_label)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 4, self.control_widget)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 6, range_item)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 7, file_path_item)
        nuke_exec_path = sys.executable

        nuke_render_cmd = r'"{}" -X "{}" "{}" "{}"'.format(
            nuke_exec_path,
            self.node.name(),
            nuke.scriptName(),
            self.frame_range
        )
        self.worker = RenderThread(
            cmd=nuke_render_cmd,
            last_frame=self.last_frame,
            node_name=self.node.name()
        )
        self.connect_ui()
        self.multi_render_obj.thread.start(self.worker)

    def connect_ui(self):
        """
        Connects ui with custom methods.

        :return: None
        """
        self.multi_render_obj.queue_checkBox.stateChanged.connect(lambda: self.set_render_queue())
        self.stop_button.clicked.connect(lambda: self.delete_kill_task())
        self.open_button.clicked.connect(self.open_folder)
        self.multi_render_obj.remove_tasks_pushButton.clicked.connect(lambda: self.remove_finish_tasks())
        self.worker.signal.progress_value.connect(self.update_progress_bar)
        self.worker.signal.time_left.connect(self.update_remaining_time)
        self.worker.signal.frame_of.connect(self.frame_diff)

    def frame_range_value(self):
        """
        Creates frame range of write node.

        :return Str: Frame range.
        """
        first_frame = self.node['custom_first'].value()
        last_frame = self.node['custom_last'].value()
        frame_range = "{}-{}".format(int(first_frame), int(last_frame))
        return frame_range

    def frame_diff(self, val):
        """
        Updates the frame difference in table widget.

        :param Str val: frame number.
        :return: None.
        """
        frame = "{} of {}".format(val, self.last_frame)
        self.frame_label.setText(frame)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 2, self.frame_label)

    def delete_kill_task(self):
        """
        Kill/Delete running subprocess and item from the table widget.

        :return: None.
        """
        recent_row_count = self.multi_render_obj.render_tableWidget.rowCount()
        for row in range(recent_row_count):
            del_node_name = self.multi_render_obj.render_tableWidget.item(row, 0).text()
            if self.node.name() == del_node_name:
                with open(r"{}\subprocessCache\ProcessID.json".format(PACKAGE_PATH), "r+") as json_file:
                    json_data = json.load(json_file)
                process_pid = json_data[str(del_node_name)]
                try:
                    os.kill(int(process_pid), 9)
                except:
                    pass
                self.multi_render_obj.render_tableWidget.removeRow(row)

    def open_folder(self):
        """
        Opens the current rendering folder.

        :return: None.
        """
        render_folder = os.path.dirname(self.render_path)
        if os.path.exists(render_folder):
            if (platform.system()).lower() == "linux":
                os.system("xdg-open '%s'" % render_folder)
            else:
                prj_path = render_folder.replace("/", "\\")
                os.startfile(prj_path)

    def update_progress_bar(self, val):
        """
        Updates the progress bar value.

        :param Int val: progress bar value.
        :return: None.
        """
        if val == 100:
            self.status_label.setText("Completed")
            self.status_label.setStyleSheet("color: rgb(85, 255, 0)")
            self.progress_bar.setStyleSheet(
                open(r"{}\UI\progressBarEnd.qss".format(PACKAGE_PATH), "r+").read()
            )
        self.progress_bar.setValue(val)

    def update_remaining_time(self, val):
        """
        Updates remaining time left in table widget item.

        :param Str val: Remaining time.
        :return: None.
        """
        time_item = QTableWidgetItem(val)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 5, time_item)

    def set_render_queue(self):
        """
        Sets the render queue or parallel render.

        :return: None.
        """
        if self.multi_render_obj.queue_checkBox.isChecked():
            self.multi_render_obj.thread.setMaxThreadCount(1)
        else:
            self.multi_render_obj.thread.setMaxThreadCount(8)

    def remove_finish_tasks(self):
        """
        Removes the completed tasks from table widget.

        :return: None.
        """
        row_count = self.multi_render_obj.render_tableWidget.rowCount()
        for row in range(row_count):
            status_item = self.multi_render_obj.render_tableWidget.cellWidget(row, 3)
            status = status_item.text()
            if status == "Completed":
                self.multi_render_obj.render_tableWidget.removeRow(row)


class WorkerSignals(QObject):
    """
    Declaring signal objects.
    """
    progress_value = Signal(int)
    time_left = Signal(str)
    frame_of = Signal(str)


class RenderThread(QRunnable):
    def __init__(self, cmd=None, last_frame=None, node_name=None):
        """
        InIt method for worker class.

        :param Str cmd: Nuke terminal render command.
        :param Int last_frame: Last frame of write node.
        :param Str node_name: Node name of write.
        """
        super(RenderThread, self).__init__()
        self.cmd = cmd
        self.total = last_frame
        self.node_name = node_name
        self.signal = WorkerSignals()
        self.start_time = time.time()

    def run(self):
        """
        Run method

        :return: None.
        """
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
                percent = (float(value) / float(self.total)) * 100
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
                self.signal.frame_of.emit(str(value))
            if render_log == "":
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    render = MultiThreadRender()
    render.show()
    sys.exit(app.exec_())

