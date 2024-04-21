import os
import datetime
import csv

class User:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registration_date = datetime.datetime.now()
        self.tasks = []

    def __str__(self):
        return f"Username: {self.username}, Email: {self.email}"

    def save_tasks(self, filename):
        with open(filename, 'w') as f:
            for task in self.tasks:
                f.write(f"{task.task_name},{task.description},{task.deadline},{task.priority},{task.completed}\n")

    def save_user(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.username, self.password, self.email])
            for task in self.tasks:
                writer.writerow([self.username, task.task_name, task.description, task.deadline, task.priority, task.completed])

    @staticmethod
    def load_users(filename):
        users = []
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3:
                        username, password, email = row
                        user = User(username, password, email)
                        users.append(user)
                    elif len(row) == 6:
                        username, task_name, description, deadline, priority, completed = row
                        user = next((u for u in users if u.username == username), None)
                        if user:
                            task = Task(task_name, description, deadline, priority, user)
                            task.completed = completed.lower() == 'true'
                            user.tasks.append(task)
        except FileNotFoundError:
            pass
        return users

class Task:
    def __init__(self, task_name, description, deadline, priority, user):
        self.task_name = task_name
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.user = user
        self.completed = False

def register_user(users, filename):
    username = input("Enter username: ")
    password = input("Enter password: ")
    email = input("Enter email address: ")
    new_user = User(username, password, email)
    users.append(new_user)
    new_user.save_user(filename)
    print("Registration successful!")

def login_user(users):
    username = input("Enter username: ")
    password = input("Enter password: ")
    found_user = None
    for user in users:
        if user.username == username and user.password == password:
            found_user = user
            break
    if found_user:
        print(f"Welcome back, {found_user.username}!")
        return found_user
    else:
        print("Invalid username or password.")
        print("Forgot Password? (y/n): ")
        forgot_password = input().lower()
        if forgot_password == 'y':
            # Handle password reset request
            temporary_password = str(random.randint(100000, 999999))
            print(f"A temporary password has been set: {temporary_password}")
            print("Please change your password on the next login.")
            found_user.password = temporary_password
            return None
        return None
    if found_user:
        if found_user.password == temporary_password:
            print("You are logged in using a temporary password.")
            print("Please set a new password: ")
            new_password = input()
            found_user.password = new_password
            # Save user object with the new password
            return found_user
        else:
            print(f"Welcome back, {found_user.username}!")
            return found_user
        
def create_task(tasks, current_user):
    task_name = input("Enter task name: ")
    description = input("Enter task description: ")
    deadline = input("Enter deadline (YYYY-MM-DD): ")
    priority = input("Enter priority (high, medium, low): ")
    while priority.lower() not in ["high", "medium", "low"]:
        print("Invalid priority. Please enter 'high', 'medium', or 'low'.")
        priority = input("Enter priority (high, medium, low): ")
    new_task = Task(task_name, description, deadline, priority, current_user)
    current_user.tasks.append(new_task)
    print("Task created successfully!")

def view_tasks(tasks):
    if not tasks:
        print("There are no tasks to display.")
    else:
        print("\nYour Tasks:")
        for idx, task in enumerate(tasks, start=1):
            completion_status = "(Completed)" if task.completed else ""
            print(f"{idx}. {task.task_name} ({task.priority}) {completion_status}")

def mark_task_complete(tasks, current_user):
    if not tasks:
        print("There are no tasks to mark complete.")
    else:
        print("Mark Task Complete:")
        print("1. By Task Name")
        print("2. By Task Index")
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            task_name = input("Enter the name of the task to mark complete: ")
            found_task = None
            for task in current_user.tasks:
                if task.task_name == task_name:
                    found_task = task
                    break
            if found_task:
                found_task.completed = True
                print("Task marked complete successfully!")
            else:
                print("Task not found.")
        elif choice == '2':
            try:
                task_index = int(input("Enter the index of the task to mark complete: "))
                if 1 <= task_index <= len(current_user.tasks):
                    current_user.tasks[task_index - 1].completed = True
                    print("Task marked complete successfully!")
                else:
                    print("Invalid task index.")
            except ValueError:
                print("Invalid input. Please enter a number for the index.")
        else:
            print("Invalid choice. Please enter 1 or 2.")

def delete_task(tasks, current_user):
    if not tasks:
        print("There are no tasks to delete.")
    else:
        print("Delete Task:")
        print("1. By Task Name")
        print("2. By Task Index")
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            task_name = input("Enter the name of the task to delete: ")
            found_task = None
            for task in current_user.tasks:
                if task.task_name == task_name:
                    found_task = task
                    break
            if found_task:
                confirmation = input(f"Are you sure you want to delete '{task_name}'? (y/n): ")
                if confirmation.lower() == 'y':
                    current_user.tasks.remove(found_task)
                    print("Task deleted successfully!")
            else:
                print("Task not found.")
        elif choice == '2':
            try:
                task_index = int(input("Enter the index of the task to delete: "))
                if 1 <= task_index <= len(current_user.tasks):
                    confirmation = input(f"Are you sure you want to delete task {task_index}? (y/n): ")
                    if confirmation.lower() == 'y':
                        del current_user.tasks[task_index - 1]
                        print("Task deleted successfully!")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Invalid task index.")
            except ValueError:
                print("Invalid input. Please enter a number for the index.")
        else:
            print("Invalid choice. Please enter 1 or 2.")

def edit_task(tasks, current_user):
    if not tasks:
        print("There are no tasks to edit.")
    else:
        print("Edit Task:")
        print("1. By Task Name")
        print("2. By Task Index")
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            task_name = input("Enter the name of the task to edit: ")
            found_task = None
            for task in current_user.tasks:
                if task.task_name == task_name:
                    found_task = task
                    break
            if found_task:
                print("Current Task Details:")
                print(f"- Task Name: {found_task.task_name}")
                print(f"- Description: {found_task.description}")
                print(f"- Deadline: {found_task.deadline}")
                print(f"- Priority: {found_task.priority}")
                edit_choice = input("What would you like to edit? (name, description, deadline, priority): ")
                if edit_choice.lower() in ['name', 'description', 'deadline', 'priority']:
                    if edit_choice == 'deadline':
                        deadline_valid = False
                        while not deadline_valid:
                            new_value = input(f"Enter the new value for {edit_choice}: ")
                            try:
                                datetime.datetime.strptime(new_value, '%Y-%m-%d')
                                deadline_valid = True
                            except ValueError:
                                print("Invalid deadline format. Please enter in YYYY-MM-DD format (e.g., 2024-04-15).")
                        setattr(found_task, edit_choice, new_value)
                    else:
                        new_value = input(f"Enter the new value for {edit_choice}: ")
                        setattr(found_task, edit_choice, new_value)
                    print("Task edited successfully!")
                else:
                    print("Invalid edit option.")
            else:
                print("Task not found.")
        elif choice == '2':
            try:
                task_index = int(input("Enter the index of the task to edit: "))
                if 1 <= task_index <= len(current_user.tasks):
                    task = current_user.tasks[task_index - 1]
                    print("Current Task Details:")
                    print(f"- Task Name: {task.task_name}")
                    print(f"- Description: {task.description}")
                    print(f"- Deadline: {task.deadline}")
                    print(f"- Priority: {task.priority}")
                    edit_choice = input("What would you like to edit? (name, description, deadline, priority): ")
                    if edit_choice.lower() in ['name', 'description', 'deadline', 'priority']:
                        if edit_choice == 'deadline':
                            deadline_valid = False
                            while not deadline_valid:
                                new_value = input(f"Enter the new value for {edit_choice}: ")
                                try:
                                    datetime.datetime.strptime(new_value, '%Y-%m-%d')
                                    deadline_valid = True
                                except ValueError:
                                    print("Invalid deadline format. Please enter in YYYY-MM-DD format (e.g., 2024-04-15).")
                            setattr(task, edit_choice, new_value)
                        else:
                            new_value = input(f"Enter the new value for {edit_choice}: ")
                            setattr(task, edit_choice, new_value)
                        print("Task edited successfully!")
                    else:
                        print("Invalid edit option.")
                else:
                    print("Invalid task index.")
            except ValueError:
                print("Invalid input. Please enter a number for the index.")
        else:
            print("Invalid choice. Please enter 1 or 2.")

def search_tasks(tasks):
    if not tasks:
        print("There are no tasks to search.")
        return
    search_term = input("Enter search term (task name): ")
    found_tasks = []
    for task in tasks:
        if search_term.lower() in task.task_name.lower():
            found_tasks.append(task)
    if found_tasks:
        print("\nSearch Results:")
        for task in found_tasks:
            completion_status = "(Completed)" if task.completed else ""
            print(f"- {task.task_name} ({task.priority}) {completion_status}")
    else:
        print("No tasks found matching the search term.")

def main():
    users = User.load_users('users.csv')
    current_user = None
    while True:
        print("\nTask Manager Menu:")
        print("1. Create Task")
        print("2. View Tasks")
        print("3. Mark Task Complete")
        print("4. Exit")
        print("5. Delete Task")
        print("6. Edit Task")
        print("7. Register")
        print("8. Login")
        print("9. View Profile")
        print("10. Search Tasks")
        print("11. Exit and Save")
        choice = input("Enter your choice (1-11): ")

        if choice in ['1', '3', '5', '6']:
            if not current_user:
                print("You need to be logged in to perform this action.")
                login_choice = input("Login (y/n)? ")
                if login_choice.lower() == 'y':
                    current_user = login_user(users)
            if choice == '1' and current_user:
                create_task(current_user.tasks, current_user)
            elif choice == '3' and current_user:
                mark_task_complete(current_user.tasks, current_user)
            elif choice == '5' and current_user:
                delete_task(current_user.tasks, current_user)
            elif choice == '6' and current_user:
                edit_task(current_user.tasks, current_user)

        elif choice == '2':
            if current_user:
                view_tasks(current_user.tasks)
            else:
                print("You need to be logged in to view tasks.")
        elif choice == '4':
            print("Exiting Task Manager...")
            break
        elif choice == '7':
            register_user(users, 'users.csv')
        elif choice == '8':
            current_user = login_user(users)
        elif choice == '9':
            if current_user:
                print("\nUser Profile:")
                print(f"Username: {current_user.username}")
                print(f"Email: {current_user.email}")
                print(f"Registration Date: {current_user.registration_date}")
            else:
                print("You need to be logged in to view your profile.")
        elif choice == '10':
            if current_user:
                search_tasks(current_user.tasks)
            else:
                print("You need to be logged in to search tasks.")
        elif choice == '11':
            if current_user:
                for user in users:
                    user.save_user('users.csv')
                print("Tasks and user data saved. Exiting...")
                break
            else:
                print("No user logged in. Exiting without saving.")
                break
        else:
            print("Invalid choice. Please enter a number between 1 and 11.")

if __name__ == "__main__":
    main()