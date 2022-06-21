import os
import pathlib
import random
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


def get_url_extension(file_path):
    parsed = urlparse(file_path)
    path, extension = os.path.splitext(parsed.path)
    return extension


def save_image_file(directory, image_url, file_name):
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    extension = get_url_extension(image_url)
    with open(f'{directory}{file_name}{extension}', 'wb') as file:
        file.write(image_response.content)


def get_upload_url():
    url = f'{vk_api_url}photos.getWallUploadServer'
    params = {
        'group_id': group_id,
        'access_token': vk_api_token,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    content = response.json()
    upload_url = content.get('response').get('upload_url')
    return upload_url


def upload_photo(upload_url, file_name):
    with open(f'{directory}{file_name}.png', 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        content = response.json()
        return content


def save_uploaded_photo(response):
    photo = response.get('photo')
    server = response.get('server')
    hash = response.get('hash')
    params = {
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash,
        'access_token': vk_api_token,
        'v': '5.131'
    }
    url = f'{vk_api_url}photos.saveWallPhoto'
    save_response = requests.post(url, params=params)
    save_response.raise_for_status()
    content = save_response.json()
    save_response = content.get('response')
    return save_response


def publish_comics(save_response, message):
    media_id = save_response[0].get('id')
    owner_id = save_response[0].get('owner_id')
    url = f'{vk_api_url}wall.post'
    params = {
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': message,
        'access_token': vk_api_token,
        'v': '5.131'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    directory = '/comics/'
    pathlib.Path(directory).mkdir(exist_ok=True)
    vk_api_token = os.getenv('ACCESS_TOKEN')
    group_id = os.getenv('GROUP_ID')
    vk_api_url = 'https://api.vk.com/method/'
    comics_url = 'https://xkcd.com/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()
    num = response.json().get('num')
    random_comics_num = random.randint(1, num)
    random_comics_url = f'https://xkcd.com/{random_comics_num}/info.0.json'
    comics_response = requests.get(random_comics_url)
    comics_response.raise_for_status()
    content = comics_response.json()
    img = content.get('img')
    file_name = content.get('title')
    message = content.get('alt')
    save_image_file(directory, img, file_name)
    upload_response = upload_photo(get_upload_url(), file_name)
    save_response = save_uploaded_photo(upload_response)
    publish_comics(save_response, message)
    os.remove(f'{directory}{file_name}.png')
