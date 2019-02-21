import numpy as np
from sys import argv
from phonecal import io, plot, linearity as lin

folder = io.path_from_input(argv)
root, images, stacks, products, results = io.folders(folder)
phone = io.read_json(root/"info.json")

colours = io.load_colour(stacks)

array_size = io.array_size_dng(folder)
mid1, mid2 = array_size // 2
center = np.s_[mid1:mid1+2, mid2:mid2+2]

colours_here = colours[center].ravel()

angles, means = io.load_means (folder, retrieve_value=io.split_pol_angle, selection=center)
means = means.reshape((len(means), -1))
print("Loaded DNG data")

offset_angle = io.load_angle(stacks)
print("Read angles")
intensities = lin.malus(angles, offset_angle)
intensities_errors = lin.malus_error(angles, offset_angle, sigma_angle0=1, sigma_angle1=1)

max_value = 2**phone["camera"]["bits"]

plot.plot_linearity_dng(intensities, means, colours_here, intensities_errors=intensities_errors, max_value=max_value, savefolder=results/"linearity")