from datetime import datetime
import json
import requests
import os
import time
from tqdm import tqdm

# класс "вк": загружает информацию по фото с вк на локальную машину в файл формата json
class vk:
    def __init__(self, user_id, token, version, count_to_upload):
        self.user_id = user_id
        self.token = token
        self.version = version
        self.count_to_upload = count_to_upload

#функция запроса информации о фотографиях пользователя и запись этой информации в файл json
    def request_photo(self):
        data_photo = {}
        URL = 'https://api.vk.com/method/photos.get'
        params = {'access_token': self.token,
                  'v': self.version,
                  'album_id': 'profile',
                  'owner_id': self.user_id,
                  'extended': 1,
                  'photo_sizes': 1
                  }
        res = requests.get(URL, params=params).json()
        max_count = res['response']['count']

        if self.count_to_upload < 1:
            print('Количество файлов для загрузки не должно быть меньше 1')
            return

        if self.count_to_upload > max_count:
            print(f'Количество файлов для загрузки не может превышать {max_count}')
            return

        params = {
                'album_id': 'profile',
                'extended': 1,
                'access_token': self.token,
                'v': self.version,
                'owner_id': self.user_id,
                'count': self.count_to_upload
            }

        URL = 'https://api.vk.com/method/photos.get'
        res = requests.get(URL, params=params).json()

        file_json = res['response']['items']

        for item in tqdm(file_json):
            time.sleep(3)
            likes = item['likes']['count']
            sizes = item['sizes']
            photo_type = sizes[-1]['type']
            max_size_url = sizes[-1]['url']

            str_date = item['date']
            str_date = datetime.fromtimestamp(str_date)
            str(str_date)

            if f'{likes}.jpg' not in data_photo:
                data_photo[f'{likes}.jpg'] = {'sizes': photo_type, "photo_url": max_size_url}
            else:
                data_photo[f'{likes}_{str_date}.jpg'] = {'sizes': photo_type, "photo_url": max_size_url}

            file_photo = f"photos/{self.user_id}/photo user.json"

            if not os.path.exists(os.path.dirname(file_photo)):
                os.makedirs(os.path.dirname(file_photo))

            with open(file_photo, 'w') as f:
                json.dump(data_photo, f, indent=2, ensure_ascii=False)



# класс "яндкс": загружает фото с вк на яндекс диск в отдельную папку
class yandex:
    def __init__(self, token, json_path, user_folder):
        self.token = token
        self.json_path = json_path
        self.user_folder = user_folder
    
    # метод  аутентификации на яндекс диске
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
    
    # метод открытия файла с данными по фото с локальной машины
    def get_data_photo_by_json(self):
        data_photo = dict()
        path = os.path.join(self.json_path, self.user_folder)

        if not os.path.exists(path):
            return False

        json_files_list = os.listdir(path)

        for json_file in tqdm(json_files_list):
            time.sleep(3)
            json_file_path = os.path.join(path, json_file)

            if not os.path.isdir(json_file_path):
                if not os.path.exists(json_file_path):
                    return False

                with open(json_file_path) as f:
                    data_photo = json.load(f)
        return data_photo
    
    # метод создания папки для загрузки фото из вк на яндекс диск
    def creat_folder(self, folders: list):
        headers = self.get_headers()
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        
        root_dir = ""

        for index, folder in tqdm(enumerate(folders)):
            time.sleep(3)
            if index == 0:
                params = {
                    "path": folder
                }

                res = requests.put(url, headers=headers, params=params)
                root_dir += f"{folder}/"

                if res.status_code == 201:
                    f_str = f"Создана папка {folder}"
                    print(f_str)
            else:
                root_dir += f"{folders[index]}/"
                params = {
                    "path": root_dir
                }

                res = requests.put(url, headers=headers, params=params)

                if res.status_code == 201:
                    f_str = f"Создана папка пользователя id {folder}, путь папки {root_dir}"
                    print(f_str)

        return root_dir
    
    # функция для загрузки фото с вк на яндекс диск
    def upload(self):
        data_photo = self.get_data_photo_by_json()

        if not data_photo:
            print("Нет файлов для загрузки")
            return

        headers = self.get_headers()
        root_path = self.creat_folder(["VK", f"{self.user_folder}"])
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload/"

        for item in tqdm(data_photo):
            time.sleep(3)
            url_path = data_photo[item]["photo_url"]
            file_photo = item

            params = {
                "path": f"{root_path}{file_photo}",
                "url": url_path
            }

            res = requests.post(url=url, headers=headers, params=params)

            if res.status_code == 202:
                print(f"Загрузка файла {file_photo} произошла успешно")
        print("Загрузка всех файлов завершена")

        photo_url = os.path.join(self.json_path, self.user_folder)
        backup_path = os.path.join(photo_url, "backup")
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)


if __name__ == '__main__':
    vk_token = ''
    yandex_token = ''
    user_name_id = '552934290'
    version = "5.131"
    files_path = os.path.join(os.getcwd(), 'photos')

    vkontakte = vk(token=vk_token, user_id=user_name_id, version=version, count_to_upload=5)
    vkontakte.request_photo()

    yandexdisk = yandex(token=yandex_token, json_path=files_path, user_folder=user_name_id)
    yandexdisk.upload()