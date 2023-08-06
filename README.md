# Flask Course Management API

This repository contains a simple Flask application that provides a RESTful API for managing courses. The API allows users to perform CRUD operations on courses, including adding, updating, deleting, and retrieving course details.

## Features

- **Flask RESTful API**: The API is built using Flask and Flask-RESTful.
- **SQLite Database**: The application uses SQLite as its database.
- **Flask-SQLAlchemy**: ORM for database operations.
- **Data Model**: The application defines a `Course` model with attributes: `id`, `name`, and `videos`.
- **Endpoints**:
  - Retrieve all courses or a specific course by ID or name.
  - Add a new course.
  - Update an existing course.
  - Delete a specific course or all courses.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/YaroslavBaienko/Flask_Rest_api.git
   ```

2. Navigate to the project directory:

   ```bash
   cd <project_directory>
   ```

3. Install the required packages:
   ```bash
   pip install flask flask_restful flask_sqlalchemy
   ```

## Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. The application will start on `http://127.0.0.1:3000/`.

3. Use the following endpoints for API operations:

   - **GET** `/api/courses`: Retrieve all courses.
   - **GET** `/api/courses/<int:course_id>`: Retrieve a course by its ID.
   - **GET** `/api/courses/by_name/<string:course_name>`: Retrieve a course by its name.
   - **POST** `/api/courses`: Add a new course.
   - **PUT** `/api/courses/<int:course_id>`: Update an existing course.
   - **DELETE** `/api/courses/<int:course_id>`: Delete a course by its ID.
   - **DELETE** `/api/courses/by_name/<string:course_name>`: Delete a course by its name.
   - **DELETE** `/api/courses/delete_all`: Delete all courses.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
