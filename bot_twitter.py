import datetime
import tweepy
from my_tweepy import api as MY_API
from brain import Brain

BOT_S_NAME = '@maidplum'
hisui = Brain()

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.text.count('RT @'): return True
        user_s_name = status.user.screen_name
        user_name = status.user.name
        user_text = status.text

        hisui.remember_person(user_s_name)
        hisui_text = hisui.listen(user_name, user_text)
        self.tweet('@' + user_s_name + ' ' + hisui_text)

    def on_error(self, status_code):
        print('[Error status code: ' + str(status_code) + ']')

    def on_timeout(self):
        print('[Timeout...]')

    def tweet(self, text):
        todaydetail = datetime.datetime.today()
        now = todaydetail.strftime('%H:%M:%S')
        footer = '【三咲町 ' + now + '】'
        count = len(text + footer)
        if count > 140:
            start = 140 - len(footer)
            end = len(text)
            text_list = list(text)
            del text_list[start:end]
            text = ''.join(text_list)
        out_text = text + footer
        MY_API.update_status(status = out_text)

if __name__ == '__main__':
    stream_listener = StreamListener()
    stream = tweepy.Stream(auth = MY_API.auth, listener = stream_listener)
    print('[Streaming]')
    stream.filter(track = [BOT_S_NAME])
    #myStream.userstream()
