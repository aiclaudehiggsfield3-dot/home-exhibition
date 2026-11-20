import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import unreal, traceback
O=SV_+'pie1119.txt'
def pie(tag):
    try:
        les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        gw=ues.get_game_world()
        open(O,'a').write(f"{tag}: in_pie={les.is_in_play_in_editor()} game_world={gw.get_name() if gw else None}\n")
    except Exception:
        open(O,'a').write(tag+' ERR '+traceback.format_exc()[-300:]+'\n')
