import PIL
import numpy as np
import cv2
import warnings

from PIL import Image
from scipy.ndimage import morphology
from skimage import morphology
from datetime import datetime

import _structuring_element


EXCEPTION_STRING_WRONG_DIMENSIONS = 'Image must be 2D.'


def load_image(filename: str):
    im = None

    try:
        im = np.array(Image.open(filename).convert("1"))

        # Top-left corner is assumed to be background. Therefore, if this pixel is high, the image is inverted.
        im = im ^ im[0, 0]

    except FileNotFoundError:
        print("File does not exist.")
    except PIL.UnidentifiedImageError:
        print("Image format not supported.")
    except Exception:
        print("Something went wrong.")

    return im


def int_to_rgb_colour(image: np.ndarray):
    image = image / np.where(image.max() == 0, 1, image.max()) * ((2**8) - 1)

    return np.array((image,
                     (2**7) * np.where(image == 0, 2, 1),
                     (2**7) * np.where(image == 0, 2, 1))).transpose(1, 2, 0).astype(np.uint8)

def save_image(image: np.ndarray, filename: str, date_stamp: bool = True):
    # Matrix must be of type np.uint8.

    if date_stamp:
        filename = filename + datetime.now().strftime("%Y%m%d_%H%M%S") + '.jpg'

    Image.fromarray(image).save(filename, 'JPEG')


def smooth_image(image: np.ndarray, factor: int = 1):
    if image.ndim != 2:
        raise ValueError(EXCEPTION_STRING_WRONG_DIMENSIONS)
    if factor <= 0:
        raise ValueError('Smoothing factor must be positive integer.')
    return morphology.binary_closing(morphology.binary_opening(image, _structuring_element.circle(factor).kernel),
                                     _structuring_element.circle(factor).kernel)


def open_image(image: np.ndarray, factor: int = 1):
    if image.ndim != 2:
        raise ValueError(EXCEPTION_STRING_WRONG_DIMENSIONS)
    if factor <= 0:
        raise ValueError('Opening factor must be positive integer.')
    return morphology.binary_opening(image, _structuring_element.circle(factor).kernel)


def dilate_image(image: np.ndarray, factor: int = 1):
    if image.ndim != 2:
        raise ValueError(EXCEPTION_STRING_WRONG_DIMENSIONS)
    if factor <= 0:
        raise ValueError('Dilation factor must be positive integer.')
    return morphology.binary_dilation(image, _structuring_element.circle(factor).kernel)


def flood_fill(image: np.ndarray):
    # Fill in pixels of binary image of a closed curve.
    # The method will first assume the middle in the order of zero-valued pixels is inside the curve,
    # and hence fill from there.
    # If the result filled the top-most pixel, the fill was of the outside of the curve.
    # The method will then run the method again on the opposite pixels.
    # Assumes there is one closed curve that is simple.

    zero_valued_pixels = np.argwhere(image == 0)
    seed_pixel = tuple(zero_valued_pixels[len(zero_valued_pixels) // 2])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        filled_im = morphology.flood_fill(image, seed_pixel, 1, connectivity=0)

    if filled_im[0, 0]:
        # If all pixels of the filled image are high, the curve either does not have an interior
        # or the curve encompasses the image border.
        if filled_im.all():
            # If the top-left ([0, 0]) corner is part of the curve, then the curve encompasses the image border,
            # return a filled matrix block.
            # Else, the curve does not have an interior, return original curve image.
            if image[0, 0]:
                return filled_im
            else:
                return image

        seed_pixel = tuple(np.argwhere(filled_im == 0)[0])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            filled_im = morphology.flood_fill(image, seed_pixel, 1, connectivity=0)

    return filled_im


def flood_fill_cv(image: np.ndarray):
    # Fill in pixels of binary image of a closed curve.
    # Fills with a seed point in the top-left corner, which is assumed background.
    # The fill is then inverted.
    # Assumes there is one closed curve that is simple.
    # Uses cv2.floodFill which is significantly faster than skimage.

    filled = image.copy().astype(np.uint8)
    seed_point = 0, 0
    mask = np.zeros((image.shape[0] + 2, image.shape[1] + 2), dtype=np.uint8)
    new_val = 2

    cv2.floodFill(filled, mask, seed_point, new_val)

    return np.where(filled == new_val, 0, 1)
