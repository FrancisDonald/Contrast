from __future__ import unicode_literals, division, print_function

import io
import logging
import os

import numpy as np

from contrast.file_loading import read_image

logger = logging.getLogger(__name__)

def create_default_file_format_loaders():
    file_format_loaders = {}
    for ext in ['jpg', 'bmp', 'png']:
        file_format_loaders[ext] = read_image
    return file_format_loaders


DEFAULT_FILE_FORMAT_LOADERS = create_default_file_format_loaders()


def get_supported_file_formats():
    """
    Return list of supported file extensions.
    """
    return list(DEFAULT_FILE_FORMAT_LOADERS.keys())

class DataDecoder(object):
    """
    Class responsible for deserializing contrast.scene.Scene objects.
    """

    def scene_from_data(self, data):
        pass


def array_to_bytes(array):
    """
    Convert numpy array to byte string.

    Parameters
    ----------
    array : ndarray
        Array to covnert.

    Returns
    -------
    str
        Array encodes as string.
    """
    stream = io.BytesIO()
    np.save(stream, array)
    return stream.getvalue()


def bytes_to_array(string):
    """
    Convert byte string to numpy array.

    Parameters
    ----------
    string : str
        Byte string convert.

    Returns
    -------
    ndarray
        Decoded array.
    """
    stream = io.BytesIO(string)
    array = np.load(stream)
    array = np.require(array, requirements=['C'])
    array.flags.writeable = False
    return array

def load_scene(path, file_format_loaders=DEFAULT_FILE_FORMAT_LOADERS):
    file_name, file_extension = os.path.splitext(path)
    logger.debug('Got file to load: {}'.format(path))
    logger.debug('File extension is {}'.format(file_extension))
    file_extension = file_extension[1:]  # Remove leading period.
    loader = file_format_loaders.get(file_extension)
    if loader is not None:
        return loader(path)
    logging.warning('Unknown file extension: {}'.format(file_extension))