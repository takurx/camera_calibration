"""
Generate metadata files for a camera given a saturated RAW image and user
inputs on the command line.

Note that if the image does not have at least one saturated pixel, the bit
depth of the camera (which is important in further calibration steps) cannot
be determined.

Command line arguments:
    * `file`: the image to be used.

To do:
    * Generate entire file structure for camera - or separate script?
"""

from spectacle import io
from sys import argv

# Get the data folder from the command line
file = io.path_from_input(argv)

# Get the data
raw_file = io.load_raw_file(file)
bayer_map = io.load_raw_colors(file)
exif = io.load_exif(file)
print("Loaded data")

# Get additional data from command line input from the user
iso_min = input("What is the *lowest* ISO speed available on this device?\n")
iso_max = input("What is the *highest* ISO speed available on this device?\n")
iso_min = int(iso_min) ; iso_max = int(iso_max)

exposure_min = input("What is the *lowest* exposure time, in seconds, available on this device?\nThis can be provided as an integer (e.g. 5 or 10), float (e.g. 0.12 or 5.1), or fraction (e.g. 1/5 or 2/3)\n")
exposure_max = input("What is the *highest* exposure time, in seconds, available on this device?\nThis can be provided as an integer (e.g. 5 or 10), float (e.g. 0.12 or 5.1), or fraction (e.g. 1/5 or 2/3)\n")

print("")

# Bit depth - find the maximum value and the corresponding bit depth
maximum_value = raw_file.raw_image.max()
bit_depth_conversion = {255: 8, 511: 9, 1023: 10, 2047: 11, 4095: 12, 8191: 13,
                        16383: 14, 32767: 15, 65535: 16}
try:
    bit_depth = bit_depth_conversion[maximum_value]
except KeyError:
    raise ValueError(f"The provided image ({file}) does not have any saturated pixels (maximum value: {maximum_value}).")

# Device properties
device = {
        "manufacturer": exif["Image Make"].printable,
        "name": exif["Image Model"].printable
        }
print("Device properties:", device)

# Image proprties
image = {
        "raw extension": file.suffix,
        "bias": raw_file.black_level_per_channel,
        "bayer pattern": raw_file.raw_pattern.tolist(),
        "bit depth": bit_depth
        }
print("Image properties:", image)

# Settings
settings = {
        "ISO min": iso_min,
        "ISO max": iso_max,
        "t_exp min": exposure_min,
        "t_exp max": exposure_max}
print("Camera settings:", settings)
