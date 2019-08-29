import numpy as np
from .general import gaussMd, curve_fit, generate_XY
from . import raw

parameter_labels = ["k0", "k1", "k2", "k3", "k4", "cx", "cy"]

_clip_border = np.s_[250:-250, 250:-250]


def clip_data(data, borders=_clip_border):
    """
    Clip the outer edges of the data set to be within the `borders`.

    To do:
        * Use camera-dependent default value
    """
    return data[borders]


def vignette_radial(XY, k0, k1, k2, k3, k4, cx_hat, cy_hat):
    """
    Vignetting function as defined in Adobe DNG standard 1.4.0.0
    Reference:
        https://www.adobe.com/content/dam/acom/en/products/photoshop/pdfs/dng_spec_1.4.0.0.pdf

    Parameters
    ----------
    XY
        array with X and Y positions of pixels, in absolute (pixel) units
    k0, ..., k4
        polynomial coefficients
    cx_hat, cy_hat
        optical center of image, in normalized euclidean units (0-1)
        relative to the top left corner of the image
    """
    x, y = XY

    x0, y0 = x[0], y[0] # top left corner
    x1, y1 = x[-1], y[-1]  # bottom right corner
    cx = x0 + cx_hat * (x1 - x0)
    cy = y0 + cy_hat * (y1 - y0)
    # (cx, cy) is the optical center in absolute (pixel) units
    mx = max([abs(x0 - cx), abs(x1 - cx)])
    my = max([abs(y0 - cy), abs(y1 - cy)])
    m = np.sqrt(mx**2 + my**2)
    # m is the euclidean distance from the optical center to the farthest corner in absolute (pixel) units
    r = 1/m * np.sqrt((x - cx)**2 + (y - cy)**2)
    # r is the normalized euclidean distance of every pixel from the optical center (0-1)

    p = [k4, 0, k3, 0, k2, 0, k1, 0, k0, 0, 1]
    g = np.polyval(p, r)
    # g is the normalization factor to multiply measured values with

    return g


def fit_vignette_radial(correction_observed, **kwargs):
    """
    Fit a radial vignetting function to the observed correction factors
    `correction_observed`. Any additional **kwargs are passed to `curve_fit`.
    """
    X, Y, XY = generate_XY(correction_observed.shape)
    popt, pcov = curve_fit(vignette_radial, XY, correction_observed.ravel(), p0=[1, 2, -5, 5, -2, 0.5, 0.5], **kwargs)
    standard_errors = np.sqrt(np.diag(pcov))
    return popt, standard_errors


def apply_vignette_radial(shape, parameters):
    """
    Apply a radial vignetting function to obtain a correction factor map.
    """
    X, Y, XY = generate_XY(shape)
    correction = vignette_radial(XY, *parameters).reshape(shape)
    return correction


def read_flat_field_correction(root, shape):
    """
    Load the flat-field correction model, the parameters of which are contained
    in `root`/calibration/flatfield_parameters.npy
    """
    filename = root/"calibration/flatfield_parameters.npy"
    parameters, errors = np.load(filename)
    correction_map = apply_vignette_radial(shape, parameters)
    return correction_map


def load_flat_field_correction_map(root, return_filename=False):
    """
    Load the flat-field correction map contained in
    `root`/calibration/flatfield_correction_modelled.npy

    If `return_filename` is True, also return the exact filename the bias map
    was retrieved from.
    """
    filename = root/"calibration/flatfield_correction_modelled.npy"
    correction_map = np.load(filename)
    if return_filename:
        return correction_map, filename
    else:
        return correction_map

def normalise_RGBG2(mean, stds, bayer_pattern):
    """
    Normalise the Bayer RGBG2 channels to 1.
    """
    # Demosaick the data
    mean_RGBG, offsets = raw.pull_apart(mean, bayer_pattern)
    stds_RGBG, offsets = raw.pull_apart(stds, bayer_pattern)

    # Convolve with a Gaussian kernel to find the maxima without being
    # sensitive to outliers
    mean_RGBG_gauss = gaussMd(mean_RGBG, sigma=(0,5,5))

    # Find the maximum per channel and cast these into an array of the same
    # shape as the data
    normalisation_factors = mean_RGBG_gauss.max(axis=(1,2))
    normalisation_array = normalisation_factors[:,np.newaxis,np.newaxis]

    # Normalise the mean and standard deviation data to 1
    mean_RGBG = mean_RGBG / normalisation_array
    stds_RGBG = stds_RGBG / normalisation_array

    # Re-mosaick the now-normalised flat-field data
    mean_remosaicked = raw.put_together_from_colours(mean_RGBG, bayer_pattern)
    stds_remosaicked = raw.put_together_from_colours(stds_RGBG, bayer_pattern)

    return mean_remosaicked, stds_remosaicked