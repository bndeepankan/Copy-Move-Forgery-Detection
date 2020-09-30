import forgery_detect
import glob

"""
Main Code
"""

# example
# image_file = input("Enter image file name:")

# forgery_detect.detect('../test_images/', image_file, '../output_images/', blockSize=256)
path = "../test_images/"
for i in glob.glob(path + "*.jpg"):
    image_file = i.split('/')[-1]
    forgery_detect.detect(path, image_file, '../output_images/', blockSize=300)
