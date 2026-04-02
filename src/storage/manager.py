from shutil import move
from typing import TYPE_CHECKING

from .csv import CSVLogger
from .sqlite import SQLLogger
from .text import BaseTextLogger
from .xlsx import XLSXLogger

if TYPE_CHECKING:
    from pathlib import Path

    from ..config import Parameter

__all__ = ["RecordManager"]


class RecordManager:
    """Check data storage path and folder"""

    detail = (
        (
            "type",
            "Post Type",
            "TEXT",
        ),
        (
            "collection_time",
            "Collected At",
            "TEXT",
        ),
        (
            "uid",
            "UID",
            "TEXT",
        ),
        (
            "sec_uid",
            "SEC_UID",
            "TEXT",
        ),
        (
            "unique_id",
            "ID",
            "TEXT",
        ),
        # ("short_id", "SHORT_ID", "TEXT",),
        (
            "id",
            "Post ID",
            "TEXT",
        ),
        (
            "desc",
            "Description",
            "TEXT",
        ),
        (
            "text_extra",
            "Topics",
            "TEXT",
        ),
        (
            "duration",
            "Video Duration",
            "TEXT",
        ),
        # ("ratio", "Video Resolution", "TEXT",),
        (
            "height",
            "Video Height",
            "INTEGER",
        ),
        (
            "width",
            "Video Width",
            "INTEGER",
        ),
        (
            "share_url",
            "Post URL",
            "TEXT",
        ),
        (
            "create_time",
            "Published At",
            "TEXT",
        ),
        (
            "uri",
            "Video URI",
            "TEXT",
        ),
        (
            "nickname",
            "Nickname",
            "TEXT",
        ),
        (
            "user_age",
            "Age",
            "INTEGER",
        ),
        (
            "signature",
            "Bio",
            "TEXT",
        ),
        (
            "downloads",
            "Download URL",
            "TEXT",
        ),
        (
            "music_author",
            "Music Author",
            "TEXT",
        ),
        (
            "music_title",
            "Music Title",
            "TEXT",
        ),
        (
            "music_url",
            "Music URL",
            "TEXT",
        ),
        (
            "static_cover",
            "Static Cover",
            "TEXT",
        ),
        (
            "dynamic_cover",
            "Dynamic Cover",
            "TEXT",
        ),
        (
            "tag",
            "Hidden Tags",
            "TEXT",
        ),
        (
            "digg_count",
            "Likes",
            "INTEGER",
        ),
        (
            "comment_count",
            "Comments",
            "INTEGER",
        ),
        (
            "collect_count",
            "Favorites",
            "INTEGER",
        ),
        (
            "share_count",
            "Shares",
            "INTEGER",
        ),
        (
            "play_count",
            "Views",
            "INTEGER",
        ),
        (
            "extra",
            "Extra Info",
            "TEXT",
        ),
    )
    comment = (
        (
            "collection_time",
            "Collected At",
            "TEXT",
        ),
        (
            "cid",
            "Comment ID",
            "TEXT",
        ),
        (
            "create_time",
            "Comment Time",
            "TEXT",
        ),
        (
            "uid",
            "UID",
            "TEXT",
        ),
        (
            "sec_uid",
            "SEC_UID",
            "TEXT",
        ),
        # ("short_id", "SHORT_ID", "TEXT",),
        # ("unique_id", "DouYin ID", "TEXT",),
        (
            "nickname",
            "Nickname",
            "TEXT",
        ),
        (
            "signature",
            "Bio",
            "TEXT",
        ),
        (
            "user_age",
            "Age",
            "INTEGER",
        ),
        (
            "ip_label",
            "IP Location",
            "TEXT",
        ),
        (
            "text",
            "Comment Content",
            "TEXT",
        ),
        (
            "sticker",
            "Comment Emoji",
            "TEXT",
        ),
        (
            "image",
            "Comment Image",
            "TEXT",
        ),
        (
            "digg_count",
            "Likes",
            "INTEGER",
        ),
        (
            "reply_comment_total",
            "Replies",
            "INTEGER",
        ),
        (
            "reply_id",
            "Reply ID",
            "TEXT",
        ),
        (
            "reply_to_reply_id",
            "Reply To",
            "TEXT",
        ),
    )
    user = (
        (
            "collection_time",
            "Collected At",
            "TEXT",
        ),
        (
            "nickname",
            "Nickname",
            "TEXT",
        ),
        (
            "url",
            "Account URL",
            "TEXT",
        ),
        (
            "signature",
            "Bio",
            "TEXT",
        ),
        (
            "unique_id",
            "DouYin ID",
            "TEXT",
        ),
        (
            "user_age",
            "Age",
            "INTEGER",
        ),
        (
            "gender",
            "Gender",
            "TEXT",
        ),
        (
            "country",
            "Country",
            "TEXT",
        ),
        (
            "province",
            "Province",
            "TEXT",
        ),
        (
            "city",
            "City",
            "TEXT",
        ),
        (
            "district",
            "Region",
            "TEXT",
        ),
        (
            "ip_location",
            "IP Location",
            "TEXT",
        ),
        (
            "verify",
            "Verification",
            "TEXT",
        ),
        (
            "enterprise",
            "Enterprise",
            "TEXT",
        ),
        (
            "sec_uid",
            "SEC_UID",
            "TEXT",
        ),
        (
            "uid",
            "UID",
            "TEXT",
        ),
        (
            "short_id",
            "SHORT_ID",
            "TEXT",
        ),
        (
            "avatar",
            "Avatar URL",
            "TEXT",
        ),
        (
            "cover",
            "Background URL",
            "TEXT",
        ),
        (
            "aweme_count",
            "Posts Count",
            "INTEGER",
        ),
        (
            "total_favorited",
            "Total Likes",
            "INTEGER",
        ),
        (
            "favoriting_count",
            "Liked Count",
            "INTEGER",
        ),
        (
            "follower_count",
            "Followers",
            "INTEGER",
        ),
        (
            "following_count",
            "Following",
            "INTEGER",
        ),
        (
            "max_follower_count",
            "Max Followers",
            "INTEGER",
        ),
    )
    search_user = (
        (
            "collection_time",
            "Collected At",
            "TEXT",
        ),
        (
            "uid",
            "UID",
            "TEXT",
        ),
        (
            "sec_uid",
            "SEC_UID",
            "TEXT",
        ),
        (
            "nickname",
            "Nickname",
            "TEXT",
        ),
        (
            "unique_id",
            "DouYin ID",
            "TEXT",
        ),
        (
            "short_id",
            "SHORT_ID",
            "TEXT",
        ),
        (
            "avatar",
            "Avatar URL",
            "TEXT",
        ),
        (
            "signature",
            "Bio",
            "TEXT",
        ),
        (
            "verify",
            "Verification",
            "TEXT",
        ),
        (
            "enterprise",
            "Enterprise",
            "TEXT",
        ),
        (
            "follower_count",
            "Followers",
            "INTEGER",
        ),
        (
            "total_favorited",
            "Total Likes",
            "INTEGER",
        ),
    )
    search_live = (
        (
            "collection_time",
            "Collected At",
            "TEXT",
        ),
        (
            "room_id",
            "Live ID",
            "TEXT",
        ),
        (
            "uid",
            "UID",
            "TEXT",
        ),
        (
            "sec_uid",
            "SEC_UID",
            "TEXT",
        ),
        (
            "nickname",
            "Nickname",
            "TEXT",
        ),
        (
            "short_id",
            "SHORT_ID",
            "TEXT",
        ),
        (
            "avatar",
            "Avatar URL",
            "TEXT",
        ),
        (
            "signature",
            "Bio",
            "TEXT",
        ),
        (
            "verify",
            "Verification",
            "TEXT",
        ),
        (
            "enterprise",
            "Enterprise",
            "TEXT",
        ),
    )
    hot = (
        (
            "position",
            "Rank",
            "INTEGER",
        ),
        (
            "word",
            "Content",
            "TEXT",
        ),
        (
            "hot_value",
            "Popularity",
            "INTEGER",
        ),
        (
            "cover",
            "Cover",
            "TEXT",
        ),
        (
            "event_time",
            "Time",
            "TEXT",
        ),
        (
            "view_count",
            "View Count",
            "INTEGER",
        ),
        (
            "video_count",
            "Video Count",
            "INTEGER",
        ),
        (
            "sentence_id",
            "SENTENCE_ID",
            "TEXT",
        ),
    )

    detail_keys = [i[0] for i in detail]
    detail_name = [i[1] for i in detail]
    detail_type = [i[2] for i in detail]
    comment_keys = [i[0] for i in comment]
    comment_name = [i[1] for i in comment]
    comment_type = [i[2] for i in comment]
    user_keys = [i[0] for i in user]
    user_name = [i[1] for i in user]
    user_type = [i[2] for i in user]
    search_user_keys = [i[0] for i in search_user]
    search_user_name = [i[1] for i in search_user]
    search_user_type = [i[2] for i in search_user]
    search_live_keys = [i[0] for i in search_live]
    search_live_name = [i[1] for i in search_live]
    search_live_type = [i[2] for i in search_live]
    hot_keys = [i[0] for i in hot]
    hot_name = [i[1] for i in hot]
    hot_type = [i[2] for i in hot]

    LoggerParams = {
        "detail": {
            "db_name": "DetailData.db",
            "title_line": detail_name,
            "title_type": detail_type,
            "field_keys": detail_keys,
        },
        "comment": {
            "db_name": "CommentData.db",
            "title_line": comment_name,
            "title_type": comment_type,
            "field_keys": comment_keys,
        },
        "user": {
            "db_name": "UserData.db",
            "title_line": user_name,
            "title_type": user_type,
            "field_keys": user_keys,
        },
        "mix": {
            "db_name": "MixData.db",
            "title_line": detail_name,
            "title_type": detail_type,
            "field_keys": detail_keys,
        },
        "search_general": {
            "db_name": "SearchData.db",
            "title_line": detail_name,
            "title_type": detail_type,
            "field_keys": detail_keys,
        },
        "search_user": {
            "db_name": "SearchData.db",
            "title_line": search_user_name,
            "title_type": search_user_type,
            "field_keys": search_user_keys,
        },
        "search_live": {
            "db_name": "SearchData.db",
            "title_line": search_live_name,
            "title_type": search_live_type,
            "field_keys": search_live_keys,
        },
        "hot": {
            "db_name": "BoardData.db",
            "title_line": hot_name,
            "title_type": hot_type,
            "field_keys": hot_keys,
        },
    }
    DataLogger = {
        "csv": CSVLogger,
        "xlsx": XLSXLogger,
        "sql": SQLLogger,
        # "mysql": BaseTextLogger,
    }

    def run(
        self,
        parameter: "Parameter",
        folder="",
        type_="detail",
        blank=False,
    ):
        root = parameter.root.joinpath(
            name := parameter.CLEANER.filter_name(folder, "Data")
        )
        self.compatible(
            parameter.root,
            root,
            name,
        )
        root.mkdir(exist_ok=True)
        params = self.LoggerParams[type_]
        logger = (
            BaseTextLogger
            if blank
            else self.DataLogger.get(parameter.storage_format, BaseTextLogger)
        )
        return root, params, logger

    @staticmethod
    def compatible(
        root: "Path",
        path: "Path",
        name: str,
    ):
        if (old := root.parent.joinpath(name)).exists() and not path.exists():
            move(old, path)
