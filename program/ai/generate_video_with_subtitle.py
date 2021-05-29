
command = f"ffmpeg -i {video_path} " \
          f"-filter_complex " \
          f"\"subtitles=x.srt:" \
          f"force_style='Fontname=Arial,Borderstyle=4,Fontsize=16,BackColour=&H80000000,Bold=1,Italic=1'\" " \
          f"{rendered_video_path}"
