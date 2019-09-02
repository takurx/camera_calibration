"""
Determines the linearity of the response of each pixel in a camera using JPEG
data. The Pearson r coefficient is used as a measure of linearity.

Command line arguments:
    * `folder`: the folder containing linearity data stacks. These should be
    NPY stacks taken at different exposure conditions, with the same ISO speed.
"""

import numpy as np
from sys import argv
from spectacle import io, linearity as lin

# Get the data folder from the command line
folder = io.path_from_input(argv)
root = io.find_root_folder(folder)
save_to = root/"intermediaries/linearity/linearity_jpeg.npy"

# Load the data
intensities_with_errors, jmeans = io.load_jmeans(folder, retrieve_value=lin.filename_to_intensity)
intensities, intensity_errors = intensities_with_errors.T
print("Loaded data")

# Calculate the Pearson r value for each pixel
print("Calculating Pearson r...", end=" ", flush=True)
r, saturated = lin.calculate_pearson_r_values_jpeg(intensities, jmeans, saturate=240)
print("... Done!")

# Save the results
np.save(save_to, r)
print(f"Saved results to '{save_to}'")
