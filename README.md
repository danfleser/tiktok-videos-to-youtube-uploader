# What this project can do?
1. Downloads videos from tiktok
2. Uploads video to youtube
3. Respond to youtube channel comments(respond to all channel comments, with random questions, that intrigues the interlocutor in communication)
4. Bulk Delete youtube channel videos(remove all videos, specific videos)
5. Bulk Edit youtube channel videos(update title, description)
6. Delete unwatched videos from youtube channel(videos with lower threshold views count)
7. Generate videos from an image and a big audio file
8. Add green screen on top of videos(ex: add athumbnail to a video)
9. Launch multiple instances of chrome browser to make views to a certian video on youtube(you need a proxy server for this to work)
10. Generate lip synced videos(provide dummy video with face to lipsync, and a txt file with the text to be read)

All commands run in parralel.

## Installation
- install [nodejs](https://nodejs.org/en/download/)
- install [python](https://www.python.org/downloads/)
- you need to run a docker container on localhost with [nvidia tacotron2 tts](https://github.com/NVIDIA/tacotron2) in order to use number 9
- optional: proxy server if you want to make views to a youtube video [i used this service](https://my.didsoft.com/) not sponsored

- exec command from node-requirements.txt file
- install requirements.txt file using pip

- add add_to_path_drivers directory to your OS path

## Usage
- add_to_path_drivers/makemoney.bat - downloads tiktok videos, uploads then to youtube, responds to comments
- add_to_path_drivers/makeviews.bat - makes views to multiple youtube videos

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.