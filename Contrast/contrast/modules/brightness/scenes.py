from __future__ import unicode_literals, division, print_function
import numpy as np
from skimage import color

from contrast.modules.brightness.bright_adapt import brightAdapt
from contrast.modules.brightness.image_manager import ArrayStackImageManager
from contrast.modules.brightness.interpolator import LinearInterpolator
from contrast.modules.brightness.lookup_table import ArrayLookupTable
from contrast.scene import Scene


class ImageStackScene(Scene):
    """
    Scene object based on a list of images and a lookup table.

    The current image to be displayed is chosen based on correspondence
    between the value in the lookup table at the position and the
    index in the image array.

    Todo: More detail about algorithm, e.g. interpolation.
    """
    scene_type = 'simple_array_stack'

    @classmethod
    def from_lum_data(cls, lum_data, interpolator=LinearInterpolator()):
        lum_values, indices = np.unique(lum_data.lum_array,
                                          return_inverse=True)
        image_array = [lum_data.frame_mapping.get(val) for val in lum_values]
        image_manager = ArrayStackImageManager(image_array)
        indices = indices.reshape(lum_data.depth_array.shape)
        lookup_table = ArrayLookupTable(indices)
        return cls(image_manager, lookup_table, interpolator)

    def __init__(self, image_manager, original, lookup_table, unique_lum,
                 interpolator=LinearInterpolator()):
        super(ImageStackScene, self).__init__()
        self.image_manager = image_manager
        self.original = original
        self.lookup_table = lookup_table
        self.interpolator = interpolator
        self.interpolator.set_unique_lum(unique_lum)

        self._current_index = 0
        self.target_index = 0
        self.gaze_pos = None

        self.p = False

    def set_index(self, brightness):
        self.target_index = brightness

    @property
    def current_index(self):
        if not self.gaze_pos:
            return
        sampled_index = self.lookup_table.sample_position(self.gaze_pos)
        if sampled_index is not None:
            self.interpolator.target = sampled_index
            self.interpolator.set_target_index()

        # TODO: remove side-effect
        self._current_index = self.interpolator.make_step()

        return self._current_index

    def render(self):
        self.image_manager.draw_image(self.current_index)

    def get_image(self, force_index=None):
        index = force_index
        if index is None:
            index = self.current_index
        return self.image_manager.load_image(index)

    def get_indices_image(self):
        array = self.lookup_table.array
        max_elem = array.max()
        min_elem = array.min()
        array_normalised = 255 * ((array - min_elem) / (max_elem - min_elem))

        return np.asarray(array_normalised, np.uint8)

    @property
    def iter_images(self):
        """
        Return an iterator for all the frame in the stack
        """
        return self.image_manager.iter_images


class SimpleArrayStackDecoder():
    """
    Naive implementation of a decoder for an ImageStackScene object.
    """

    def scene_from_data(self, data):
        h, w, d = data.shape
        if d == 4:
            data = color.rgba2rgb(data)

        original = data
        image = color.rgb2lab(data)
        detail_val = 5
        grey = color.rgb2grey(data)
        grey = grey*255/detail_val
        grey = grey.astype(int)*detail_val
        lut = ArrayLookupTable(grey)

        unique_lum = np.unique(grey)

        #Dictionary storing contrast corrected image values alongside their corresponding key luminance values.
        data_dict = {}

        for l in range(len(unique_lum)):
            data_dict[unique_lum[l]] = self.create_frame(image, unique_lum[l])

        image_manager = ArrayStackImageManager(data_dict)
        scene = ImageStackScene(image_manager, original,  lut, unique_lum)
        return scene

    def create_frame(self, data, brightness):
        # Return edited frame for unique brightness value
        frame = brightAdapt(data, brightness)

        return frame
