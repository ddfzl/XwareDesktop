#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))

from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtQuick import QQuickView
from PyQt5.QtGui import QGuiApplication

from Widgets import CustomQuickView

import constants


class QmlMain(CustomQuickView):
    def __init__(self, parent):
        super().__init__(parent)
        app = QGuiApplication.instance()

        self.setTitle("Xware Desktop with QML (experimental)")
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.qmlUrl = QUrl.fromLocalFile(os.path.join(constants.FRONTEND_DIR, "QML/Main.qml"))
        self.rootContext().setContextProperty("adapters", app.adapterManager)
        self.rootContext().setContextProperty("taskModel", app.proxyModel)
        self.setSource(self.qmlUrl)
        self.resize(QSize(800, 600))


class DummyApp(QGuiApplication):
    def __init__(self, *args):
        super().__init__(*args)

        from models import TaskModel, AdapterManager, ProxyModel
        from libxware import XwareAdapterThread

        self.taskModel = TaskModel()
        self.proxyModel = ProxyModel()
        self.proxyModel.setSourceModel(self.taskModel)

        self.adapterManager = AdapterManager()
        self.xwareAdapterThread = XwareAdapterThread({
            "host": "127.0.0.1",
            "port": 9000,
        })
        self.xwareAdapterThread.start()

        self.qmlWin = QmlMain(None)
        self.qmlWin.show()

from PyQt5.QtCore import QtMsgType, QMessageLogContext, QtDebugMsg, QtWarningMsg, QtCriticalMsg, \
    QtFatalMsg


def installQtMsgHandler(msgType: QtMsgType, context: QMessageLogContext, msg: str):
    strType = {
        QtDebugMsg: "DEBUG",
        QtWarningMsg: "WARN",
        QtCriticalMsg: "CRITICAL",
        QtFatalMsg: "FATAL"
    }[msgType]

    print("Qt[{strType}] {category} {function} in {file}, on line {line}\n"
          "    {msg}".format(strType = strType,
                             category = context.category,
                             function = context.function,
                             file = context.file,
                             line = context.line,
                             msg = msg),
          file = sys.stdout if msgType in (QtDebugMsg, QtWarningMsg) else sys.stderr)


if __name__ == "__main__":
    from PyQt5.QtCore import qInstallMessageHandler
    qInstallMessageHandler(installQtMsgHandler)
    app = DummyApp(sys.argv)
    sys.exit(app.exec())
