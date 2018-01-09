import random
from bot_DB import Bot_DB
from pyknp import Jumanpp
from datetime import datetime

class Brain():

    def __init__(self):
        self.memory = Bot_DB()
        self.positive_messages = self.memory.get_table('positive_messages')
        self.normal_messages = self.memory.get_table('normal_messages')
        self.negative_messages = self.memory.get_table('negative_messages')

    def remember_person(self, name):
        self.now_name = name
        table = 'persons'
        column = 'name'
        conditions = {'name':name}
        person = self.memory.get_field(table, column, conditions)
        #Unknown person
        if person is None:
            values = [name, name, 50]
            self.memory.insert_record(table, values)
            print('Nice to meet to you, ' + name + '.')
        #Know person
        else:
            print('Hello, ' + name + '.')

    def listen(self, name, text, debug = None):
        text = self.__change_text_format(text)
        e_value = self.evaluate_text(text)
        if debug: print('evaluate_value: ' + str(e_value))
        if e_value > 0:
            random.shuffle(self.positive_messages)
            return self.positive_messages[0][0].replace('(NAME)', name)
        elif e_value == 0:
            random.shuffle(self.normal_messages)
            return self.normal_messages[0][0].replace('(NAME)', name)
        elif e_value < 0:
            random.shuffle(self.negative_messages)
            return self.negative_messages[0][0].replace('(NAME)', name)

    def __change_text_format(self, text):
        text = text.replace('\n', '')
        text_list = text.split(' ')
        # text_list[0] is bot's screen name,
        text = '、'.join(text_list[1:len(text_list)])
        return text

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

    def evaluate_text(self, text):
        e_value = 0
        result = self.analysis_text(text)
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
        return e_value

    def update_love(self, e_value):
        e_love = int(e_value * 100)
        if e_love > 5: e_love = 5
        elif e_love < -3: e_love = -3
        table = 'persons'
        column = 'love'
        conditions = {'name':self.now_name}
        love = self.get_field(table, column, conditions)
        love += e_love
        value = love
        self.update_field(table, column, conditions, value)

