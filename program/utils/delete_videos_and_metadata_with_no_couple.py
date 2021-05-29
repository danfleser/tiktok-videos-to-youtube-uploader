import os
import sys
import glob


def delete_videos_and_metadata_with_no_couple():
    # load videos dir path
    videos_dir_path = f"{sys.argv[1:][0]}"

    # Loops over every json metadata  file
    list_of_json_files = glob.glob(os.path.join(videos_dir_path, '*.json'))
    for index, json_path in enumerate(list_of_json_files):
        path = json_path.replace(".json", ".mp4")

        # if json does not have video, delete it
        if not os.path.exists(path):
            os.remove(json_path)

    # Loops over every video file
    list_of_video_files = glob.glob(os.path.join(videos_dir_path, '*.mp4'))
    for index, video_path in enumerate(list_of_video_files):
        path = video_path.replace(".mp4", ".json")

        # if video does not have json metadata, delete it
        if not os.path.exists(path):
            os.remove(video_path)


delete_videos_and_metadata_with_no_couple()
