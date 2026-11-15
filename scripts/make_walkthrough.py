# -*- coding: utf-8 -*-
"""
배치별 '입구 → A → 문 → 소파(영상 시청) → 출구' 관객 시점 영상 만들기 (UE 5.4)

실행: py "/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/Scripts/make_walkthrough.py"
1) 레벨마다 걷는 카메라(EX_WalkCam)와 시퀀스(Exhibition/Sequences/LS_Walk_레벨)를 만들고
2) Movie Render Queue로 프레임을 Saved/Walkthrough/레벨/ 에 렌더합니다.
"""
import unreal

LAYOUTS = ["Opt5A", "Opt5B", "Opt5C", "Opt5D"]
FPS = 30
RES = (1280, 720)
EYE, SIT = 160, 110          # 서 있을 때 / 앉았을 때 눈높이
ROOT = "/Game/Exhibition"
OUT_DIR = unreal.Paths.project_saved_dir() + "Walkthrough/"

lib = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
els = unreal.EditorLoadingAndSavingUtils
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


# ---------------------------------------------------------------------
# 동선: (초, x, y, 높이, 바라보는 방향 yaw, 고개 pitch)
#   yaw 0 = 오른쪽(+X), 90 = 아래쪽(+Y), 180 = 왼쪽, 270(-90) = 위쪽
# ---------------------------------------------------------------------
def path_vertical(S):
    sx = S + 15                       # 소파 등받이 위치
    return [
        (0,   40, -90, EYE,  90, -5),     # 입구 밖
        (2,   40,  10, EYE,  90, -5),     # 입구 통과
        (5,   S / 2, 120, EYE,  65, -3),  # A 복도: 왼쪽 벽의 사회 영상을 봄
        (8,   S / 2, 200, EYE,  75, -3),
        (10,  S / 2, 250, EYE,  90, -5),
        (11.5, S / 2, 250, EYE,  0, -5),  # 문 쪽으로 돌아섬
        (13.5, S + 35, 250, EYE, 0, -5),  # 문 통과, B 진입
        (15.5, sx + 100, 245, EYE, -60, -8),
        (18,  sx + 40, 150, SIT,  0, -2), # 소파에 앉음
        (24,  sx + 42, 150, SIT,  0, -2), # 영상 시청
        (26,  sx + 100, 140, EYE, -60, -5), # 일어남
        (28.5, 240, 40, EYE, -90, -5),    # 출구 앞
        (30.5, 240, -25, EYE, -90, -5),   # 출구 통과
    ]


def path_horizontal():
    return [
        (0,  -90, 50, EYE,   0, -5),      # 입구 밖 (왼쪽 벽)
        (2,   10, 50, EYE,   0, -5),
        (5,  110, 45, EYE,  15, -3),      # A 복도: 오른쪽 가벽의 사회 영상을 봄
        (8,  200, 45, EYE,  10, -3),
        (10, 250, 50, EYE,   0, -5),
        (11.5, 250, 50, EYE, 90, -5),     # 문 쪽으로 돌아섬
        (13.5, 250, 150, EYE, 90, -5),    # 문 통과, B 진입
        (15.5, 160, 205, EYE, 180, -8),   # 소파 쪽으로
        (18,  80, 200, SIT, 360, -2),     # 소파에 앉음 (오른쪽 화면을 봄)
        (24,  82, 200, SIT, 360, -2),     # 영상 시청
        (26, 150, 235, EYE, 405, -5),     # 일어남
        (28.5, 240, 270, EYE, 450, -5),   # 출구 앞
        (30.5, 240, 325, EYE, 450, -5),   # 출구 통과
    ]


def path_v2():
    return [
        (0,  -90, 50, EYE,   0, -5),      # 입구 밖 (왼쪽 벽)
        (2,   10, 50, EYE,   0, -5),
        (5,  110, 45, EYE,  15, -3),      # A 복도: 오른쪽 가벽의 사회 영상을 봄
        (8,  180, 45, EYE,  10, -3),
        (10, 228, 50, EYE,   0, -5),
        (11.5, 230, 50, EYE, 90, -5),     # 문 쪽으로 돌아섬
        (13.5, 230, 118, EYE, 90, -5),    # 문 통과, B 진입
        (15.5, 190, 170, EYE, 150, -8),   # 소파 앞으로
        (18, 248, 210, SIT, 180, -2),     # 소파에 앉음 (왼쪽 벽 화면을 봄)
        (24, 246, 210, SIT, 180, -2),     # 영상 시청
        (26, 180, 245, EYE, 135, -5),     # 일어남
        (28.5, 50, 272, EYE, 90, -5),     # 출구 앞
        (30.5, 50, 325, EYE, 90, -5),     # 출구 통과
    ]


def path_v5():
    """안 5: 지하철 칸(폭 80) → 집 쪽으로 열리는 문 → 소파에서 브라운관 시청 → 출구"""
    return [
        (0,  -90, 40, EYE,   0, -4),      # 입구 밖
        (2,   10, 40, EYE,   0, -4),      # 지하철 칸 진입
        (5,  100, 40, EYE,  -8, 2),       # 손잡이·광고를 올려다봄
        (8,  180, 40, EYE,  25, -3),      # 문 쪽으로 고개를 돌리기 시작 (막힌 벽만 보이지 않게)
        (10, 228, 40, EYE,  70, -5),
        (11.5, 230, 40, EYE, 90, -5),     # 문 앞
        (13.5, 230, 110, EYE, 125, -8),   # 문 밀고 집으로, 브라운관 쪽을 봄
        (15.5, 190, 150, EYE, 150, -10),  # 브라운관 쪽으로
        (18, 248, 195, SIT, 180, -10),    # 소파에 앉음 (왼쪽 벽 브라운관)
        (24, 246, 195, SIT, 180, -11),    # TV 시청
        (26, 180, 240, EYE, 135, -6),     # 일어남
        (28.5, 60, 272, EYE, 90, -5),     # 출구 앞
        (30.5, 60, 325, EYE, 90, -5),     # 출구 통과
    ]


PATHS = {"Current": lambda: path_vertical(120), "Opt1": lambda: path_vertical(120),
         "Opt2": lambda: path_vertical(90), "Opt3": path_horizontal,
         "Opt4": path_v2, "Opt5A": path_v5, "Opt5B": path_v5, "Opt5C": path_v5, "Opt5D": path_v5}


def manual_exposure(ps):
    for k, v in [("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
                 ("auto_exposure_apply_physical_camera_exposure", False),
                 ("auto_exposure_bias", 0.0),
                 ("motion_blur_amount", 0.0)]:   # 고개 돌릴 때 번짐 없애기
        ps.set_editor_property("override_" + k, True)
        ps.set_editor_property(k, v)
    return ps


def make_sequence(key):
    els.load_map("{}/Maps/L_{}".format(ROOT, key))
    for a in actors.get_all_level_actors():
        if a.get_actor_label() == "EX_WalkCam":
            actors.destroy_actor(a)
    cam = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, EYE))
    cam.set_actor_label("EX_WalkCam")
    cam.set_folder_path("Exhibition/Cameras")
    cc = cam.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", 16.0)
    fs = cc.get_editor_property("focus_settings")
    fs.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    cc.set_editor_property("focus_settings", fs)
    cc.set_editor_property("post_process_settings", manual_exposure(cc.get_editor_property("post_process_settings")))

    name = "LS_Walk_" + key
    d = ROOT + "/Sequences"
    if lib.does_asset_exist(d + "/" + name):
        lib.delete_asset(d + "/" + name)
    seq = tools.create_asset(name, d, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    pts = PATHS[key]()
    end = int(pts[-1][0] * FPS)
    seq.set_display_rate(unreal.FrameRate(FPS, 1))
    seq.set_tick_resolution(unreal.FrameRate(FPS, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(end)

    b = seq.add_possessable(cam)
    tr = b.add_track(unreal.MovieScene3DTransformTrack)
    sec = tr.add_section()
    sec.set_range(0, end)
    ch = sec.get_all_channels()   # x, y, z, roll, pitch, yaw, sx, sy, sz
    for (t, x, y, z, yaw, pitch) in pts:
        f = unreal.FrameNumber(int(round(t * FPS)))
        for i, v in [(0, x), (1, y), (2, z), (3, 0.0), (4, pitch), (5, yaw)]:
            ch[i].add_key(f, float(v), interpolation=unreal.MovieSceneKeyInterpolation.AUTO)

    # 화면 영상도 시퀀스 시간에 맞춰 재생 (렌더 속도와 상관없이 영상 속도가 정확해짐)
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.MediaPlate):
            src = a.get_editor_property("media_plate_component").get_editor_property("media_playlist").get(0)
            pb = seq.add_possessable(a)
            mt = pb.add_track(unreal.MovieSceneMediaTrack)
            ms = mt.add_section()
            ms.set_range(0, end)
            ms.set_editor_property("media_source", src)
            try:
                ms.set_editor_property("looping", True)
            except Exception:
                pass

    cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
    cs = cut.add_section()
    cs.set_range(0, end)
    try:
        bid = seq.get_portable_binding_id(seq, b)
    except Exception:
        bid = unreal.MovieSceneSequenceExtensions.get_binding_id(seq, b)
    cs.set_camera_binding_id(bid)

    lib.save_asset(d + "/" + name)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    els.save_map(world, "{}/Maps/L_{}".format(ROOT, key))
    unreal.log("[워크스루] 시퀀스 완료: " + name)
    return d + "/" + name


def render(seq_paths):
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    for j in list(queue.get_jobs()):
        queue.delete_job(j)
    for key, sp in seq_paths:
        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.job_name = key
        job.map = unreal.SoftObjectPath("{}/Maps/L_{}.L_{}".format(ROOT, key, key))
        job.sequence = unreal.SoftObjectPath(sp + "." + sp.split("/")[-1])
        cfg = job.get_configuration()
        out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        out.output_resolution = unreal.IntPoint(RES[0], RES[1])
        out.output_directory = unreal.DirectoryPath(OUT_DIR + key)
        out.file_name_format = "{frame_number}"
        out.zero_pad_frame_numbers = 4
        cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_JPG)
        aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        aa.engine_warm_up_count = 60       # 시작 전 조명·영상이 자리 잡을 시간
        aa.use_camera_cut_for_warm_up = False
    subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
    unreal.log("[워크스루] 렌더 시작: " + ", ".join(k for k, _ in seq_paths))


seqs = [(k, make_sequence(k)) for k in LAYOUTS]
els.load_map("{}/Maps/L_Current".format(ROOT))
render(seqs)
