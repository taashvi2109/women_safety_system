from flask import Flask, render_template, request, redirect, session
import oracledb

app = Flask(__name__)
app.secret_key = "secret123"

# -------- DB CONNECTION --------
connection = oracledb.connect(
    user="system",
    password="1234",
    dsn="localhost:1521/XEPDB1"
)
cursor = connection.cursor()


# -------- HOME --------
@app.route('/')
def home():
    return render_template("index.html")


# -------- LOGIN --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')

        if role == "user":
            email = request.form.get('email')
            password = request.form.get('password')

            cursor.execute(
                "SELECT USER_ID, NAME FROM USERS WHERE EMAIL = :1 AND PASSWORD = :2",
                (email, password)
            )
            user = cursor.fetchone()

            if user:
                session['user'] = user[1]
                session['user_id'] = user[0]
                session['role'] = "user"
                return redirect('/user_dashboard')

        elif role == "admin":
            email = request.form.get('email')
            password = request.form.get('password')

            cursor.execute(
                "SELECT ADMIN_ID, NAME FROM ADMIN WHERE EMAIL = :1 AND PASSWORD = :2",
                (email, password)
            )
            admin = cursor.fetchone()

            if admin:
                session['user'] = admin[1]
                session['role'] = "admin"
                return redirect('/admin_dashboard')

        elif role == "officer":
            name = request.form.get('name')
            contact = request.form.get('contact')

            cursor.execute(
                "SELECT OFFICER_ID, NAME FROM OFFICER WHERE NAME = :1 AND PHONE = :2",
                (name, contact)
            )
            officer = cursor.fetchone()

            if officer:
                session['user'] = officer[1]
                session['officer_id'] = officer[0]
                session['role'] = "officer"
                return redirect('/officer_dashboard')

        return "Invalid Credentials ❌"

    return render_template("login.html")


# -------- DASHBOARDS --------
@app.route('/user_dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect('/login')
    return render_template("user_dashboard.html")


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template("admin_dashboard.html")


@app.route('/officer_dashboard')
def officer_dashboard():
    if session.get('role') != 'officer':
        return redirect('/login')
    return render_template("officer_dashboard.html")


# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# -------- USERS (UPDATED: NO ID, NO NAME) --------
@app.route('/users')
def users():
    if session.get('role') != 'admin':
        return redirect('/login')

    cursor.execute("""
    SELECT USER_ID, NAME, EMAIL, PHONE, ADDRESS
    FROM USERS
    """)

    data = cursor.fetchall()
    return render_template("users.html", data=data)


# -------- OFFICERS --------
@app.route('/officers')
def officers():
    if session.get('role') != 'admin':
        return redirect('/login')

    cursor.execute("SELECT OFFICER_ID, NAME FROM OFFICER")
    data = cursor.fetchall()
    return render_template("officers.html", data=data)


# -------- COMPLAINT --------
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if session.get('role') != 'user':
        return redirect('/login')

    if request.method == 'POST':
        desc = request.form['description']
        cat = request.form['category']
        user_id = session['user_id']

        cursor.execute(
            "INSERT INTO COMPLAINT (COMPLAINT_ID, USER_ID, CATEGORY_ID, DESCRIPTION, STATUS_ID) VALUES (complaint_seq.NEXTVAL, :1, :2, :3, 1)",
            (user_id, cat, desc)
        )
        connection.commit()

        return redirect('/success')

    cursor.execute("SELECT CATEGORY_ID, CATEGORY_NAME FROM CATEGORY")
    categories = cursor.fetchall()

    return render_template("complaint.html", categories=categories)


# -------- SUCCESS --------
@app.route('/success')
def success():
    return render_template("success.html")


# -------- USER: ONLY OWN COMPLAINTS --------
@app.route('/my_complaints')
def my_complaints():
    if session.get('role') != 'user':
        return redirect('/login')

    user_id = session['user_id']

    cursor.execute("""
    SELECT 
        c.COMPLAINT_ID,
        cat.CATEGORY_NAME,
        s.STATUS_NAME,
        NVL(o.NAME, 'Not Assigned'),
        c.DESCRIPTION
    FROM COMPLAINT c
    JOIN CATEGORY cat ON c.CATEGORY_ID = cat.CATEGORY_ID
    JOIN STATUS s ON c.STATUS_ID = s.STATUS_ID
    LEFT JOIN ASSIGNMENT a ON c.COMPLAINT_ID = a.COMPLAINT_ID
    LEFT JOIN OFFICER o ON a.OFFICER_ID = o.OFFICER_ID
    WHERE c.USER_ID = :1
    ORDER BY c.COMPLAINT_ID DESC
    """, (user_id,))

    data = cursor.fetchall()
    return render_template("view.html", data=data)


# -------- ADMIN VIEW --------
@app.route('/view')
def view():
    if session.get('role') != 'admin':
        return redirect('/login')

    cursor.execute("""
    SELECT 
        c.COMPLAINT_ID,
        cat.CATEGORY_NAME,
        s.STATUS_NAME,
        NVL(o.NAME, 'Not Assigned'),
        c.DESCRIPTION
    FROM COMPLAINT c
    JOIN CATEGORY cat ON c.CATEGORY_ID = cat.CATEGORY_ID
    JOIN STATUS s ON c.STATUS_ID = s.STATUS_ID
    LEFT JOIN ASSIGNMENT a ON c.COMPLAINT_ID = a.COMPLAINT_ID
    LEFT JOIN OFFICER o ON a.OFFICER_ID = o.OFFICER_ID
    ORDER BY c.COMPLAINT_ID DESC
    """)

    data = cursor.fetchall()
    return render_template("view.html", data=data)


# -------- ASSIGN --------
@app.route('/assign', methods=['GET', 'POST'])
def assign():
    if session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        cid = int(request.form['complaint_id'])
        oid = int(request.form['officer_id'])

        cursor.execute("SELECT * FROM ASSIGNMENT WHERE COMPLAINT_ID = :1", (cid,))
        result = cursor.fetchone()

        if result:
            cursor.execute(
                "UPDATE ASSIGNMENT SET OFFICER_ID = :1 WHERE COMPLAINT_ID = :2",
                (oid, cid)
            )
        else:
            cursor.execute(
                "INSERT INTO ASSIGNMENT VALUES (assign_seq.NEXTVAL, :1, :2, SYSDATE)",
                (cid, oid)
            )

        cursor.execute(
            "UPDATE COMPLAINT SET STATUS_ID = 2 WHERE COMPLAINT_ID = :1",
            (cid,)
        )

        connection.commit()
        return redirect('/view')

    cursor.execute("SELECT OFFICER_ID, NAME FROM OFFICER")
    officers = cursor.fetchall()

    cursor.execute("SELECT COMPLAINT_ID FROM COMPLAINT")
    complaints = cursor.fetchall()

    return render_template("assign.html", officers=officers, complaints=complaints)


# -------- OFFICER: ONLY ASSIGNED --------
@app.route('/officer_complaints')
def officer_complaints():
    if session.get('role') != 'officer':
        return redirect('/login')

    oid = session['officer_id']

    cursor.execute("""
    SELECT 
        c.COMPLAINT_ID,
        cat.CATEGORY_NAME,
        s.STATUS_NAME,
        c.DESCRIPTION
    FROM COMPLAINT c
    JOIN CATEGORY cat ON c.CATEGORY_ID = cat.CATEGORY_ID
    JOIN STATUS s ON c.STATUS_ID = s.STATUS_ID
    JOIN ASSIGNMENT a ON c.COMPLAINT_ID = a.COMPLAINT_ID
    WHERE a.OFFICER_ID = :1
    """, (oid,))

    data = cursor.fetchall()
    return render_template("officer_view.html", data=data)


# -------- RESOLVE --------
@app.route('/resolve/<int:cid>')
def resolve(cid):
    if session.get('role') != 'officer':
        return redirect('/login')

    cursor.execute(
        "UPDATE COMPLAINT SET STATUS_ID = 3 WHERE COMPLAINT_ID = :1",
        (cid,)
    )
    connection.commit()

    return redirect('/officer_complaints')


# -------- FEEDBACK --------
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if session.get('role') != 'user':
        return redirect('/login')

    user_id = session['user_id']

    if request.method == 'POST':
        cid = request.form['complaint_id']
        rating = request.form['rating']
        comments = request.form['comments']

        cursor.execute(
            "INSERT INTO FEEDBACK (FEEDBACK_ID, COMPLAINT_ID, RATING, COMMENTS) VALUES (feedback_seq.NEXTVAL, :1, :2, :3)",
            (cid, rating, comments)
        )
        connection.commit()

        return redirect('/feedback_success')

    cursor.execute("""
    SELECT COMPLAINT_ID FROM COMPLAINT 
    WHERE USER_ID = :1 AND STATUS_ID = 3
    """, (user_id,))

    complaints = cursor.fetchall()

    return render_template("feedback.html", complaints=complaints)


# -------- FEEDBACK SUCCESS --------
@app.route('/feedback_success')
def feedback_success():
    return render_template("feedback_success.html")


# -------- RUN --------
if __name__ == "__main__":
    app.run(debug=True)