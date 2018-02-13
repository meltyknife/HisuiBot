import random
import re
from bot_DB import Bot_DB
from pyknp import Jumanpp
from datetime import datetime


import requests
import json
import types

class Brain():

    memory = Bot_DB()
    positive_messages = memory.get_table('positive_messages')
    normal_messages = memory.get_table('normal_messages')
    negative_messages = memory.get_table('negative_messages')
    my_name = 'maidhisui'
    URL_PATTERN = ' http.*'
    AT_PATTERN = '@.* |\n'
    url_re = re.compile(URL_PATTERN)
    at_re = re.compile(AT_PATTERN)

    DOCOMO_KEY =''
    ENDPOINT  = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=REGISTER_KEY'
    URL = ENDPOINT.replace('REGISTER_KEY', DOCOMO_KEY)
    context = ''
    payload = {'utt' : '', 'context': ''}
    headers = {'Content-type': 'application/json'}

    """
    def __init__(self):
        self.memory = Bot_DB()
        self.positive_messages = self.memory.get_table('positive_messages')
        self.normal_messages = self.memory.get_table('normal_messages')
        self.negative_messages = self.memory.get_table('negative_messages')
    """

    def remember_person(self, name, debug = None):
        table = 'persons'
        column = 'name'
        conditions = {'name':name}
        person = self.memory.get_field(table, column, conditions)
        #Unknown person
        if person is None:
            values = [name, name, 50]
            self.memory.insert_record(table, values)
            if debug: print('[Nice to meet to you, %s.]'% name)
        #Know person
        else:
            if debug: print('[Hello, %s.]'% name)

    def listen(self, s_name, text, debug = None):
        if debug: print()
        self.remember_person(s_name, debug)
        text = self.__change_text_format(text)
        result = self.analysis_text(text)
        self.is_change_call(s_name, result)
        love = self.update_love(s_name)
        if debug: print('[love:%d]'% love)

        table = 'persons'
        column = 'call_name'
        conditions = {'name':s_name}
        call_name = self.memory.get_field(table, column, conditions)

        e_value = self.evaluate_text(result, debug)

        #1回目の会話の入力
        if self.context == '':
            utt_content = text
            self.payload['utt'] = utt_content
            r = requests.post(self.URL, data=json.dumps(self.payload), headers=self.headers)
            data = r.json()
            #jsonの解析
            response = data['utt']
            self.context = data['context']
            #表示
            print("response: %s" %(response))
            return [response, love]
        #2回目以降の会話(Ctrl+Cで終了)
        else:
            utt_content = text
            self.payload['utt'] = utt_content
            self.payload['context'] = self.context
            r = requests.post(self.URL, data=json.dumps(self.payload), headers=self.headers)
            data = r.json()
            response = data['utt']
            self.context = data['context']
            print("response: %s" %(response))
            return [response, love]
        """
        if e_value > 0:
            random.shuffle(self.positive_messages)
            message = self.positive_messages[0][0].replace('NAME', call_name)
        elif e_value == 0:
            random.shuffle(self.normal_messages)
            message = self.normal_messages[0][0].replace('NAME', call_name)
        elif e_value < 0:
            random.shuffle(self.negative_messages)
            message = self.negative_messages[0][0].replace('NAME', call_name)
        return [message, love]
        """

    def make_markov(self):
        table = 'markov_groups'
        end_keywords = [']', '。', '．']
        list_sentence = []
        next_keyword = '['
        while True:
            conditions = {'word1':next_keyword}
            group = self.memory.get_random_record(table, conditions)
            list_sentence.extend(group[:2])
            next_keyword = group[2]
            if next_keyword in end_keywords: break
        sentence = ''.join(list_sentence)
        sentence = sentence.replace('\u3000','')
        sentence = sentence.replace('[','')
        if 'NAME' in sentence:
            table = 'persons'
            conditions = None
            user_data = self.memory.get_random_record(table, conditions)
            sentence = sentence.replace('NAME', user_data[1])
        return sentence

    #Special method(not generic)
    def is_change_call(self, s_name, result):
        #Only update call_name
        mrphs = result.mrph_list()
        for i in range(len(mrphs)):
            if i > 0 and i + 1 < len(mrphs):
                midasi  = mrphs[i].midasi
                if midasi == 'と' or midasi == 'って':
                    print(midasi)
                    repname = mrphs[i + 1].repname
                    if repname == '呼ぶ/よぶ' or repname == '呼べる/よべる':
                        text = ''
                        for mrph in mrphs: text += mrph.midasi
                        print('Update call_name')
                        tmp = text.split(midasi)
                        call_name = tmp[0]
                        call_name = call_name.replace('、', '')
                        call_name = call_name.replace('@', '')
                        print(call_name)
                        table = 'persons'
                        column = 'call_name'
                        conditions = {'name':s_name}
                        value = call_name
                        self.memory.update_field(table, column, conditions, value)

    def update_call_name(self, call_name):
        table = 'persons'
        column = 'call_name'
        conditions = {'name':self.now_name}
        value = call_name
        self.update_field(table, column, conditions, value)

    def analysis_text(self, text, debug = None):
        jumanpp = Jumanpp()
        #There may be unknown error in jumanpp. what...
        try:
            result = jumanpp.analysis(text)
        except:
            return None
        if debug: self.__print_analyzed(result)
        return result

    def __change_text_format(self, text):
        print('[Original input:%s]'% text)
        text = self.url_re.sub('', text)
        text = self.at_re.sub('', text)
        print('[Changed input:%s]'% text)
        return text

    def __print_analyzed(self, result):
        for mrph in result.mrph_list():
            print('見出し：' + mrph.midasi)
            print('読み：' + mrph.yomi)
            print('品詞：' + mrph.hinsi)
            print('原型：' + mrph.genkei)
            print('品詞細分類：' + mrph.bunrui)
            print('活用型：' + mrph.katuyou1)
            print('活用形：' + mrph.katuyou2)
            print('意味情報：' + mrph.imis)
            print('代表表記：' + mrph.repname)
            print()

    def evaluate_text(self, result, debug = None):
        e_value = 0
        if result is None: return e_value
        table = 'polarity'
        column = 'value'
        for mrph in result.mrph_list():
            conditions = {'midasi':mrph.midasi, 'yomi':mrph.yomi, 'hinsi':mrph.hinsi}
            tmp_value = self.memory.get_field(table, column, conditions)
            if tmp_value is None:
                conditions = {'yomi':mrph.yomi, 'hinsi':mrph.hinsi}
                tmp_value = self.memory.get_field(table, column, conditions)
            if not tmp_value is None: e_value += tmp_value
        e_value /= len(result.mrph_list())
        if debug: print('[evaluate_value:%s]'% e_value)
        return e_value

    def update_love(self, s_name):
        table = 'persons'
        column = 'love'
        conditions = {'name':s_name}
        love = self.memory.get_field(table, column, conditions)
        love += 1
        value = love
        self.memory.update_field(table, column, conditions, value)
        return love
