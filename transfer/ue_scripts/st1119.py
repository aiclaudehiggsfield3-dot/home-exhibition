import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import unreal, traceback
OUT=SV_+'st1119.txt'
def st(tag):
    try:
        w=unreal.EditorLevelLibrary.get_game_world()
        if not w:
            open(OUT,'a').write(tag+': no game world\n'); return
        A={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)}
        fire=A['EX_Snd_Fire'].get_editor_property('audio_component'); sub=A['EX_Snd_Subway'].get_editor_property('audio_component')
        mp=A['EX_Screen_B_Home'].get_editor_property('media_plate_component').get_media_player()
        qr=A['EX_QR_Screen'].get_component_by_class(unreal.StaticMeshComponent).get_material(0)
        show=qr.get_scalar_parameter_value('Show') if isinstance(qr,unreal.MaterialInstanceDynamic) else '-'
        v=A['EX_Visitor']; l=v.get_actor_location()
        s=(f"{tag}: fire={fire.is_playing()} subway={sub.is_playing()} tv_url={mp.get_url().split('/')[-1] if mp else None} tv_idx={mp.get_playlist_index() if mp else None} "
           f"qr={qr.get_name()} show={show} light1={'OFF' if A['EX_Light_B_Warm_1'].get_editor_property('hidden') else 'ON'} "
           f"visitor={'hidden' if v.get_editor_property('hidden') else 'shown'}@({l.x:.0f},{l.y:.0f})")
        open(OUT,'a').write(s+'\n')
    except Exception:
        open(OUT,'a').write(tag+' ERR '+traceback.format_exc()+'\n')
open(OUT,'a').write('--- loaded\n')
