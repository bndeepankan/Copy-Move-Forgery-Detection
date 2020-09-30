from PIL import Image
import cv2
import scipy.misc
import numpy as np
from tqdm import tqdm
import time
import Container
import Blocks
import imageio


class image_object(object):
    """
    Object to contains a single image, then detect a fraud in it
    """

    def __init__(self, imageDirectory, imageName, blockDimension, outputDirectory):
        """
        Constructor to initialize the algorithm's parameters
        :return: None
        """

        print (imageName)
        print ("Step 1 of 4: Object and variable initialization")

        # image parameter
        self.imageOutputDirectory = outputDirectory
        self.imagePath = imageName
        self.imageData = Image.open(imageDirectory + imageName)
        self.imageWidth, self.imageHeight = self.imageData.size  # height = vertikal, width = horizontal

        if self.imageData.mode != 'L':  # L means grayscale
            self.isThisRGBImage = True
            self.imageData = self.imageData.convert('RGB')
            self.imageGrayscale = self.imageData.convert('L')  # creates a grayscale version of current image to be used later

        else:
            self.isThisRGBImage = False
            self.imageData = self.imageData.convert('L')

        self.blockDimension = blockDimension
        self.Max_Count = 15

        # container initialization to later contains several data
        self.featuresContainerKeypoints = Container.Container()
        self.featuresContainerDescriptors = Container.Container()
        self.blockPairContainer = Container.Container()
        self.matched_coordinate = Container.Container()
        self.offsetDictionary = {}
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary
        self.flann = cv2.FlannBasedMatcher(index_params,search_params)

    def run(self):
        """
        Run the created algorithm
        :return: None
        """

        self.compute()
        self.compareFeature()
        imageResult = self.createMask()
        return imageResult

    def compute(self):
        """
        To compute the characteristic features of image block
        :return: None
        """
        print ("Step 2 of 4: Computing feature vectors")

        for i in tqdm(range(0, self.imageWidth, self.blockDimension)):
            # print (i)
            for j in range(0, self.imageHeight, self.blockDimension):
                imageBlockRGB = self.imageData.crop((i, j, i + self.blockDimension, j + self.blockDimension))
                imageBlockGrayscale = self.imageGrayscale.crop((i, j, i + self.blockDimension, j + self.blockDimension))
                imageBlock = Blocks.Blocks(imageBlockGrayscale, imageBlockRGB, i, j, self.blockDimension)
                keypoints, descriptors = imageBlock.computeBlock()
                self.blockPairContainer.addBlock([i, j])
                self.featuresContainerKeypoints.addBlock(keypoints)
                self.featuresContainerDescriptors.addBlock(descriptors)

    def sort(self):
        """
        To sort the container's elements
        :return: None
        """
        self.matched_coordinate.sortFeatures()

    def compareFeature(self):

        print ("Step 3 of 4: Comparing feature vectors")

        featureContainerKeypointsLength = self.featuresContainerKeypoints.getLength()
        # print (self.featuresContainerKeypoints.getLength())
        # print (self.featuresContainerDescriptors.getLength())
        for i in tqdm(range(featureContainerKeypointsLength)):
            self.des1 = self.featuresContainerDescriptors.getValues(i)
            if self.des1 is not None and len(self.des1) >= 2:
                for j in range(i+1, featureContainerKeypointsLength):
                    self.des2 = self.featuresContainerDescriptors.getValues(j)
                    if self.des2 is not None and len(self.des2) >= 2:
                        self.matches = self.flann.knnMatch(np.asarray(self.des1,np.float32),np.asarray(self.des2,np.float32),k=2)
                        if self.matches is not None:
                            good = []
                            for pair in self.matches:
                                try:
                                    m, n = pair
                                    if m.distance < 0.7*n.distance:
                                        good.append(m)
                                except ValueError:
                                    continue
                            imgsrc = self.blockPairContainer.getValues(i)
                            imgdst = self.blockPairContainer.getValues(j)
                            keyQuery = self.featuresContainerKeypoints.getValues(i)
                            keyTrain = self.featuresContainerKeypoints.getValues(j)
                            self.checkvalid(good, keyQuery, keyTrain, imgsrc, imgdst)

    def checkvalid(self, values, querypts, trainpts, src, dst):
        if len(values) > self.Max_Count:
            for i in range(0, len(values)):
                src_pts = querypts[values[i].queryIdx].pt
                dst_pts = trainpts[values[i].trainIdx].pt
                src_pts = (int(src_pts[0]) + src[0], int(src_pts[1]) + src[1])
                dst_pts = (int(dst_pts[0]) + dst[0], int(dst_pts[1]) + dst[1])
                self.matched_coordinate.addBlock(src_pts)
                self.matched_coordinate.addBlock(dst_pts)

    def createMask(self):

        print ("Step 4 of 4: Reconstruct the groundtruth Image")

        # imagesegment = np.zeros((self.imageHeight, self.imageWidth), dtype=np.uint8)  # Use this to create mask
        imagesegment = np.array(self.imageGrayscale)  # This is mark copied region on the original image
        self.sort()
        for i in tqdm(range(self.matched_coordinate.getLength())):
            u, v = self.matched_coordinate.getValues(i)
            imagesegment[v-15:v+15, u-15:u+15] = 255

        groundtruthImage = Image.fromarray(imagesegment, 'L')
        timeStamp = time.strftime("%Y%m%d_%H%M%S")
        imageio.imwrite(self.imageOutputDirectory + timeStamp + self.imagePath, groundtruthImage)

        return imagesegment
