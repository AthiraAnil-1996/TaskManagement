from flask import Flask,render_template,request,redirect,url_for,flash,session
import mysql.connector
import secrets



# create a flask application

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
def get_db_cursor():

  connection = mysql.connector.connect(
     host = "localhost",
     user = "root",
     password = "root",
     database = "task_manage"
   )
  cursor = connection.cursor()
  return connection,cursor


@app.route('/',methods =['GET', 'POST'])

def hello():
   return render_template('main.html')


@app.route('/main',methods =['GET', 'POST'])

def main():
   return render_template('main.html')

# -----------------------LOGIN----------------------------------------------

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
           username = request.form['username']
           password = request.form['password']
           

           connection, cursor = get_db_cursor()

           cursor.execute('select * from login where username = %s and password = %s',(username, password))
           user = cursor.fetchone()

           if user:
               session['loggedin'] = True
               session['id'] = user[0]
               session['username'] = user[1]
               print(session['id'])
               msg = 'Login Successful'
               return redirect(url_for('dashboard'))
           else:
               msg = 'Invalid username or password'
    return render_template('login.html',msg=msg)

#----------------------------SIGN UP ----------------------------------------------------------

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg = ''
    try:
       if request.method == 'POST':
           username = request.form['username']
           password = request.form['password']
           confirm_password = request.form['confirm_password']

           connection, cursor = get_db_cursor()

           cursor.execute('select * from login where username = %s',(username,))
           account = cursor.fetchone()

           if not username or not password or not confirm_password:
               msg = 'All Fields are required'
           elif password!=confirm_password:
               msg = 'Password does not match'
           else:
            #check if the username is already taken
            #existing_user = users.query.filter_by(username=username).first()
               if account:
                  msg = 'Username is already added'
               else:
                # Create a new user and add it to the database
                  sql_query = 'INSERT INTO login (username, password) VALUES (%s, %s)'
                  values = (username, password)
                  cursor.execute(sql_query,values)
                  connection.commit()
                  msg = 'You have successfully registered !'
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        msg = f"An error occurred: {err}"

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection is not None:
            connection.close()
           

    # Commit the transaction
                 
    return render_template('signup.html',msg=msg)

#------------------------------ DASHBOARD -------------------------------------------

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    connection, cursor = get_db_cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
    status_counts = dict(cursor.fetchall())

    task_count = len(tasks)


    cursor.close()
    connection.close()

    return render_template('dashboard.html', tasks=tasks, task_count=task_count,status_counts=status_counts)

#--------------------------------DELETE-------------------------------------------------

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    # Delete the task from the database
    connection, cursor = get_db_cursor()
    sql_query = 'DELETE FROM tasks WHERE id=%s'
    cursor.execute(sql_query,(task_id,))
    connection.commit()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


#-------------------------------UPDATE/SELECT-------------------------------------------------
def get_task_data_by_id(task_id):
    connection, cursor = get_db_cursor()
    try:
        query = "SELECT * FROM tasks WHERE id =%s"
        data = (task_id,)
        cursor.execute(query, data)
        task_data = cursor.fetchone()
        print(task_data)

        if task_data:
            task_dict = {
                'Task_id':task_data[0],
                'title': task_data[1],
                'description': task_data[2],
                'duedate': task_data[3],
                'status': task_data[4]
                
            }
            return task_dict
        else:
            return None
    except Exception as e:
        print(f"Error in get_task_data_by_id: {e}")
        return None

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    connection, cursor = get_db_cursor()
    print("Inside AddTask route function")
    form_data = None 
    msg = '' 
    action = 'create'
    task_id = request.args.get('id')
    if task_id:
        form_data = get_task_data_by_id(task_id)
        action = 'update'
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            user_id = session.get('id')
            title = request.form.get('title')
            description = request.form.get('description')
            due_date = request.form.get('dueDate')
            status = request.form.get('status')
            print(user_id)
            

            query = "INSERT INTO tasks ( title, description, duedate, status, user_id) VALUES (%s, %s, %s, %s, %s)"
            data = (title, description, due_date, status, user_id)

            cursor.execute(query, data)
            connection.commit()

            msg = 'Task Created successfully!'
            return redirect(url_for('dashboard'))
        elif action == 'update':
            
            user_id = session.get('id')
            title = request.form.get('title')
            description = request.form.get('description')
            due_date = request.form.get('dueDate')
            status = request.form.get('status')
            task_id = request.form.get('id')
            print(task_id)
           

            query = "UPDATE tasks SET title=%s, description=%s, duedate=%s, status=%s WHERE id=%s"
            data = (title, description, due_date, status, task_id)

            cursor.execute(query, data)
            connection.commit()

            msg = 'Task Updated successfully!'
            return redirect(url_for('dashboard'))
    cursor.close()
    connection.close()

    return render_template('/addtask.html', form_data=form_data, msg=msg,action=action)

#-------------------------------LOGOUT------------------------------------------------------

@app.route('/logout',methods =['GET', 'POST'])

def logout():
   return render_template('login.html')


# Run the flask app

if __name__ == '__main__':
   app.run(debug=True)