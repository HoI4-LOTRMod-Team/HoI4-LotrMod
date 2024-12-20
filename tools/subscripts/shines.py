import sys
import glob
import os




str = """    spriteType = {
        name = GFX_goal_FILE_ID_shine
        texturefile = FILE_PATH
        effectFile = gfx/FX/buttonstate.lua
        animation = {
            animationmaskfile = FILE_PATH
            animationtexturefile = gfx/interface/goals/shine_overlay.dds
            animationrotation = -90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        animation = {
            animationmaskfile = FILE_PATH
            animationtexturefile = gfx/interface/goals/shine_overlay.dds
            animationrotation = 90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        legacy_lazy_load = no
    }
"""




print("spriteTypes = {")
print("\t# This file was auto-generated by the GFX-Maker.py")


for root, dirs, files in os.walk("../../gfx/interface/goals"):
	for file in files:
		if file.endswith(".dds"):
			file_id = file[0:len(file)-4]
			file_path = os.path.join(root[6:], file).replace('\\', '/')
			
			# Ignore the shine-files
			if file_id == "shine_mask" or file_id == "shine_overlay": continue
			
			print(str.replace("FILE_ID", file_id).replace("FILE_PATH", file_path))


print("}")
exit(0)