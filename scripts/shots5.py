# -*- coding: utf-8 -*-
# shots5.py — Saved/shots.txt 의 첫 레벨을 열고 카메라 5대로 사진을 찍는다 (실행할 때마다 다음 레벨)
# 결과: Saved/Screenshots/MacEditor/{레벨}_{카메라}.png, 기록: Saved/shots5_log.txt
# ※ 레벨 열기는 실행 순간에만 한다 (화면 갱신 중에 레벨을 열면 Unreal이 꺼짐)
import unreal
SAVED = unreal.Paths.project_saved_dir()
keys = [k.strip() for k in open(SAVED + "shots.txt").read().split(",") if k.strip()]
LV = keys[0]
open(SAVED + "shots.txt", "w").write(",".join(keys[1:]))
CAMS = ["TopView", "A_Subway", "B_Door", "B_OverSofa", "CCTV"]
ROOT = "/Game/Exhibition"
els = unreal.EditorLoadingAndSavingUtils
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

def log(m):
    open(SAVED + "shots5_log.txt", "a").write(m + "\n")

def ceilings(hidden):
    for a in actors.get_all_level_actors():
        if a.get_actor_label().startswith("EX_Ceiling"):
            a.set_actor_hidden_in_game(hidden)

def play_media():
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.MediaPlate):
            c = a.get_editor_property("media_plate_component")
            p = c.get_media_player()
            if not p:
                continue
            if p.is_ready():
                if not p.is_playing():
                    p.play()
            else:
                p.set_editor_property("play_on_open", True)
                p.set_looping(True)
                p.open_source(c.get_editor_property("media_playlist").get(0))

ceilings(False)
els.save_dirty_packages(True, True)
els.load_map("%s/Maps/L_%s" % (ROOT, LV))
play_media()
log("load " + LV)
st = {"i": 0, "wait": 4.0, "h": None}

def tick(dt):
    try:
        st["wait"] -= dt
        if st["wait"] > 0:
            return
        if st["i"] >= len(CAMS):
            ceilings(False)
            unreal.unregister_slate_post_tick_callback(st["h"])
            log("DONE " + LV)
            return
        cam = CAMS[st["i"]]
        st["i"] += 1          # 먼저 올림: 스크린샷 도중 콜백이 다시 불려도 같은 카메라를 또 찍지 않게
        st["wait"] = 6.5
        L = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
        ceilings(cam == "TopView")
        play_media()
        unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "%s_%s.png" % (LV, cam), camera=L["EX_Cam_" + cam], delay=2.5)
        log("shot %s %s" % (LV, cam))
    except Exception as e:
        log("ERROR %s" % e)
        unreal.unregister_slate_post_tick_callback(st["h"])

st["h"] = unreal.register_slate_post_tick_callback(tick)
