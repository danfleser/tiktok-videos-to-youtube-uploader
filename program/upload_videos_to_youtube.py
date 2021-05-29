import os
import sys
import glob

from program.utils.libs.upload_youtube_selenium import YouTubeUploader


def start():
    # load video and json metadata
    videos_dir_path = f"{sys.argv[1:][0]}"
    list_of_video_files = glob.glob(os.path.join(videos_dir_path, '*.mp4'))

    cookie_dir = sys.argv[1:][1]
    youtube_uploader = YouTubeUploader(True, cookie_dir)

    # Loops over every tiktok
    for index, video_path in enumerate(list_of_video_files):
        try:
            # upload to youtube
            metadata_path = video_path.replace(".mp4", ".json")
            uploaded = youtube_uploader.upload(video_path, metadata_path)

            if not uploaded:
                break

            # remove file from disk
            os.remove(video_path)
            os.remove(metadata_path)
        except:
            break

    try:
        youtube_uploader.quit()
    except:
        pass


start()
