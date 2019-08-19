"""
Compare JPEG linearity data to an sRGB model with a given gamma factor and
calculate the best-fitting normalisation as well as the R^2 value of the best-
fitting model and the RMS difference between model and data.

These calculations are all done for each individual pixel.

Command line arguments:
    * `folder`: the folder containing linearity data stacks.
    * `gamma`: the gamma value of the sRGB model to compare to the data.
"""

import numpy as np
from sys import argv
from spectacle import io, linearity as lin

# Get the data folder from the command line
folder, gamma = io.path_from_input(argv)
gamma = float(str(gamma))
root, images, stacks, products, results = io.folders(folder)
save_folder = root/"results/linearity/"

# Load the data
intensities_with_errors, jmeans = io.load_jmeans(folder, retrieve_value=lin.filename_to_intensity)
intensities, intensity_errors = intensities_with_errors.T
print("Loaded data")

# Fit the model
print(f"Fitting sRGB model with gamma = {gamma} ...")
normalizations, Rsquares, RMSes, RMSes_relative = lin.sRGB_compare_gamma(intensities, jmeans, gamma=gamma)

# Save the output
for param, label_simple in zip([normalizations, Rsquares, RMSes, RMSes_relative], ["normalization", "R2", "RMS", "RMS_rel"]):
    save_to = save_folder/f"sRGB_gamma{gamma}_{label_simple}.npy"
    np.save(save_to, param)
    print(f"Saved {label_simple} results to '{save_to}'")
