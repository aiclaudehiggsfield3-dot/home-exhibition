# rebuild_one.py — Saved/one.txt 에 적힌 레벨만 다시 짓기 (쉼표로 여러 개: Opt5A,Opt5B)
import unreal, re
keys=[k.strip() for k in open(unreal.Paths.project_saved_dir()+'one.txt').read().split(',') if k.strip()]
src=open(unreal.Paths.project_dir()+'Scripts/build_layouts.py',encoding='utf-8').read()
src=re.sub(r'^BUILD = \[.*?\]', 'BUILD = %r' % keys, src, count=1, flags=re.M)
src=re.sub(r'^OPEN_AFTER = ".*?"', 'OPEN_AFTER = "%s"' % keys[0], src, count=1, flags=re.M)
exec(compile(src,'build_layouts','exec'),{'__name__':'__main__'})
