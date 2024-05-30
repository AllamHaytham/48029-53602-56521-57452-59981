import asyncio
import csv
import aiofiles
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup

class User:
    def __init__(self, username, password, email, tasks=None):
        self.username = username
        self.password = password
        self.email = email
        self.tasks = tasks if tasks else []

    async def save_user(self, filename):
        users = []
        try:
            async with aiofiles.open(filename, mode='r') as file:
                async for line in file:
                    users.append(line.strip().split(','))
        except FileNotFoundError:
            pass

        for i, user in enumerate(users):
            if user[0] == self.username:
                users[i] = [self.username, self.password, self.email]
                break
        else:
            users.append([self.username, self.password, self.email])

        async with aiofiles.open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(users)

    async def save_tasks(self, filename):
        async with aiofiles.open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            tasks_data = [[self.username, task.task_name, task.description, task.deadline, task.priority, str(task.completed)] for task in self.tasks]
            writer.writerows(tasks_data)

class Task:
    def __init__(self, task_name, description, deadline, priority, user):
        self.task_name = task_name
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.user = user
        self.completed = False

class TaskManagerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users = []
        self.current_user = None
        self.task_list = BoxLayout(orientation='vertical')
        self.logged_in = False
        Clock.schedule_once(self.update_tasks, 1)

    async def load_users(self, user_filename, task_filename):
        users = []
        tasks = {}
        try:
            async with aiofiles.open(user_filename, mode='r') as file:
                async for line in file:
                    row = line.strip().split(',')
                    if len(row) == 3:
                        username, password, email = row
                        users.append(User(username, password, email))
        except FileNotFoundError:
            pass

        try:
            async with aiofiles.open(task_filename, mode='r') as file:
                async for line in file:
                    row = line.strip().split(',')
                    if len(row) == 6:
                        username, task_name, description, deadline, priority, completed = row
                        if username not in tasks:
                            tasks[username] = []
                        tasks[username].append(Task(task_name, description, deadline, priority, None))
        except FileNotFoundError:
            pass

        for user in users:
            if user.username in tasks:
                user.tasks = tasks[user.username]

        return users

    async def save_users_and_tasks(self, user_filename, task_filename):
        users = await self.load_users(user_filename, task_filename)
        tasks = {}
        for user in users:
            if user.username not in tasks:
                tasks[user.username] = []
            for task in user.tasks:
                tasks[user.username].append([user.username, task.task_name, task.description, task.deadline, task.priority, str(task.completed)])

        async with aiofiles.open(user_filename, mode='w', newline='') as user_file, \
                aiofiles.open(task_filename, mode='w', newline='') as task_file:
            user_writer = csv.writer(user_file)
            task_writer = csv.writer(task_file)
            for user in users:
                user_writer.writerow([user.username, user.password, user.email])
            for username, user_tasks in tasks.items():
                task_writer.writerows(user_tasks)

    def update_tasks(self, dt=None):
        self.task_list.clear_widgets()
        if self.current_user:
            for task in self.current_user.tasks:
                completion_status = "(Completed)" if task.completed else ""
                task_label = Label(text=f"{task.task_name} ({task.priority}) {completion_status}")
                self.task_list.add_widget(task_label)
        Clock.schedule_once(self.update_tasks, 5)  # Update tasks every 5 seconds

    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.title_label = Label(text="Task Manager", font_size=24)
        self.layout.add_widget(self.title_label)

        self.result_label = Label(text="")  # Label to display results
        self.layout.add_widget(self.result_label)

        self.register_button = Button(text="Register", on_press=self.show_register_popup)
        self.login_button = Button(text="Login", on_press=self.show_login_popup)
        self.layout.add_widget(self.register_button)
        self.layout.add_widget(self.login_button)

        self.add_task_button = Button(text="Add Task", on_press=self.show_task_popup)
        self.view_tasks_button = Button(text="View Tasks", on_press=self.view_tasks)
        self.mark_complete_button = Button(text="Mark Complete", on_press=self.show_mark_complete_popup)
        self.delete_task_button = Button(text="Delete Task", on_press=self.show_delete_task_popup)
        self.edit_task_button = Button(text="Edit Task", on_press=self.show_edit_task_popup)
        self.logout_button = Button(text="Logout", on_press=self.logout_user)
        self.save_exit_button = Button(text="Save and Exit", on_press=self.save_and_exit)

        self.layout.add_widget(self.add_task_button)
        self.layout.add_widget(self.view_tasks_button)
        self.layout.add_widget(self.mark_complete_button)
        self.layout.add_widget(self.delete_task_button)
        self.layout.add_widget(self.edit_task_button)
        self.layout.add_widget(self.logout_button)
        self.layout.add_widget(self.save_exit_button)
        self.layout.add_widget(self.task_list)

        self.task_popup = Popup(title='Add Task', size_hint=(0.8, 0.8))
        self.task_input = TextInput(hint_text="Enter task name")
        self.submit_button = Button(text="Next", on_press=self.create_task)
        self.back_button = Button(text="Back", on_press=self.close_task_popup)
        self.task_popup_content = BoxLayout(orientation='vertical')
        self.task_popup_content.add_widget(self.task_input)
        self.task_popup_content.add_widget(self.submit_button)
        self.task_popup_content.add_widget(self.back_button)
        self.task_popup.content = self.task_popup_content
        self.task_popup.auto_dismiss = False

        return self.layout

    def show_task_popup(self, instance):
        self.task_input.text = ""
        self.current_input_field = 1
        self.task_input.hint_text = "Enter task name"
        self.task_popup.open()

    def close_task_popup(self, instance):
        self.task_popup.dismiss()

    def create_task(self, instance):
        if self.current_user:
            task_details = self.task_input.text
            if self.current_input_field == 1:
                self.task_name = task_details
                self.task_input.text = ""
                self.task_input.hint_text = "Enter task description"
                self.current_input_field += 1
            elif self.current_input_field == 2:
                self.task_description = task_details
                self.task_input.text = ""
                self.task_input.hint_text = "Enter task deadline (YYYY-MM-DD)"
                self.current_input_field += 1
            elif self.current_input_field == 3:
                self.task_deadline = task_details
                self.task_input.text = ""
                self.task_input.hint_text = "Enter task priority"
                self.current_input_field += 1
            elif self.current_input_field == 4:
                self.task_priority = task_details
                new_task = Task(self.task_name, self.task_description, self.task_deadline, self.task_priority, self.current_user)
                self.current_user.tasks.append(new_task)
                asyncio.run(self.current_user.save_tasks('tasks.csv'))
                self.result_label.text = "Task created successfully!"
                self.task_popup.dismiss()
        else:
            self.result_label.text = "You need to be logged in to add tasks."

    async def exit_app(self, instance):
        if self.current_user:
            await self.current_user.save_tasks('tasks.csv')
            await self.save_users_and_tasks('users.csv', 'tasks.csv')
        self.stop()

    def show_register_popup(self, instance):
        self.register_popup = Popup(title='Register', size_hint=(0.8, 0.8))
        self.register_content = BoxLayout(orientation='vertical')
        self.register_username_input = TextInput(hint_text="Enter username")
        self.register_password_input = TextInput(hint_text="Enter password", password=True)
        self.register_email_input = TextInput(hint_text="Enter email")
        self.register_submit_button = Button(text="Submit", on_press=self.register_user)
        self.register_back_button = Button(text="Back", on_press=self.close_register_popup)
        self.register_content.add_widget(self.register_username_input)
        self.register_content.add_widget(self.register_password_input)
        self.register_content.add_widget(self.register_email_input)
        self.register_content.add_widget(self.register_submit_button)
        self.register_content.add_widget(self.register_back_button)
        self.register_popup.content = self.register_content
        self.register_popup.open()

    def close_register_popup(self, instance):
        self.register_popup.dismiss()

    def register_user(self, instance):
        username = self.register_username_input.text
        password = self.register_password_input.text
        email = self.register_email_input.text

        if not username or not password or not email:
            self.result_label.text = "All fields are required for registration."
            return

        new_user = User(username, password, email)
        self.users.append(new_user)
        asyncio.run(new_user.save_user('users.csv'))
        self.result_label.text = "Registration successful!"
        self.register_popup.dismiss()

    def show_login_popup(self, instance):
        self.login_popup = Popup(title='Login', size_hint=(0.8, 0.8))
        self.login_content = BoxLayout(orientation='vertical')
        self.login_username_input = TextInput(hint_text="Enter username")
        self.login_password_input = TextInput(hint_text="Enter password", password=True)
        self.login_submit_button = Button(text="Submit", on_press=self.login_user)
        self.login_back_button = Button(text="Back", on_press=self.close_login_popup)
        self.login_content.add_widget(self.login_username_input)
        self.login_content.add_widget(self.login_password_input)
        self.login_content.add_widget(self.login_submit_button)
        self.login_content.add_widget(self.login_back_button)
        self.login_popup.content = self.login_content
        self.login_popup.open()

    def close_login_popup(self, instance):
        self.login_popup.dismiss()

    def login_user(self, instance):
        username = self.login_username_input.text
        password = self.login_password_input.text

        user = next((u for u in self.users if u.username == username and u.password == password), None)
        if user:
            self.logged_in = True
            self.current_user = user
            self.result_label.text = f"Login successful! Logged in as {self.current_user.username}"
            self.login_popup.dismiss()
        else:
            self.result_label.text = "Invalid username or password."

    def logout_user(self, instance):
        self.current_user = None
        self.logged_in = False
        self.result_label.text = "Logged out."

    def view_tasks(self, instance):
        if self.current_user:
            self.task_list.clear_widgets()
            for task in self.current_user.tasks:
                completion_status = "(Completed)" if task.completed else ""
                task_label = Label(text=f"{task.task_name} ({task.priority}) {completion_status}")
                self.task_list.add_widget(task_label)
        else:
            self.result_label.text = "You need to be logged in to view tasks."

    def show_mark_complete_popup(self, instance):
        if self.logged_in:
            if self.current_user.tasks:
                self.mark_complete_popup = Popup(title='Mark Complete', size_hint=(0.8, 0.8))
                self.mark_complete_content = BoxLayout(orientation='vertical')
                for task in self.current_user.tasks:
                    task_button = Button(text=f"{task.task_name} ({task.priority})", on_press=lambda instance, t=task: self.complete_task(t))
                    self.mark_complete_content.add_widget(task_button)
                self.mark_complete_back_button = Button(text="Back", on_press=self.close_mark_complete_popup)
                self.mark_complete_content.add_widget(self.mark_complete_back_button)
                self.mark_complete_popup.content = self.mark_complete_content
                self.mark_complete_popup.open()
            else:
                self.result_label.text = "No tasks available to mark complete."
        else:
            self.result_label.text = "You need to be logged in to mark tasks complete."

    def complete_task(self, task):
        task.completed = True
        asyncio.run(self.current_user.save_tasks('tasks.csv'))
        self.result_label.text = f"Task '{task.task_name}' marked as complete."
        self.mark_complete_popup.dismiss()

    def close_mark_complete_popup(self, instance):
        self.mark_complete_popup.dismiss()

    def show_delete_task_popup(self, instance):
        if self.logged_in:
            if self.current_user.tasks:
                self.delete_task_popup = Popup(title='Delete Task', size_hint=(0.8, 0.8))
                self.delete_task_content = BoxLayout(orientation='vertical')
                for task in self.current_user.tasks:
                    task_button = Button(text=f"{task.task_name} ({task.priority})", on_press=lambda instance, t=task: self.remove_task(t))
                    self.delete_task_content.add_widget(task_button)
                self.delete_task_back_button = Button(text="Back", on_press=self.close_delete_task_popup)
                self.delete_task_content.add_widget(self.delete_task_back_button)
                self.delete_task_popup.content = self.delete_task_content
                self.delete_task_popup.open()
            else:
                self.result_label.text = "No tasks available to delete."
        else:
            self.result_label.text = "You need to be logged in to delete tasks."

    def remove_task(self, task):
        self.current_user.tasks.remove(task)
        asyncio.run(self.current_user.save_tasks('tasks.csv'))
        self.result_label.text = f"Task '{task.task_name}' deleted."
        self.delete_task_popup.dismiss()
        self.update_tasks()

    def close_delete_task_popup(self, instance):
        self.delete_task_popup.dismiss()

    def show_edit_task_popup(self, instance):
        if self.logged_in:
            if self.current_user.tasks:
                self.edit_task_popup = Popup(title='Edit Task', size_hint=(0.8, 0.8))
                self.edit_task_content = BoxLayout(orientation='vertical')
                for task in self.current_user.tasks:
                    task_button = Button(text=f"{task.task_name} ({task.priority})", on_press=lambda instance, t=task: self.show_edit_task_details(t))
                    self.edit_task_content.add_widget(task_button)
                self.edit_task_back_button = Button(text="Back", on_press=self.close_edit_task_popup)
                self.edit_task_content.add_widget(self.edit_task_back_button)
                self.edit_task_popup.content = self.edit_task_content
                self.edit_task_popup.open()
            else:
                self.result_label.text = "No tasks available to edit."
        else:
            self.result_label.text = "You need to be logged in to edit tasks."

    def show_edit_task_details(self, task):
        self.edit_details_popup = Popup(title='Edit Task Details', size_hint=(0.8, 0.8))
        self.edit_details_content = BoxLayout(orientation='vertical')
        self.new_name_input = TextInput(hint_text="Enter new name", text=task.task_name)
        self.new_description_input = TextInput(hint_text="Enter new description", text=task.description)
        self.new_deadline_input = TextInput(hint_text="Enter new deadline", text=task.deadline)
        self.new_priority_input = TextInput(hint_text="Enter new priority", text=task.priority)
        self.save_changes_button = Button(text="Save Changes", on_press=lambda instance: self.save_task_changes(task))
        self.edit_details_back_button = Button(text="Back", on_press=self.close_edit_details_popup)
        self.edit_details_content.add_widget(self.new_name_input)
        self.edit_details_content.add_widget(self.new_description_input)
        self.edit_details_content.add_widget(self.new_deadline_input)
        self.edit_details_content.add_widget(self.new_priority_input)
        self.edit_details_content.add_widget(self.save_changes_button)
        self.edit_details_content.add_widget(self.edit_details_back_button)
        self.edit_details_popup.content = self.edit_details_content
        self.edit_details_popup.open()

    def save_task_changes(self, task):
        task.task_name = self.new_name_input.text
        task.description = self.new_description_input.text
        task.deadline = self.new_deadline_input.text
        task.priority = self.new_priority_input.text
        asyncio.run(self.current_user.save_tasks('tasks.csv'))
        self.result_label.text = "Task updated successfully!"
        self.edit_details_popup.dismiss()

    def close_edit_details_popup(self, instance):
        self.edit_details_popup.dismiss()

    def close_edit_task_popup(self, instance):
        self.edit_task_popup.dismiss()

    def update_task(self, task):
        task.task_name = self.edit_task_name_input.text
        task.description = self.edit_task_description_input.text
        task.deadline = self.edit_task_deadline_input.text
        task.priority = self.edit_task_priority_input.text
        asyncio.run(self.current_user.save_tasks('tasks.csv'))
        self.result_label.text = "Task updated!"
        self.edit_task_popup.dismiss()

    def show_task_selection_popup(self, title, callback):
        self.task_selection_popup = Popup(title=title, size_hint=(0.8, 0.8))
        self.task_selection_content = BoxLayout(orientation='vertical')
        self.task_buttons = []
        for task in self.current_user.tasks:
            task_button = Button(text=task.task_name)
            task_button.bind(on_press=lambda btn, t=task: callback(t))
            self.task_buttons.append(task_button)
            self.task_selection_content.add_widget(task_button)
        self.task_selection_popup.content = self.task_selection_content
        self.task_selection_popup.open()

    def save_and_exit(self, instance):
        # Clear the current data in 'users.csv' and 'tasks.csv'
        with open('users.csv', 'w', newline='') as f:
            f.truncate()

        with open('tasks.csv', 'w', newline='') as f:
            f.truncate()

        # Save the users and tasks
        asyncio.run(self.save_all_users('users.csv'))
        asyncio.run(self.current_user.save_tasks('tasks.csv'))

        # Close the app
        self.stop()

    async def save_all_users(self, filename):
        for user in self.users:
            await user.save_user(filename)

if __name__ == '__main__':
    TaskManagerApp().run()
