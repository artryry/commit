from typing import Sequence

import numpy as np


class VectorMath:
    @staticmethod
    def cosine(a: Sequence[float], b: Sequence[float]) -> float:
        va = np.asarray(a, dtype=np.float64)
        vb = np.asarray(b, dtype=np.float64)
        n = np.linalg.norm(va) * np.linalg.norm(vb)
        if n == 0:
            return 0.0
        return float(np.dot(va, vb) / n)
