import sqlite3
from datetime import datetime

class Bot_DB:
    def __init__(self):
        self.con = sqlite3.connect('bot_DB.db', isolation_level = None)
        self.cur = self.con.cursor()

    def init_persons(self):
        sql = u"""
        create table if not exists persons(
            name varchar(255),
            call_name varchar(255),
            love integer
        );
        """
        self.con.execute(sql)

    def init_polarity(self):
        sql = u"""
        create table if not exists polarity(
            midasi varchar(255),
            yomi varchar(255),
            hinsi varchar(255),
            value real
        );
        """
        self.con.execute(sql)
        #Take a little while.
        F_PATH = 'resources/PolarityDictionary.txt'
        f = open(F_PATH)
        lines = f.readlines()
        for line in lines:
            tmp_line = line.replace('\n','')
            values = tmp_line.split(':')
            midasi = values[0]
            yomi = values[1]
            hinsi = values[2]
            value = float(values[3])
            in_values = [midasi, yomi, hinsi, value]
            self.insert_record('polarity', in_values)

    def init_messages(self):
        MESSAGE_TYPES = ['positive', 'normal', 'negative']
        for m_type in MESSAGE_TYPES:
            sql = u"""
            create table if not exists %s(
                message varchar(255)
            );
            """ % (m_type + '_messages')
            self.con.execute(sql)
            F_PATH = 'resources/' + m_type + '_messages.txt'
            f = open(F_PATH)
            lines = f.readlines()
            for line in lines:
                tmp_line = line.replace('\n','')
                values = [tmp_line]
                self.insert_record(m_type + '_messages', values)

    def delete_table(self, table):
        sql = "drop table %s" % (table)
        self.cur.execute(sql)

    def insert_record(self, table, values):
        sql = u"insert into %s values" % (table)
        insert = ' ('
        for value in values:
            insert += self.__change_value_format(value)
            insert += ','
        insert = insert[0:len(insert)-1]
        insert += ')'
        sql += insert
        self.con.execute(sql)

    def update_field(self, table, column, conditions, value):
        sql = u"update %s set %s = '%s'" % (table, column, value)
        where = self.__make_where(conditions)
        sql += where
        self.con.execute(sql)

    def delete_record(self, table, conditions):
        sql = u'delete from %s' % (table)
        where = self.__make_where(conditions)
        sql += where
        self.con.execute(sql)

    def get_field(self, table, column, conditions):
        sql = u'select %s from %s' % (column, table)
        if not conditions is None:
            where = self.__make_where(conditions)
            sql += where
        self.cur.execute(sql)
        record = self.cur.fetchone()
        if record is None: return None
        else: return record[0]

    def get_table(self, table):
        sql = u'select * from %s' % (table)
        self.cur.execute(sql)
        table_tuple = self.cur.fetchall()
        return table_tuple

    def print_table(self, table):
        sql = u"select * from %s" % (table)
        self.cur.execute(sql)
        for row in self.cur:
            print(row)

    def print_db(self):
        sql = u'select * from sqlite_master'
        self.cur.execute(sql)
        for row in self.cur:
            print(row)

    def __change_value_format(self, value):
        if isinstance(value, str): return "'" + value + "'"
        else: return str(value)

    def __make_where(self, conditions):
        text = u' where '
        for column, value in conditions.items():
            text += column + '='
            text += self.__change_value_format(value)
            text += ' and '
        return text[0:len(text) - 5]
