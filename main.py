from flask import Flask, render_template, jsonify, abort, redirect, url_for, session, request, g
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from functools import wraps
import config

app = Flask(__name__)
app.secret_key = 'your_secret_key'
api = Api(app)
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key=config.consumer_key,
    consumer_secret=config.consumer_secret,
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Request parser for course data
parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True, help="Name of the course is required")
parser.add_argument("videos", type=int, required=True, help="Number of videos is required")


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    videos = db.Column(db.Integer, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'videos': self.videos
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('github_token')
        if not token:
            # Проверяем заголовок Authorization
            token = request.headers.get('Authorization')
            if token:
                # Извлекаем значение токена, удаляя префикс "Bearer "
                token = token.split(" ")[1]
            else:
                return {'message': 'Token is missing.'}, 403

        # Здесь вы можете добавить дополнительную верификацию токена, если это необходимо

        return f(*args, **kwargs)

    return decorated


class CourseResource(Resource):
    @token_required
    def get(self, course_id=None, course_name=None):
        if course_id:
            course = Course.query.get(course_id)
            if course:
                return course.serialize
            else:
                abort(404, message="Course with id {} doesn't exist".format(course_id))
        elif course_name:
            course = Course.query.filter_by(name=course_name).first()
            if course:
                return course.serialize
            else:
                abort(404, message="Course with name {} doesn't exist".format(course_name))
        else:
            courses = Course.query.all()
            return [course.serialize for course in courses]

    @token_required
    def post(self):
        args = parser.parse_args()
        existing_course = Course.query.filter_by(name=args['name']).first()
        if existing_course:
            abort(400, message=f"A course with the name {args['name']} already exists.")
        course = Course(name=args['name'], videos=args['videos'])
        db.session.add(course)
        db.session.commit()
        return course.serialize, 201

    @token_required
    def put(self, course_id=None, course_name=None):
        args = parser.parse_args()
        course = None
        if course_id:
            course = Course.query.get(course_id)
        elif course_name:
            course = Course.query.filter_by(name=course_name).first()

        if not course:
            abort(404, message=f"Course not found.")

        course.name = args['name']
        course.videos = args['videos']

        db.session.commit()
        return course.serialize

    @token_required
    def delete(self, course_id=None, course_name=None):
        course = None
        if course_id:
            course = Course.query.get(course_id)
        elif course_name:
            course = Course.query.filter_by(name=course_name).first()

        if not course:
            abort(404, message=f"Course not found.")

        db.session.delete(course)
        db.session.commit()
        return {'message': 'Course has been deleted.'}


class DeleteAllCourses(Resource):
    @token_required
    def delete(self):
        Course.query.delete()
        db.session.commit()
        return {'message': 'All courses have been deleted.'}


api.add_resource(DeleteAllCourses, '/api/courses/delete_all')
api.add_resource(CourseResource, "/api/courses", "/api/courses/<int:course_id>",
                 "/api/courses/by_name/<string:course_name>")


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token')
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['github_token'] = (resp['access_token'], '')
    github_user = github.get('user')
    user = User.query.filter_by(username=github_user.data['login']).first()
    if not user:
        user = User(username=github_user.data['login'], email=github_user.data['email'])
        db.session.add(user)
        db.session.commit()
    return jsonify(username=github_user.data['login'], email=github_user.data['email'])


@app.route('/get_token')
def get_token():
    return jsonify(token=session.get('github_token'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000, host="127.0.0.1")
