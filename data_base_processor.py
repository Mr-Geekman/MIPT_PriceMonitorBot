"""
Class for managing data base with users
"""

import sqlite3


class DataBaseProcessor:
    def __init__(self, filename):
        """
        Connect to data base with users
        :param filename: name of file with data base
        """
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        with self.connection:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS Users ("
                "    UserID INT NOT NULL,"
                "    ProductTitle VARCHAR(32) NOT NULL,"
                "    ProductLink VARCHAR(1024) NOT NULL,"
                "    PropIDS VARCHAR(32),"
                "    CurrentPrice FLOAT NOT NULL,"
                "    PRIMARY KEY (UserID, ProductTitle)"
                ")"
            )

    def close(self):
        """
        Close connection and cursor
        """
        self.cursor.close()
        self.connection.close()

    def drop(self):
        """
        Drop the table
        """
        with self.connection:
            self.cursor.execute(
                "DROP TABLE IF EXISTS Users"
            )

    def truncate(self):
        """
        Truncate the table
        """
        with self.connection:
            self.cursor.execute(
                'DELETE FROM Users;'
            )

    def add(self, user_id, title, link, prop_ids, price):
        """
        Add new product
        :param user_id: chat_id with this user
        :param title: title of product
        :param link: link to product
        :param prop_ids: ids for prices
        :param price: current price of the product
        """
        try:
            with self.connection:
                self.cursor.execute(
                    "INSERT INTO Users VALUES(?, ?, ?, ?, ?)",
                    (user_id, title, link, prop_ids, price)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def delete(self, user_id, title):
        """
        Delete product with defined title
        :param user_id: chat_id with this user
        :param title: title of product
        """
        with self.connection:
            self.cursor.execute(
                "DELETE FROM Users WHERE UserID=? AND ProductTitle=?",
                (user_id, title)
            )

    def update(self, user_id, title, new_price):
        """
        Updat product's price
        :param user_id: chat_id with this user
        :param title: title of product
        :param new_price: new price of the product
        """
        with self.connection:
            self.cursor.execute(
                "UPDATE Users SET CurrentPrice=? "
                "WHERE UserID=? AND ProductTitle=?",
                (new_price, user_id, title)
            )

    def show(self, user_id):
        """
        Show user's products
        :param user_id: chat_id with this user
        :return: list of products
        """
        with self.connection:
            self.cursor.execute(
                "SELECT ProductTitle, ProductLink, PropIDS, CurrentPrice "
                "FROM Users WHERE UserID=?", (user_id,)
            )
        return self.cursor.fetchall()

    def show_all(self):
        """
        Show all users' products
        :return: list of products
        """
        with self.connection:
            self.cursor.execute(
                "SELECT * FROM Users"
                ""
            )
        return self.cursor.fetchall()
