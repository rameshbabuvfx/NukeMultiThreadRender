# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RenderPanel.ui',
# licensing of 'RenderPanel.ui' applies.
#
# Created: Thu Oct 28 14:37:51 2021
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1022, 322)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(25)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.queue_checkBox = QtWidgets.QCheckBox(Form)
        self.queue_checkBox.setObjectName("queue_checkBox")
        self.horizontalLayout.addWidget(self.queue_checkBox)
        self.remove_tasks_pushButton = QtWidgets.QPushButton(Form)
        self.remove_tasks_pushButton.setObjectName("remove_tasks_pushButton")
        self.horizontalLayout.addWidget(self.remove_tasks_pushButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.render_tableWidget = QtWidgets.QTableWidget(Form)
        self.render_tableWidget.setStyleSheet("selection-background-color: rgb(46, 46, 46);\n"
"selection-color: rgb(204, 204, 204);")
        self.render_tableWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.render_tableWidget.setLineWidth(0)
        self.render_tableWidget.setMidLineWidth(0)
        self.render_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.render_tableWidget.setDragDropOverwriteMode(False)
        self.render_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.render_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.render_tableWidget.setShowGrid(False)
        self.render_tableWidget.setGridStyle(QtCore.Qt.NoPen)
        self.render_tableWidget.setObjectName("render_tableWidget")
        self.render_tableWidget.setColumnCount(7)
        self.render_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.render_tableWidget.setHorizontalHeaderItem(6, item)
        self.render_tableWidget.horizontalHeader().setVisible(True)
        self.render_tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.render_tableWidget.horizontalHeader().setMinimumSectionSize(100)
        self.render_tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.render_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.render_tableWidget.verticalHeader().setVisible(False)
        self.render_tableWidget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.render_tableWidget)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.queue_checkBox.setText(QtWidgets.QApplication.translate("Form", "Queue Renders", None, -1))
        self.remove_tasks_pushButton.setText(QtWidgets.QApplication.translate("Form", "Remove Finished", None, -1))
        self.render_tableWidget.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("Form", "Node", None, -1))
        self.render_tableWidget.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("Form", "Progress", None, -1))
        self.render_tableWidget.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("Form", "Status", None, -1))
        self.render_tableWidget.horizontalHeaderItem(3).setText(QtWidgets.QApplication.translate("Form", "Controls", None, -1))
        self.render_tableWidget.horizontalHeaderItem(4).setText(QtWidgets.QApplication.translate("Form", "Time Remaining", None, -1))
        self.render_tableWidget.horizontalHeaderItem(5).setText(QtWidgets.QApplication.translate("Form", "Frame Range", None, -1))
        self.render_tableWidget.horizontalHeaderItem(6).setText(QtWidgets.QApplication.translate("Form", "Task", None, -1))

