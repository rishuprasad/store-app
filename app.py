
# neccessary imports
import sqlite3
from flask import *
from numpy import product
from werkzeug.utils import secure_filename
from datetime import date


app = Flask(__name__)
app.secret_key = 'random string'


# Rishabh Prasad
# initial index page of the website (no user should be logged in)
@app.route('/')
def begin():
    session.clear() # clear the current session if there was a previously logged in user
    with sqlite3.connect('store.db') as conn: # query for products
        cur = conn.cursor()
        cur.execute('SELECT product_id, product_name, inventory, price, image FROM product')
        itemData = cur.fetchall()
    itemData = parse(itemData)  
    return render_template('index.html', itemData=itemData, loggedIn=False) # This displays the home page and sets "loggedIn" to False to force the user to login to their account

# Christopher Lynch
# already logged in
@app.route('/home') # This function is for the home page of the website once the user has logged in
def home():
    isAdmin = False
    if 'admin' in session:  # change page layout depending on admin privs
        isAdmin = True

    loggedIn, first_name = getLoginDetails() # Helper function to dispay the user's name on the home page
 
    with sqlite3.connect('store.db') as conn: # Connects to database and displays the products
        cur = conn.cursor()
        cur.execute('SELECT product_id, product_name, inventory, price, image FROM product')
        itemData = cur.fetchall()
    itemData = parse(itemData) 

    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, first_name=first_name.title(), isAdmin=isAdmin) # sets the current frame to index.html w/ the user's name displayed at the top

# Christopher Lynch
# user can see their profile information
@app.route('/profileForm')
def profile():
    loggedIn, first_name = getLoginDetails()
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT username, password, first_name, last_name, email FROM account WHERE email = ?', (session['email'], )) # query user information based on session email # This statement is how we can get all of the profile information 
        profileData = cur.fetchall() # Put all the profile info from the account table into a array that we then parse to get into the correct format. 
    profileData = parse(profileData)
    isAdmin = False
    if 'admin' in session: # check if Admin
        isAdmin = True
    return render_template('profile.html', profileData=profileData, loggedIn=loggedIn, first_name=first_name.title(), isAdmin=isAdmin) # take user to profile page # Once everything is completed, we can bring back all of the profile data to the page


# Christopher Lynch
# helper function to query if user is logged in
def getLoginDetails(): 
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        if 'email' not in session: # check if the user's email appears in session e.g. they are logged in to our site
            loggedIn = False
            first_name = ''
            noOfItems = 0
        else:                   # user is logged in, get their id and first name from the data base
            loggedIn = True
            cur.execute("SELECT user_id, first_name FROM account WHERE email = ?", (session['email'], ))
            user_id, first_name = cur.fetchone()
            # cur.execute("""SELECT order_quantity FROM cart_items WHERE cart_id = (
            #                                                             SELECT cart_id FROM cart WHERE user_id = ?)""", (user_id, ))
            # noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, first_name) # return the login status and user's first name

# Christopher Lynch
# helper function to parse the data queried from the database
def parse(data): 
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i]) # append data to array
            i += 1
        ans.append(curr) # append previous array to answer array
    return ans

# Christopher Lynch
# takes the user to their account page
@app.route('/createuser') 
def account():
    return render_template('Account.html')


# Christopher Lynch
# redirects to login page
@app.route("/loginForm")
def loginForm():
    if 'email' in session: # verify the user is logged in
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='') # if not, take user to login page

# Christopher Lynch
# helper function to verify the user is a valid user (appears in the database)
def is_valid(email, password):
    con = sqlite3.connect('store.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM account')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == password:
            return True
    return False

# Christopher Lynch
# log the user in to the website
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']           # get email and password from HTML text box forms
        password = request.form['password']
        if is_valid(email, password):     # if a valid user, set the session email to the user's email
            session['email'] = email
            
            with sqlite3.connect('store.db') as con:
                cur = con.cursor()
                cur.execute("SELECT user_id FROM account WHERE email = ?", (email, ))
                user_id = cur.fetchone()[0]
                
                cur.execute("SELECT * FROM admin WHERE user_id = ?", (user_id, ))
                admin = cur.fetchone()

                if admin != None:
                    session['admin'] = 'admin'
            return redirect(url_for('home'))  # go back to home page after storing session
        else:
            error = 'Invalid UserId / Password' # notify of failure
            return render_template('login.html', error=error) # go back to login page


# Christopher Lynch
@app.route("/logout") # log the user out of the website
def logout():
    session.pop('email', None) # remove the user's email from the session
    return redirect(url_for('home')) # back to home page

# Akash Jothi
# take the user to the register page
@app.route("/registrationForm")
def registrationForm():
    return render_template("register.html")

# Akash Jothi
# allows a user to register an account
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':    # gather info from HTML text boxes
        # parse form data    
        username = request.form["username"]
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        membership = request.form['membership']

        with sqlite3.connect('store.db') as con:
            try:
                cur = con.cursor()

                # insert information into account table
                cur.execute('INSERT INTO account (username, password, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)', (username, password, first_name, last_name, email))                
                con.commit()

                # retrieve the user_id that was just created 
                cur.execute('SELECT user_id FROM account WHERE username=? AND password=? AND first_name=? AND last_name=? AND email=?', (username, password, first_name, last_name, email, ))
                user_id = cur.fetchone()[0]

                # add info to user table
                cur.execute('INSERT INTO user (user_id, mem_level) VALUES (?, ?)', (user_id, membership))
                con.commit()

                # add info to cart table
                cur.execute('INSERT INTO cart (user_id) VALUES (?)', (user_id, ))
                con.commit()

                msg = "Registered Successfully"  # notify of success
            except:
                con.rollback()
                msg = "Error occured"           # notify of failure
        con.close()
        return render_template("login.html", error=msg) # return to login

# Akash Jothi
@app.route("/orderHistory") # This is the order history section. In this part of the code, i essentially look through the current users order history by accessign their user id through their email. Once I get to their user id,
def orderHistory(): # I can then look through ALL of that users orders in the order table, and parse them to make sure they are in a clean format.
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName = getLoginDetails()
    email = session['email']
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM account WHERE email = ?", (email, )) # get the user id from the session email
        user_id = cur.fetchone()[0]
       
        cur.execute("SELECT * from orders WHERE orders.user_id = ?", (user_id, )) # get all orders from the orders table
        orders = cur.fetchall()
    orders = parse(orders) # convert it into a list of lists
 
    return render_template("orderHistory.html", orders=orders, loggedIn=loggedIn, first_name=firstName) # return the lists of lists which i then iterate through in the html file. I use a table format to print out all of the orders for that particular user

# Akash Jothi
# redirects user to edit their profile information
@app.route("/editProfileForm") 
def editProfileForm():
    if 'email' not in session: # check if user is logged in
        return redirect(url_for('loginForm')) # if not, take them to login page
    if 'admin' in session: # check if the user is an Admin
        return redirect(url_for("editProfileAdmin")) # if so, take them to Admin edit page
    loggedIn, firstName = getLoginDetails()
    return render_template("editProfile.html", loggedIn=loggedIn, first_name=firstName, email=session['email']) # take user to edit profile page

# Rishabh Prasad
# redirects the user to the edit user accounts page for Admins
@app.route("/editProfileAdmin") 
def editProfileAdmin():
    loggedIn, firstName = getLoginDetails()
    return render_template("editProfileAdmin.html", loggedIn=loggedIn, first_name=firstName)

# Akash Jothi
# update a user's own profile information
@app.route("/updateProfile", methods=["GET", "POST"]) 
def updateProfile():
    if request.method == 'POST':                # retrieve the information from the HTML page
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        with sqlite3.connect('store.db') as con: # connect to database and update the account information based on the user's email
                try:
                    cur = con.cursor()      
                    cur.execute('UPDATE account SET username = ?, password = ?, first_name = ?, last_name = ? WHERE email = ?', (username, password, first_name, last_name, email))
 
                    con.commit()
                    msg = "Saved Successfully" # notify of success
                except:
                    con.rollback()
                    msg = "Error occured" # notify of failure
        con.close()
        return redirect(url_for('profile')) # go back to the profile page

# Rishabh Prasad
#allows an Admin to update user accounts update any profile in the database given admin access to user IDs
@app.route("/updateProfileAdmin", methods=["GET", "POST"])
def updateProfileAdmin():
    if request.method == 'POST' and 'admin' in session: # get form info from HTML page
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        with sqlite3.connect('store.db') as con:
                try:
                    # update the account table with inputs using the user_id entered by the admin
                    cur = con.cursor()
                    # update the user account information in the database
                    cur.execute('UPDATE account SET username = ?, password = ?, first_name = ?, last_name = ?, email = ? WHERE user_id = ?', (username, password, first_name, last_name, email, user_id, ))

                    con.commit()
                    msg = "Saved Successfully" # notify of success
                except:
                    con.rollback()
                    msg = "Error occured" # notify of failure
        con.close()
        return redirect(url_for('profile')) # go back to profile page

# Akash Jothi  
# deletes a user's own profile
@app.route("/deleteProfile", methods=["POST"]) 
def deleteProfile():
    if 'email' not in session:  # make sure the user is logged in, if not take them to login page
        return redirect(url_for('loginForm'))
    email = session["email"] # get logged in user's email
    if request.method == 'POST':
        with sqlite3.connect('store.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('DELETE FROM account WHERE email = ?', (email, )) # delete the account with the given email from the session
 
                    con.commit()
                    msg = "Delete Successfully" # notify of success
                except:
                    con.rollback()
                    msg = "Error occured" # notify of failure
        con.close()
        return render_template("login.html", error=msg) # take the user back to the login page

# Rishabh Prasad
# allows an Admin to delete a user account
@app.route("/deleteProfileAdmin1")
def deleteProfileAdmin1():
    if 'email' not in session or 'admin' not in session: # check if user is logged in and they are an admin
        return redirect(url_for('loginForm')) # take user to login form
    loggedIn, firstName = getLoginDetails()
    return render_template("deleteProfileAdmin.html", loggedIn=loggedIn, first_name=firstName) # take admin to delete profile HTML page

# Rishabh Prasad
# allows an Admin to delete a user account
@app.route("/deleteProfileAdmin2", methods=["POST"])
def deleteProfileAdmin2():
    if 'email' not in session or 'admin' not in session: # check if user is logged in and they are an admin
        return redirect(url_for('loginForm')) # take back to login form
    if request.method == 'POST':
        with sqlite3.connect('store.db') as con: # connect to database and extract user ID from HTML form
                try:
                    user_id = request.form["user_id"]

                    cur = con.cursor()
                    cur.execute('DELETE FROM account WHERE user_id = ?', (user_id, )) # remove user account from database

                    con.commit()
                    msg = "Delete Successfully" # notify of success

                    print("Deleted profile with user_id", user_id)
                except:
                    con.rollback()
                    msg = "Error occured" # notify of failure
        con.close()
        return redirect(url_for("profile")) # go back to profile page

# Rishabh Prasad
# add items to user's cart
@app.route("/addToCart") 
def addToCart():
    if 'email' not in session:      # check if user is logged in
        return redirect(url_for('loginForm'))
    else:
        product_id = int(request.args.get('product_id')) # get the selected product ID
       
        with sqlite3.connect('store.db') as conn:
            cur = conn.cursor()
 
 
            cur.execute("SELECT inventory FROM product WHERE product_id = ?", (product_id, )) # query database for product ID
            inventory = cur.fetchone()[0]
 
            if inventory <= 0: # no inventory
                flash(u'Invalid password provided', 'error')
                return redirect(url_for('home')) # go back to home page
 
            cur.execute("SELECT user_id FROM account WHERE email = ?", (session['email'], )) # get the logged in user's ID
            user_id = cur.fetchone()[0]
           
            cur.execute("SELECT cart_id FROM cart WHERE user_id = ?", (user_id, )) # get corresponding cart ID
            cart_id = cur.fetchone()[0]
 
            cur.execute("SELECT order_quantity FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, product_id, )) # query for the order quantity of corresponding cart
            order_quantity = cur.fetchone()
            print("order_quantity", order_quantity)
            # adding product for first time
            if order_quantity == None:
                try:
                    cur.execute("INSERT INTO cart_items (cart_id, product_id, order_quantity) VALUES (?, ?, ?)", (cart_id, product_id, 1)) # if the item is not already in the cart, add it
                    conn.commit()
                except:
                    conn.rollback()
                    msg = "Error occured for first time product insertion" # notify of failure
            # product already in cart
            else:
                try:
                    cur.execute("UPDATE cart_items SET order_quantity = ? WHERE cart_id = ? AND product_id = ?", (order_quantity[0]+1, cart_id, product_id)) # item already in cart, update quantity
                    conn.commit()
                except:
                    conn.rollback()
                    msg = "Error occured for incrementing existing product" # notify of failure
 
        conn.close()
        return redirect(url_for('home')) # redirect to home page so user can add more items

# Rishabh Prasad
# this allows a user to add items to their cart
@app.route("/cart")
def cart():
    if 'email' not in session: # check that user is logged in if not go back to log in page
        return redirect(url_for('loginForm'))
    loggedIn, firstName = getLoginDetails()
    email = session['email'] # get email from session
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM account WHERE email = ?", (email, )) # get user ID based on current session email
        user_id = cur.fetchone()[0]

        cur.execute("SELECT cart_id FROM cart WHERE user_id = ?", (user_id, )) # get corresponding cart ID 
        cart_id = cur.fetchone()[0]
        
        cur.execute("SELECT product_id FROM cart_items WHERE cart_id = ?", (cart_id, ) ) # get products in the given cart ID
        product_id_list = cur.fetchall()

        # iterate through products in cart
        for i in range(len(product_id_list)):
            product_id_list[i] = product_id_list[i][0]

        products = []
        order_quants = []
        for product_id in product_id_list:
            cur.execute("SELECT product_name, price, image FROM product WHERE product_id = ?", (product_id, )) # get product information from database
            temp = cur.fetchall()[0]
            temp_list = []
            for i in temp:
                temp_list.append(i)
            temp_list.insert(0, product_id)
            products.append(temp_list)
            cur.execute("SELECT order_quantity FROM cart_items WHERE product_id = ? AND cart_id = ?", (product_id, cart_id)) # get order quantity from cart
            temp_quant = cur.fetchone()[0]
            order_quants.append(temp_quant)
            
    totalPrice = 0
    for i, row in enumerate(products):
        totalPrice += row[2] * order_quants[i]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName) # take user back to their cart page

# Rishabh Prasad
# allow a user to remove items from their cart
@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session: # check to make sure current user is logged in
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId')) # get the product ID from HTML
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM account WHERE email = ?", (email, )) # get user ID matching session email
        user_id = cur.fetchone()[0]

        cur.execute("SELECT cart_id FROM cart WHERE user_id = ?", (user_id, )) # get corresponding cart ID
        cart_id = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, productId)) # delete product from cart 
            conn.commit()
            msg = "removed successfully" # notify of success
        except:
            conn.rollback()
            msg = "error occured" # notify of failure
    conn.close()
    return redirect(url_for('cart')) # go back to cart page

# Rishabh Prasad
# allow a user to add items to their cart
@app.route("/add1ToCart")
def add1ToCart():
    if 'email' not in session: # check to see if user is logged in, else go to login page
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId')) # get product ID from HTML
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM account WHERE email = ?", (email, )) # get corresponding user ID from session email
        user_id = cur.fetchone()[0]

        cur.execute("SELECT cart_id FROM cart WHERE user_id = ?", (user_id, )) # get corresponding cart ID
        cart_id = cur.fetchone()[0]

        cur.execute("SELECT order_quantity FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, productId)) # get order quantity of specific item
        order_quant = cur.fetchone()[0]
        try:
            cur.execute("UPDATE cart_items SET order_quantity = ? WHERE cart_id = ? AND product_id = ?", (order_quant+1, cart_id, productId)) # update cart to reflect quantity
            conn.commit()
            msg = "added successfully" # notify of success
        except:
            conn.rollback()
            msg = "error occured" # notify of failure
    conn.close()
    return redirect(url_for('cart')) # go back to cart

# Rishabh Prasad
# allow a user to remove an item from their cart
@app.route("/remove1FromCart")
def remove1FromCart():
    if 'email' not in session: # check if user is logged in, else go to login page
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId')) # get product ID from HTML
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM account WHERE email = ?", (email, )) # get user ID of currently logged in user
        user_id = cur.fetchone()[0]

        cur.execute("SELECT cart_id FROM cart WHERE user_id = ?", (user_id, )) # get matching cart ID for logged in user
        cart_id = cur.fetchone()[0]

        cur.execute("SELECT order_quantity FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, productId)) # get quantity of product from database
        order_quant = cur.fetchone()[0]

        try:
            cur.execute("UPDATE cart_items SET order_quantity = ? WHERE cart_id = ? AND product_id = ?", (order_quant-1, cart_id, productId)) # update the product quantity in cart
            conn.commit()
            msg = "added successfully" # notify of success
        except:
            conn.rollback()
            msg = "error occured" # notify of failure
    conn.close()
    return redirect(url_for('cart')) # go back to cart 

# Akash Jothi
# adds new order record, updates order_items with each product in the new order, clears the cart since order was completed
@app.route("/checkout")
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    today = date.today()
    cost = float(request.args.get('cost'))  # store the total cost that was passed in by the HTML
    email = session['email']
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM account WHERE email = ?", (email, ))
        user_id = cur.fetchone()[0]
         
        # create new order record using today's date, incomplete status by default, and the total cost of the cart 
        try:
            cur.execute("INSERT INTO orders (user_id, date, status, cost) VALUES (?, ?, ?, ?)", (user_id, today, "Incomplete", cost, ))
            conn.commit()
            print("Added", user_id, "to orders")
        except:
            conn.rollback()
            msg = "error occured"
        
        # retrieve order_id that was created for the order that was just created
        cur.execute("SELECT order_id FROM orders WHERE user_id = ? AND date = ? AND status = ? AND cost = ?", (user_id, today, "Incomplete", cost, ))
        order_id = cur.fetchone()[0]

        # retrieve list of all products contained within a specific user's cart        
        cur.execute("SELECT cart_id FROM cart WHERE user_id = ?", (user_id, ))
        cart_id = cur.fetchone()[0]
        
        cur.execute("SELECT product_id FROM cart_items WHERE cart_id = ?", (cart_id, ) )
        product_id_list = cur.fetchall()
        
        for i in range(len(product_id_list)):
            product_id_list[i] = product_id_list[i][0]
        
        # create parallel list containing the order quantity of each product within the cart
        order_quants = []
        for product_id in product_id_list:
            cur.execute("SELECT order_quantity FROM cart_items WHERE product_id = ? AND cart_id = ?", (product_id, cart_id))
            temp_quant = cur.fetchone()[0]
            order_quants.append(temp_quant)

        # insert each order-product pair with quantity into the order_items table
        for i, product_id in enumerate(product_id_list):
            try:
                cur.execute("INSERT INTO order_items (order_id, product_id, order_quantity) VALUES (?, ?, ?)", (order_id, product_id, order_quants[i]))
                conn.commit()
                print("Added", product_id, "to order_items")
            except:
                conn.rollback()
                msg = "error occured"
        
        # reset the contents of the cart since the order was submitted
        try:
            cur.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id, ))
            conn.commit()
            print("Reset cart items")
        except:
            conn.rollback()
            msg = "error occured"

    return redirect(url_for('home'))


# Akash Jothi
@app.route("/updateStatus") # This function is how we were able to update the order status of a users order
def updateStatus():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    order_id = int(request.args.get('order_id')) # We will just check here for the order ID that we parse in from the HTML file
    print(order_id)
    with sqlite3.connect('store.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("Received", order_id, )) # Once we have gotten into the database, we can then update the status of an order from the orders table
            conn.commit()
            print("Updated order status to \"Received\"")
        except:
            conn.rollback()
            msg = "error occurred"
    return redirect(url_for("orderHistory")) # Go back to the order page once the order status has been updated.

# Christopher Lynch
# redirects to the admin page for adding items
@app.route("/addItemForm")
def addItemForm():
    if 'email' not in session or 'admin' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName = getLoginDetails()
    return render_template("addItem.html", loggedIn=loggedIn, first_name=firstName, email=session['email']) # This is where we get all of the information 

# Akash Jothi 
# adds new item to product table based on admin entries
@app.route("/addNewItem", methods=["GET","POST"]) # This function will allow a admin to add a new item to shop
def addNewItem():
    if request.method == "POST":
        product_id = int(request.form['product_id'])
        product_name = request.form['product_name']
        price = float(request.form['price'])
        inventory = int(request.form['inventory']) # first, we ask the admin to input all of the attributes of the new order
 
        with sqlite3.connect('store.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('INSERT INTO product (product_id, product_name, price, inventory, image) VALUES (?, ?, ?, ?, ?)', (product_id, product_name, price, inventory, "stock.png")) # This SQL statement will update the database
                conn.commit()
                msg="added successfully" # Update the databse with the new product information that the admin had initially inputed
                print("Added product with id", product_id) # Print out that the product was added
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        isAdmin = False
        if 'admin' in session:
            isAdmin = True
        return redirect(url_for("home")) # Return to the homescreen once the product has been added

# Joycelin Gu
# modify membership status in the account table
@app.route("/updateMembership", methods=["GET", "POST"]) # This function is how a user can update their current membership. 
def updateMembership():
    if request.method == 'POST':
        membership = request.form['membership']
        email = request.form['email'] # Have the user input a new membership and get their email from the current session
        with sqlite3.connect('store.db') as con:
                cur = con.cursor()
                cur.execute('SELECT user_id FROM account WHERE email=?', (email, ))  # retrieve user_id using email
                user_id = cur.fetchone()[0]
                try:
                    cur.execute('UPDATE user SET mem_level = ? WHERE user_id = ?', (membership, user_id, ))  # update the table

                    con.commit()
                    msg = "New Membership Saved Successfully" # The membership was successfully saved once we update the table in the database. 
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('membership'))

# Joycelin Gu
# rediirect to the page for editing membership
@app.route("/editMembershipForm")
def editMembershipForm():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName = getLoginDetails()
    return render_template("editMembership.html", loggedIn=loggedIn, first_name=firstName, email=session['email'])

# Joycelin Gu
# redirect to show current membership information
@app.route('/membershipForm') # This is a function to gather all of the relavent information of a users membership level to display it to the webpage
def membership():
    loggedIn, first_name = getLoginDetails()
    email = session['email']
    with sqlite3.connect('store.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM account WHERE email=?', (email, )) # Get the user id based on the stored session email
        user_id = cur.fetchone()[0]
        cur.execute('SELECT mem_level FROM user WHERE user_id = ?', (user_id, )) # retrieve the current memebership level based on the user id. 
        mem_level =  cur.fetchone()[0]
    return render_template('membership.html', mem_level=mem_level, loggedIn=loggedIn, first_name=first_name.title())

# Joycelin Gu
# remove user's current membership
@app.route("/deleteMembership", methods=["POST"]) # This function lets the user choose to delete their membership
def deleteMembership():
    if request.method == 'POST':
        email = session['email'] # store the current email that is in session
        with sqlite3.connect('store.db') as con:
                cur = con.cursor()
                cur.execute('SELECT user_id FROM account WHERE email=?', (email, )) # Go into the account table in the database, and get the user id from the email
                user_id = cur.fetchone()[0]
                try:
                    cur.execute('UPDATE user SET mem_level = ? WHERE user_id = ?', ("Cancelled", user_id, )) # once we have the user ID, we then use that to update the users membership level in the user table

                    con.commit()
                    msg = "Membership successfully cancelled" # let the user know that their membership has been successfully cancelled
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('membership')) # direct the user back to their current membership page to see what it is after canceling it

# Joycelin Gu
# take the user to the edit product page
@app.route("/editProductForm")
def editProduct():
    loggedIn, firstName = getLoginDetails()
    return render_template("editProduct.html", loggedIn=loggedIn, first_name=firstName)

# Akash Jothi
# update product information
@app.route("/updateProduct", methods=["GET", "POST"]) # This function is how we are able to update a current product that is already in the database
def updateProduct():
    if request.method == 'POST' and 'admin' in session:
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        price = float(request.form['price'])
        inventory = request.form['inventory'] # This if statement checks if the admin is in session, and it allows us to get all of the product information from the admins inpit
   
        with sqlite3.connect('store.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE product SET product_name = ?, price = ?, inventory = ? WHERE product_id = ?', (product_name, price, inventory, product_id, )) # Once we have all the data, we can then  
 
                    con.commit() # update the products table with the new information that the admin had inputed
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('profile')) # Go back to the profile page so the admin can see the newly updated information

# Joycelin Gu
# redirect to page for deleting product
@app.route("/deleteProductForm")
def deleteProductForm():
    if 'email' not in session or 'admin' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName = getLoginDetails()
    return render_template("deleteProduct.html", loggedIn=loggedIn, first_name=firstName)

# Joycelin Gu
# deleted a given product from the product table
@app.route("/deleteProduct", methods=["POST"])
def deleteProduct():
    if 'email' not in session or 'admin' not in session:
        return redirect(url_for('loginForm'))
    if request.method == 'POST':
        with sqlite3.connect('store.db') as con:
                try:
                    product_id = request.form["product_id"]
 
                    cur = con.cursor()
                    cur.execute('DELETE FROM product WHERE product_id = ?', (product_id, ))   # delete the product entry
 
                    con.commit()
                    msg = "Deleted Successfully"
 
                    print("Deleted product with product id", product_id)
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for("profile"))

# Joycelin Gu
# redirect to page for editing order records 
@app.route("/editOrderForm")
def editOrderForm():
    loggedIn, firstName = getLoginDetails()
    return render_template("editOrder.html", loggedIn=loggedIn, first_name=firstName)
 
# Joycelin Gu
# update product information with values given by admin
@app.route("/updateOrder", methods=["GET", "POST"])
def updateOrder():
    if request.method == 'POST' and 'admin' in session:
        # retrieve the input values from the form
        order_id = request.form['order_id']
        user_id = request.form['user_id']
        date = request.form['date']
        status = request.form['status']
        cost = float(request.form['cost'])
   
        with sqlite3.connect('store.db') as con:
                try:
                    # update the order records using the given order_id
                    cur = con.cursor()
                    cur.execute('UPDATE orders SET user_id = ?, date = ?, status = ?, cost = ? WHERE order_id = ?', (user_id, date, status, cost, order_id, ))
 
                    con.commit()
                    msg = "Saved Orders Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('profile'))
 
# Joycelin Gu
# redirect to page for deleting orders
@app.route("/deleteOrderForm")
def deleteOrderForm():
    if 'email' not in session or 'admin' not in session:
        return redirect(url_for('loginForm')) # This is the form to get all of the information for the delete order webpage
    loggedIn, firstName = getLoginDetails()
    return render_template("deleteOrder.html", loggedIn=loggedIn, first_name=firstName)

# Joycelin Gu
# deletes a specific order record from order table
@app.route("/deleteOrder", methods=["POST"])
def deleteOrder():
    if 'email' not in session or 'admin' not in session:
        return redirect(url_for('loginForm'))
    if request.method == 'POST':
        with sqlite3.connect('store.db') as con:
                try:
                    order_id = request.form["order_id"]
 
                    cur = con.cursor()
                    cur.execute('DELETE FROM orders WHERE order_id = ?', (order_id, ))     # delete specific order record
 
                    con.commit()
                    msg = "Deleted Order Successfully"
 
                    print("Deleted order with order id", order_id)
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for("profile"))

if __name__ == '__main__':
   
   app.run(port='8000', debug=True)