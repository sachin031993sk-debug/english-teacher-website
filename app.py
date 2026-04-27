from flask import Flask, render_template, request, redirect, send_from_directory

import os
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute('''

        CREATE TABLE IF NOT EXISTS students (

            id TEXT,
            name TEXT,
            roll TEXT,
            marks TEXT

        )

    ''')
    cursor.execute('''

    CREATE TABLE IF NOT EXISTS attendance (

        student_id TEXT,
        status TEXT

    )

''')

    conn.commit()

    conn.close()


init_db()


# ================= LOGIN DATA =================

teacher_username = "teacher"
teacher_password = "1234"

notes = []

questions = []


# ================= HOME PAGE =================

@app.route('/')
def home():

    return render_template("index.html")


# ================= TEACHER LOGIN =================

@app.route('/teacher', methods=['GET', 'POST'])
def teacher():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == teacher_username and password == teacher_password:

            conn = sqlite3.connect('students.db')

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM students")

            data = cursor.fetchall()

            conn.close()

            return render_template(
                "teacher.html",
                students=data,
                notes=notes
            )

    return render_template("teacher_login.html")


# ================= STUDENT LOGIN =================

@app.route('/student', methods=['GET', 'POST'])
def student():

    if request.method == 'POST':

        sid = request.form['student_id']
        roll = request.form['roll']

        conn = sqlite3.connect('students.db')

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE id=? AND roll=?",
            (sid, roll)
        )

        student_data = cursor.fetchone()

        conn.close()

        if student_data:

         cursor = conn.cursor()
 
    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=?",
        (sid,)
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'",
        (sid,)
    )

    present = cursor.fetchone()[0]

    attendance_percent = 0

    if total > 0:

        attendance_percent = (present / total) * 100

    student = {
        "name": student_data[1],
        "marks": student_data[3]
    }

    return render_template(
        "student.html",
        student=student,
        notes=notes,
        attendance_percent=attendance_percent
    )
    return render_template("student_login.html")


# ================= ADD STUDENT =================

@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form['name']
    sid = request.form['sid']
    roll = request.form['roll']
    marks = request.form['marks']

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?)",
        (sid, name, roll, marks)
    )

    conn.commit()

    conn.close()

    return redirect('/teacher')


# ================= PDF UPLOAD =================

@app.route('/upload_note', methods=['POST'])
def upload_note():

    file = request.files['note']

    if file:

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename
        )

        file.save(filepath)

        notes.append(file.filename)

    return redirect('/teacher')


@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


# ================= ONLINE TEST =================

@app.route('/add_question', methods=['POST'])
def add_question():

    q = request.form['question']
    op1 = request.form['op1']
    op2 = request.form['op2']
    op3 = request.form['op3']
    op4 = request.form['op4']
    ans = request.form['answer']

    questions.append({
        "question": q,
        "options": [op1, op2, op3, op4],
        "answer": ans
    })

    return redirect('/teacher')


@app.route('/test')
def test():

    return render_template(
        "test.html",
        questions=questions
    )


@app.route('/submit_test', methods=['POST'])
def submit_test():

    score = 0

    for i, q in enumerate(questions):

        selected = request.form.get(f'q{i}')

        if selected == q['answer']:

            score += 1

    return f"Your Score: {score}/{len(questions)}"


# ================= RUN SERVER =================
@app.route('/mark_attendance/<sid>/<status>')
def mark_attendance(sid, status):

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO attendance VALUES (?, ?)",
        (sid, status)
    )

    conn.commit()

    conn.close()

    return redirect('/teacher')

if __name__ == '__main__':

    app.run(debug=True)