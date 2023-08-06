from flask import Flask, render_template, jsonify, abort
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

# Flask-SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Data model definition
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


# Request parser for course data
parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True, help="Name of the course is required")
parser.add_argument("videos", type=int, required=True, help="Number of videos is required")


class CourseResource(Resource):
    def get(self, course_id=None):
        if course_id is None:
            return jsonify([course.serialize for course in Course.query.all()])
        course = Course.query.get(course_id)
        if course:
            return jsonify(course.serialize)
        else:
            abort(404, message=f"Course with ID {course_id} not found")

    def delete(self, course_id=None, course_name=None):
        if course_id:
            course = Course.query.get(course_id)
        elif course_name:
            course = Course.query.filter_by(name=course_name).first()
        else:
            return {'message': 'Provide either course_id or course_name'}, 400

        if course:
            db.session.delete(course)
            db.session.commit()
            return {'message': f'Course deleted successfully'}
        else:
            abort(404, message=f"Course not found")

    def post(self):
        args = parser.parse_args()
        existing_course = Course.query.filter_by(name=args['name']).first()
        if existing_course:
            return {'message': f"A course with the name '{args['name']}' already exists."}, 400
        new_course = Course(name=args['name'], videos=args['videos'])
        db.session.add(new_course)
        db.session.commit()
        return jsonify(new_course.serialize), 201

    def put(self, course_id=None):
        args = parser.parse_args()
        course = Course.query.filter_by(name=args['name']).first()

        if course:
            # If a course with this name exists, only update the number of videos
            course.videos = args['videos']
        else:
            # If the course doesn't exist, create a new course with the provided data
            course = Course(name=args['name'], videos=args['videos'])
            db.session.add(course)

        db.session.commit()
        return jsonify(course.serialize)


class DeleteAllCourses(Resource):
    def delete(self):
        Course.query.delete()
        db.session.commit()
        return {'message': 'All courses have been deleted.'}


api.add_resource(DeleteAllCourses, '/api/courses/delete_all')
# API resource registration
api.add_resource(CourseResource, "/api/courses", "/api/courses/<int:course_id>",
                 "/api/courses/by_name/<string:course_name>")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database table
    app.run(debug=True, port=3000, host="127.0.0.1")
