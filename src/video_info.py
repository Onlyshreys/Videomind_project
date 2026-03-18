from youtube_transcript_api import YouTubeTranscriptApi 
from bs4 import BeautifulSoup
import requests
import re
from typing import Optional, List, Tuple

class GetVideo:
    @staticmethod
    def _fetch_piped_caption(video_id: str, label: str = "English") -> Optional[str]:
        try:
            response = requests.get(f"https://piped.video/api/v1/captions/{video_id}", timeout=10)
            response.raise_for_status()
            captions = response.json()
            track = next((c for c in captions if label.lower() in c.get("label", "").lower()), None)
            if not track and captions:
                track = captions[0]
            if not track or "url" not in track:
                return None
            caption_file = requests.get(track["url"], timeout=10)
            caption_file.raise_for_status()
            return caption_file.text
        except Exception:
            return None

    @staticmethod
    def _webvtt_to_plain(vtt_text: str) -> str:
        lines: List[str] = []
        for raw_line in vtt_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("WEBVTT") or "-->" in line or line.isdigit():
                continue
            lines.append(line)
        return " ".join(lines)

    @staticmethod
    def _webvtt_to_timestamped(vtt_text: str) -> str:
        entries: List[Tuple[str, str]] = []
        current_time: Optional[str] = None
        buffer: List[str] = []

        def flush():
            nonlocal buffer, current_time
            if current_time and buffer:
                entries.append((current_time, " ".join(buffer)))
            buffer = []
            current_time = None

        for raw_line in vtt_text.splitlines():
            line = raw_line.strip()
            if "-->" in line:
                flush()
                current_time = line.split("-->")[0].strip()
            elif not line:
                flush()
            elif not line.startswith("WEBVTT") and not line.isdigit():
                buffer.append(line)
        flush()

        def normalize(ts: str) -> str:
            base = ts.split('.')[0]
            parts = base.split(':')
            parts = [int(p) for p in parts]
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                h, m, s = 0, parts[0], parts[1]
            else:
                h, m, s = 0, 0, parts[0]
            return f"{h:02d}:{m:02d}:{s:02d}"

        return " ".join(f"{text} (time:{normalize(ts)})" for ts, text in entries)

    @staticmethod
    def Id(link):
        """Extracts the video ID from a YouTube video link."""

        pattern = r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})"

        match = re.search(pattern, link)

        if match:
            return match.group(1)

        return None

    @staticmethod
    def title(link):
        """Gets the title of a YouTube video."""
        video_id = GetVideo.Id(link)

        if not video_id:
            return "⚠️ Unable to fetch video title. Check the YouTube link."

        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "title" in data:
                return data["title"]
        except Exception:
            pass

        try:
            noembed_url = f"https://noembed.com/embed?url=https://youtube.com/watch?v={video_id}"
            response = requests.get(noembed_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "title" in data:
                return data["title"]
        except Exception:
            pass

        try:
            piped_url = f"https://piped.video/api/v1/video/{video_id}"
            response = requests.get(piped_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "title" in data:
                return data["title"]
        except Exception:
            pass

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(f"https://youtube.com/watch?v={video_id}", headers=headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            meta = soup.find("meta", itemprop="name")
            if meta and meta.get("content"):
                return meta["content"]
        except Exception:
            pass

        return "⚠️ Unable to fetch video title. Check the YouTube link."

    @staticmethod
    def transcript(link):
        """Gets the transcript of a YouTube video."""
        video_id = GetVideo.Id(link)

        if not video_id:
            return "⚠️ Invalid YouTube link."

        try:
            api = YouTubeTranscriptApi()

            transcript_list = api.list(video_id)

            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['en'])

            transcript_data = transcript.fetch()

            final_transcript = " ".join(snippet.text for snippet in transcript_data)

            return final_transcript

        except Exception as e:
            piped = GetVideo._fetch_piped_caption(video_id)
            if piped:
                return GetVideo._webvtt_to_plain(piped)
            return f"⚠️ Transcript error: {e}"

    @staticmethod
    def transcript_time(link):
        """Gets transcript with timestamps."""
        video_id = GetVideo.Id(link)

        if not video_id:
            return "⚠️ Invalid YouTube link."

        try:
            api = YouTubeTranscriptApi()

            transcript_list = api.list(video_id)
            transcript = transcript_list.find_transcript(['en'])
            transcript_data = transcript.fetch()

            final_transcript = ""

            for snippet in transcript_data:
                final_transcript += snippet.text

                seconds = int(snippet.start)

                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                sec = seconds % 60

                timestamp = f"{hours:02d}:{minutes:02d}:{sec:02d}"

                final_transcript += f' (time:{timestamp}) '

            return final_transcript

        except Exception as e:
            piped = GetVideo._fetch_piped_caption(video_id)
            if piped:
                return GetVideo._webvtt_to_timestamped(piped)
            return f"⚠️ Transcript error: {e}"