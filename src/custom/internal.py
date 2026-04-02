from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.joinpath("Volume")
PROJECT_ROOT.mkdir(exist_ok=True)
VERSION_MAJOR = 5
VERSION_MINOR = 8
VERSION_BETA = True
__VERSION__ = f"{VERSION_MAJOR}.{VERSION_MINOR}.{'beta' if VERSION_BETA else 'stable'}"
PROJECT_NAME = f"DouK-Downloader V{VERSION_MAJOR}.{VERSION_MINOR} {
    'Beta' if VERSION_BETA else 'Stable'
}"

REPOSITORY = "https://github.com/JoeanAmier/TikTokDownloader"
LICENCE = "GNU General Public License v3.0"
DOCUMENTATION_URL = "https://github.com/JoeanAmier/TikTokDownloader/wiki/Documentation"
RELEASES = "https://github.com/JoeanAmier/TikTokDownloader/releases/latest"

DISCLAIMER_TEXT = (
    "DouK-Downloader Disclaimer:\n"
    "\n"
    "1. Use of this project is at the user's own discretion and risk. The author is not responsible for any loss, liability, or risk arising from use.\n"
    "2. The code and features are developed based on existing knowledge and technology. The author strives to ensure correctness and security but does not guarantee the code is free of errors or defects.\n"
    "3. All third-party libraries, plugins, or services follow their respective licenses. Users must review and comply with those agreements. The author assumes no responsibility for third-party components.\n"
    "4. Users must strictly comply with the GNU General Public License v3.0 requirements and properly attribute GPL v3.0 code where applicable.\n"
    "5. Users must research applicable laws and ensure their usage is legal and compliant. Any legal liability from violations is solely the user's responsibility.\n"
    "6. Users must not use this tool for any intellectual property infringement, including unauthorized downloading or distributing copyrighted content. The developer does not participate in, support, or endorse any illegal content acquisition.\n"
    "7. This project is not responsible for the compliance of users' data collection, storage, or transmission activities. Users must comply with applicable laws; legal liability for violations is solely the user's.\n"
    "8. Users must not associate the project's author, contributors, or related parties with their usage, nor hold them responsible for any loss or damage.\n"
    "9. The author will not provide a paid version of DouK-Downloader, nor offer any commercial services related to it.\n"
    "10. Any derivative works, modifications, or compiled programs based on this project are unrelated to the original author, who assumes no responsibility for such derivative works.\n"
    "11. This project grants no patent licenses. Users assume all risks for patent disputes. Commercial promotion or sub-licensing requires written authorization from the author.\n"
    "12. The author reserves the right to terminate service to any user who violates this disclaimer and may require destruction of obtained code and derivative works.\n"
    "13. The author reserves the right to update this disclaimer without notice. Continued use constitutes acceptance of revised terms.\n"
    "\n"
    "Before using this project, please carefully consider and accept this disclaimer. If you have any"
    "questions or disagreements, do not use this project. By using this project, you acknowledge"
    "that you fully understand and accept this disclaimer, and voluntarily assume all risks"
    "and consequences.\n"
)

RETRY = 5
TIMEOUT = 10

PHONE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "CriOS/125.0.6422.51 Mobile/15E148 Safari/604.1",
}
USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
BLANK_HEADERS = {
    "User-Agent": USERAGENT,
}
REFERER = "https://www.douyin.com/?recommend=1"
REFERER_TIKTOK = "https://www.tiktok.com/explore"
PARAMS_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "*/*",
    "Content-Type": "text/plain;charset=UTF-8",
    "Referer": REFERER,
    "User-Agent": USERAGENT,
}
PARAMS_HEADERS_TIKTOK = PARAMS_HEADERS | {
    "Referer": REFERER_TIKTOK,
}
DATA_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "*/*",
    "Referer": REFERER,
    "User-Agent": USERAGENT,
}
DATA_HEADERS_TIKTOK = DATA_HEADERS | {
    "Referer": REFERER_TIKTOK,
}
DOWNLOAD_HEADERS = {
    "Accept": "*/*",
    "Range": "bytes=0-",
    "Referer": REFERER,
    "User-Agent": USERAGENT,
}
DOWNLOAD_HEADERS_TIKTOK = DOWNLOAD_HEADERS | {
    "Referer": REFERER_TIKTOK,
}
QRCODE_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "*/*",
    "Referer": REFERER,
    "User-Agent": USERAGENT,
}

BLANK_PREVIEW = "static/images/blank.png"

VIDEO_INDEX: int = -1
VIDEO_TIKTOK_INDEX: int = 0
IMAGE_INDEX: int = -1
IMAGE_TIKTOK_INDEX: int = -1
VIDEOS_INDEX: int = -1
DYNAMIC_COVER_INDEX: int = -1
STATIC_COVER_INDEX: int = -1
MUSIC_INDEX: int = -1
COMMENT_IMAGE_INDEX: int = -1
COMMENT_STICKER_INDEX: int = -1
LIVE_COVER_INDEX: int = -1
AUTHOR_COVER_INDEX: int = -1
HOT_WORD_COVER_INDEX: int = -1
COMMENT_IMAGE_LIST_INDEX: int = 0
BITRATE_INFO_TIKTOK_INDEX: int = 0
LIVE_DATA_INDEX: int = 0
AVATAR_LARGER_INDEX: int = 0
AUTHOR_COVER_URL_INDEX: int = 0
SEARCH_USER_INDEX: int = 0
SEARCH_AVATAR_INDEX: int = 0
MUSIC_COLLECTION_COVER_INDEX: int = 0
MUSIC_COLLECTION_DOWNLOAD_INDEX: int = 0

if __name__ == "__main__":
    print(__VERSION__)
