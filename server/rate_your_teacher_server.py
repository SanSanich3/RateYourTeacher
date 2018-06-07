from flask import *
from settings import *
from DataBase import DataBase
from Teacher import Teacher
app = Flask(__name__)


# app.config['DEBUG'] = True
app.secret_key = '1'
db = DataBase("rate_your_teacher", HOST, DATABASE_USER, DATABASE_USER_PASSWORD)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/error')
def error():
    return render_template("error.html")


@app.route('/top')
def get_top():
    return 'top'


@app.route('/search', methods=['POST', 'GET'])
def search():
    surname = request.form['surname']
    teacher_id = Teacher.find_by_surname(db, surname)
    if teacher_id is None:
        return render_template("error.html")
    return redirect(url_for('teacher_page', teacher_id=teacher_id))


@app.route('/teacher/<teacher_id>')
def teacher_page(teacher_id):
    teacher_id = int(teacher_id)
    base_info = Teacher.get_base_info(db, teacher_id)
    rating = round(Teacher.get_rating(db, teacher_id), 3)
    bonus = Teacher.get_amount_of_bonus(db, teacher_id)
    print(rating, bonus)
    return render_template("teacher_page.html",
                           base_info=base_info,
                           rating=rating,
                           bonus=bonus,
                           budget=BUDGET)


@app.route('/teacher/plot/<teacher_id>')
def build_plot(teacher_id):
    teacher_id = int(teacher_id)
    response = make_response(Teacher.build_plot(Teacher.get_statistics(db, teacher_id)))
    response.mimetype = 'image/png'
    return response


@app.route('/api/top.json')
def api_top():
    top = Teacher.get_top(db)
    return jsonify({'top': top})


if __name__ == '__main__':
    app.run(debug=False, host=HOST, port=PORT)
