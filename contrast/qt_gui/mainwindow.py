from __future__ import unicode_literals, division, print_function

import logging
import webbrowser

from PyQt4 import QtGui
from functools import partial

from PyQt4.QtCore import QDir, Qt, QEvent
from PyQt4.QtGui import QAction, QFileDialog, QMainWindow, QMenu, \
    QSizePolicy, QErrorMessage
from PyQt4.QtGui import QActionGroup

import contrast
from contrast.qt_gui.cwidget import CImageWidget


class ContrastMainWindow(QMainWindow):
    def __init__(self):
        super(ContrastMainWindow, self).__init__()

        self.render_area = CImageWidget(None)
        self.render_area.setSizePolicy(QSizePolicy.Ignored,
                                       QSizePolicy.Ignored)
        self.setCentralWidget(self.render_area)


    def update_scene(self, scene):
        self.render_area.c_scene = scene
        self.render_area.update()

    def update(self, *__args):
        super(ContrastMainWindow, self).update()
        self.render_area.update()

    def mouseDoubleClickEvent(self, *args, **kwargs):
        super(ContrastMainWindow, self).mouseDoubleClickEvent(*args)
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_F12:
                self.toggle_fullscreen()
                return True
        return super(ContrastMainWindow, self).event(event)