import requests
import time
import Time
from urllib.request import urlopen
from skimage.io import *
from io import BytesIO


class Bot:
    def __init__(self, url, token, update_frequency=1):
        self.URL = url
        self.TOKEN = token
        self.offset = 0

        # время обновления в секундах
        self.update_frequency = update_frequency

    def get_updates(self):
        """
        метод который получет новые сообщения для бота, опрашивая сервер телеграмма
        """
        data = {'offset': self.offset, 'limit': 0, 'timeout': 0}
        return self._send_request('/getUpdates', data)

    def execute_update(self, update):
        """
        метод выполняет комманды которые ему приходят от пользователей
        """
        self.update_offset(update)
        if ('message' not in update) or \
                ('text'not in update['message'] and 'photo' not in update['message']):
            return
        info = {
            'chat': update['message']['chat'],
            'from': update['message']['from'],
            'date': update['message']['date'],
            'message_id': update['message']['message_id']
        }

        if 'reply_to_message' in update['message']:
            info['reply_to_message'] = update['message']['reply_to_message']

        if 'text' in update['message']:
            info['text'] = update['message']['text']
            if update['message']['text'].strip()[0] == '/':
                command = update['message']['text'].strip().split(" ")
                method_name = "on_"+command[0][1:]+"_command"
                if hasattr(self, method_name):
                    method_to_call = getattr(self, method_name)
                    method_to_call(info)
                elif hasattr(self, "default_command"):
                    self.default_command(info)
            elif hasattr(self, "on_message_received"):
                self.on_message_received(info)
            else:
                return
        if 'photo' in update['message']:
            if hasattr(self, "on_photo_received"):
                info['photo'] = self._get_photo(update)
                if 'caption' in update['message']:
                    info['caption'] = update['message']['caption']
                else:
                    info['caption'] = ""
                self.on_photo_received(info)
            else:
                return

    def _send_request(self, command, data, files=None):
        try:
            if files is None:
                res = requests.post(self.URL + self.TOKEN + command, data=data)
            else:
                res = requests.post(self.URL + self.TOKEN + command, data=data, files=files)
            if res is not None and not res.status_code == 200:
                print("answer is not sent")
                return None
            else:
                return res
        except Exception as ex:
            print(ex)
            return None

    def send_message(self, chat_id, text):
        data = {
            'chat_id': str(chat_id),
            'text': text,
            'parse_mode': 'HTML'
        }
        return self._send_request('/sendMessage', data)

    def send_photo(self, chat_id, img, caption):
        data = {
            'chat_id': str(chat_id),
            'parse_mode': 'HTML',
            'caption': caption
        }

        str_io = BytesIO()
        imsave(str_io, img, plugin='pil', format_str='png')
        str_io.seek(0)

        files = {
            'photo': str_io
        }
        self._send_request('/sendPhoto', data, files=files)

    def _get_photo(self, update):
        # получаем номер фотки с самым большим размром
        file_id = update['message']['photo'][-1]['file_id']
        response = self._send_request('/getFile', data={'file_id': file_id})
        if response is None:
            return None
        photo_path = response.json()['result']['file_path']
        # request = requests.get("https://api.telegram.org/file/bot" + self.TOKEN + "/" +
        #                        photo_path, verify=False)
        request = urlopen("https://api.telegram.org/file/bot" + self.TOKEN + "/" + photo_path)
        if request is None:
            return None
        try:
            img = imread(request)
            return img
        except:
            return None

    def update_offset(self, update):
        """
        метод который обновляет id поселднего обработанного запроса
        """
        self.offset = update['update_id'] + 1

    def run(self):
        lecture = Time.Lecture()
        print("Bot is started")
        try:
            while True:
                time.sleep(self.update_frequency)
                # print("Current lecture num:", lecture.current_num)
                self.check(lecture)
                request = self.get_updates()
                # print("update...")
                if request is None:
                    continue
                # print(request.json())
                for update in request.json()['result']:
                    self.execute_update(update)

        except KeyboardInterrupt:
            print("\nBot will come back!")
