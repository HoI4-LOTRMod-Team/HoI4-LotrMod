import sys
import glob
import os
from wand import image

def apply_mask(img, mask):
    img.alpha_channel = True

    with image.Image(width=img.width, height=img.height, background=image.Color("transparent")) as alpha_image:
        #alpha_image.composite_channel("alpha", mask, "copy_alpha")
        img.composite_channel("alpha", mask, "copy_alpha")

def convert_image(img_file, out_path):
	frame = image.Image(filename='empty_frame.png')
	mask = image.Image(filename='mask.png')
	img = image.Image(filename=img_file)

	# resize image to small
	img.resize(width=mask.width, height=mask.height, filter='lanczos', blur=1)

	apply_mask(img, mask)
	frame.composite(img)

	with frame as op:
	    op.compression = 'dxt5'
	    op.save(filename=out_path)


if(len(sys.argv) > 1):
	old_path = "../"+sys.argv[1]
	print("Processing path " + old_path)
	for file in glob.glob(old_path+"/*.dds"):
		print("File:" + file)
		newpath = "../"+sys.argv[1]+"/small"
		newfile = newpath + "/" + os.path.basename(file)
		if not os.path.exists(newpath):
		    os.makedirs(newpath)
		convert_image(file, newfile)