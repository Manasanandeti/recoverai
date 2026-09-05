from backend.database import get_db_connection

connection = get_db_connection()
cursor = connection.cursor()

cursor.execute("""
INSERT INTO customers (name, email, phone)
VALUES ('Demo Customer', 'demo@recoverai.com', '9999999999')
""")

customer_id = cursor.lastrowid

cursor.execute("""
INSERT INTO transactions
(customer_id, amount, payment_method, status, failure_reason)
VALUES (%s, %s, %s, %s, %s)
""", (
    customer_id,
    500,
    "UPI",
    "FAILED",
    "Insufficient balance"
))

transaction_id = cursor.lastrowid

connection.commit()

cursor.close()
connection.close()

print("SUCCESS: Demo data created!")
print("Customer ID:", customer_id)
print("Transaction ID:", transaction_id)