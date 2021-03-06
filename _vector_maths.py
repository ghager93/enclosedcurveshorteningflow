import numpy as np


def tangent(curve: np.ndarray):
    edge = edge_length(curve)
    edge[edge == 0] = 10e-5

    return (curve - np.roll(curve, 1, axis=0)) / edge[:, None]


def normal(curve: np.ndarray):
    tangent_ = tangent(curve)
    edge = edge_length(curve)
    second_diff_edge = np.roll(edge, -1, axis=0) + edge
    second_diff_edge[second_diff_edge == 0] = 10e-5

    return 2 * (np.roll(tangent_, -1, axis=0) - tangent_) / second_diff_edge[:, None]


def inward_normal(curve: np.ndarray):
    # The inward normal is the normal pointing toward the interior of a closed curve.
    # It is the tangent vector rotated clockwise 90 degrees.

    return tangent(curve) @ np.array([[0, -1], [1, 0]])


def edge_length(curve: np.ndarray):
    # Euclidean distance between each neighbouring vertex.

    return np.linalg.norm(curve - np.roll(curve, 1, axis=0), axis=1)


def centre_of_mass(curve: np.ndarray):
    # Returns the average point of a closed curve.
    # For a circle, this is the centre.

    return curve.mean(axis=0)
