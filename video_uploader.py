import os
import json
import requests
import cloudinary
import cloudinary.uploader
import google.oauth2.credentials
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload

# Configuration
CLOUDINARY_CONFIG = {
    'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
}
YOUTUBE_CLIENT_SECRETS = json.loads(os.environ.get('YOUTUBE_CLIENT_SECRETS'))
VIDEO_LINKS_FILE = 'video_links.txt'


def get_youtube_service():
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(YOUTUBE_CLIENT_SECRETS, [
        'https://www.googleapis.com/auth/youtube.upload'])
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
    return youtube


def upload_video_to_cloudinary(video_path):
    cloudinary.config(
        cloud_name=CLOUDINARY_CONFIG['cloud_name'],
        api_key=CLOUDINARY_CONFIG['api_key'],
        api_secret=CLOUDINARY_CONFIG['api_secret']
    )
    response = cloudinary.uploader.upload_large(video_path, resource_type="video")
    return response['secure_url']


def upload_video_to_youtube(video_path):
    youtube = get_youtube_service()
    request_body = {
        'snippet': {
            'title': 'Your Video Title',
            'description': 'Your Video Description',
            'tags': ['tag1', 'tag2'],
            'categoryId': '22'  # Category ID for "People & Blogs"
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    with open(video_path, 'rb') as video_file:
        youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        ).execute()


def process_videos():
    with open(VIDEO_LINKS_FILE, 'r') as file:
        video_link = file.read().strip()

    # Download video
    video_response = requests.get(video_link)
    video_path = '/tmp/temp_video.mp4'
    with open(video_path, 'wb') as file:
        file.write(video_response.content)

    # Upload to Cloudinary
    cloudinary_video_url = upload_video_to_cloudinary(video_path)

    # Upload to YouTube
    upload_video_to_youtube(video_path)


if __name__ == "__main__":
    process_videos()
