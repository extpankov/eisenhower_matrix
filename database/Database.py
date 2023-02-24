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
    
    def remove_record(self, user_id, type, number):
        req = self.get_records(user_id, type)[number - 1]
        print(req)
        self.cursor.execute("DELETE FROM `records` WHERE `user_id` =? AND `type` = ? AND `record` = ? AND `description` =? AND `deadline` = ?", (req[0], req[1], req[2], req[3], req[4]))
        self.conn.commit()
        return True