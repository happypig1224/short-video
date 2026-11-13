import subprocess, glob, os

files = sorted(glob.glob(r'c:\Users\33046\Desktop\short video\rendered_clips\*.mp4'))
for f in files:
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,r_frame_rate,codec_name:format=duration,size', '-of', 'default=noprint_wrappers=1', f]).decode()
    print('===', os.path.basename(f), '===')
    print(out.strip())
