
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
cache_file = Path(__file__).parent / "video_cache.json"

MAX_RESULTS = 20


def collect_videos(keyword):

    if cache_file.exists():
        try:
            cache = json.loads(
                cache_file.read_text(encoding="utf-8")
            )

            cached_at = datetime.fromisoformat(
                cache["cached_at"]
            )

            cache_age = datetime.now(timezone.utc) - cached_at

            if (
                cache["keyword"] == keyword
                and cache_age < timedelta(hours=1)
                and cache.get("max_results") == MAX_RESULTS
            ):
                return cache["videos"]

        except (ValueError, KeyError, TypeError, OSError):
            pass

    seven_days_ago = (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    search_url = "https://www.googleapis.com/youtube/v3/search"

    search_params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": MAX_RESULTS,
        "order": "viewCount",
        "publishedAfter": seven_days_ago,
        "key": api_key
    }

    response = requests.get(
        search_url,
        params=search_params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    video_ids = [
        item["id"]["videoId"]
        for item in data["items"]
    ]

    if not video_ids:
        return []

    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    videos_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": api_key
    }

    response = requests.get(
        videos_url,
        params=videos_params,
        timeout=30
    )

    response.raise_for_status()

    videos = response.json()["items"]

    cache = {
        "keyword": keyword,
        "max_results": MAX_RESULTS,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "videos": videos
    }

    cache_file.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return videos
