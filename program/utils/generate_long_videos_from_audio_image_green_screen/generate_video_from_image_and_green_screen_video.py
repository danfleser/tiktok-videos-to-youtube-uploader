import os
import sys
import glob

from program.utils.file_utils.get_file_size import is_file_broken_size


def resize_image_to_res(image_path):
    resized_image_output_name = image_path.replace(".jpg", "resize.jpg")

    width = 1920
    height = 1080

    resize_image_cmd = f"ffmpeg -i {image_path} -vf scale={width}:{height} {resized_image_output_name} > nul 2>&1"
    os.system(resize_image_cmd)

    # remove long video as we don't need it anymore, because we have watermarked video
    os.remove(image_path)

    # rename file to original name
    os.rename(resized_image_output_name, image_path)


def generate_video_from_image_with_green_screen(image_path, green_screen_video_path):
    # green
    video_output_name = image_path.replace(".jpg", ".mp4")
    green_color = "0F990A"

    video_cmd = f"ffmpeg -i {image_path} -i {green_screen_video_path} " \
                f"-filter_complex " \
                f"\"[1:v]colorkey=0x{green_color}:0.5:0.1[chkeyvid];" \
                f"[0:v]eq=brightness=-0.1[img];" \
                f"[img][chkeyvid]overlay[overlayout];" \
                f"[overlayout]scale=1920:1080[out];" \
                f"[out]boxblur=luma_radius=10:chroma_radius=10:luma_power=1[out]\" " \
                f"-map \"[out]\" {video_output_name} > nul 2>&1"
    os.system(video_cmd)

    # check file to see if was converted ok
    if is_file_broken_size(video_output_name):
        os.remove(video_output_name)
        return


def start():
    arguments = sys.argv[1:]
    # load image files
    image_dir_path = f"{arguments[0]}"
    list_of_image_files = glob.glob(os.path.join(image_dir_path, '*.jpg'))
    # load green screen video
    video_path = f"{arguments[1]}"

    # resize_image_to_res(list_of_image_files[0])
    # generate_video_from_image_with_green_screen(list_of_image_files[0], video_path)

    # Loops over every image
    for index, image_path in enumerate(list_of_image_files):

        try:
            resize_image_to_res(image_path)
            generate_video_from_image_with_green_screen(image_path, video_path)
        except Exception as e:
            print(e)
            pass


start()
