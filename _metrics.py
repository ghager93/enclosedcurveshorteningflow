import numpy as np
import skgeom

import _vector_maths


def curvature(curve: np.ndarray):
    # Curvature is the cross-product of the normal and the tangent, divided by a normalising factor.
    # k = t x n / ||t||**3
    #   = x'y" - x"y' / (x'**2 + y'**2)**(3/2)

    tangent = _vector_maths.tangent(curve)
    normal = _vector_maths.normal(curve)

    return ((tangent[:, 1] * normal[:, 0] - normal[:, 1] * tangent[:, 0])
            / ((tangent[:, 1] ** 2 + tangent[:, 0] ** 2) ** (3 / 2)))


def normalised_curvature(curve: np.ndarray):
    # Restrict curvature to between [-1, 1]

    curvature_ = curvature(curve)
    norm = np.max(abs(curvature_))
    if norm == 0:
        return curvature_
    else:
        return curvature_ / norm


def normalised_curvature_positive_l1(curve):
    # Scale curvature such that the maximum positive curvature is one.
    # If no positive curvature, return unscaled.

    curvature_ = curvature(curve)
    norm = np.max(curvature_)
    if norm <= 0:
        return curvature_
    else:
        return curvature_ / norm


def total_edge_length(curve: np.ndarray):
    return _vector_maths.edge_length(curve).sum()


def concavity(curve: np.ndarray):
    curvature_ = curvature(curve)

    return -sum(curvature_[curvature_ < 0])


def enclosed_area(curve: np.ndarray):
    # scikit-geometry calculates the area of clockwise curves as negative and counter-clockwise as positive.
    # Since only simple curves are considered, the absolute value is returned to avoid ambiguity.

    return abs(float(skgeom.Polygon(curve).area()))


def mean_distance_to_centre_of_mass(curve: np.ndarray):
    # Metric for determining number of iterations to singularity.
    # d = 1/|curve| * sum_s(||curve(s) - 1/|curve| * sum_s'(curve(s')) ||)

    return np.linalg.norm(curve-curve.mean(axis=0), axis=1).mean()