from utils.http_wrapper import HttpWrapper
import urllib

class TelegramWrapper(object):
    API_BASE_URL = 'https://api.telegram.org'

    def __init__(self, bot_api_key):
        self.bot_api_key = bot_api_key

    def bot_send_message_to_chat(self, chat_id, message, use_markdown = True):
        if use_markdown:
            return HttpWrapper.get(f'{self.API_BASE_URL}/bot{self.bot_api_key}/sendMessage?chat_id={chat_id}&parse_mode=html&text={self.__url_encode(message)}')
        else:
            return HttpWrapper.get(f'{self.API_BASE_URL}/bot{self.bot_api_key}/sendMessage?chat_id={chat_id}&text={self.__url_encode(message)}')


    def bot_edit_message(self, chat_id, message_id, message):
        return HttpWrapper.get(f'{self.API_BASE_URL}/bot{self.bot_api_key}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={message}')

    def __url_encode(self, s):
        return urllib.parse.quote(s)