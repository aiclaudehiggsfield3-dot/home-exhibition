# walk_one.py — Saved/one.txt 에 적힌 레벨만 워크스루 렌더 (쉼표로 여러 개)
import unreal, re
keys=[k.strip() for k in open(unreal.Paths.project_saved_dir()+'one.txt').read().split(',') if k.strip()]
src=open(unreal.Paths.project_dir()+'Scripts/make_walkthrough.py',encoding='utf-8').read()
src=re.sub(r'^LAYOUTS = \[.*?\]', 'LAYOUTS = %r' % keys, src, count=1, flags=re.M)
exec(compile(src,'make_walkthrough','exec'),{'__name__':'__main__'})
