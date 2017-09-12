from __future__ import unicode_literals, division, print_function
from contrast.eyetracking.one_euro_filter import OneEuroFilter
import numpy as np


class Interpolator(object):
    """
    A Interpolator provides stepwise interpolation between a start and a
    target value.
    """

    def __init__(self, start=0, target=0):
        self.current_value = start
        self.target = target

    def make_step(self):
        """
        Do one interpolation step.
        """
        pass


class SplineInterpolator(Interpolator):
    def __init__(self, start, target, steps_to_target, start_speed=0):
        Interpolator.__init__(self, start, target)
        self.steps_to_target = steps_to_target
        self.current_speed = start_speed
        # TODO Implement
        raise NotImplementedError

    def make_step(self):
        pass


class InstantInterpolator(Interpolator):
    def make_step(self):
        return self.target


class LinearInterpolator(Interpolator):
    """
    Every step will move by the specified amount towards the target.
    """
    def __init__(self, start=0, target=0, step_size=1):
        Interpolator.__init__(self, start, target)
        self.step_size = step_size
        self.unique_lum = None
        self.target_index = 0

        config = {
            'freq': 60,  # Hz
            'mincutoff': 1,  # FIXME
            'beta': 0.01,  # FIXME
            'dcutoff': 1.0  # this one should be ok
        }

        self.index_filter = OneEuroFilter(**config)

    def make_step(self):
        if self.current_value > self.target_index:
            self.current_value -= self.step_size
        elif self.current_value < self.target_index:
            self.current_value += self.step_size

        if self.current_value < 0:
            self.current_value = 0
        elif self.current_value >= len(self.unique_lum):
            self.current_value = len(self.unique_lum) - 1

        return self.unique_lum[self.current_value]

    def set_unique_lum(self, unique_lum):
        self.unique_lum = unique_lum

    def set_target_index(self):
        self.target = self.find_nearest(self.unique_lum, self.target)
        self.target_index = np.where(self.unique_lum == self.target)[0]
        self.target_index = int(self.index_filter(self.target_index))

    def find_nearest(self, unique_lum, value):
        idx = (np.abs(unique_lum - value)).argmin()
        return unique_lum[idx]


class ExponentialInterpolator(Interpolator):
    """
    Every step will half the distance towards the target (using integer
    division).
    """
    def make_step(self):
        diff = self.target - self.current_value
        self.current_value += diff // 2
        return self.current_value
