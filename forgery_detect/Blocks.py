import numpy as np
import cv2

class Blocks(object):
    """
    Contains a single image block and handles the calculation of characteristic features
    """

    def __init__(self, grayscaleImageBlock, rgbImageBlock, x, y, blockDimension):
        """
        Initializing the input image
        :param grayscaleImageBlock: grayscale image block
        :param rgbImageBlock: rgb image block
        :param x: x coordinate (upper-left)
        :param y: y coordinate (upper-left)
        :return: None
        """
        self.imageGrayscale = grayscaleImageBlock  # block of grayscale image

        if rgbImageBlock is not None:
            self.imageRGB = rgbImageBlock
            self.imageRGBPixels = self.imageRGB.load()
            self.isImageRGB = True
        else:
            self.isImageRGB = False

        self.coor = (x, y)
        self.blockDimension = blockDimension
        self.sift = cv2.xfeatures2d.SIFT_create()

    def computeBlock(self):
        """
        Create a representation of the image block
        :return: image block representation data
        """
        self.imageGrayscale = np.array(self.imageGrayscale)
        kp, des = self.sift.detectAndCompute(self.imageGrayscale, None)
        return kp, des