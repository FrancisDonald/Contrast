import logging

from skimage import io, color, util, exposure
from skimage.viewer import ImageViewer

logger = logging.getLogger(__name__)

def read_image(path):
    logger.debug('Reading file as image: {}'.format(path))
    try:
        image = io.imread(path)
        #lab = color.rgb2lab(rgb)
        gray = color.rgb2lab(image)/255
        viewer = ImageViewer(gray)
        viewer.show()
        return
    except RuntimeError:
        logger.exception('Failed to read file as image.')
