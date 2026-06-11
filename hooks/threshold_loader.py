# L0: 행동 임계값이 근거 없이 흩어져 고정되면 잘못된 기준이 영구히 모든 판단을 지배한다
# L1: 모든 임계값은 thresholds.json(단일 진실원)에서 derive — 부재 시 기본값(fail-open)
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thresholds.json")


def get(key, default):
    """임계값 조회. SSOT 부재/키 부재/파싱 실패 = 기본값 (게이트가 장애가 되면 안 됨)."""
    try:
        with open(_PATH, encoding="utf-8") as f:
            data = json.load(f)
        entry = data.get(key)
        if isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        return default
    except Exception:
        return default
