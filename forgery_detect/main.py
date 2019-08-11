import forgery_detect
import glob

"""
Main Code
"""

# example
image_file = raw_input("Enter image file name:")

forgery_detect.detect('../test_images/', image_file, '../output_images/', blockSize=256)
# path = "/Users/deepankanbn/Downloads/MICC-F220/"
# for i in glob.glob(path + "*sony_61tamp*.jpg"):
#     image_file = i.split('/')[-1]
#     forgery_detect.detect(path, image_file, '../output_images/', blockSize=300)
