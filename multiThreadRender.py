import os
import sys
# import nuke
# import nukescripts

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from UI.RenderPanel import Ui_Form


class MultiThreadRender(Ui_Form, QWidget):
    def __init__(self):
        super(MultiThreadRender, self).__init__()
        self.setupUi(self)
        self.node = "Write10"
        self.render_tableWidget.setRowCount(3)
        self.add_node_name_widget()

    def add_node_name_widget(self):
        self.item = QTableWidgetItem(self.node)
        self.render_tableWidget.setItem(0, 0, self.item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    render = MultiThreadRender()
    render.show()
    sys.exit(app.exec_())
