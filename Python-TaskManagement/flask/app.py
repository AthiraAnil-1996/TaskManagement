from flask import Flask,render_template,request,redirect,url_for,flash
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

#class user:

#cursor.execute("select username from login")
#result = cursor.fetchall()


#users = [row[0] for row in result]

#cursor.close()
#connection.close()
# Define the route

@app.route('/',methods =['GET', 'POST'])

def hello():
   return render_template('main.html')

@app.route('/main',methods =['GET', 'POST'])

def main():
   return render_template('main.html')

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
               msg = 'Login Successful'
               return redirect(url_for('dashboard'))
           else:
               msg = 'Invalid username or password'
    return render_template('login.html',msg=msg)

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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    connection, cursor = get_db_cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('dashboard.html', tasks=tasks)



@app.route('/add_task', methods=['GET'])
def add_task():
    return render_template('addtask.html', form_title='Add New Task', form_action='/add_task', button_text='Add Task')



@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    # Delete the task from the database
    connection, cursor = get_db_cursor()
    sql_query = 'DELETE FROM tasks WHERE id=%s'
    cursor.execute(sql_query,(task_id,))
    connection.commit()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

#@app.route('/get_task/<int:task_id>', methods=['GET'])
#def get_task(task_id):
    
        
   #     connection, cursor = get_db_cursor()
   #     sql_query = 'SELECT * FROM tasks WHERE id=%s'
   #     cursor.execute(sql_query, (task_id,))
    #    task = cursor.fetchone()
   #     print('task',type(task))



@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    try:
        
        connection, cursor = get_db_cursor()
        sql_query = 'SELECT * FROM tasks WHERE id=%s'
        cursor.execute(sql_query, (task_id,))
        task = cursor.fetchone()
        print('task',type(task))

        if task:
            if request.method == 'POST':
                # Handle the form submission if POST method
                title = request.form.get('title')
                description = request.form.get('description')
                duedate = request.form.get('duedate')
                status = request.form.get('status')

                sql_query_update = 'UPDATE tasks SET title=%s, description=%s, duedate=%s, status=%s WHERE id=%s'
                cursor.execute(sql_query_update, (title, description, duedate, status, task_id))
                connection.commit()

                flash('Task updated successfully!', 'success')
                return redirect(url_for('dashboard'))

            return render_template('addtask.html', form_title='Update Task', form_action=f'/update_task/{task_id}',
                                   button_text='Update Task', task=task)
        else:
            flash('Task not found', 'error')
            return redirect(url_for('add_task'))
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')
        return redirect(url_for('update_task',task_id=task_id))
    finally:
        cursor.close()
        connection.close()

@app.route('/add_task', methods=['POST'])
def add_task_to_db():
    try:
        connection, cursor = get_db_cursor()
        title = request.form.get('title')
        description = request.form.get('description')
        duedate = request.form.get('duedate')
        status = request.form.get('status')

        sql_query = 'INSERT INTO tasks (title, description, duedate, status) VALUES (%s, %s, %s, %s)'
        values = (title, description, duedate, status)

        cursor.execute(sql_query, values)
        connection.commit()

        flash('Task added successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('dashboard'))






# Run the flask app

if __name__ == '__main__':
   app.run(debug=True)