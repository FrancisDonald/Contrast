from __future__ import unicode_literals, division, print_function

import logging
from contrast import cio

from functools import partial

from PyQt4.QtCore import QDir, Qt, QEvent
from PyQt4.QtGui import QAction, QFileDialog, QMainWindow, QMenu, \
    QSizePolicy
from PyQt4.QtGui import QActionGroup

from contrast.qt_gui.async import BlockingTask
from contrast.qt_gui.cwidget import CImageWidget

logger = logging.getLogger(__name__)


class ContrastMainWindow(QMainWindow):
    def __init__(self, tracking_apis=None):
        super(ContrastMainWindow, self).__init__()

        # Ete tracking setup
        self.tracking_apis = tracking_apis if tracking_apis is not None else {}
        self.tracker = None

        #Main layout
        self.render_area = CImageWidget(None)
        self.render_area.setSizePolicy(QSizePolicy.Ignored,
                                       QSizePolicy.Ignored)
        self.setCentralWidget(self.render_area)


        # Create actions
        self.open_action = QAction("&Open...",
                                   self,
                                   shortcut="Ctrl+O",
                                   triggered=self.load_scene_procedure)

        self.exit_action = QAction("&Exit",
                                   self,
                                   shortcut="Ctrl+Q",
                                   triggered=self.close
                                   )

        self._make_tracker_select_menu()

        # Create Menues
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Create Option Menu
        self.options_menu = QMenu("&Options", self)

        tracker_menu = self.options_menu.addMenu('Select Tracker')
        tracker_menu.addActions(self.select_tracker_action_group.actions())

        # Set default gaze input or mouse simulation
        if self.select_tracker_action_group.actions():
            self.select_tracker_action_group.actions()[0].trigger()
        else:
            self.mouse_toggle_action.trigger()

        # Add menus to menu bar
        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.options_menu)

        # Add handlers for fullscreen mode
        self._fullscreen = False

        self.setWindowTitle("Contrast")
        self.resize(800, 600)

    def _make_tracker_select_menu(self):
        self.select_tracker_action_group = QActionGroup(self)
        self.select_tracker_action_group.setExclusive(True)

        # Add detected eye trackers
        for name, api in self.tracking_apis.items():
            action = QAction(name,
                             self,
                             triggered=partial(self.select_eye_tracker, name),
                             checkable=True,
                             )
            self.select_tracker_action_group.addAction(action)

        # Add mouse input as fallback
        mouse_mode = QAction("Mouse",
                             self,
                             triggered=self.toggle_mouse_mode,
                             checkable=True,
                             )
        self.select_tracker_action_group.addAction(mouse_mode)

    def select_eye_tracker(self, tracker_api_key):
        self.disable_mouse_mode()
        logger.debug('Selecting tracker {}'.format(tracker_api_key))
        if self.tracker:
            self.tracker.on_event = []
        self.tracker = self.tracking_apis.get(tracker_api_key)

        self.tracker.on_event.append(self.render_area.update_gaze)

    def toggle_mouse_mode(self):
        self.render_area.mouse_mode = not self.render_area.mouse_mode

    def disable_mouse_mode(self):
        self.render_area.mouse_mode = False

    def update_scene(self, scene):
        self.render_area.c_scene = scene
        self.render_area.update()

    def load_scene_procedure(self):
        """
        Starts UI procedure to load scene form .gc file.
        """
        file_name = QFileDialog.getOpenFileName(self,
                                                "Open File",
                                                QDir.currentPath(),
                                                filter="Image File (*.bmp *.jpg *.png *.tif)"
                                                )
        if file_name:
            self.load_scene_file(str(file_name))

    def load_scene_file(self, path):
        """
        Parameters
        ----------
        path: str
            Path to file that will be loaded.
        """
        self.render_area.c_scene.interpolator.current_value = 0

        scene_load_func = partial(cio.load_scene, path)
        loader = BlockingTask(scene_load_func,
                              'Loading file.',
                              parent=self)
        loader.load_finished.connect(self.update_scene)
        loader.start_task()

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

            elif event.key() == Qt.Key_M:
                self.toggle_mouse_mode()
        return super(ContrastMainWindow, self).event(event)
