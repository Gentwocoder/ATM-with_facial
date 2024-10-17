import sqlite3


class backend:    
    def user_table(self):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS user (
                           user_id INTEGER PRIMARY KEY,
                           account_holder TEXT,
                           password CHAR,
                           account_balance REAL,
                           face_enrolled BLOB
                           )""")
            connection.commit()

    def transaction_table(self):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
                           id INTERGER PRIMARY KEY,
                           user_id INTEGER,
                           amount REAL,
                           transaction_type TEXT NOT NULL,
                           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY(user_id) REFERENCES user(user_id)
                           )""")
            connection.commit()

    def create_user(self, account_holder, password, account_balance, face_enrolled):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO user VALUES(NULL, ?,?,?,?)""", (account_holder, password, account_balance, face_enrolled))
            connection.commit()

    
    def get_user_id(self, account_holder):
                with sqlite3.connect("data.db") as connection:
                    cursor = connection.cursor()

                    # Fetch user_id for the given card number
                    cursor.execute("SELECT id FROM user WHERE account_holder=?", (account_holder))
                    result = cursor.fetchone()
                    connection.commit()

                    if result:
                        return result[0]  # Return user_id
                    else:
                        return None
                    
    # Function to log the transaction
    def log_transaction(self, amount, transaction_type):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()

        # Insert the transaction record into the transactions table
            cursor.execute('''
                INSERT INTO transactions (amount, transaction_type) 
                VALUES (?, ?, ?)
            ''', (amount, transaction_type))
        
            connection.commit()
    
    def update_balance(self, account_holder, account_balance, amount):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user SET account_balance=account_balance + ? WHERE account_holder=?", (account_holder, account_balance, amount))
            user_id = self.get_user_id(account_holder)

            # Log the transaction (transaction_type: "deposit" or "withdrawal")

            self.log_transaction(user_id, amount, "deposit")
                
            connection.commit()

    def update_password(self, account_holder, password):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user SET password=? WHERE account_holder=?", (account_holder, password))
            connection.commit()

    def withdraw_balance(self, account_holder, account_balance, amount):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user SET account_balance=account_balance - ? WHERE account_holder=?", (account_holder, account_balance, amount))
            user_id = self.get_user_id(account_holder)
            self.log_transaction(user_id, amount, "withdrawal")
            connection.commit()

    def check_balance(self, account_holder):
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT account_balance FROM user WHERE account_holder=?", (account_holder,))
            result = cursor.fetchone()
            connection.commit()
            if result:
                return result[0]
            
    
app = backend()
app.transaction_table()
