import json
import random
from typing import Optional, Dict, Any

# Assuming get_students_collection is correctly defined in your db.py
from .db import get_students_collection

# Database connection
students_collection = get_students_collection()

# --- Mock Data Population ---

def populate_db_with_mock_data():
    """
    Populates the students collection with mock data for testing.
    This function is called at application startup.
    """
    if students_collection is None:
        print("Could not populate mock data: database connection failed.")
        return

    # Clear existing data
    students_collection.delete_many({})
    print("Clearing existing mock data.")

    # Generate and insert new mock data
    mock_students = [
        {"id": "23-1001", "name": "Ayesha Khan", "department": "Computer Science", "email": "ayesha@saylani.edu"},
        {"id": "23-1002", "name": "Usman Ali", "department": "Software Engineering", "email": "usman@saylani.edu"},
        {"id": "23-1003", "name": "Fatima Rehman", "department": "Data Science", "email": "fatima@saylani.edu"},
        {"id": "23-1004", "name": "Bilal Ahmed", "department": "Computer Science", "email": "bilal@saylani.edu"},
        {"id": "23-1005", "name": "Sana Ejaz", "department": "Software Engineering", "email": "sana@saylani.edu"}
    ]
    students_collection.insert_many(mock_students)
    print("Populated database with mock data.")

# --- Student Management Tools (CRUD) ---

def list_students():
    """
    Lists all students in the database.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    students = list(students_collection.find({}, {"_id": 0}))
    return json.dumps(students, indent=2)

def get_student(id: str):
    """
    Retrieves a single student's record by their ID.
    
    Args:
        id (str): The ID of the student to retrieve.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    student = students_collection.find_one({"id": id}, {"_id": 0})
    if student:
        return json.dumps(student, indent=2)
    return f"Error: No student found with ID {id}."

def add_student(id: str, name: str, department: str, email: str):
    """
    Adds a new student record to the database.
    
    Args:
        id (str): The new student's ID.
        name (str): The new student's full name.
        department (str): The new student's department.
        email (str): The new student's email.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    if students_collection.find_one({"id": id}):
        return f"Error: Student with ID {id} already exists."
    
    new_student = {
        "id": id,
        "name": name,
        "department": department,
        "email": email
    }
    students_collection.insert_one(new_student)
    return f"Success: Student {name} with ID {id} has been added."

def update_student(id: str, field: str, new_value: str):
    """
    Updates a specific field for a student record.
    
    Args:
        id (str): The ID of the student to update.
        field (str): The field to update (e.g., 'name', 'department', 'email').
        new_value (str): The new value for the field.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    
    result = students_collection.update_one(
        {"id": id},
        {"$set": {field: new_value}}
    )
    if result.matched_count == 0:
        return f"Error: No student found with ID {id}."
    return f"Success: Student with ID {id} updated successfully."

def delete_student(id: str):
    """
    Deletes a student record by their ID.
    
    Args:
        id (str): The ID of the student to delete.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    
    result = students_collection.delete_one({"id": id})
    if result.deleted_count == 0:
        return f"Error: No student found with ID {id}."
    return f"Success: Student with ID {id} has been deleted."

# --- Campus Analytics Tools ---

def get_total_students():
    """
    Returns the total count of students in the database.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    count = students_collection.count_documents({})
    return str(count)

def get_students_by_department():
    """
    Returns a count of students grouped by their department.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    
    pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1}}}
    ]
    results = list(students_collection.aggregate(pipeline))
    dept_counts = {item['_id']: item['count'] for item in results}
    return json.dumps(dept_counts, indent=2)

def get_recent_onboarded_students(limit: Optional[int] = 5):
    """
    Returns a list of the most recently onboarded students.
    (This is a mock implementation since we don't have a date field.)
    
    Args:
        limit (int): The number of recent students to return.
    """
    if students_collection is None:
        return "Error: Database connection failed."
    
    # In a real app, you would sort by a 'created_at' timestamp.
    # Here, we'll just return a random subset of students.
    all_students = list(students_collection.find({}, {"_id": 0}))
    random.shuffle(all_students)
    recent = all_students[:limit]
    return json.dumps(recent, indent=2)

def get_active_students_last_7_days():
    """
    Returns the number of active students in the last 7 days.
    (This is a mock implementation as there are no activity logs.)
    """
    if students_collection is None:
        return "Error: Database connection failed."
    total_students = students_collection.count_documents({})
    # Return a random number to simulate activity
    active_count = random.randint(int(total_students * 0.5), total_students)
    return str(active_count)

# --- Campus FAQ Tools ---

def get_cafeteria_timings():
    """
    Provides the timings for the campus cafeteria.
    """
    return "The cafeteria is open from 8:00 AM to 10:00 PM."

def get_library_hours():
    """
    Provides the operating hours for the campus library.
    """
    return "The library is open from 9:00 AM to 9:00 PM on weekdays and 10:00 AM to 6:00 PM on weekends."

def get_event_schedule():
    """
    Provides the schedule for upcoming campus events.
    """
    return "Upcoming events: AI Hackathon on 25th Oct, Annual Sports Day on 15th Nov."

# --- Notification Tool ---

def send_email(student_id: str, message: str):
    """
    Simulates sending an email to a student.
    
    Args:
        student_id (str): The ID of the student to email.
        message (str): The content of the email.
    """
    print(f"--- MOCK EMAIL ---")
    print(f"To: Student with ID {student_id}")
    print(f"Message: {message}")
    print(f"--- END MOCK EMAIL ---")
    return f"Success: A mock email has been sent to student ID {student_id}."
