import os
import sys
import time

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
        self.progress_bar.setMinimumWidth(250)
        self.progress_bar.setRange(1, 100)
        self.progress_bar.setValue(50)

        name_item = QTableWidgetItem(node.name())
        range_item = QTableWidgetItem(str(node.frameRange()))
        file_path_item = QTableWidgetItem(node["file"].value())
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(lambda: self.delete_row())

        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 0, name_item)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 3, self.stop_button)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 5, range_item)
        self.multi_render_obj.render_tableWidget.setItem(self.row_count, 6, file_path_item)
        self.multi_render_obj.render_tableWidget.setCellWidget(self.row_count, 1, self.progress_bar)

        self.worker = RenderThread()
        self.worker.signal.progress_value.connect(self.update_progress_bar)
        self.multi_render_obj.thread.start(self.worker)

    def delete_row(self):
        selected_row = self.multi_render_obj.render_tableWidget.currentRow()
        self.multi_render_obj.render_tableWidget.removeRow(selected_row)

    def update_progress_bar(self, val):
        self.progress_bar.setValue(val)

    def set_render_queue(self):
        print("check value")
        if self.multi_render_obj.queue_checkBox.isChecked():
            self.multi_render_obj.thread.setMaxThreadCount(1)


class WorkerSignals(QObject):
    progress_value = Signal(int)


class RenderThread(QRunnable):
    def __init__(self):
        super(RenderThread, self).__init__()
        self.signal = WorkerSignals()

    def run(self):
        # render_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        # with open(r"{}\pid.log".format(package_path), "w+") as pid_file:
        #     pid_file.write(str(render_process.pid))
        #     pid_file.close()
        # while True:
        #     render_log = render_process.stdout.readline().decode(encoding="utf-8")
        #     if render_log:
        #         render_progress = str(render_log)
        #     else:
        #         render_progress = "Render Completed"
        #         break
            for i in range(100):
                self.signal.progress_value.emit(i)
                time.sleep(0.5)

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
