import logging
from contrast.modules.brightness import scenes
from skimage import io

logger = logging.getLogger(__name__)

def read_image(path):
    logger.debug('Reading file as image: {}'.format(path))
    with open(path, 'rb') as in_file:

        try:
            image = io.imread(path)
            decoder = scenes.SimpleArrayStackDecoder()
            imtable = decoder.scene_from_data(image)

            return imtable
        except RuntimeError:
            logger.exception('Failed to read file as image.')
