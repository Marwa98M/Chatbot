from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()
print("DB Host:", os.getenv("DB_HOST"))


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca="./certs/ca.pem"
    )


# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    cnx = get_db()
    try:
        # Initializing the cursor, Calling the stored procedure, Committing the changes, Closing the cursor
        cursor = cnx.cursor()
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db='pandeyji_eatery';")
        for proc in cursor.fetchall():
            print(proc)
        cursor.execute("USE pandeyji_eatery;")
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))
        cnx.commit()
        cursor.close()
        print("Order item inserted successfully!")
        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()  # Rollback changes if necessary
        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()  # Rollback changes if necessary
        return -1


# Function to execute the SQL query to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    cnx = get_db()
    cursor = cnx.cursor()
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))
    cnx.commit()
    cursor.close()


# Function to execute the SQL query to get the total order price
def get_total_order_price(order_id):
    cnx = get_db()
    cursor = cnx.cursor()
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Fetching the result
    cursor.close()
    return result


# Function to executing the SQL query to get the next available order_id.
def get_next_order_id():
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Fetching the result
    cursor.close()
    if result is None:  # if it is empty
        return 1
    else:
        return result + 1


# Function for executing the SQL query to fetch the order status from the order_tracking table
def get_order_status(order_id):
    cnx = get_db()
    try:
        cursor = cnx.cursor()
        # query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()  # Fetching the result
        cursor.close()
        return result[0] if result else None

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# if __name__ == "__main__": # all methods are tested
# insert_order_tracking(99, "in progress") # works well
# print(get_next_order_id()) # Works well 100
# insert_order_item('Samosa', 3, 99) # works well; Order item inserted successfully!
# print(get_total_order_price(40)) # working well; 20.00
# insert_order_item('Milk', 1, 99) # works well; Order item inserted successfully!
# print(get_order_status(41)) # working well; 43-None, 40-in transit, 41-delivered

