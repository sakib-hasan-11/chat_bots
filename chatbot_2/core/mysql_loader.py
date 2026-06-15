import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()


class MySQLService:
    
    DEFAULT_CONVERSATION_TITLE = "Default Chat"

    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                port=int(os.getenv("MYSQL_PORT")),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
            )

            if self.connection.is_connected():
                print(" Successfully connected to MySQL!")

            self.cursor = self.connection.cursor(
                dictionary=True
            )  # dictionary give json output structure.

        except Error as e:
            print(f" MySQL Connection Error: {e}")

    
    def close(self):
        self.cursor.close()
        self.connection.close()

    
    
    def commit(self):
        self.connection.commit()

    
    
    def create_user_if_not_exists(self, user_id: str):

        query = """
            SELECT id
            FROM users
            WHERE user_id = %s
        """

        self.cursor.execute(query, (user_id,))

        user = self.cursor.fetchone()

        if user:
            return user["id"]

        insert_query = """
            INSERT INTO users(user_id)
            VALUES(%s)
        """

        self.cursor.execute(insert_query, (user_id,))

        self.connection.commit()

        return self.cursor.lastrowid

    
    
    
    def get_or_create_active_conversation(
        self,
        user_db_id: int,
    ):

        query = """
            SELECT id
            FROM conversations
            WHERE user_id = %s
            LIMIT 1
        """

        self.cursor.execute(query, (user_db_id,))

        conversation = self.cursor.fetchone()

        if conversation:
            return conversation["id"]

        insert_query = """
            INSERT INTO conversations
            (
                user_id,
                title
            )
            VALUES
            (
                %s,
                %s
            )
        """

        self.cursor.execute(
            insert_query,
            (
                user_db_id,
                self.DEFAULT_CONVERSATION_TITLE,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    
    
    
    
    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ):

        query = """
            INSERT INTO messages
            (
                conversation_id,
                role,
                content
            )
            VALUES
            (
                %s,
                %s,
                %s
            );
        """

        self.cursor.execute(
            query,
            (
                conversation_id,
                role,
                content,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid
