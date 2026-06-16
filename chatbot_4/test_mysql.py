from core.mysql_loader import MySQLService

mysql = MySQLService()

user_db_id = mysql.create_user_if_not_exists("user_123")

conversation_id = mysql.get_or_create_active_conversation(user_db_id)

print(conversation_id)

mysql.save_message(conversation_id, "user", "Hello MySQL!")
