import tweepy
from my_tweepy import api as MY_API
from brain import Brain
from character import Character

BOT_S_NAME = '@maidHisui'
#hisui = Brain()
hisui = Character('Hisui')

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.text.count('RT @'): return True
        if not status.text.count(BOT_S_NAME): return True
        tweet_id = status.id
        user_id = status.user.id
        user_s_name = status.user.screen_name
        user_name = status.user.name
        user_text = status.text

        hisui_result = hisui.listen(user_s_name, user_text, True)
        hisui_text = hisui_result[0]
        hisui_love = hisui_result[1]
        self.tweet(tweet_id, user_s_name, hisui_text)
        if hisui_love >= 70:
            try:
                MY_API.create_friendship(user_id)
            except:
                print('[Already follow]')

    def on_error(self, status_code):
        print('[Error status code: ' + str(status_code) + ']')

    def on_timeout(self):
        print('[Timeout...]')

    def tweet(self, tweet_id, s_name, text):
        footer = ' twitter.com/%s/status/%s' % (s_name, tweet_id)
        count = len(text + footer)
        if count > 280:
            start = 280 - len(footer)
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
