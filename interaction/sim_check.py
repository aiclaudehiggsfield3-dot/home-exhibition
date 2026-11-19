#!/usr/bin/env python3
"""가상 시연 결과 채점: home_tracker 결과(results/visit_*.json)를 sim_truth.json과 비교."""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
truth = json.loads((HERE / "sim_truth.json").read_text(encoding="utf-8"))
ev = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sim_events.json").read_text(encoding="utf-8"))

print("── 감지된 사건 (영상 시간)")
for t, name, val in ev["events"]:
    v = val[0] if val else ""
    if name == "result":
        v = f"QR 주소 {len(val[0])}자"
    print(f"  {t:6.1f}s  {name:6s} {v}")

print("\n── 기대한 사건")
for e in truth["expected"]:
    print("  ·", e)

frames = truth["frames"]
fps = truth["fps"]
errs = []
for vf in sorted((HERE / "results").glob("visit_*.json")):
    v = json.loads(vf.read_text(encoding="utf-8"))
    enter_t = next(t for t, n, val in ev["events"] if n == "enter" and val and val[0] == v["id"])
    e = []
    for (ts, x, y, s) in v["samples"]:
        fr = frames[min(len(frames) - 1, int(round((enter_t + ts) * fps)))]
        if fr["feet"] is None:
            continue
        fx, fy = fr["feet"]
        if not (0 <= fx <= 340 and 0 <= fy <= 190):      # 바닥 밖(입장·퇴장 순간)은 제외
            continue
        e.append(float(np.hypot(x - fx, y - fy)))
    errs += e
    print(f"\n── 관객 #{v['id']:04d}: 머문 {v['stay_s']}초 · {v['why']} · 동선 점 {len(v['samples'])}개")
    print(f"  만진 물건: {v['events']}")
    if e:
        print(f"  위치 오차(발 기준): 평균 {np.mean(e):.0f}cm · 중앙값 {np.median(e):.0f}cm · 90% {np.percentile(e, 90):.0f}cm")
