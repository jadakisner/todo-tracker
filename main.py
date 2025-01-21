from fasthtml.common import *
from database import get_connection, init_db
from datetime import datetime
import sqlite3

# Initialize the database
init_db()

app, rt = fast_app()

# Home route
@rt('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY creation_time DESC")
    tasks = cursor.fetchall()
    conn.close()

    task_list = [
        Div(
            H3(task[1]),  # Title
            P(task[2]),   # Body
            P(f"Due: {task[4] if task[4] else 'No due date'}"),  # Due date
            P(f"Tags: {task[6] if task[6] else 'No tags'}"),  # Tags
            P(f"Status: {'Completed' if task[5] else 'Not Completed'}"),  # Completion status
            Input(
                name=f"completed_{task[0]}",
                placeholder="Completed? (yes/no)",
                value="yes" if task[5] else "no",  # Display 'yes' if task is completed, 'no' otherwise
            ),
            Button(
                "Mark Complete" if not task[5] else "Mark Incomplete",
                hx_post=f"/toggle/{task[0]}"
            ),
            hx_target="this",
        )
        for task in tasks
    ]

    return Div(
        H1("ToDo Tracker"),
        A("Add Task", href="/add"),
        Div(*task_list),
    )

# Add task route
@rt('/add', methods=["GET", "POST"])
def add_task(title=None, body=None, due_date=None, tags=None, completed=None):
    if title:  # POST request
        # Basic validation to ensure title and body are not empty
        if not title or not body:
            return Div(
                H3("Error: Title and body cannot be empty!"),
                A("Go back", href="/add")
            )

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tasks (title, body, creation_time, due_date, tags, is_completed) VALUES (?, ?, ?, ?, ?, ?)",
                (title, body, datetime.now().isoformat(), due_date, tags, 1 if completed == "yes" else 0),
            )
            conn.commit()
        except sqlite3.Error as e:
            return Div(
                H3(f"Database error: {e}"),
                A("Go back", href="/add")
            )
        finally:
            conn.close()
        
        return Redirect("/")
    else:  # GET request
        return Div(
            H1("Add a New Task"),
            Form(
                Input(name="title", placeholder="Title", required=True),
                P("Details"),
                Textarea(name="body", placeholder="Enter task details here"),
                Input(name="due_date", type="date"),
                P("Tags (comma-separated)"),
                Input(name="tags", placeholder="e.g. work, personal"),
                P("Mark as completed? (yes/no)"),
                Input(name="completed", placeholder="yes or no"),
                Button("Add Task", type="submit"),
                method="post",
            ),
        )

# Toggle task completion
@rt('/toggle/{task_id}', methods=["POST"])
def toggle_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tasks SET is_completed = NOT is_completed WHERE id = ?",
            (task_id,)
        )
        conn.commit()
    except sqlite3.Error as e:
        return Div(
            H3(f"Database error: {e}"),
            A("Go back", href="/")
        )
    finally:
        conn.close()

    return Redirect("/")

# Run the server
serve()
