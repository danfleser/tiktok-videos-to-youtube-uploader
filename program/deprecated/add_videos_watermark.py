import io
import json
import os
import sys
import glob
from pathlib import Path

from program.utils.file_utils.get_file_size import is_file_broken_size


def add_watermark(video_path, metadata_path, metadata):
    watermark_path = os.path.join(Path(__file__).parent, '../utils', 'check_desc.png')
    idx = video_path.index(".mp4")

    # make video 1 minute
    long_video_name = video_path[:idx] + 'long' + video_path[idx:]
    extend_video_cmd = f"ffmpeg -stream_loop 60 -i {video_path} -t 00:00:59.6 {long_video_name} > nul 2>&1"
    os.system(extend_video_cmd)
    # check file to see if was converted ok
    if is_file_broken_size(long_video_name):
        os.remove(long_video_name)
        return
    # remove original video as we don't need it anymore, because we have long video
    os.remove(video_path)

    # add watermark
    video_with_watermark = video_path[:idx] + 'marked' + video_path[idx:]
    scrape_cmd = f"ffmpeg -i {long_video_name} \
                    -i {watermark_path} \
                    -c:v h264_nvenc -qmin 30 -qmax 30 -y \
                    -filter_complex \"pad=height=ih:color=#191919,overlay=0:0,scale=1080:-1\" \
                    {video_with_watermark} > nul 2>&1"
    os.system(scrape_cmd)
    # check file to see if was converted ok
    if is_file_broken_size(video_with_watermark):
        os.remove(video_with_watermark)
        return
    # remove long video as we don't need it anymore, because we have watermarked video
    os.remove(long_video_name)

    # rename file to original name
    os.rename(video_with_watermark, video_path)

    # save metadata file
    metadata['isProcessed'] = True
    with io.open(metadata_path, 'w', encoding="utf-8") as metadataFile:
        json.dump(metadata, metadataFile, ensure_ascii=False, indent=4)


def start():
    arguments = sys.argv[1:]
    # load videos
    videos_dir_path = f"{arguments[0]}"
    list_of_video_files = glob.glob(os.path.join(videos_dir_path, '*.mp4'))

    # Loops over every tiktok
    for index, video_path in enumerate(list_of_video_files):
        try:
            # read metadata fle
            metadata_path = video_path.replace('.mp4', '.json')
            with io.open(metadata_path, encoding="utf-8") as json_file:
                metadata = json.load(json_file)

            if 'isProcessed' not in metadata or not metadata['isProcessed']:
                add_watermark(video_path, metadata_path, metadata)
        except Exception as e:
            print(e)
            pass


start()
