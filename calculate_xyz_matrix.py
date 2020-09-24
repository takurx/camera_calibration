"""
Calculate the matrices for converting camera RGB colours to CIE XYZ
coordinates. Both E (equal-energy) and D65 (daylight) illuminants will
be supported.

Command line arguments:
    * `folder`: folder containing the Camera information file.
"""

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
from spectacle import xyz, spectral, io
import colorio

# Get the data folder from the command line
folder = io.path_from_input(argv)
root = io.find_root_folder(folder)

# Load Camera objects
camera = io.load_camera(root)
print(f"Loaded Camera object: {camera}")

# Save folder
savefolder = camera.filename_analysis("spectral_response", makefolders=True)

# Load the SRFs
camera._load_spectral_response()
SRF_wavelengths, SRF_RGB = camera.spectral_response[0], camera.spectral_response[1:4]

# Plot xyz curves and SRFs
kwargs = {"lw": 3}
colours = ["#d95f02", "#1b9e77", "#7570b3"]
fig, axs = plt.subplots(nrows=2, figsize=(4,3), sharex=True)
for c, letter, colour in zip(xyz.xyz, "xyz", colours):
    axs[0].plot(xyz.wavelengths, c, c=colour, label=f"$\\bar {letter}$", **kwargs)
axs[0].set_ylabel("XYZ Response")
axs[0].legend(loc="upper left", bbox_to_anchor=(1,1))
axs[0].set_xlim(390, 700)
axs[0].set_ylim(ymin=0)

for c, letter, colour in zip(SRF_RGB, "rgb", colours):
    axs[1].plot(SRF_wavelengths, c, c=colour, label=f"${letter}$", **kwargs)
axs[1].set_xlabel("Wavelength [nm]")
axs[1].set_ylabel("RGB response")
axs[1].set_ylim(ymin=0)
axs[1].legend(loc="upper left", bbox_to_anchor=(1,1))

plt.show()
plt.close()

# Interpolate the SRFs
SRF_RGB_interpolated = spectral.interpolate_spectral_data(SRF_wavelengths, SRF_RGB, xyz.wavelengths)

# Convolve the SRFs and XYZ curves
# Resulting matrix:
# [X_R  X_G  X_B]
# [Y_R  Y_G  Y_B]
# [Z_R  Z_G  Z_B]
SRF_XYZ_product = np.einsum("xw,rw->xr", xyz.xyz, SRF_RGB_interpolated) / len(xyz.wavelengths)
base_vectors = np.hsplit(SRF_XYZ_product, 3)
base_xyz = [vector / vector.sum() for vector in base_vectors]
base_xy = [vector[:2].T[0] for vector in base_xyz]

colorio._tools.plot_flat_gamut()
triangle = plt.Polygon(base_xy, fill=False, linestyle="--", label=camera.name)
plt.gca().add_patch(triangle)
plt.legend(loc="upper right")
plt.title(f"{camera.name} colour space\ncompared to sRGB and human eye")
plt.savefig(savefolder/"colour_space.pdf", bbox_inches="tight")
plt.show()
plt.close()