from __future__ import unicode_literals, division, print_function

import numpy as np

from PyQt4.QtCore import QPoint, QSize, Qt, QPointF
from PyQt4.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt4.QtOpenGL import QGLWidget

class CImageWidget(QGLWidget):

    def __init__(self, c_scene, *args, **kwargs):
        super(CImageWidget, self).__init__(*args, **kwargs)

        self._last_sample = None
        self._gaze = None

        self.active_pixmap_size = QSize(0, 0)

        self._c_scene = None
        self.c_scene = c_scene

    @property
    def c_scene(self):
        return self._c_scene

    @c_scene.setter
    def c_scene(self, scene):
        self._c_scene = scene
        self.update_gaze(self._last_sample)

    def update_gaze(self, sample):
        self._last_sample = sample

        if self.c_scene is None:
            return

        self.update()


    def get_current_image(self):
        if self.c_scene is None:
            return None

        image = self.c_scene

        return image


    def get_scaled_pixmap(self):
        image = self.get_current_image()

        if image is None:
            return None

        pixmap = image
        return pixmap.scaled(self.size(), Qt.KeepAspectRatio)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        pixmap = self.get_scaled_pixmap()
        if pixmap is not None:
            self.active_pixmap_size = pixmap.size()
            painter.drawPixmap(QPointF(0.0, 0.0), pixmap)

        painter.end()