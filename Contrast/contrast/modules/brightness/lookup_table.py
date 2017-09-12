from __future__ import unicode_literals, division, print_function

from abc import ABCMeta
import numpy as np

import logging

logger = logging.getLogger(__name__)


class LookupTable(object):
    __metaclass__ = ABCMeta

    def sample_position(self, pos):
        """
        Return the key for the image that should be shown for this position.
        Parameters
        ----------
        pos: tuple
            Normalised position in ([0, 1[, [0, 1[).

        Returns
        -------
            Value at the given position.
        """
        pass


class ArrayLookupTable(LookupTable):
    def __init__(self, array):
        super(ArrayLookupTable, self).__init__()
        self.array = array
        self.view_array = np.zeros((4, 4))

    #Method for taking the average luminance of a 4*4 pixel area around the user's gaze position.
    def sample_position(self, pos):
        try:
            x = self.array.shape[0]
            y = self.array.shape[1]
            if x == 1 or y == 1:
                return None

            limit = 6
            x_pos = int(x * pos[1])
            y_pos = int(y * pos[0])
            if x_pos >= x:
                x_pos = x-limit
            elif x_pos <= 0:
                x_pos = limit

            if y_pos >= y:
                y_pos = y-limit
            elif y_pos <= 0:
                y_pos = limit

            for ex in range (0, 4):
                for ey in range (0, 4):
                    values = ((x_pos + ex) - limit, (y_pos + ey) - limit)
                    self.view_array[ex, ey] = self.array[values]

            mean = int(np.mean(self.view_array))
            return mean
        except IndexError:
            msg = "Index Error with position x:{}, y:{} in ArrayLookupTable."
            logger.warning(msg.format(pos[0], pos[1]))
            return None
