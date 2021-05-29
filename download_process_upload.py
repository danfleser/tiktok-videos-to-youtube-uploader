import glob
import math
import multiprocessing
import os
import random
from pathlib import Path
from joblib import Parallel, delayed

from program.utils.file_utils.json_file_reader import load_json_file

tiktokHashtags = {
    'addisonrae': 0,
    'jamescharles': 0,
    'charlidamelio': 0,
    'dixiedamelio': 0,
    'cheater': 0,
    'cheating': 0,
    'girlfriend': 0,
    'hollywood': 0,
    'hollywoodlife': 0,
    'hollywoodstudios': 0,
    'hollywoodfix': 0,
    'lasvegas': 0,
    'lasvegasfood': 0,
    'news': 0,
    'wow': 0,
    'insta': 0,
    'instagram': 0,
    'facebook': 0,
    'twitter': 0,
    'reddit': 0,
    'crazy': 0,
    'cardib': 0,
    'drake': 0,
    'daviddobrik': 0,
    'sad': 0,
    'happy': 0,
    'sports': 0,
    'reno': 0,
    'DIY': 0,
    'skincare': 0,
    'cooking': 0,
    'hacks': 0,
    'advice': 0,
    'Pranks': 0,
    'Fitness': 0,
    'Home': 0,
    'Beauty': 0,
    'Fashion': 0,
    'Recipes': 0,
    'Life': 0,
    'Outdoors': 0,
}

currentDir = Path.cwd()
accountsDir = os.path.join(currentDir, 'accounts')
downloads_directory_path = os.path.join(currentDir, f'downloads')
path_to_history_dir = os.path.join(currentDir, f'scrapedVideosHistory')
path_to_history_json_file = os.path.join(path_to_history_dir, 'tiktok_history.json')

account_hashtags = {}
HOW_MANY_VIDEOS_TO_UPLOAD = 50


def get_hashtag_already_downloaded_history_count(hashtag):
    try:
        history_data = load_json_file(path_to_history_json_file)
        hashtag_info = history_data[f'hashtag_{hashtag}']

        if hashtag_info:
            arr = load_json_file(hashtag_info['file_location'])
            return len(arr) + 1
    except:
        return 0


def get_directory_videos_count(directory):
    if not os.path.exists(directory):
        return 0

    return len(glob.glob1(directory, "*.mp4"))


def get_scrape_count(hashtag, already_downloaded_videos_count):
    history_count = get_hashtag_already_downloaded_history_count(hashtag)
    return history_count + (HOW_MANY_VIDEOS_TO_UPLOAD - already_downloaded_videos_count)


def remove_unwatched_videos(account):
    remove_unwatched_cmd = f"python -m program.remove_youtube_unwatched_videos {account['account_path']}"
    os.system(remove_unwatched_cmd)


def remove_copyrighted_videos(account):
    remove_unwatched_cmd = f"python -m program.remove_youtube_copyrighted_videos {account['account_path']}"
    os.system(remove_unwatched_cmd)


def bulk_comments_reply(account):
    remove_unwatched_cmd = f"python -m program.bulk_comment_reply_youtube_channel {account['account_path']}"
    os.system(remove_unwatched_cmd)


def clean_directory(account):
    # clean directory of files with no couples(only .mp4/ only .json)
    clean_dir_cmd = f"python -m program.utils.delete_videos_and_metadata_with_no_couple \
                       {account['hashtag_videos_directory_path']}"
    os.system(clean_dir_cmd)


def download_videos(account):
    while account['already_downloaded_videos_count'] < HOW_MANY_VIDEOS_TO_UPLOAD and account['download_tries'] < account['download_max_tries']:
        scrape_cmd = f"tiktok-scraper hashtag {account['hashtag']} \
                        -n {account['scrape_videos_count']} \
                        -d \
                        --filepath {downloads_directory_path} \
                        -t json \
                        --historypath {path_to_history_dir} \
                        -s \
                        --session sid_tt=asdasd13123123123adasda \
                        > nul 2>&1"  # do not print anything to console
        os.system(scrape_cmd)

        # when we already downloaded ${scrape_videos_no}
        # tiktok-scraper does not save anything, and we need to increase the ${scrape_videos_no} number
        json_metadata_file = [filename for filename in os.listdir(account['hashtag_videos_directory_path']) if
                              filename.startswith(account['hashtag'])]
        if len(json_metadata_file) > 0:
            json_metadata_file_path = os.path.join(account['hashtag_videos_directory_path'], json_metadata_file[0])

            gen_metadata = f"python -m program.generate_videos_json_metadata \
                                {account['hashtag_videos_directory_path']} \
                                {json_metadata_file_path}"
            os.system(gen_metadata)

            os.remove(json_metadata_file_path)

        account['download_tries'] += 1
        # check if we have more videos to scrape
        account['already_downloaded_videos_count'] =\
            get_directory_videos_count(account['hashtag_videos_directory_path'])
        account['scrape_videos_count'] =\
            get_scrape_count(account['hashtag'], account['already_downloaded_videos_count'])\
            + account['download_tries']*20  # videos have too many banned words and we increase scrape_videos_count

    print(f"{account['account_name']}- {account['hashtag']}- TRIES {account['download_tries']}")
    if account['download_tries'] > account['download_max_tries']:
        clean_directory(account)
        init_account(account, account['account_name'])
        download_videos(account)
        print(f"REASSIGNED: {account['account_name']}- {account['hashtag']}- TRIES {account['download_tries']}")


def upload_videos(account):
    start_number_of_videos = len(glob.glob(os.path.join(account['hashtag_videos_directory_path'], '*.mp4')))
    upload_cmd = f"python -m program.upload_videos_to_youtube \
                    {account['hashtag_videos_directory_path']} \
                    {account['account_path']}"  # do not print anything to console
    os.system(upload_cmd)
    end_number_of_videos = len(glob.glob(os.path.join(account['hashtag_videos_directory_path'], '*.mp4')))
    total_number_of_uploaded_videos = start_number_of_videos - end_number_of_videos
    print(f"{account['account_name']}- {account['hashtag']}\
            -UP {total_number_of_uploaded_videos} FROM {start_number_of_videos}")

    # tiktok downloader did not download any videos
    if start_number_of_videos == 0:
        clean_directory(account)
        init_account(account, account['account_name'])
        download_videos(account)
        upload_videos(account)


def init_account(account, account_name):
    hashtags_list = list(tiktokHashtags.keys())
    hashtag = random.choice(hashtags_list)

    while tiktokHashtags[hashtag] == 1:
        hashtag = random.choice(hashtags_list)
    tiktokHashtags[hashtag] = 1

    account['hashtag'] = hashtag
    account['download_tries'] = 0  # sometimes tiktok-scraper download loops forever because does not find videos
    account['download_max_tries'] = 10  # limit tiktok-scraper loop only "max_tries"
    account['upload_tries'] = 0
    account['upload_max_tries'] = 1
    account['hashtag_videos_directory_path'] = os.path.join(downloads_directory_path, f'#{account["hashtag"]}')
    account['account_name'] = account_name
    account['account_path'] = os.path.join(accountsDir, account_name)
    # number of videos already downloaded on the disk for this "hashtag"
    account['already_downloaded_videos_count'] = get_directory_videos_count(account['hashtag_videos_directory_path'])
    # number of videos from tiktok-scraper-history + (HOW_MANY_VIDEOS_TO_UPLOAD - already_downloaded_videos_count)
    account['scrape_videos_count'] = get_scrape_count(account['hashtag'], account['already_downloaded_videos_count'])


def set_account_hashtags_dict():
    for account_name in os.listdir(accountsDir):
        account_hashtags[account_name] = {}
        init_account(account_hashtags[account_name], account_name)


def start_parallel_download_upload():
    set_account_hashtags_dict()
    num_cores = multiprocessing.cpu_count()
    # num_cores = 1

    # clear screen
    os.system("cls")

    # delete odd month videos less than 100 views and even month videos less than 500
    # if datetime.datetime.today().day % 30 == 0:
    print('Started removing unwatched videos')
    Parallel(n_jobs=num_cores)(
        delayed(remove_unwatched_videos)(account) for account in list(account_hashtags.values())
    )
    print('Finished removing unwatched videos\n')

    print('Started cleaning')
    Parallel(n_jobs=num_cores)(
        delayed(clean_directory)(account) for account in list(account_hashtags.values())
    )
    print('Finished cleaning\n')
    
    print('Started downloading')
    Parallel(n_jobs=num_cores)(
        delayed(download_videos)(account) for account in list(account_hashtags.values())
    )
    print('Finished downloading\n')

    print('Started uploading')
    Parallel(n_jobs=num_cores)(
        delayed(upload_videos)(account) for account in list(account_hashtags.values())
    )
    print('Finished uploading')

    print('Started bulk comments reply')
    Parallel(n_jobs=num_cores)(
        delayed(bulk_comments_reply)(account) for account in list(account_hashtags.values())
    )
    print('Finished bulk comments reply\n')

    wait 3 hours to let youtube process uploaded videos to know that are copyrighted
    time.sleep(60 * 60 * 3)

    print('Started removing copyrighted videos')
    Parallel(n_jobs=num_cores)(
        delayed(remove_copyrighted_videos)(account) for account in list(account_hashtags.values())
    )
    print('Finished removing copyrighted videos\n')

    # kill firefox zombie processes if any
    os.system("taskkill /IM firefox.exe /F")


start_parallel_download_upload()
