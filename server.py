from flask import Flask, render_template, redirect, request, session, flash

from flask_bcrypt import Bcrypt

import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

from MySQLconnection import connectToMySQL 
# import the function that will return an instance of a connection

app = Flask(__name__)
app.secret_key = "keep it secret"
app.secret_key ="keep it secret"
bcrypt = Bcrypt(app)

#flash require a secret key as well as session

# show a page with a form to create a new user


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index_total():
    return render_template('/index-total.html')

@app.route('/register', methods=['POST'])
def register():
    is_valid = True

    mysql = connectToMySQL('wall')
    query = 'SELECT * FROM users_table WHERE email = %(em)s;'
    data = {
    'em': request.form['email']
    }
    email_result = mysql.query_db(query, data)
    
    if len(email_result) >= 1:
      is_valid = False
      flash("email already registered in database")
    print(email_result)
    
    if len(request.form['fname']) < 1:
      is_valid = False
      flash("Please enter a first name")

    if len(request.form['lname']) < 1:
      is_valid = False
      flash("Please enter a last name")
   
    if len(request.form['email']) < 1:
      is_valid = False
      flash("Email cannot be blank.")

    if len(request.form['pw']) < 8:
      is_valid = False
      flash('Password must be atleast 8 characters')

    if (request.form['pw'] != request.form['cpw']):
      is_valid = False
      flash('Passwords do NOT match')
 
    if not EMAIL_REGEX.match(request.form['email']):
      # test whether a field matches the pattern.  If it does not fit the pattern, then redirect. if email fits pattern, continue.
      is_valid = False
      flash("email cannot be blank or invalid")
   
    ##### at this point, I have checked every field
    ##### if any of the fields weren't valid, is_valid will be False
    ##### if all the fields are valid, is_valid will be True
    if not is_valid:
      return redirect('/')
      # return render_template('/') could use also in this case
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['pw'])
        # pw_hash can be called anything including mickey
        print(pw_hash)   
        # put the pw_hash in our data dictionary, NOT the password the user provided
        # prints something like b'$2b$12$sqjyok5RQccl9S6eFLhEPuaRaJCcH3Esl2RWLm/cimMIEnhnLb7iC'
        # be sure you set up your database so it can store password hashes this long (60 characters)
      
        mysql = connectToMySQL("wall")
    
        query = "INSERT INTO users_table (first_name,last_name, email, password) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s);"
    # put the pw_hash in our data dictionary, NOT the password the user provided
    
        data = {
          "fn": request.form['fname'],
          "ln": request.form['lname'],
          "em": request.form['email'],
          "pw": pw_hash
        }
    #make the call of the function to the database. 
        result = mysql.query_db(query, data)
        session['id_mickey_user']=result
    # never render on a post, always redirect!
        flash("Login info successfuly added.  Please login!")
        
      # either way the application should return to the index and display the messag
      #   never render on a post, always redirect!
        return redirect("/")

# login the database  
@app.route('/login', methods = ['POST'])
def login():
    mysql = connectToMySQL('wall')
    query = 'SELECT * FROM users_table WHERE email = %(em)s;'
    data = {
    'em': request.form['email']
    }
    result = mysql.query_db(query, data)
    print(result)
    if len(result)>0:
   
      if bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
        session['id_mickey_user'] = result[0]['id_user']

      session['mickeys_first_name'] = result[0]['first_name']
      #look in session and result the first name at login
      return redirect('/wall')
    flash("You could not be logged in")
    return redirect ('/')

@app.route('/logout')
def logout():
    print(session)
    session.clear()
    flash("You've been logged out")
    return redirect('/')


@app.route('/wall', methods=['GET', 'POST'])
def display_wall():
    if 'id_mickey_user' not in session:
      flash("You need to be logged in to view this page")
      return redirect('/')
    else:
      flash("welcome to the wall")
        
    MySQL = connectToMySQL('wall')
        
    query_all_recipients ='SELECT * FROM users_table ORDER BY first_name;'
        
    data={
              "fn":['first_name'],
    }
        
    all_recipients = MySQL.query_db(query_all_recipients, data)
      
    MySQL=connectToMySQL('wall')
        
    query_count_incoming_posts = 'SELECT COUNT(*) FROM posts_table WHERE id_receiver = %(id_rec)s'
        
    data = {
    'id_rec': session['id_mickey_user'] 
    }
    print('your id is', id)
      
    total_message_count = MySQL.query_db(query_count_incoming_posts, data)
    print('You have messages', total_message_count)

        
    db = connectToMySQL('wall')

    query_inbox_messages = 'SELECT * FROM posts_table JOIN users_table ON posts_table.id_sender = users_table.id_user WHERE id_receiver= %(id_rec)s;'

    data = {
    'id_rec': session['id_mickey_user']

    }
    print('id_rec')
       
    print('id_sender says', {query_inbox_messages})
        
    incoming_messages = db.query_db(query_inbox_messages, data)

    print('id_sender says', incoming_messages)

    return render_template('/wall.html', id_receivers=all_recipients,counts=total_message_count, all_messages=incoming_messages)


@app.route('/send_post', methods = ['POST'])
def send_post_content():
    print("Hitting 1")
    # print(request.form)
    # print(session['id_mickey_user'])
    print("Hitting 2")
    print(request.form)
    if len(request.form['p_content']) < 5:
    # post_content is the name in the form on the wall.html
      print("Hitting if")

      flash('Say something of value')
      return redirect('/wall')
    else:
      db = connectToMySQL('wall')
    print("Hitting 4")

 # #this is telling the computer to find the table name posts 
    query_insert_content = 'INSERT INTO posts_table (id_sender, id_receiver, post_content, created_at, updated_at) VALUES (%(id_sen)s, %(id_rec)s, %(pc)s, NOW(), NOW());'
    print("Hitting 5")

        # #id_mem in purple are whatever we want these variables to be and they are set to the yellow colored variables found in the database .
    form_data = {
    # this is setting the variable id_mem that was set above in the database above to session and set to equal to id_membr found in the form.
    'id_sen': session['id_mickey_user'],
    'id_rec': request.form['id_receive'],
    'pc': request.form['p_content']
    }
    print("Hitting 6")

    # print('***********************')
    # print(request.form)
    # print(request.form['id_receive'])
    # print(['p_content'])
    # print('***********************') 

# connect to the database for table posts
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    all_messages=db.query_db(query_insert_content, form_data)
    print(request.form)
    
    return redirect ('/wall')

@app.route('/delete/<id>', methods=['GET'])
def process_delete(id):
    #     print('user to ??')
    MySQL = connectToMySQL("wall")

    # #write an UPDATE query
    query = "DELETE from posts_table WHERE id_post = %(mickey_id)s;"
    print(id)
    
    data = {
        'mickey_id': id
        # if id is from a form unlike this case where there is no form for id, then you will need to do a request.form like above for hidden inputs or like in the messages inthe wall. 
    }
    MySQL.query_db(query, data)
    flash("removed")
    return redirect ('/wall')


#     flash an error message and redirect back to a safe route
# ************************************************
# *************************************************

if __name__ == "__main__":
  app.run(debug=True)

# show a page with a form to create a new user
# @app.route('/users/new', methods=["GET"])
# def index():
#     return render_template("new_user_form.html")

# process user requires an action and redirect
# @app.route('/users/create', methods=["POST"])
# def process_user():
#     print("Post data")
#     print(request.form)
#     fname = request.form['fname']
#     lname = request.form['lname']
#     em= request.form['email']
#     return render_template("show_one_user.html", fname='first_name', lname='last_name', em='email')
#     # connect to to the MySQL schema name
    
#     #this is telling the computer to find the table name users 
#     query = "INSERT INTO users (first_name,last_name, email, created_at,updated_at) VALUES ( %(fn)s, %(ln)s, %(em)s, NOW(), NOW() );"
#     # #fname is the variable name from the form and fn is from whatever we create the variable to be and first_name is what I have in database. 
#     data = {
#         "fn": request.form["fname"],
#         "ln": request.form["lname"],
#         "em": request.form["email"]
#     }

#     db=connectToMySQL("wall")
#     user_id = db.query_db(query, data)
#     # return render_template('/show_one_user.html')
#     #this prints it to show the show_one_user
#     return redirect('users/create/show_one_user/' + str(user_id))
  #change this route in the futureto users/create/show_one_user


# @app.route('/users/create/show_one_user/<id>', methods=['GET'])
# def show_one_user(id):
#     #get info about a specific user

#     # return render_template (show_one_user.html)
#     #for temporary solution use this render_template

#     MySQL = connectToMySQL("wall")
#     #connect to to the MySQL schema name
#     query = "(SELECT * FROM users WHERE id_user= %(or)s);"
#     print(id)
#     data = {
#         'or':id
#     }   #run query
#     db = connectToMySQL
#     #connection to the datapage
#     id = MySQL.query_db(query, data)
#     # pass results to the page
#     return render_template ("show_one_user.html", all_users=id)        
#   #all_users in orange put in HTML  come from show_one_user in for loop template and id comes from what we called the database.

# #this app route needs to follow the form action and line up exactly with the redirect above.
# @app.route('/users/create/show_all_users', methods=['GET'])
# def show_all_users():
#     # #make a connection to the database
#     MySQL = connectToMySQL("wall")
#     # pass results to the page
#     # # # #write a query
#     query = "(SELECT * FROM users);"
#     print(id)
#     #do not need to define data because we are requesting all data
#     #run query
#     #connection to the datapage
#     results = MySQL.query_db(query)
#     #results is a variable used to define the call in the return statement
#     # # # #pass results to the template for rendering
#     return render_template ("/show_all_users.html", all_users=results)
#     #the orange is what you see in the HTML

# # # # show the form to edit specific users
# @app.route('/users/edit_form/<id>', methods=["GET"])
# def show_edit_form(id):
#     MySQL = connectToMySQL("wall")

#     query = "(SELECT * FROM users WHERE id_user= %(x)s);"
#     print(id)
#     data = {
#         'x':id
#     } 
#     # # # # #run query
#     users = MySQL.query_db(query, data)
#     return render_template("edit_form.html", all_users=users)


# @app.route('/users/edit/show_one_user/<id>', methods=['POST'])
# def process_edit_form(id):
#     print(id)
#     # #connect to db to show users info in the form
#     MySQL = connectToMySQL("wall")
#     # # # # #write query for getting specific users
 
#     query = "UPDATE users SET first_name = %(fn)s,last_name=%(ln)s, email=%(em)s, created_at = NOW(), updated_at = NOW() WHERE id_user = %(id)s;"

#     data = {
#     "fn": request.form["fname"],
#     "ln": request.form["lname"],
#     "em": request.form["email"],
#     "id": id
#     }
#     # #possibly a value from the url,

#     MySQL.query_db(query, data)
   
#    # where to go after this is complete
#     return redirect('/users/edit_form/' + str(id))
   
#     #orange is what you do in the HTML

# @app.route('/users/delete/<id>', methods=['GET'])
# def delete_user(id):
#     #     print('user to ??')
#     MySQL = connectToMySQL("wall")

#     # #write an UPDATE query
#     query = "DELETE from users WHERE ID_user = %(x)s;"
#     print(id)
    
#     data = {
#         'x': id
#     }
#     MySQL.query_db(query, data)
#     flash("removed")
#     return redirect('/users/create/show_all_users')


