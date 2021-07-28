import numpy as np

import concave_enclosed_csf_list
import csf_list


def enclosed_csf_list(curve: np.ndarray, n_subsets: int, step_size: float = 1):
    ecsf_obj = concave_enclosed_csf_list.ConcaveEnclosedCSFList(curve, step_size=step_size)

    try:
        ecsf_obj.run()
    except Exception as e:
        raise e

    num_concave_curves = max(1, int((1 - ecsf_obj.last_to_first_curve_area_ratio()) * n_subsets))

    concave_curves = ecsf_obj.get_n_curves(num_concave_curves)

    csf_obj = csf_list.CSFList(concave_curves[-1])

    convex_curves = csf_obj.mm_subset(n_subsets - num_concave_curves)

    return concave_curves + convex_curves