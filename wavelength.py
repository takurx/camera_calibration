from matplotlib import pyplot as plt
import numpy as np
from sys import argv

from ispex import general, io, plot, wavelength, raw

filename = argv[1]

boost=2.5

img = io.load_dng_raw(filename)
image_cut  = raw.cut_out_spectrum(img.raw_image)
colors_cut = raw.cut_out_spectrum(img.raw_colors)

RGBG, offsets = raw.pull_apart(image_cut, colors_cut)
plot.RGBG_stacked(RGBG, extent=(raw.xmin, raw.xmax, raw.ymax, raw.ymin), show_axes=True, saveto="TL_cutout.png", boost=boost)

RGB = raw.to_RGB_array(image_cut, colors_cut)
RGB = plot._to_8_bit(RGB, boost=boost)
plot.Bayer(RGB, saveto="RGBG_Bayer.png")
del RGB  # conserve memory

lines = wavelength.find_fluorescent_lines(RGBG, offsets)

lines_fit = lines.copy()
for j in (0,1,2):  # fit separately for R, G, B
    idx = np.isfinite(lines[j])
    coeff = np.polyfit(raw.y[idx], lines[j][idx], wavelength.degree_of_spectral_line_fit)
    lines_fit[j] = np.polyval(coeff, raw.y)

plot.fluorescent_lines(raw.y, lines.T, lines_fit.T, saveto="TL_lines.png")

wavelength_fits = wavelength.fit_many_wavelength_relations(raw.y, lines_fit.T)
coefficients, coefficients_fit = wavelength.fit_wavelength_coefficients(raw.y, wavelength_fits)
plot.wavelength_coefficients(raw.y, wavelength_fits, coefficients_fit, saveto="TL_coeff.png")

wavelength.save_coefficients(coefficients, saveto="wavelength_solution.npy")

coefficients = wavelength.load_coefficients("wavelength_solution.npy")

wavelengths_cut = wavelength.calculate_wavelengths(coefficients, raw.x, raw.y)

#wavelengths_cut = np.array([np.polyval(c, raw.x) for c in coefficients_fit])
wavelengths_split, offsets = raw.pull_apart(wavelengths_cut, colors_cut)
#nm_diff = np.diff(wavelengths_split, axis=1)/2
#nm_width = nm_diff[:,1:,:] + nm_diff[:,:-1,:]
#wavelengths_split = wavelengths_split[:,1:-1,:]
#RGBG = RGBG[:,1:-1,:] / nm_width

lambdarange, all_interpolated = wavelength.interpolate_multi(wavelengths_split, RGBG)
plot.RGBG_stacked(all_interpolated, extent=(lambdarange[0], lambdarange[-1], raw.ymax, raw.ymin), show_axes=True, xlabel="$\lambda$ (nm)", aspect=0.5 * len(lambdarange) / len(raw.x), saveto="TL_cutout_corrected.png", boost=boost)
plot.RGBG_stacked_with_graph(all_interpolated, x=lambdarange, extent=(lambdarange[0], lambdarange[-1], raw.ymax, raw.ymin), xlabel="$\lambda$ (nm)", aspect=0.5 * len(lambdarange) / len(raw.x), saveto="TL_cutout_corrected_spectrum.png", boost=boost)

plot.RGBG(RGBG, vmax=800, saveto="TL_split.png", size=30)
plot.RGBG(all_interpolated, vmax=800, saveto="TL_split_interpolated.png", size=30)

stacked = wavelength.stack(lambdarange, all_interpolated)
plot.plot_spectrum(stacked[:,0], stacked[:,1:])