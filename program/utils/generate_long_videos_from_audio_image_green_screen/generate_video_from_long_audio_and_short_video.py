import os
import sys
import glob

from program.utils.file_utils.get_file_size import is_file_broken_size


def render_video(video_path, audio_path):
    video_output_name = audio_path.replace(".mp3", ".mp4")

    video_cmd = f"ffmpeg -stream_loop -1 -i \"{video_path}\" -i \"{audio_path}\" -t 09:59:59.6 \
                  -map 0:v:0 -map 1:a -y -c:v h264_nvenc -qmin 40 -qmax 40  \
                  -filter_complex \"scale=1920:-1080\" \
                  \"{video_output_name}\""
    os.system(video_cmd)

    # check file to see if was converted ok
    if is_file_broken_size(video_output_name):
        os.remove(video_output_name)
        return


def start():
    arguments = sys.argv[1:]

    # load videos
    videos_dir_path = f"{arguments[0]}"
    list_of_video_files = glob.glob(os.path.join(videos_dir_path, '*.mp4'))

    # load audio files
    audio_dir_path = f"{arguments[1]}"
    list_of_audio_files = glob.glob(os.path.join(audio_dir_path, '*.mp3'))

    # # Loops over every audio mp3
    for index, video_path in enumerate(list_of_video_files):
        try:
            render_video(video_path, list_of_audio_files[index])
        except Exception as e:
            print(e)
            pass


start()
