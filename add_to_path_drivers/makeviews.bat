d:
cd D:\dev\youtube-bot\tiktok-download
cmd "/K C:\ProgramData\Anaconda3\Scripts\activate.bat tiktok-downloader && for /l %%x in (1, 1, 10) do python -m program.views.make_views %1"
