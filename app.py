from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)


db = mysql.connector.connect(
    host="localhost",
    user="root",              
    password="yashu123", 
    database="users"
)
cursor = db.cursor(dictionary=True)


@app.route('/hello')
def hello():
    return "Hello World!"

@app.route('/users')
def users():
    """Display all users"""
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        if not user.get('avatar_url'):
            user['avatar_url'] = ""
    return render_template('users.html', users=users)

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    """Add new user"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        avatar_url = request.form.get('avatar_url', "").strip()

        cursor.execute(
            "INSERT INTO users (name, email, role, avatar_url) VALUES (%s, %s, %s, %s)",
            (name, email, role, avatar_url)
        )
        db.commit()
        return redirect(url_for('users'))

    return render_template('new_user.html')

@app.route('/users/<int:user_id>')
def user_detail(user_id):
    """Display user details"""
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.get('avatar_url'):
        user['avatar_url'] = ""

    return render_template('user_detail.html', user=user)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit existing user"""
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        avatar_url = request.form.get('avatar_url', "").strip()

        cursor.execute("""
            UPDATE users
            SET name = %s, email = %s, role = %s, avatar_url = %s
            WHERE id = %s
        """, (name, email, role, avatar_url, user_id))
        db.commit()
        return redirect(url_for('user_detail', user_id=user_id))

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user"""
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return redirect(url_for('users'))

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
