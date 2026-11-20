import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import unreal, traceback
L=[]
try:
    P='/Game/Exhibition/Media/PL_NOW'
    if unreal.EditorAssetLibrary.does_asset_exist(P):
        pl=unreal.load_asset(P)
    else:
        pl=unreal.AssetToolsHelpers.get_asset_tools().create_asset('PL_NOW','/Game/Exhibition/Media',unreal.MediaPlaylist,None)
    src=unreal.load_asset('/Game/Exhibition/Media/PL_TV').get(0)
    while pl.num()>0: pl.remove_at(0)
    pl.add(src)
    L.append('PL_NOW n=%d item=%s'%(pl.num(),pl.get(0).get_name()))
    L.append('save PL_NOW='+str(unreal.EditorAssetLibrary.save_asset(P,only_if_is_dirty=False)))
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    A={a.get_actor_label():a for a in sub.get_all_level_actors()}
    mpc=A['EX_Screen_B_Home'].get_editor_property('media_plate_component')
    mpc.set_editor_property('media_playlist',pl)
    L.append('plate playlist='+mpc.get_editor_property('media_playlist').get_path_name()+' loop='+str(mpc.get_editor_property('loop')))
    L.append('save level='+str(unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)))
except Exception:
    L.append(traceback.format_exc())
open(SV_+'pl1120.txt','w').write('\n'.join(L))
