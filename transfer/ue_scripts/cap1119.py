import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
# 관객 눈 카메라 미리보기: 몇 자리에서 EX_VisitorEye와 같은 렌즈로 찍어 PNG로 (플레이 없이)
import unreal, traceback, math
SV=SV_+''
L=[]
try:
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    by={a.get_actor_label():a for a in sub.get_all_level_actors()}
    eye=by['EX_VisitorEye']; c=eye.get_cine_camera_component()
    v=by['EX_Visitor']; vloc0=v.get_actor_location(); vrot0=v.get_actor_rotation()
    W,H=540,720                                   # 반쪽 화면 비율 (세로로 김)
    hfov=2*math.degrees(math.atan(c.filmback.sensor_width/2/c.current_focal_length))
    rt=unreal.RenderingLibrary.create_render_target2d(world,W,H,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=sub.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(0,0,0))
    cc=cap.get_editor_property('capture_component2d')
    cc.set_editor_property('texture_target',rt); cc.set_editor_property('fov_angle',hfov)
    cc.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property('capture_every_frame',False)
    cc.set_editor_property('post_process_settings',c.get_editor_property('post_process_settings')); cc.set_editor_property('post_process_blend_weight',1.0)
    shots=[('1_subway',(40,40),0),('2_subway_walk',(150,45),0),('3_to_door',(230,40),90),('4_home_in',(230,120),90),
           ('5_to_sofa',(230,140),90),('6_sofa_tv',(232,215),180),('7_to_exit',(120,250),180),('8_exit',(50,275),135)]
    for name,(x,y),yaw in shots:
        v.set_actor_location(unreal.Vector(x,y,85),False,True)
        v.set_actor_rotation(unreal.Rotator(roll=0.0,pitch=0.0,yaw=float(yaw)),True)
        cap.set_actor_location(eye.get_actor_location(),False,True); cap.set_actor_rotation(eye.get_actor_rotation(),True)
        cc.capture_scene()
        unreal.RenderingLibrary.export_render_target(world,rt,SV+'eyecam','v2_'+name+'.png')
        L.append(f"{name} eye={eye.get_actor_location()} yaw={yaw}")
    v.set_actor_location(vloc0,False,True); v.set_actor_rotation(vrot0,True)
    sub.destroy_actor(cap)
    L.append(f"hfov={hfov:.1f}")
except Exception:
    L.append(traceback.format_exc())
open(SV+'cap1119.txt','w').write('\n'.join(map(str,L)))
