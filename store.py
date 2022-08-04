import sqlite3

# Joycelin 
conn = sqlite3.connect('store.db')

conn.execute('''DROP TABLE product''')

conn.execute('''CREATE TABLE IF NOT EXISTS account
            (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS user
            (user_id INTEGER PRIMARY KEY REFERENCES account(user_id) NOT NULL,
            mem_level VARCHAR(50) NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS admin
            (user_id INTEGER PRIMARY KEY REFERENCES account(user_id) NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER,
            date VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            cost REAL NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS product
            (product_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            product_name VARCHAR(50) NOT NULL,
            inventory INTEGER NOT NULL,
            price REAL NOT NULL,
            image VARCHAR(50) NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS order_items
            (order_id INTEGER NOT NULL,
            product_id INTEGER PRIMARY KEY NOT NULL,
            order_quantity INTEGER NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS cart
            (cart_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER REFERENCES user(user_id) NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS cart_items
            (cart_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            order_quantity INTEGER NOT NULL,
            PRIMARY KEY(cart_id, product_id),
            FOREIGN KEY (cart_id) REFERENCES cart(cart_id),
            FOREIGN KEY (product_id) REFERENCES product(product_id))''')

conn.close() 