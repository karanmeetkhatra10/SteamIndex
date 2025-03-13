import requests
from bs4 import BeautifulSoup
import yt_dlp
import json
import os
from datetime import datetime, timedelta
import pytz

# All channel names (weird name for buccaneers because of they way it is set up)
channel_names = ["49ers", "AtlantaFalcons", "azcardinals", "BaltimoreRavens",
                 "broncos", "browns", "channel/UC0Wwu7r1ybaaR09ANhudTzA", "buffalobills",
                 "CarolinaPanthers", "chargers", "ChicagoBears", "colts", "commandersnfl",
                 "DallasCowboys", "detroitlionsnfl", "HoustonTexans", "jaguars", "KansasCityChiefs",
                 "LARams", "MiamiDolphins", "NewOrleansSaints", "NewYorkGiants", "nyjets", "packers",
                 "raiders", "Seahawks", "steelers", "patriots", "Titans", "vikings"]
# URLs for Eagles and Bengals video pages
eagles_url = 'https://www.philadelphiaeagles.com/video/press-conferences'
bengals_url = 'https://www.bengals.com/video/pressconferences'

# Path to the directory containing ffmpeg and ffprobe executables (if not in PATH)
ffmpeg_location = 'c:/users/12505/AppData/Local/Programs/Python/Python312/Lib/site-packages/ffmpeg/bin'
# Limiting the number of videos to fetch. No need to fetch all the videos
max_videos_to_fetch = 20


def load_downloaded_videos(record_file):
    if os.path.exists(record_file):
        with open(record_file, 'r') as f:
            return json.load(f)
    return []


def save_downloaded_videos(record_file, downloaded_videos):
    with open(record_file, 'w') as f:
        json.dump(downloaded_videos, f)


def download_audio(url, output_path, upload_date, duration):
    ydl_opts = {
        'outtmpl': f'{output_path}/{upload_date} - {duration} - %(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_location,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error downloading {url}: {e}")


# scraper function built to download videos straight from the team's websites
# (currently for eagles and bengals as they both don't upload to Youtube)
def scrape_video_urls(page_url, tag, video_class, link_type=None):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    video_urls = []
    print(f"Checking {max_videos_to_fetch} videos from the link...{page_url}")
    if link_type:
        # Case 1: Specific link_type attribute condition, both for eagles and bengals
        if page_url == eagles_url:
            for video_tag in soup.find_all(tag, {'data-link_type': link_type}):
                video_url = 'https://www.philadelphiaeagles.com' + video_tag['href']
                video_urls.append(video_url)
                if len(video_urls) >= max_videos_to_fetch:
                    break
        elif page_url == bengals_url:
            for video_tag in soup.find_all(tag, {'data-link_type': link_type}):
                video_url = 'https://www.bengals.com' + video_tag['href']
                video_urls.append(video_url)
                if len(video_urls) >= max_videos_to_fetch:
                    break
    else:
        # Case 2: Any tag with specific class condition, only for bengals top 4 videos
        for video_tag in soup.find_all(tag, class_=video_class):
            video_url = 'https://www.bengals.com' + video_tag['href']
            video_urls.append(video_url)
            if len(video_urls) >= max_videos_to_fetch:
                break
    return video_urls


def get_latest_videos(channel_url, downloaded_videos):
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'playlistend': max_videos_to_fetch,
        'skip_download': True,
        'match_filter': '!is_live'  # Skip live videos
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        one_day_ago = datetime.now() - timedelta(days=7)  # 7-day buffer
        new_videos = []
        print(f"Checking {len(result['entries'])} videos from the channel...{channel_url}")
        for entry in result['entries']:
            video_id = entry['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                # Get detailed info for each video to check upload date
                with yt_dlp.YoutubeDL({'quiet': True, 'match_filter': '!is_live'}) as ydl:
                    video_info = ydl.extract_info(video_url, download=False)
                duration = seconds_to_hms(video_info['duration'])
                print(duration)
                upload_date = datetime.strptime(video_info['upload_date'], '%Y%m%d')
                print(upload_date)
                # print("Video:" , datetime.strptime(video_info['upload_date'], '%Y%m%d'))
                if upload_date > one_day_ago and video_id not in downloaded_videos:
                    print(f"Adding video {video_url}, uploaded on {video_info['upload_date']}")
                    new_videos.append((video_url, video_info['upload_date'], duration))
                else:
                    print(f"Skipping video {video_url}, uploaded on {video_info['upload_date']}")
                    break
            except Exception as e:
                print(f"Error processing video {video_url}: {e}")

        return new_videos


def seconds_to_hms(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hours:02}{minutes:02}{seconds:02}"


# function built to download videos that were scraped from the website
def process_videos(video_urls, downloaded_videos, output_dir, record_file):
    for video_url in video_urls:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                video_info = ydl.extract_info(video_url, download=False)
            duration = seconds_to_hms(video_info['duration'])
            print(duration)
            upload_date = datetime.strptime(video_info['upload_date'], '%Y%m%d')
            print(upload_date)
            video_id = video_url.split('/')[-1]
            if video_id not in downloaded_videos:
                download_audio(video_url, output_dir, video_info['upload_date'], duration)
                downloaded_videos.append(video_id)
                save_downloaded_videos(record_file, downloaded_videos)
            else:
                print(f"Skipping video {video_url}, uploaded on {video_info['upload_date']}")
                break
        except Exception as e:
            print(f"Error processing video {video_url}: {e}")


def main():
    for channel_name in channel_names:
        # Path to save the record of downloaded video IDs
        record_file = f'videos/{channel_name}/downloaded_videos.json'
        # Directory to save downloaded audio files
        output_dir = f'videos/{channel_name}'
        # Channel URL
        if channel_name == "channel/UC0Wwu7r1ybaaR09ANhudTzA" or channel_name == "detroitlionsnfl":
            channel_url = f'https://www.youtube.com/{channel_name}/videos'
        elif channel_name == "Seahawks":
            channel_url = f'https://www.youtube.com/@SeahawksPressers/videos'
        else:
            channel_url = f'https://www.youtube.com/c/{channel_name}/videos'

        # To Get Live Streams
        if channel_name == "channel/UC0Wwu7r1ybaaR09ANhudTzA" or channel_name == "detroitlionsnfl":
            live_url = f'https://www.youtube.com/{channel_name}/streams'
        else:
            live_url = f'https://www.youtube.com/c/{channel_name}/streams'
        print(channel_url)
        downloaded_videos = load_downloaded_videos(record_file)
        latest_videos = get_latest_videos(channel_url, downloaded_videos)
        latest_live = get_latest_videos(live_url, downloaded_videos)
        try:
            for video_url, upload_date, duration in latest_videos:  # Get latest videos
                print(f"Downloading audio for {video_url}")
                download_audio(video_url, output_dir, upload_date, duration)
                video_id = video_url.split('=')[1]
                downloaded_videos.append(video_id)

            for video_url, upload_date, duration in latest_live:  # Get latest live streams
                print(f"Downloading audio for {video_url}")
                download_audio(video_url, output_dir, upload_date, duration)
                video_id = video_url.split('=')[1]
                downloaded_videos.append(video_id)

            save_downloaded_videos(record_file, downloaded_videos)
        except Exception as e:
            print(f"Error processing video {video_url}: {e}")
            continue
    # Eagles videos
    channel_name = 'eagles'
    record_file = f'videos/{channel_name}/downloaded_videos.json'
    output_dir = f'videos/{channel_name}'

    downloaded_videos = load_downloaded_videos(record_file)
    eagles_video_urls = scrape_video_urls(eagles_url, 'a', None, 'video-presspass-and-conferences')
    process_videos(eagles_video_urls, downloaded_videos, output_dir, record_file)

    # Bengals videos
    channel_name = 'Bengals'
    record_file = f'videos/{channel_name}/downloaded_videos.json'
    output_dir = f'videos/{channel_name}'

    # Bengals videos (split into two functions because the top 4 posted videos have the first class meanwhile
    # the remaining batch of videos is a part of a different class
    downloaded_videos = load_downloaded_videos(record_file)
    bengals_video_urls = scrape_video_urls(bengals_url, None, 'd3-o-media-object d3-o-media-object--vertical')
    process_videos(bengals_video_urls, downloaded_videos, output_dir, record_file)

    downloaded_videos = load_downloaded_videos(record_file)
    bengals_video_urls = scrape_video_urls(bengals_url, 'a', None, 'press-conferences')
    process_videos(bengals_video_urls, downloaded_videos, output_dir, record_file)


if __name__ == "__main__":
    main()
    print("Done!")
