"""This module implements uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc."""
import random
from typing import DefaultDict, Optional
from collections import defaultdict
import json
import time
from .Constant import *
from pathlib import Path

from program.utils.libs.Firefox import Firefox, By


def load_metadata(metadata_json_path: Optional[str] = None) -> DefaultDict[str, str]:
    if metadata_json_path is None:
        return defaultdict(str)
    with open(metadata_json_path, encoding="utf-8") as metadata_json_file:
        return defaultdict(str, json.load(metadata_json_file))


class YouTubeUploader:
    """A class for uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc"""

    def __init__(self, headless, cookie_working_dir: Optional[str] = None) -> None:
        if cookie_working_dir:
            self.cookie_working_dir = cookie_working_dir
            self.browser = Firefox(
                cookies_folder_path=self.cookie_working_dir,
                extensions_folder_path=self.cookie_working_dir,
                headless=headless
            )
        else:
            current_working_dir = str(Path.cwd())
            self.cookie_working_dir = current_working_dir
            self.browser = Firefox(self.cookie_working_dir, self.cookie_working_dir, headless=headless)
        self.__login()

    def __login(self):
        self.browser.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.refresh()
        else:
            print('Please sign in and then press enter')
            input()
            self.browser.get(Constant.YOUTUBE_URL)
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.save_cookies()

    def upload(self, video_path: str, metadata_json_path: Optional[str] = None):
        try:
            metadata_dict = load_metadata(metadata_json_path)
            self.__validate_inputs(metadata_dict, video_path)
            return self.__upload(video_path, metadata_dict)
        except Exception as e:
            print(e)
            return False

    def __set_channel_language_english(self):
        try:
            self.browser.driver.find_element_by_id("img").click()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_xpath("(//yt-icon[@id='right-icon'])[6]").click()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_xpath("(//yt-formatted-string[@id='label'])[26]").click()
            time.sleep(Constant.USER_WAITING_TIME)
        except:
            pass

    def __upload(self, video_path: str, metadata_dict: DefaultDict[str, str] = None) -> (bool, Optional[str]):
        self.browser.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        # set english as language
        self.__set_channel_language_english()

        self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
        time.sleep(5)

        # attach video
        absolute_video_path = str(Path.cwd() / video_path)
        self.browser.find(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(absolute_video_path)
        time.sleep(5)

        # Catch max uploads/day limit errors
        next_button = self.browser.find(By.ID, Constant.NEXT_BUTTON)
        if next_button.get_attribute('hidden') == 'true':
            error_short_by_xpath = self.browser.find(By.XPATH, Constant.ERROR_SHORT_XPATH)
            print(f"ERROR: {error_short_by_xpath.text} {self.cookie_working_dir}")
            return False

        # set title & description
        title_and_description = self.browser.driver.find_elements_by_css_selector(Constant.title_description_containers)

        # set title
        title_field = title_and_description[0]
        title_field.click()
        time.sleep(Constant.USER_WAITING_TIME)
        title_field.clear()
        time.sleep(Constant.USER_WAITING_TIME)
        title_field.send_keys(metadata_dict[Constant.VIDEO_TITLE])

        # set description
        description_field = title_and_description[1]
        description_field.click()
        time.sleep(Constant.USER_WAITING_TIME)
        description_field.clear()
        time.sleep(Constant.USER_WAITING_TIME)
        description_field.send_keys(metadata_dict[Constant.VIDEO_DESCRIPTION])
        time.sleep(Constant.USER_WAITING_TIME)

        try:
            # go to VISIBILITY tab by the section badges 2021 feature
            self.browser.driver.find_element_by_id("step-badge-3").click()
        except:
            # 2021 feature is not showing because is not showing on all channels. do no why
            # go to VISIBILITY tab by pressing next buttons

            # go to CARDS tab
            next_button.click()
            # go to VISIBILITY tab
            self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
            time.sleep(Constant.USER_WAITING_TIME)

        # set VISIBILITY public
        visibility_main_button = self.browser.find(By.NAME, Constant.PUBLIC_BUTTON)
        self.browser.find(By.ID, Constant.RADIO_LABEL, visibility_main_button).click()

        # wait until video uploads
        # uploading progress text contains ": " - Timp ramas/Remaining time: 3 minutes.
        # we wait until ': ' is removed, so we know the text has changed and video has entered processing stage
        uploading_progress_text = self.browser.find(By.CSS_SELECTOR, Constant.UPLOADING_PROGRESS_SELECTOR).text
        while ': ' in uploading_progress_text:
            time.sleep(5)
            uploading_progress_text = self.browser.find(By.CSS_SELECTOR, Constant.UPLOADING_PROGRESS_SELECTOR).text

        try:
            done_button = self.browser.find(By.ID, Constant.DONE_BUTTON, None, 60)
            time.sleep(Constant.USER_WAITING_TIME)
            video_id = self.__get_video_id()
            done_button.click()
            time.sleep(Constant.USER_WAITING_TIME)
            # print(f"Id: {video_id}")
        except Exception as e:
            print(e)
            raise

        return True

    def remove_unwatched_videos(self, remove_copyrighted, remove_unwatched_views):
        try:
            self.browser.get(Constant.YOUTUBE_URL)
            time.sleep(Constant.USER_WAITING_TIME)

            # set english as language
            self.__set_channel_language_english()

            self.browser.driver.get("https://studio.youtube.com/")
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_id("menu-paper-icon-item-1").click()
            time.sleep(Constant.USER_WAITING_TIME)

            if self.__is_videos_available():
                return True

            self.browser.driver.find_element_by_css_selector("#page-size .ytcp-text-dropdown-trigger").click()
            time.sleep(Constant.USER_WAITING_TIME)
            # clock 50 items per page
            pagination_sizes = self.browser.driver.find_elements_by_css_selector("#select-menu-for-page-size #dialog .paper-item")
            pagination_sizes[2].click()
            time.sleep(Constant.USER_WAITING_TIME)

            # filter to delete only copyrighted videos
            if remove_copyrighted:
                self.browser.driver.find_element_by_id("filter-icon").click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_css_selector("ytcp-text-menu#menu tp-yt-paper-dialog tp-yt-paper-listbox paper-item#text-item-1 ytcp-ve div").click()
                time.sleep(Constant.USER_WAITING_TIME)

            # filter to delete videos with views lower than 100
            if remove_unwatched_views:
                views_no = "100000"
                self.browser.driver.find_element_by_id("filter-icon").click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_css_selector("ytcp-text-menu#menu tp-yt-paper-dialog tp-yt-paper-listbox paper-item#text-item-5 ytcp-ve div").click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_xpath("//iron-input[@id='input-2']/input").click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_xpath("//iron-input[@id='input-2']/input").clear()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_xpath("//iron-input[@id='input-2']/input").send_keys(views_no)
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_xpath("//input[@type='text']").click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_xpath("//tp-yt-paper-listbox[@id='operator-list']/paper-item[2]").click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_xpath("//ytcp-button[@id='apply-button']/div").click()
                time.sleep(Constant.USER_WAITING_TIME)

            return self.__remove_unwatched_videos()
        except Exception as e:
            print(e)
            return False

    def __is_videos_available(self):
        # if there are no videos to be deleted, this element should be visible
        # if not visible throw error, and proceed to delete more videos
        try:
            self.browser.driver.find_element_by_xpath("//ytcp-video-section-content[@id='video-list']/div/div[2]/div")
            # return True, there are no more video to be deleted
            return True
        except:
            return False

    def __remove_unwatched_videos(self):
        DELETE_WAIT_TIME = 60 * 2

        # check if videos deletion process has finished
        # if not visible throw error, and proceed to delete more videos
        try:
            self.browser.driver.find_element_by_xpath("//div[@id='header']/div/span[2]")
            # wait for the videos to be deleted and try delete videos after
            time.sleep(DELETE_WAIT_TIME)
            return self.__remove_unwatched_videos()
        except:
            pass

        if self.__is_videos_available():
            return True

        self.browser.driver.find_element_by_id("checkbox-container").click()
        time.sleep(Constant.USER_WAITING_TIME)
        self.browser.driver\
            .find_element_by_css_selector(".ytcp-bulk-actions .toolbar .ytcp-select .ytcp-text-dropdown-trigger .ytcp-dropdown-trigger .right-container .ytcp-dropdown-trigger")\
            .click()
        time.sleep(Constant.USER_WAITING_TIME)
        self.browser.driver.find_element_by_css_selector("#select-menu-for-additional-action-options #dialog #paper-list #text-item-1").click()
        time.sleep(Constant.USER_WAITING_TIME)
        self.browser.driver.find_element_by_css_selector("#dialog-content-confirm-checkboxes #confirm-checkbox #checkbox-container").click()
        time.sleep(Constant.USER_WAITING_TIME)
        self.browser.driver.find_element_by_css_selector(".ytcp-confirmation-dialog #dialog-buttons #confirm-button").click()
        # wait 5 minutes for the videos to be deleted
        time.sleep(DELETE_WAIT_TIME)

        return self.__remove_unwatched_videos()

    def close_youtube_annoying_popup(self):
        self.browser.execute_script(
            "document.querySelectorAll('ytcp-feature-discovery-callout').forEach(e => e.remove())")
        time.sleep(Constant.USER_WAITING_TIME)

    def bulk_comments_reply(self):
        self.browser.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        # set english as language
        self.__set_channel_language_english()

        self.__bulk_comments_reply()

    def __bulk_comments_reply(self):
        questions = [
            "Did you like the video?",
            "Is cereal soup? Why or why not?",
            "What is the sexiest and least sexy name?",
            "What secret conspiracy would you like to start?",
            "What’s invisible but you wish people could see?",
            "What’s the weirdest smell you have ever smelled?",
            "Is a hot-dog a sandwich? Why or why not?",
            "What’s the best Wi-Fi name you’ve seen?",
            "What’s the most ridiculous fact you know?",
            "What is something that everyone looks stupid doing?",
            "What is the funniest joke you know by heart?",
            "In 40 years, what will people be nostalgic for?",
            "What are the unwritten rules of where you work?",
            "How do you feel about putting pineapple on pizza?",
            "What part of a kid’s movie completely scarred you?",
            "What kind of secret society would you like to start?",
            "If animals could talk, which would be the rudest?",
            "Toilet paper, over or under?",
            "What’s the best type of cheese?",
            "Where is the strangest place you’ve urinated or defecated?",
            "What’s the best inside joke you’ve been a part of?",
            "In one sentence, how would you sum up the internet?",
            "How many chickens would it take to kill an elephant?",
            "What is the most embarrassing thing you have ever worn?",
            "What’s the most imaginative insult you can come up with?",
            "Which body part do you wish you could detach and why?",
            "What used to be considered trashy but now is very classy?",
            "What’s the weirdest thing a guest has done at your house?",
            "What mythical creature would improve the world most if it existed?",
            "What inanimate object do you wish you could eliminate from existence?",
            "What is the weirdest thing you have seen in someone else’s home?",
            "What would be the absolute worst name you could give your child?",
            "What would be the worst thing for the government to make illegal?",
            "What are some of the nicknames you have for customers or coworkers?",
            "If peanut butter wasn’t called peanut butter, what would it be called?",
            "What movie would be greatly improved if it was made into a musical?",
            "What are some of the biggest challenges you have faced?",
            "Do you enjoy overcoming challenges or do you prefer things to be easy? Why?",
            "What is a challenge you would never want to face?",
            "What is the most challenging job you can think of?",
            "Do you think that challenges improve a person’s character?",
            "What is the biggest challenge you are facing right now?",
            "What was the most challenging thing about your childhood?",
            "What are some big challenges that people have overcome that you have heard of?",
            "What are the biggest challenges your country is facing right now?",
            "What is the craziest diet you’ve heard of?",
            "What diets have you tried?",
            "Is dieting healthy or unhealthy?",
            "What diets are popular now?",
            "Is dieting an effective way to lose weight and keep it off?",
            "Why do you think there are so many diet trends?",
            "Do you know anyone who has lost a lot of weight on a diet?",
            "Will there ever be a miracle weight loss solution?",
        ]

        try:
            self.browser.driver.get("https://studio.youtube.com/")
            time.sleep(Constant.USER_WAITING_TIME)

            # go to channel comments page
            self.close_youtube_annoying_popup()
            self.browser.driver.find_element_by_css_selector("#menu-item-4").click()
            time.sleep(Constant.USER_WAITING_TIME)

            # remove tooltips because blocks clicking buttons
            self.browser.execute_script("document.querySelectorAll('ytcp-paper-tooltip').forEach(e => e.remove())")

            # check if we have comments
            self.close_youtube_annoying_popup()
            comments_box = self.browser.driver.find_element_by_css_selector("#contents")
            if comments_box.get_attribute('hidden') == 'true':
                return False

            self.close_youtube_annoying_popup()
            like_buttons = self.browser.driver.find_elements_by_css_selector("#like-button #button #button")
            for like in like_buttons:
                liked = "Unlike" in like.get_attribute("aria-label")
                if not liked:
                    self.close_youtube_annoying_popup()
                    like.click()
                    time.sleep(Constant.USER_WAITING_TIME)

            self.close_youtube_annoying_popup()
            heart_buttons = self.browser.driver.find_elements_by_css_selector("#creator-heart #button")
            for heart in heart_buttons:
                hearted = "Remove heart" in heart.get_attribute("aria-label")
                if not hearted:
                    self.close_youtube_annoying_popup()
                    heart.click()
                    time.sleep(Constant.USER_WAITING_TIME)

            self.close_youtube_annoying_popup()
            reply_buttons = self.browser.driver.find_elements_by_css_selector("#reply-button #button")
            for reply in reply_buttons:
                self.close_youtube_annoying_popup()
                reply.click()
                time.sleep(Constant.USER_WAITING_TIME)

            self.close_youtube_annoying_popup()
            textarea_buttons = self.browser.driver.find_elements_by_xpath("//textarea[@id='textarea']")
            for textarea in textarea_buttons:
                self.close_youtube_annoying_popup()
                textarea.click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.close_youtube_annoying_popup()
                textarea.send_keys(random.choice(questions))
                time.sleep(Constant.USER_WAITING_TIME)

            self.close_youtube_annoying_popup()
            submit_buttons = self.browser.driver.find_elements_by_css_selector("#submit-button")
            for submit in submit_buttons:
                self.close_youtube_annoying_popup()
                submit.click()
                time.sleep(Constant.USER_WAITING_TIME)

            time.sleep(2)
            self.__bulk_comments_reply()
        except:
            self.__bulk_comments_reply()

    def __get_video_id(self) -> Optional[str]:
        video_id = None
        try:
            video_url_container = self.browser.find(By.XPATH, Constant.VIDEO_URL_CONTAINER)
            video_url_element = self.browser.find(By.XPATH, Constant.VIDEO_URL_ELEMENT,
                                                  element=video_url_container)
            video_id = video_url_element.get_attribute(Constant.HREF).split('/')[-1]
        except:
            pass
        return video_id

    def __validate_inputs(self, metadata_dict, video_path):
        if not metadata_dict[Constant.VIDEO_TITLE]:
            print("The video title was not found in a metadata file")
            metadata_dict[Constant.VIDEO_TITLE] = Path(video_path).stem
            print("The video title was set to {}".format(Path(video_path).stem))
        if not metadata_dict[Constant.VIDEO_DESCRIPTION]:
            print("The video description was not found in a metadata file")

    def quit(self):
        self.browser.driver.quit()

    def publish_draft_videos(self):
        self.browser.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        # set english as language
        self.__set_channel_language_english()

        self.__publish_draft_videos()

    def __publish_draft_videos(self):
        try:
            self.browser.driver.get("https://studio.youtube.com/")
            time.sleep(Constant.USER_WAITING_TIME)

            # go to channel comments page
            self.close_youtube_annoying_popup()
            self.browser.driver.find_element_by_css_selector("#menu-item-1").click()
            time.sleep(Constant.USER_WAITING_TIME)

            # remove tooltips because blocks clicking buttons
            self.browser.execute_script("document.querySelectorAll('ytcp-paper-tooltip').forEach(e => e.remove())")

            # check if we have comments
            self.close_youtube_annoying_popup()

            self.browser.driver.find_element_by_id("filter-icon").click()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_xpath("//paper-item[@id='text-item-6']/ytcp-ve/div").click()
            time.sleep(Constant.USER_WAITING_TIME)

            # check to see if we have draft videos
            visibility_checkboxes_texts = self.browser.driver.find_elements_by_css_selector("#checkbox-group ul li .label.label-text.ytcp-checkbox-group")
            if visibility_checkboxes_texts[4].text != "Draft":
                return

            visibility_checkboxes = self.browser.driver.find_elements_by_css_selector("#checkbox-group ul #checkbox-container")
            # click DRAFT
            visibility_checkboxes[4].click()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_xpath("//ytcp-button[@id='apply-button']/div").click()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_xpath(
                "(//ytcp-text-dropdown-trigger[@id='trigger']/ytcp-dropdown-trigger/div/div[3]/tp-yt-iron-icon)[3]").click()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.driver.find_element_by_id("text-item-2").click()
            time.sleep(Constant.USER_WAITING_TIME)

            edit_draft_buttons = self.browser.driver.find_elements_by_css_selector(".edit-draft-button")
            if len(edit_draft_buttons) == 0:
                return

            for edit_draft in edit_draft_buttons:
                edit_draft.click()
                time.sleep(10)
                self.browser.driver.find_element_by_id('step-badge-2').click()
                time.sleep(Constant.USER_WAITING_TIME)
                self.browser.driver.find_element_by_id('done-button').click()
                time.sleep(10)
                self.browser.driver.find_element_by_css_selector('#dialog #dialog .footer #close-button').click()
                time.sleep(Constant.USER_WAITING_TIME)

            self.__publish_draft_videos()
        except Exception as e:
            print(e)
            pass