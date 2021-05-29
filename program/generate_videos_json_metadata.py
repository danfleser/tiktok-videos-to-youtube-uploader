import os
import io
import json
import random
import re
import sys
from pathlib import Path

from program.utils.file_utils.json_file_reader import load_json_file
from program.utils.file_utils.json_file_writer import write_json_file

utils_dir_path = os.path.join(Path(__file__).parent, "utils")
banned_words = open(os.path.join(
    utils_dir_path, "banned_words_short.txt"), "r").readlines()


def check_banned_words(title):
    found = False

    for word in banned_words:
        if word.strip().lower() in title:
            found = True
            break

    return found


def save_video_metadata(tiktok, metadata_file_location):
    # set title
    title = tiktok['text']

    if check_banned_words(title.lower()):
        video_path = metadata_file_location
        video_path = video_path.replace(".json", ".mp4")
        os.remove(video_path)
        return

    # remove big empty spaces
    title = re.sub(' +', ' ', title).strip()

    # dan @dan boss #cox #mafiot => dan @dan boss
    first_hashtag_pos = title.find('#')
    title = title[0: first_hashtag_pos]

    # dan @dan boss => dan
    first_at_pos = title.find('@')
    title = title[0: first_at_pos]

    if title == "":
        nr = random.randint(1, 3)

        if nr == 1:
            title = "WELL THIS WAS FUNNY!!"
        if nr == 2:
            title = "IS THIS TRUE?!"
        if nr == 3:
            title = "IS THIS A MOTIVATIONAL VIDEO??!"

    # trim title to 100 chars, which youtube allows max
    check_description_text = ' See Description'
    trim_length = 95 - len(check_description_text)
    title = title[0:trim_length] if len(title) > trim_length else title
    title = title.strip() + check_description_text

    # uppercase
    title = title.upper()

    # set description
    video_desc = '\nBUY A FACE MASK https://amzn.to/3mSaJec' \
                 '\nBUY A PITTA MASK https://amzn.to/2WMc6k5' \
                 '\n' \
                 '\nBEST EDITING PC - A LOT OF VALUE FOR LITTLE MONEY' \
                 '\nMACBOOK AIR M1 https://amzn.to/3rT6FhH' \
                 '\nMAC MINI M1 https://amzn.to/2X90ub1' \
                 '\n' \
                 '\nPERIPHERALS - A LOT OF VALUE FOR LITTLE MONEY' \
                 '\nAPPLE MAGIC KEYBOARD https://amzn.to/38cPi3o' \
                 '\nAPPLE MAGIC TRACKPAD https://amzn.to/2Xd9KuE' \
                 '\nCONTROL MULTIPLE MAC COMPUTERS AND EFFORTLESSLY TRANSFER TEXT, IMAGES, AND FILES BETWEEN THEM.' \
                 '\nMULTI PC MOUSE https://amzn.to/2JP3aru' \
                 '\nMULTI PC KEYBOARD https://amzn.to/3rREG1O' \
                 '\n' \
                 '\nPHONES' \
                 '\nIPHONE 12 PRO MAX https://amzn.to/3pT3TY1' \
                 '\nIPHONE 12 PRO https://amzn.to/3hFRT9g' \
                 '\nIPHONE 12 https://amzn.to/3nkBWGY' \
                 '\nIPHONE 12 MINI https://amzn.to/392ewRk' \
                 '\n' \
                 '\nGADGETS' \
                 '\nIPAD PRO https://amzn.to/3ruQPcU' \
                 '\nAIRPODS https://amzn.to/3rCsvWL' \
                 '\nAIRPODS PRO https://amzn.to/34KY86w' \
                 '\nFIRE TV STICK 4K https://amzn.to/34K0oeh' \
                 '\nECHO DOT https://amzn.to/37UCkHL' \
                 '\nHOME SMART CAMERA https://amzn.to/2KsxOY3' \
                 '\nWIFI ROUTER https://amzn.to/3nUDecw' \
                 '\nKARAOKE MIC SPEAKER https://amzn.to/3pspA0W' \
                 '\nRGB LET STRIP LIGHTS https://amzn.to/38Di5xi' \
                 '\nUSB-C CHARGER https://amzn.to/38FeuP7' \
                 '\nNINTENDO SWITCH https://amzn.to/3mWfWSc' \
                 '\nSMART PLUG https://amzn.to/38NvvHc' \
                 '\nINSTANT CAMERA https://amzn.to/2WPGudg' \
                 '\n' \
                 '\nPC PARTS' \
                 '\nSAMSUNG 1TB SSD https://amzn.to/2WIXRN4' \
                 '\nSAMSUNG 1TB M.2 https://amzn.to/2KC0rlw' \
                 '\n' \
                 '\nSD CARD' \
                 '\nSANDISK 128G NINTENDO https://amzn.to/2WOzQE9' \
                 '\n' \
                 '\nGIFTS' \
                 '\nWATER BALLOONS https://amzn.to/3psT8ve' \
                 '\nPLAYSTATION GIFT CARD https://amzn.to/2JoAXYg' \
                 '\nWINDPROOF UMBRELLA https://amzn.to/37ZGhuN' \
                 '\nCAR MOUNT PHONE HOLDER https://amzn.to/3nZYfCL' \
                 '\nSTYLISH WALLET https://amzn.to/3rzjX2H' \
                 '\nSPACE SAVING CLOSET HANGERS https://amzn.to/38FgQO0' \
                 '\n' \
                 '\nBEAUTY PERSONAL CARE' \
                 '\nREVLON HAIR DRYER https://amzn.to/37NUP07' \
                 '\nPOSTURE CORRECTOR https://amzn.to/3aO2Ggc' \
                 '\nWEIGHTED BLANKET https://amzn.to/3aO4Zjm' \
                 '\n' \
                 '\nCLOTHING' \
                 '\nLEGGINGS https://amzn.to/37SP0P2' \
                 '\nSUPER SOFT HIGH WAISTED LEGGINGS https://amzn.to/3ptt5UH' \
                 '\n' \
                 '\nBOOKS' \
                 '\nLIFE CHANGING BOOK https://amzn.to/37SMEQc' \
                 '\nBARACK OBAMA https://amzn.to/34SK3nz' \
                 '\nBUILD GOOD HABITS, BREAK BAD ONES https://amzn.to/3rDaEi7' \
                 '\nKINDLE E-BOOK READER https://amzn.to/2KBdkwi' \
                 '\n' \
                 '\nBOARD GAMES TO CURE HOME ISOLATION' \
                 '\nCARDS AGAINST HUMANITY https://amzn.to/37OcS6s' \
                 '\nJENGA CLASSIC GAME https://amzn.to/2KvKmhk' \
                 '\nWHAT DO YOU MEME? https://amzn.to/34QudtG' \
                 '\n' \
                 '\nHOME CLEANING' \
                 '\nVACUUM CLEANER https://amzn.to/3mQq3rN' \
                 '\nCAR VACUUM CLEANER https://amzn.to/3po1XX9' \
                 '\nESSENTIAL OIL DIFFUSER https://amzn.to/3rEY1mW' \
                 '\nWASHING MACHINE CLEANER https://amzn.to/3nQhAWR' \
                 '\n' \
                 '\nKITCHEN/COOKING' \
                 '\nRICE COOKER INSTANT POT DUO https://amzn.to/3aMFQ8G' \
                 '\nEGG COOKER DASH https://amzn.to/3pCzAor' \
                 '\nKITCHEN GIZMO SNAP N STRAIN STRAINER https://amzn.to/3roeueW' \
                 '\nREUSABLE STORAGE BAG https://amzn.to/2Mf869T' \
                 '\nBLENDER https://amzn.to/34MIHe0' \
                 '\nWAFFLE MAKER https://amzn.to/3rAgrFd' \
                 '\n' \
                 '\nPETS' \
                 '\nGROOMING GLOVE https://amzn.to/3hnmVT8' \
                 '\n' \
                 '\nTOOLS' \
                 '\nDRIVER KIT https://amzn.to/3aItpux' \
                 '\n' \
                 '\nHIKING' \
                 '\nPERSONAL WATER FILTER https://amzn.to/3hm7quY' \
                 '\n' \
                 '\nFor promotions/clip removal, contact xxx@xxx.com.' \
                 '\nCopyright Disclaimer, Under Section 107 of the Copyright Act 1976, allowance is made for \'fair use\' for purposes such as criticism, comment, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational or personal use tips the balance in favor of fair use.' \
                 '\n#Shorts Thumbs up and subscribe!'
    description = video_desc

    # save metadata file
    metadata = {'title': title,
                'description': description, 'isProcessed': False}
    write_json_file(metadata_file_location, metadata)


def generate_metadata_files():
    # Loops over every tiktok
    hashtag_videos_directory_path = sys.argv[1:][0]

    # read json metadata
    json_metadata_file_path = sys.argv[1:][1]
    videos = load_json_file(json_metadata_file_path)

    for index, tiktok in enumerate(videos):
        try:
            metadata_file_location = os.path.join(
                hashtag_videos_directory_path, f"{tiktok['id']}.json")
            # save video&meta to disk
            save_video_metadata(tiktok, metadata_file_location)
        except:
            pass


generate_metadata_files()
