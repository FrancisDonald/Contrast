from __future__ import unicode_literals, division, print_function

import numpy as np
from PyQt4.QtCore import QPoint, QSize, Qt, QPointF
from PyQt4.QtGui import QImage, QPixmap, QPainter
from PyQt4.QtOpenGL import QGLWidget

from contrast import eyetracking


class CImageWidget(QGLWidget):
    """
    Widget that draws gaze contingent scenes based on current gaze position.
    Wraps the UI agnostic Scene object.
    """

    def __init__(self, c_scene, *args, **kwargs):
        super(CImageWidget, self).__init__(*args, **kwargs)

        self.mouse_mode = False

        self._last_sample = None
        self._gaze = None

        self.active_pixmap_size = QSize(0, 0)

        self._c_scene = None
        self.c_scene = c_scene

        self.lum_map = None

        self.setMouseTracking(True)

    @property
    def c_scene(self):
        return self._c_scene

    @c_scene.setter
    def c_scene(self, scene):
        self._c_scene = scene
        self.update_gaze(self._last_sample)

    def local_to_image_norm_coordinates(self, local_pos):
        """
        Converts local coordinates to normalised coordinates relative to the
        current image array.

        Parameters
        ----------
        local_pos : tuple
            Local position.

        Returns
        -------
        tuple of float
            Normalised coordinates in (0,1), relative to current image/pixmap.
            If no pixmap is set returns (0,0).
        """

        size = self.active_pixmap_size

        try:

            norm_pos_x = local_pos[0] / size.width()
            norm_pos_y = local_pos[1] / size.height()

            if(norm_pos_x > 1):
                norm_pos_x = 0
                norm_pos_y = 0
            if (norm_pos_y > 1):
                norm_pos_x = 0
                norm_pos_y = 0

        except ZeroDivisionError:
            return 0, 0

        return norm_pos_x, norm_pos_y

    def update_gaze(self, sample):
        self._last_sample = sample

        if self.c_scene is None:
            return

        if sample is None:
            x, y = 0, 0
        else:
            x, y = sample.pos

        local_pos = self.mapFromGlobal(QPoint(x, y))
        image_norm_pos = self.local_to_image_norm_coordinates((local_pos.x(),
                                                               local_pos.y()))
        self._gaze = local_pos
        self.c_scene.update_gaze(tuple(np.clip(image_norm_pos, 0, 1)))
        self.update()

        current_index = self.c_scene.interpolator.current_value
        target = self.c_scene.interpolator.target_index

        while current_index != target:
            self.c_scene.interpolator.make_step()
            current_index = self.c_scene.interpolator.current_value
            target = self.c_scene.interpolator.target_index
            self.update()

    def get_current_image(self):
        if self.c_scene is None:
            return None

        else:
            image = self.c_scene.get_image()

        return image

    def get_scaled_pixmap(self):
        pixmap = self.get_current_image()

        if pixmap is None:
            return None

        qImg = QImage((255*pixmap).astype("uint8"), pixmap.shape[1], pixmap.shape[0], pixmap.shape[1]*3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        return pixmap.scaled(self.size(), Qt.KeepAspectRatio)

    @staticmethod
    def mouse_event_to_gaze_sample(event):
        return eyetracking.api.EyeData(-1,
                                       (float(event.globalX()),
                                        float(event.globalY())))

    def mouseMoveEvent(self, event):
        if self.mouse_mode:
            sample = self.mouse_event_to_gaze_sample(event)
            self.update_gaze(sample)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        pixmap = self.get_scaled_pixmap()
        if pixmap is not None:
            self.active_pixmap_size = pixmap.size()
            painter.drawPixmap(QPointF(0.0, 0.0), pixmap)

        painter.end()

    def heightForWidth(self, p_int):
        width = self.self.c_scene.get_image().size().width()
        height = self.self.c_scene.get_image().size().height()
        return (p_int / width) * height
