# -*- coding:utf-8 -*-
import tweepy

API_KEY = ''
API_SECRET = ''
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)

ACCESS_KEY = ''
ACCESS_SECRET = ''

auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

api = tweepy.API(auth)
print('[API setup done]')
