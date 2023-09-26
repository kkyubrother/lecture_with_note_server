import requests

from lecture_with_note_server.utils.config import load_google_api_key


def get_youtube_video_title_from_video_id(video_id: str) -> dict:
    api_key = load_google_api_key()
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        title = data['items'][0]['snippet']['title']
        return {"title": title}

    else:
        print('An error occurred:', response.status_code)
        raise ValueError(response.text)
