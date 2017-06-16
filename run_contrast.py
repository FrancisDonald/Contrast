from __future__ import unicode_literals, division, print_function

import sys
import os
import argparse

import nose

import logging

DEBUG_LOG_FILE = 'debug.log'
logging.basicConfig(filename=DEBUG_LOG_FILE, level=logging.DEBUG, filemode='w')

logger = logging.getLogger(__name__)


def log_heading():
    logging.info('*' * 70)
    logging.info('*' * 3 + ' In case of problems with this applications please'
                           ' provide the  ***')
    logging.info(
        '*** content of this file for diagnostics.' + ' ' * 26 + '*' * 3)
    logging.info('*' * 70)

def run_ct_gui():
    """
    Set up example configuration to run ct gui with eyex and save log files.
    """

    log_heading()

    import contrast
    from PyQt4 import QtGui, QtCore
    from contrast.qt_gui.mainwindow import ContrastMainWindow
    import contrast.cio

    app = QtGui.QApplication(sys.argv)

    import ctypes
    app_id = 'contrast'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    try:
        # Pyinstaller workaround to find assets while deployed.
        if getattr(sys, 'frozen', False):
            # noinspection PyProtectedMember
            base_path = sys._MEIPASS
        else:
            base_path = './'

        # Create window
        imageviewer = ContrastMainWindow()
        imageviewer.show()

        # Set default scene
        default_scene_path = 'contrast/assets/test.jpg'
        sample_scene = contrast.cio.load_scene(
            os.path.join(base_path, default_scene_path))
        imageviewer.update_scene(sample_scene)



    except RuntimeError:
        logger.exception('Could not load sample scene.')

    sys.exit(app.exec_())


def run_tests():
    return nose.main(argv=sys.argv[:1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true',
                        help='run test suite')
    args = parser.parse_args()

    if args.d:
        run_tests()
    else:
        try:
            run_ct_gui()
        except RuntimeError:
            logging.exception('Program terminated with an exception. ')
