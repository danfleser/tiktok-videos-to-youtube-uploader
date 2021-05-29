import time
from random import randrange

from selenium import webdriver
from selenium.webdriver import Proxy, DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import ProxyType
from fake_useragent import UserAgent


def start_video_player(driver):
    box1 = False
    box2 = False
    box3 = False
    box4 = False
    try:
        box1 = driver.find_element_by_css_selector("tp-yt-paper-dialog")
    except:
        pass
    try:
        box2 = driver.find_element_by_css_selector("ytd-popup-container")
    except:
        pass
    try:
        box3 = driver.find_element_by_css_selector("iron-overlay-backdrop")
    except:
        pass
    try:
        box4 = driver.find_element_by_css_selector("ytd-consent-bump-lightbox")
    except:
        pass

    if box1 or box2 or box3 or box4:
        # remove accept terms and conditions popup
        try:
            driver.execute_script("document.querySelector('tp-yt-paper-dialog').remove()")
        except:
            pass

        try:
            driver.execute_script("document.querySelector('ytd-popup-container').remove()")
        except:
            pass

        try:
            driver.execute_script("document.querySelector('iron-overlay-backdrop').remove()")
        except:
            pass

        try:
            driver.execute_script("document.querySelector('ytd-consent-bump-lightbox').remove()")
        except:
            pass

        # press mute button
        time.sleep(1)
        try:
            is_muted = driver.find_element_by_css_selector('.ytp-chrome-controls .ytp-mute-button.ytp-button') \
                .get_attribute("title")
            if is_muted == "Mute (m)":
                driver.execute_script("document.querySelector('.ytp-mute-button').click()")

            # set 144p resolution
            time.sleep(1)
            driver.execute_script("document.querySelector('.ytp-settings-button').click()")
            time.sleep(1)
            driver.execute_script("document.querySelector('.ytp-settings-menu .ytp-menuitem:nth-child(2)').click()")
            time.sleep(1)
            driver.execute_script(
                "document.querySelector('.ytp-settings-menu .ytp-quality-menu .ytp-panel-menu .ytp-menuitem:nth-child(6)').click()")
        except:
            pass

        # start button
        try:
            time.sleep(1)
            is_playing = driver.find_element_by_css_selector('.ytp-chrome-controls .ytp-play-button.ytp-button')\
                .get_attribute("title")
            if is_playing == "Play (k)":
                driver.execute_script("document.querySelector('.ytp-chrome-controls .ytp-play-button.ytp-button').click()")
        except:
            pass


def start_youtube_work(driver):
    time.sleep(60 * 2)
    # confirm consent
    try:
        driver.execute_script("document.querySelector('c-wiz form div div div').click()")
    except:
        pass
    try:
        driver.execute_script("document.querySelector('form .button').click()")
    except:
        pass

    # wait page to load
    time.sleep(60)
    try:
        # mobile version of the website we close it because does not function properly
        box5 = driver.find_element_by_css_selector("ytm-upsell-dialog-renderer")
        if box5:
            driver.quit()
    except:
        pass
    start_video_player(driver)

    # after 5 min test to check if popups are deleted, due to many simultaneously browser loads
    # some instances of chrome do not load correctly
    for x in range(0, 10):
        time.sleep(60)
        start_video_player(driver)

    time.sleep(60 * 60 * randrange(8, 10))
    driver.quit()


def start_view_video(youtube_urls):
    youtube_video_url = youtube_urls.pop()

    preferences = {
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False
    }

    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--mute-audio")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("prefs", preferences)

    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')

    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = "46.4.73.88:2000"
    proxy.sslProxy = "46.4.73.88:2000"
    capabilities = DesiredCapabilities.CHROME
    proxy.add_to_capabilities(capabilities)

    driver = webdriver.Chrome(desired_capabilities=capabilities, options=options)
    driver.get(youtube_video_url)

    time.sleep(60 * 2)
    start_youtube_work(driver)

    if len(youtube_urls) > 0:
        start_view_video(youtube_urls)
