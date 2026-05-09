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

    @staticmethod
    def lerp_unit(a: Sequence[float], b: Sequence[float], alpha: float) -> list[float]:
        """Convex blend then L2-normalize; alpha in [0,1] moves from `a` toward `b`."""
        va = np.asarray(a, dtype=np.float64)
        vb = np.asarray(b, dtype=np.float64)
        if va.shape != vb.shape or va.size == 0:
            return list(map(float, va))
        t = float(np.clip(alpha, 0.0, 1.0))
        out = (1.0 - t) * va + t * vb
        norm = np.linalg.norm(out)
        if norm < 1e-12:
            return list(map(float, va))
        out = out / norm
        return [float(x) for x in out]
