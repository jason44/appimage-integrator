import sys
from pathlib import Path
import os
import shutil
import magic
import io
import ctypes as ct

desktop = Path(os.path.expanduser('~')) / 'Desktop'

def get_clib():
	if not Path.exists(Path('./libwrapperc.so')):
		os.system('gcc -c wrapper.c')
		os.system('gcc -shared wrapper.o -lappimage -o libwrapperc.so')
	thumbnailer = ct.cdll.LoadLibrary('./libwrapperc.so')
	return thumbnailer 

def is_appimage(file):
	with open(file, 'rb') as f:
		f.seek(0x8)
		t = f.read(0x2)
		if t == b'AI':
			return True
		else:
			return False

def exec_integration():
	arg = sys.argv[1]
	if arg is None:
		print('missing argument: appimage or directory containing appimages')
		exit()

	appimage_dir = desktop / '.appimages'
	thumbnail_dir = appimage_dir / 'thumbnails'
	req_dirs = [desktop, appimage_dir, thumbnail_dir]
	for _dir in req_dirs:
		if not Path.is_dir(_dir):
			Path.mkdir(_dir)
			print(f"created {_dir}")
		
	arg = Path(arg)
	if Path.is_file(arg):
		integrate_app(arg, appimage_dir)
	elif Path.is_dir(arg):
		integrate_apps(arg, appimage_dir)
	else:
		#integrate_symlink(arg, appimage_dir)
		pass

def create_desktop_file(app, thumbnail_dir):
	libwrapper = get_clib()
	src = ct.c_char_p(bytes(app))
	if not libwrapper.register_appimage(src):
		print(f"failed to register {app}")
		exit()
	print(f"{app} is registered")
	# .DirIcon is a png according to AppImage documentation
	dest = ct.c_char_p(bytes(thumbnail_dir.as_posix() + '/' + app.stem + '.png', 'utf-8'))
	libwrapper.extract_icon(src, dest)
	libwrapper.extract_desktop_file(src, ct.c_char_p(bytes(desktop)))
	print(f"created .desktop file for {app} in {desktop}")
	
def integrate_app(app, appimage_dir):
	app_path = Path.absolute(app)
	shutil.copy(app_path, appimage_dir)	
	new_app_path = appimage_dir / app.name
	os.system(f"chmod +x {new_app_path}")
	print(f"moved {app.name} to {appimage_dir}")
	# pass in the new appimage, not the original appimage
	create_desktop_file(new_app_path, appimage_dir / 'thumbnails')

def integrate_apps(apps, appimage_dir):
	for app in Path.iterdir(apps):
		if Path.is_file(app):
			if is_appimage(app):
				shutil.copy(app, appimage_dir)	
				print(f"moved {app.name} to {appimage_dir}")

if __name__ == "__main__":
	exec_integration()
