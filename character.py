import threading
import shelve
import datetime
import time
from brain import Brain

class Character(threading.Thread, Brain):
    def __init__(self, name):
        super().__init__()
        self.NAME = name
        s = shelve.open(self.NAME+ '.db', writeback = True)
        #Make character
        if not name in s:
            s.close()
            self.__make_char()
            s = shelve.open(self.NAME + '.db', writeback = True)
        #Read character
        try:
            self.data = s[self.NAME]
        finally:
            s.close()

    def __make_char(self):
        print('[Make %s]'%self.NAME)
        s = shelve.open(self.NAME + '.db', writeback = True)
        s[self.NAME] = {'activity_time': 172800}
        s.close()

    def update(self, key, value):
        s = shelve.open(self.NAME + '.db', writeback = True)
        try:
            s[self.NAME][key] = value
            self.data = s[self.NAME]
        finally:
            s.close()

    #Start life
    def run(self):
        print('[Start life]')
        while True:
            time.sleep(1)
            self.update('activity_time', self.data['activity_time'] - 1)
            print(self.data)

if __name__ == '__main__':
    hisui = Character('Hisui')
    hisui.start()
    print(hisui.listen('meltyknife', '@maidHisui 今日はいいね'))
    print('Main End')
