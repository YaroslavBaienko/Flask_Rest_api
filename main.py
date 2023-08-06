from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api()

courses = {1: {"name": "Python", "videos": 15},
           2: {"name": "Java", "videos": 10},
           3: {"name": "C#", "videos": 2},
           4: {"name": "Java Script", "videos": 1}
           }

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True)
parser.add_argument("videos", type=int, required=True)


class Main(Resource):
    def get(self, course_id=None):
        if course_id is None:
            return courses
        else:
            return courses[course_id]

    def delete(self, course_id):
        if course_id not in courses:
            abort(404, message=f"Course with course_id {course_id} not found")
        del courses[course_id]
        return courses

    def post(self):
        new_course = parser.parse_args()
        course_id = max(int(v) for v in courses.keys()) + 1
        courses[course_id] = new_course
        return courses, 201

    def put(self, course_id):
        courses[course_id] = parser.parse_args()
        return courses


api.add_resource(Main, "/api/courses/<int:course_id>", "/api/courses")
api.init_app(app)


@app.get("/")
def index():
    return render_template()


if __name__ == '__main__':
    app.run(debug=True, port=3000, host="127.0.0.1")
