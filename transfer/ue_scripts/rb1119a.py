import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
# -*- coding: utf-8 -*-
# L_Current를 홈페이지(experience.html, 11/19) 최신 배치로 다시 짓기.
# 블루프린트가 가리키는 6개(PointLight_1·2, MediaPlate_1, StaticMeshActor_27, CineCameraActor_0·1)는 지우지 않고 옮기기만 함.
# 좌표: X 왼→오 0~300, Y 위(지하철)→아래(집) 0~300, Z 높이 (cm). html (x, z) m → (X, Y) cm.
import unreal, json, traceback
OUT = SV_+'rb1119a.txt'
log = []
def P(*a):
    log.append(' '.join(str(x) for x in a))
try:
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    lib = unreal.EditorAssetLibrary
    mel = unreal.MaterialEditingLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    els = unreal.EditorLoadingAndSavingUtils
    ROOT, PREFIX, F, TOP = "/Game/Exhibition", "EX_", 2, 242
    CUBE = lib.load_asset("/Engine/BasicShapes/Cube.Cube")
    PLANE = lib.load_asset("/Engine/BasicShapes/Plane.Plane")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert world.get_name() == "L_Current", "지금 열린 레벨이 L_Current가 아님: " + world.get_name()

    COLORS = {"Ground": (0.05, 0.05, 0.05), "S_Wall": (0.35, 0.37, 0.40), "S_Floor": (0.075, 0.085, 0.095),
              "S_Ceiling": (0.45, 0.48, 0.52), "H_Cream": (0.81, 0.72, 0.56), "H_Wood": (0.19, 0.067, 0.025),
              "H_Ceiling": (0.88, 0.80, 0.67), "Door": (0.43, 0.19, 0.07), "ExitDoor": (0.69, 0.61, 0.47),
              "Steel": (0.60, 0.62, 0.64), "Strap": (0.04, 0.05, 0.06), "Ring": (0.80, 0.80, 0.80),
              "Silhouette": (0.008, 0.009, 0.011), "CRT_Body": (0.62, 0.57, 0.48), "TVStand": (0.69, 0.58, 0.42),
              "Glass_Dark": (0.015, 0.02, 0.025), "Rug": (0.80, 0.72, 0.56), "Sofa_Small": (0.55, 0.12, 0.026),
              "Blanket_G": (0.028, 0.27, 0.20), "Remote": (0.012, 0.012, 0.012), "Shelf_W": (0.53, 0.24, 0.08),
              "Pot": (0.32, 0.15, 0.06), "Plant": (0.14, 0.40, 0.08), "LampBlack": (0.024, 0.024, 0.024),
              "LampShade_Off": (1.0, 0.87, 0.69), "Book": (0.10, 0.18, 0.38), "Device": (0.02, 0.02, 0.02)}
    EMISSIVE = {"Emit_Cold": ((0.90, 0.95, 1.00), 2.0), "Emit_Ad1b": ((0.90, 0.42, 0.30), 0.35),
                "Emit_Ad2b": ((0.30, 0.58, 0.90), 0.35), "Emit_Ad3b": ((0.95, 0.85, 0.40), 0.35)}

    def get_material(name, color):
        path = "{}/Materials/M_{}".format(ROOT, name)
        if lib.does_asset_exist(path):
            return lib.load_asset(path)
        mat = tools.create_asset("M_" + name, ROOT + "/Materials", unreal.Material, unreal.MaterialFactoryNew())
        c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
        c.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
        mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
        r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
        r.set_editor_property("r", 0.8)
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        mel.recompile_material(mat); lib.save_asset(path)
        return mat
    def get_emissive(name, color, s):
        path = "{}/Materials/M_{}".format(ROOT, name)
        if lib.does_asset_exist(path):
            return lib.load_asset(path)
        mat = tools.create_asset("M_" + name, ROOT + "/Materials", unreal.Material, unreal.MaterialFactoryNew())
        b = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
        b.set_editor_property("constant", unreal.LinearColor(color[0] * .3, color[1] * .3, color[2] * .3, 1.0))
        mel.connect_material_property(b, "", unreal.MaterialProperty.MP_BASE_COLOR)
        e = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 200)
        e.set_editor_property("constant", unreal.LinearColor(color[0] * s, color[1] * s, color[2] * s, 1.0))
        mel.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(mat); lib.save_asset(path)
        return mat
    mats = {k: get_material(k, v) for k, v in COLORS.items()}
    mats.update({k: get_emissive(k, c, s) for k, (c, s) in EMISSIVE.items()})

    def label(a, name, folder):
        a.set_actor_label(PREFIX + name)
        a.set_folder_path("Exhibition/" + folder)
        a.set_editor_property("tags", [unreal.Name(name), unreal.Name("EX")])
    def box(name, x0, x1, y0, y1, z0, z1, col, folder="Structure"):
        a = actors.spawn_actor_from_object(CUBE, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, F + (z0 + z1) / 2.0))
        a.set_actor_scale3d(unreal.Vector(abs(x1 - x0) / 100.0, abs(y1 - y0) / 100.0, abs(z1 - z0) / 100.0))
        a.static_mesh_component.set_material(0, mats[col])
        label(a, name, folder)
        return a
    def ceiling(name, x0, x1, y0, y1, z, col):
        # 아래를 보는 한 면짜리 판: 안에서는 천장, 천장 CCTV(위)에서는 투명
        a = actors.spawn_actor_from_object(PLANE, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, F + z), unreal.Rotator(roll=180.0, pitch=0.0, yaw=0.0))
        a.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, 1.0))
        a.static_mesh_component.set_material(0, mats[col])
        label(a, name, "Structure")
    def light(name, x, y, z, kelvin, lumens, radius=350.0):
        a = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, F + z))
        c = a.get_editor_property("light_component")
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
        c.set_intensity(float(lumens)); c.set_editor_property("use_temperature", True)
        c.set_editor_property("temperature", float(kelvin)); c.set_editor_property("attenuation_radius", radius)
        label(a, name, "Lights")
    def camera(name, x, y, z, pitch, yaw, focal):
        a = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(x, y, F + z), unreal.Rotator(roll=0.0, pitch=float(pitch), yaw=float(yaw)))
        cc = a.get_cine_camera_component()
        cc.set_editor_property("current_focal_length", float(focal))
        ps = cc.get_editor_property("post_process_settings")
        for k, v in [("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_apply_physical_camera_exposure", False), ("auto_exposure_bias", 0.0)]:
            ps.set_editor_property("override_" + k, True); ps.set_editor_property(k, v)
        cc.set_editor_property("post_process_settings", ps)
        label(a, name, "Cameras")

    # ---- 1. 지킬 액터(블루프린트 참조) / 지울 액터 ----
    KEEP = {"PointLight_1", "PointLight_2", "MediaPlate_1", "StaticMeshActor_27", "CineCameraActor_0", "CineCameraActor_1"}
    KEEP_LABEL = {"EX_PostProcess", "EX_PlayerStart", "EX_WalkCam"}
    keep, removed = {}, []
    for a in list(actors.get_all_level_actors()):
        n, l = a.get_name(), a.get_actor_label()
        if n in KEEP:
            keep[n] = a; continue
        if l in KEEP_LABEL:
            keep[l] = a; continue
        if l.startswith(PREFIX):
            removed.append(l); actors.destroy_actor(a)
    P("지킴:", sorted((k, v.get_actor_label()) for k, v in keep.items()))
    P("지움", len(removed), "개:", removed)
    missing = KEEP - set(keep)
    if missing:
        P("!! 블루프린트 참조 액터가 없음:", missing)

    # ---- 2. 바닥 · 벽 · 천장 ----
    H = 240
    box("Ground", -500, 800, -500, 800, -10, -5, "Ground")
    box("Floor_Subway", 0, 300, 0, 72, -4, 0, "S_Floor")
    box("Floor_Home", 0, 300, 72, 300, -4, 0, "H_Wood")
    box("Wall_Top", -10, 310, -5, 0, 0, H, "S_Wall")
    box("Wall_Left_Subway", -5, 0, 0, 77, 0, H, "S_Wall")
    box("Wall_Right_Subway", 300, 305, 0, 77, 0, H, "S_Wall")
    box("Wall_Left_Home", -5, 0, 77, 300, 0, H, "H_Cream")
    box("Wall_Right_Home", 300, 305, 77, 300, 0, H, "H_Cream")
    box("Wall_Bottom_0", -5, 10, 300, 305, 0, H, "H_Cream")            # 출구 X 10~90
    box("Wall_Bottom_1", 90, 305, 300, 305, 0, H, "H_Cream")
    box("Wall_Bottom_ExitHeader", 10, 90, 300, 305, 200, H, "H_Cream")
    box("Partition_1", 0, 190, 72, 82, 0, H, "H_Cream")                  # 가벽: 판 + 문 X 190~270 + 판
    box("Partition_2", 270, 300, 72, 82, 0, H, "H_Cream")
    box("Partition_DoorHeader", 190, 270, 72, 82, 200, H, "H_Cream")
    box("Partition_Face_1", 0, 190, 71.6, 72, 0, H, "S_Wall")            # 지하철 쪽 면은 회색
    box("Partition_Face_2", 270, 300, 71.6, 72, 0, H, "S_Wall")
    ceiling("Ceiling_Subway", 0, 300, 0, 72, 215, "S_Ceiling")
    ceiling("Ceiling_Home", 0, 300, 82, 300, 240, "H_Ceiling")
    # 문: 열린 상태로 (가벽 문은 집 쪽, 경첩 오른쪽 X 270 / 출구 문은 바깥쪽, 경첩 X 90)
    box("Door_Partition", 266, 270, 82, 162, 0, 200, "Door")
    box("Door_Exit", 86, 90, 305, 385, 0, 200, "ExitDoor")

    # ---- 3. 지하철 칸 (Y 0~72) ----
    box("Sub_LED", 20, 280, 32, 40, 209, 212, "Emit_Cold", "Subway")
    for j, y in enumerate([23, 60]):
        box("Sub_Rail_%d" % j, 10, 290, y - 1.3, y + 1.3, 193.7, 196.3, "Steel", "Subway")
        for i in range(7):
            x = 35 + i * 38.5
            box("Sub_Strap_%d_%d" % (j, i), x - 1.1, x + 1.1, y - .5, y + .5, 180, 195, "Strap", "Subway")
            box("Sub_Ring_%d_%d" % (j, i), x - 4.5, x + 4.5, y - .9, y + .9, 171.5, 180.5, "Ring", "Subway")
    for i in range(5):
        x = 32 + i * 59
        box("Sub_Ad_%d" % i, x - 23, x + 23, 0, 1.2, 157, 187, ["Emit_Ad1b", "Emit_Ad2b", "Emit_Ad3b"][i % 3], "Subway")
    for k, (x, y, s) in enumerate([(55, 10, 1.0), (145, 12, 1.06), (250, 10, 1.0)]):
        b = lambda n, x0, x1, z0, z1: box("Sub_Person_%s_%d" % (n, k), x + x0 * s, x + x1 * s, y - 1, y + 1, z0 * s, z1 * s, "Silhouette", "Subway")
        b("Body", -21, 21, 0, 140); b("Neck", -7.5, 7.5, 140, 148); b("Head", -11, 11, 147, 169)

    # ---- 4. 집 (Y 82~300) ----
    box("TV_Stand", 26, 71, 156, 216, 0, 50, "TVStand", "Home")
    box("TV_CRT_Body", 26, 68, 163, 209, 50, 88, "CRT_Body", "Home")
    box("TV_CRT_Glass", 67.5, 70.5, 166, 206, 53, 85, "Glass_Dark", "Home")
    box("TV_Antenna_1", 44, 46, 177, 179, 88, 122, "Steel", "Home")
    box("TV_Antenna_2", 44, 46, 193, 195, 88, 122, "Steel", "Home")
    box("Rug", 89, 191, 142.5, 249.5, 0, 1.2, "Rug", "Home")
    box("Sofa_Seat", 200, 255, 175.5, 254.5, 0, 42, "Sofa_Small", "Home")       # 작은 소파 폭 101 · 깊이 67, TV(왼쪽)를 봄
    box("Sofa_Back", 251, 267, 164.5, 265.5, 0, 85, "Sofa_Small", "Home")
    box("Sofa_Arm_1", 200, 255, 164, 177, 0, 60, "Sofa_Small", "Home")
    box("Sofa_Arm_2", 200, 255, 252, 265, 0, 60, "Sofa_Small", "Home")
    box("Blanket", 208.5, 241.5, 219.5, 252.5, 42, 48, "Blanket_G", "Home")
    box("Remote", 225.5, 230.5, 162, 178, 60, 62.5, "Remote", "Home")
    for k, (x, y) in enumerate([(48, 94), (282, 286)]):
        box("Lamp_Base_%d" % (k + 1), x - 12, x + 12, y - 12, y + 12, 0, 3, "LampBlack", "Home")
        box("Lamp_Pole_%d" % (k + 1), x - 1.2, x + 1.2, y - 1.2, y + 1.2, 3, 133, "LampBlack", "Home")
        box("Lamp_Shade_%d" % (k + 1), x - 14, x + 14, y - 14, y + 14, 130, 156, "LampShade_Off", "Home")
    box("Plant_Pot", 73, 99, 82, 106, 0, 30, "Pot", "Home")
    box("Plant_Leaf", 68, 104, 84, 112, 32, 72, "Plant", "Home")
    box("Shelf", 103, 159, 83, 111, 0, 80, "Shelf_W", "Home")
    box("Shelf_Item_1", 144, 156, 90, 100, 80, 94, "Device", "Home")
    box("Shelf_Item_2", 106, 124, 95, 99, 80, 102, "Book", "Home")
    box("QR_Screen", 102, 138, 297, 300, 116, 144, "Glass_Dark", "Home")       # 출구 옆 QR 화면
    box("CCTV_Dome", 145, 155, 186, 196, 230, 236, "Device", "Home")

    # ---- 5. 조명 · 카메라 (새로) ----
    light("Light_A_Cold_1", 90, 36, 205, 6500, 2)
    light("Light_A_Cold_2", 220, 36, 205, 6500, 2)
    camera("Cam_A_Subway", 8, 40, 158, -4, 0, 13)
    camera("Cam_B_Door", 232, 96, 165, -18, 120, 12)
    camera("Cam_B_OverSofa", 262, 215, 150, -14, 180, 15)

    # ---- 6. 블루프린트가 쓰는 액터 옮기기 ----
    def move(n, x, y, z=None, rot=None):
        a = keep.get(n)
        if not a:
            P("  옮기기 실패(없음):", n); return
        l = a.get_actor_location()
        a.set_actor_location(unreal.Vector(x, y, l.z if z is None else z), False, False)
        if rot is not None:
            a.set_actor_rotation(rot, False)
        P("  옮김:", n, a.get_actor_label(), "→", round(x), round(y), round(l.z if z is None else z))
    for n, (x, y) in [("PointLight_1", (48, 94)), ("PointLight_2", (282, 286))]:      # 스탠드 2개 = 3500K 웜
        move(n, x, y, F + 143)
        c = keep[n].get_editor_property("light_component") if n in keep else None
        if c:
            c.set_editor_property("use_temperature", True); c.set_editor_property("temperature", 3500.0)
    if "MediaPlate_1" in keep:                                                     # 브라운관 유리 안 (오른쪽을 봄)
        mp = keep["MediaPlate_1"]
        move("MediaPlate_1", 71.0, 186.0, F + 69.0, unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
        mp.set_actor_scale3d(unreal.Vector(1.0, 0.34, 0.34 * 9 / 16))
    vis = keep.get("StaticMeshActor_27")
    if vis:
        move("StaticMeshActor_27", 20, 36)                                          # 형체: 지하철 칸 입구 쪽
    eye = keep.get("CineCameraActor_0")
    if eye and vis and eye.get_attach_parent_actor() != vis:
        vl = vis.get_actor_location(); move("CineCameraActor_0", vl.x, vl.y)
    if "EX_PlayerStart" in keep:
        move("EX_PlayerStart", 20, 36, 90, unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))

    els.save_map(world, "/Game/Exhibition/Maps/L_Current")
    P("저장 완료")
except Exception:
    P("오류:\n" + traceback.format_exc())
open(OUT, "w").write("\n".join(log))
