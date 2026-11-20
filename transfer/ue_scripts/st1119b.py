import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import unreal, traceback
OUT2=SV_+'st1119b.txt'
def st2(tag):
    try:
        w=unreal.EditorLevelLibrary.get_game_world()
        if not w:
            open(OUT2,'a').write(tag+': no game world\n'); return
        A={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)}
        def ac(n): return A[n].get_editor_property('audio_component')
        f,s,t=ac('EX_Snd_Fire'),ac('EX_Snd_Subway'),ac('EX_Snd_TV')
        mp=A['EX_Screen_B_Home'].get_editor_property('media_plate_component').get_media_player()
        tvv=(mp.is_playing(), (mp.get_url() or '').split('/')[-1]) if mp else None
        v=A['EX_Visitor']; l=v.get_actor_location(); r=v.get_actor_rotation()
        line=(f"{tag}: subway={s.is_playing()} tv_snd={t.is_playing()} vol={t.get_editor_property('volume_multiplier'):.2f} "
              f"fire={f.is_playing()} vol={f.get_editor_property('volume_multiplier'):.2f} "
              f"tv_video={tvv} light={'OFF' if A['EX_Light_B_Warm_1'].get_editor_property('hidden') else 'ON'} visitor=({l.x:.0f},{l.y:.0f}) yaw={r.yaw:.0f}")
        open(OUT2,'a').write(line+'\n')
    except Exception:
        open(OUT2,'a').write(tag+' ERR '+traceback.format_exc()[-400:]+'\n')
open(OUT2,'w').write('--- loaded v7\n')
