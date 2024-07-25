from flask import Flask,request,render_template,jsonify
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv


# confoguring app
app = Flask(__name__)

cors = CORS(app)



# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize the database
db = SQLAlchemy(app)

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    
    test_case_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(500), nullable=False)
    estimated_time = db.Column(db.Integer, nullable=False)
    module = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Enum('High', 'Low', 'Medium', name='priority_enum'))
    status = db.Column(db.Enum('Pass', 'Fail', 'Idle', name='status_enum'), default='Idle')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TestCase {self.test_case_id}>'

@app.before_first_request
def initialize_database():
    # Create all tables
    db.create_all()

    # Check if the table is empty and add dummy data if it is
    if not TestCase.query.first():
        dummy_cases = [
            TestCase(description="Login functionality test", estimated_time=5, module="Authentication", priority="High", status="Pass"),
            TestCase(description="Signup functionality test", estimated_time=10, module="Registration", priority="Medium", status="Fail"),
            TestCase(description="Data export feature", estimated_time=15, module="Data Management", priority="Low", status="Idle"),
        ]
        db.session.bulk_save_objects(dummy_cases)
        db.session.commit()




# routes for the app
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"



# adding a test case to the table
@app.route('/add_dummy_data', methods=['POST'])
def add_dummy_data():
    # List of dummy test cases to add
    dummy_cases = [
        TestCase(description="Login functionality test", estimated_time=5, module="Authentication", priority="High", status="Pass"),
        TestCase(description="Signup functionality test", estimated_time=10, module="Registration", priority="Medium", status="Fail"),
        TestCase(description="Data export feature", estimated_time=15, module="Data Management", priority="Low", status="Idle"),
    ]
    
    # Add each dummy test case to the session and commit
    for case in dummy_cases:
        db.session.add(case)
    db.session.commit()
    
    return jsonify({"message": "Dummy data added successfully!"}), 201


# getting the list of test cases
@app.route('/get_test_cases', methods=['GET'])
def get_test_cases():
    # Query all test cases from the database
    test_cases = TestCase.query.all()
    print(test_cases);
    
    # Create a list of dictionaries to hold the test cases data
    test_cases_list = [
        {
            'test_case_id': test_case.test_case_id,
            'description': test_case.description,
            'estimated_time': test_case.estimated_time,
            'module': test_case.module,
            'priority': test_case.priority,
            'status': test_case.status,
            'created_at' : test_case.created_at
        }
        for test_case in test_cases
    ]

    print(test_cases_list)
    
    # Return the data as a JSON response
    return jsonify(test_cases_list)
    return "This request is working"

# updating the "status" of test case with "created at time"
@app.route('/update_test_case/<int:test_case_id>', methods=['POST'])
def update_test_case(test_case_id):

    print(request.json)  # See what is being received in the request
    new_status = request.json.get('status')
    print(new_status)  # Check the value of new_status
    print(datetime.utcnow())
    test_case = TestCase.query.get(test_case_id)
    if test_case:
        test_case.status = new_status
        test_case.created_at = datetime.utcnow()  # Update the time to current UTC time
        db.session.commit()
        return jsonify({'message': 'Status and timestamp updated successfully'}), 200
    return jsonify({'error': 'Test case not found'}), 404
