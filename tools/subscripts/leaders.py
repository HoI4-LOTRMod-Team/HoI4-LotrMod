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
	frame = image.Image(filename='res/leader_frame.png')
	mask = image.Image(filename='res/leader_mask.png')
	img = image.Image(filename=img_file)

	# resize target image
	img.resize(width=mask.width, height=mask.height, filter='lanczos2', blur=1)

	# Apply alpha mask
	apply_mask(img, mask)

	# Add it ontop of the frame
	frame.composite(img, top=7, left=3)

	with frame as op:
	    op.compression = 'dxt5'
	    op.save(filename=out_path)


print("spriteTypes = {")
print("\t# This file was auto-generated by the GFX-Maker.py")
if(len(sys.argv) > 1):
	old_path = "../../gfx/leaders/"+sys.argv[1]
	for file in glob.glob(old_path+"/*.dds"):
		filename = os.path.basename(file)
		#print("File:" + filename)
		newpath = "../../gfx/leaders/"+sys.argv[1]+"/small"
		newfile = newpath + "/" + filename
		if not os.path.exists(newpath):
		    os.makedirs(newpath)
		convert_image(file, newfile)

		gfx_id = str.lower(filename[0:len(filename)-4])
		print("\tspriteType = { name = \"GFX_"+gfx_id+"\" texturefile = \"gfx/leaders/"+sys.argv[1]+"/"+filename+"\" }")
		#print("\tspriteType = { name = \"GFX_"+gfx_id+"_small\" texturefile = \"gfx/leaders/"+sys.argv[1]+"/small/"+filename+"\" }")
		print("\tspriteType = { name = \"GFX_idea_"+gfx_id+"\" texturefile = \"gfx/leaders/"+sys.argv[1]+"/small/"+filename+"\" }")

print("}")
exit(0)