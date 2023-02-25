import sqlite3

class Database():
    def __init__(self):
        self.conn = sqlite3.connect('database/database.db')
        self.cursor = self.conn.cursor()

    def add_record(self, user_id, type, name, desc, deadline = None):
        self.cursor.execute("INSERT INTO `records` (`user_id`, `type`, `record`, `description`, `deadline`) VALUES (?, ?, ?, ?, ?)", (user_id, type, name, desc, deadline))
        self.conn.commit()

    def get_records(self, user_id, type):
        result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` = ? AND `type` = ?", (user_id, type))
        return result.fetchall()
    
    def get_completed_records(self, user_id, type):
        result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` =? AND `type` =? AND `is_completed` = 1", (user_id, type))
        return result.fetchall()
    
    def __get_record_id(self, user_id, type, number):
        res = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` =? AND `type` =?", (user_id, type)).fetchall()[number]
        return res[0]
    
    def remove_record(self, user_id, type, number):
        id = self.__get_record_id(user_id, type, number)
        self.cursor.execute("DELETE FROM `records` WHERE `id` =?", (id,))
        self.conn.commit()
        return True
    
    def edit_record(self, user_id, type, number, name = None, desc = None, deadline = None):
        id = self.__get_record_id(user_id, type, number)
        if name == None and desc == None and deadline == None:
            return None
        if name != None:
            self.cursor.execute("UPDATE `records` SET `record` =? WHERE `id` =?", (name, id))
        elif desc!= None:
            self.cursor.execute("UPDATE `records` SET `description` =? WHERE `id` =?", (desc, id))
        elif deadline!= None:
            self.cursor.execute("UPDATE `records` SET `deadline` =? WHERE `id` =?", (deadline, id))
        self.conn.commit()
        return True
    
    def delegate_record(self, user_id, type, number, new_type):
        id = self.__get_record_id(user_id, type, number)
        self.cursor.execute("UPDATE `records` SET `type` =? WHERE `id` =?", (new_type, id))
        self.conn.commit()
        return True

    def complete_record(self, user_id, type, number):
        id = self.__get_record_id(user_id, type, number)
        self.cursor.execute("UPDATE `records` SET `is_completed` = 1 WHERE `id` = ?", (id,))
        self.conn.commit()
        return True
