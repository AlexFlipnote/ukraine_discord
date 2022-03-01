import requests
import json
import time
import os
import traceback
import random

from datetime import datetime, timedelta
from colorama import Fore, Style
from bs4 import BeautifulSoup


def traceback_maker(err):
    """ Make a traceback from the error """
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = ('{1}{0}: {2}').format(type(err).__name__, _traceback, err)
    return error


class Feed:
    def __init__(self, html_data):
        self.html = html_data
        self.info = html_data.find("div", {"class": "title"}).text
        self.id = html_data.attrs.get("data-id", None)
        self.extra = html_data.find("a", {"data-id": self.id, "class": "comment-link"}).attrs.get("href", None)

    @property
    def video(self):
        """ Returns the video url if available """
        main_video = self.html.attrs.get("data-twitpic", None)
        if main_video and "video" in main_video:
            return main_video

        find_video = self.html.find("blockquote", {"class": "twitter-video"})
        if not find_video:
            return None
        return find_video.find("a").attrs.get("href", None)

    @property
    def image(self):
        """ Get the image of the feed """
        find_img = self.html.find("div", {"class": "img"})
        if not find_img:
            return None
        try:
            return find_img.find("img").attrs.get("src", None)
        except AttributeError:
            return None


class Article:
    def __init__(self, feed: Feed, html_data):
        self.html = html_data
        self.feed = feed

        self.image = feed.image
        self.info = feed.info
        self.id = feed.id
        self.extra = feed.extra
        self.video = feed.video

    @property
    def source(self):
        """ Get the source of the article """
        html = self.html.find("a", {"class": "source-link"})
        if not html:
            return None
        return html.attrs.get("href", None)


def read_json(key: str = None, default=None):
    """ Read the config.json file, also define default key for keys """
    with open("./config.json", "r") as f:
        data = json.load(f)
    if key:
        return data.get(key, default)
    return data


def write_json(**kwargs):
    """ Use the config.json to write to the file """
    data = read_json()
    for key, value in kwargs.items():
        data[key] = value
    with open("./config.json", "w") as f:
        json.dump(data, f, indent=2)


def debug_html(content: str):
    debug = read_json("debug", False)
    if debug:
        if not os.path.exists("./debug"):
            os.mkdir("./debug")
        with open(f"./debug/debug_{int(time.time())}.html", "w", encoding="utf8") as f:
            f.write(content)


def webhook(html_content: Article):
    """ Send webhook to Discord """
    utc_timestamp = datetime.utcnow()
    ukraine_timestamp = utc_timestamp + timedelta(hours=2)
    timestamp_string = "%d/%m/%Y %H:%M | %I:%M %p"

    now_unix = int(time.time())
    discord_timestamps = f"<t:{now_unix}:d> <t:{now_unix}:t>"

    embed = {
        "author": {
            "name": "New update about Ukraine",
            # please don't remove this <3
            "url": "https://github.com/AlexFlipnote/ukraine_discord",
        },
        "color": 0xf1c40f,
        "thumbnail": {"url": "https://cdn.discordapp.com/emojis/691373958087442486.png"},
        "fields": [{
            "name": "Timezones",
            "value": "\n".join([
                f"🇬🇧 {utc_timestamp.strftime(timestamp_string)}",
                f"🇺🇦 {ukraine_timestamp.strftime(timestamp_string)}",
                f"🌍 {discord_timestamps}"
            ]),
            "inline": False
        }]
    }

    if html_content.source:
        embed["description"] = f"[ℹ️ Source of the news]({html_content.source})\n{html_content.info}"
    else:
        embed["description"] = f"ℹ️ Unable to find source...\n{html_content.info}"

    if html_content.image and read_json("embed_image", True):
        embed["image"] = {"url": html_content.image}
    if html_content.video:
        embed["description"] += f"\n\n> Warning: Can be graphical, view at own risk\n[Twitter video]({html_content.video})"

    return requests.post(
        read_json("webhook_url", None),
        headers={"Content-Type": "application/json"},
        data=json.dumps({"content": None, "embeds": [embed]}),
    )


def pretty_print(symbol: str, text: str):
    """ Use colorama to print text in pretty colours """
    data = {
        "+": Fore.GREEN, "-": Fore.RED,
        "!": Fore.YELLOW, "?": Fore.CYAN,
    }

    colour = data.get(symbol, Fore.WHITE)
    print(f"{colour}[{symbol}]{Style.RESET_ALL} {text}")


def fetch(url: str):
    """ Simply fetch any URL given, and convert from bytes to string """
    # cookies=read_json("cookies", {})
    r = requests.get(
        url, headers={
            "User-Agent": read_json("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        }
    )
    text = r.content.decode("utf-8")
    debug_html(text)
    return text


def main():
    while True:
        try:
            # Random wait time to not be too obvious
            # Since we are scraping the website, lol
            check_in_rand = random.randint(45, 75)

            pretty_print("?", f"{datetime.now()} - Checking for new articles")
            pretty_print("+", "Fetching all articles and parsing HTML...")

            r = fetch("https://liveuamap.com/")
            html = BeautifulSoup(r, "html.parser")

            try:
                feeder = html.find("div", {"id": "feedler"})
                latest_news = next((g for g in feeder), None)
            except TypeError:
                # For some weird reason, this website loves to crash with HTTP 5XX
                # So we just try again because the website encourages us to, really.
                pretty_print("!", "Failed to get feeder, probably 500 error, trying again...")
                time.sleep(5)
                continue

            news = Feed(latest_news)
            if news.id != read_json("last_id", None):
                pretty_print("+", "New article found, checking article...")
                r_extra = fetch(news.extra)
                extra_html = BeautifulSoup(r_extra, "html.parser")
                webhook(Article(news, extra_html))
                write_json(last_id=news.id)
                pretty_print("!", news.info)
            else:
                pretty_print("-", f"Found no news... waiting {check_in_rand} seconds")
        except Exception as e:
            pretty_print("!", traceback_maker(e))

        time.sleep(check_in_rand)


try:
    main()
except KeyboardInterrupt:
    pretty_print("!", "Exiting...")
