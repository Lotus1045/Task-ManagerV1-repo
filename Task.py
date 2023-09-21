import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
from io import BytesIO
import requests
from datetime import datetime

# Function to validate date format
def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

class Task:
    def __init__(self, description, date, priority, progress=0, subtasks=None, notes=None, attachments=None, status="Incomplete", created_timestamp=None, last_modified_timestamp=None):
        self.description = description
        self.date = date
        self.priority = priority
        self.progress = progress  # Progress tracking
        self.subtasks = subtasks or []  # List to store subtasks
        self.notes = notes
        self.attachments = attachments or []  # List to store attachments file paths
        self.status = status  # Adding a status attribute
        self.created_timestamp = created_timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Setting creation timestamp
        self.last_modified_timestamp = last_modified_timestamp  # Last modified timestamp

    def to_string(self):
        return f"{self.description}|{self.date}|{self.priority}|{self.progress}|{'&'.join(self.subtasks)}|{self.notes}|{'&'.join(self.attachments)}|{self.status}|{self.created_timestamp}|{self.last_modified_timestamp}"

    @classmethod
    def from_string(cls, task_string):
        parts = task_string.split('|')
        while len(parts) < 10:  
            if len(parts) == 3:  # Old format
                parts.extend([0, "", "", "", "Incomplete", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None])  # Default values
            else:
                parts.append("")  

        if not parts[7]:
            parts[7] = "Incomplete"

        return cls(parts[0], parts[1], parts[2], int(parts[3]), parts[4].split('&'), parts[5], parts[6].split('&'), parts[7], parts[8], parts[9] if parts[9] else None)


class IndividualTaskManager(tk.Toplevel):
    def __init__(self, category):
        super().__init__()
        
        self.category = category

        self.title(f"{self.category} Tasks")
        self.geometry("800x900") 

        # Fetch and set the background image
        url = "https://assets.newatlas.com/dims4/default/6aa437c/2147483647/strip/true/crop/4000x2309+0+0/resize/2880x1662!/quality/90/?url=http%3A%2F%2Fnewatlas-brightspot.s3.amazonaws.com%2Faa%2F91%2Ff448ca5842388fee5cf0cee89263%2Fwebb-s-portrait-of-the-pillars-of-creation.jpg"
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((800, 900), Image.LANCZOS)
        self.background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        self.tasks_frame = ttk.Frame(self)
        self.tasks_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tasks_scrollbar = ttk.Scrollbar(self.tasks_frame, orient="vertical")
        self.tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tasks_listbox = tk.Listbox(self.tasks_frame, font=("Arial", 14), fg="red", yscrollcommand=self.tasks_scrollbar.set, selectbackground="black", activestyle="none", height=15)

        self.tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tasks_scrollbar.config(command=self.tasks_listbox.yview)

        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(pady=10, fill=tk.X)

        self.task_entry = ttk.Entry(self.entry_frame, width=20, font=("Arial", 14))  # Adjusted font size
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.date_entry = ttk.Entry(self.entry_frame, width=15, font=("Arial", 14))  # Adjusted font size
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.priority = tk.StringVar(value="Low")
        self.priority_menu = tk.OptionMenu(self.entry_frame, self.priority, "Low", "Medium", "High")
        self.priority_menu.pack(side=tk.LEFT, padx=5)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)

        self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add_task, width=10)
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = ttk.Button(self.button_frame, text="Edit", command=self.edit_task, width=10)  # Changed the label to "Edit" and linked to the edit_task function
        self.edit_button.grid(row=0, column=1, padx=5)

        self.complete_button = ttk.Button(self.button_frame, text="Complete", command=self.complete_task, width=10)  # Linked to the complete_task function
        self.complete_button.grid(row=0, column=2, padx=5)

        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_task, width=10)
        self.delete_button.grid(row=0, column=3, padx=5)

        self.details_button = ttk.Button(self.button_frame, text="Details", command=self.view_task_details, width=10)
        self.details_button.grid(row=1, column=0, padx=5)

        self.move_up_button = ttk.Button(self.button_frame, text="Move up", command=self.move_task_up, width=10)  # Changed the label to "Move up" and linked to the move_task_up function
        self.move_up_button.grid(row=1, column=1, padx=5)

        self.move_down_button = ttk.Button(self.button_frame, text="Move Down", command=self.move_task_down, width=10)
        self.move_down_button.grid(row=1, column=2, padx=5)

        self.task_list = []
        self.load_tasks()
        
    def move_task_up(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            if selected_task_index > 0:
                self.task_list[selected_task_index], self.task_list[selected_task_index - 1] = self.task_list[selected_task_index - 1], self.task_list[selected_task_index]
                self.update_task_display()
                self.tasks_listbox.selection_set(selected_task_index - 1)
                self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to move!")

    def move_task_down(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            if selected_task_index < len(self.task_list) - 1:
                self.task_list[selected_task_index], self.task_list[selected_task_index + 1] = self.task_list[selected_task_index + 1], self.task_list[selected_task_index]
                self.update_task_display()
                self.tasks_listbox.selection_set(selected_task_index + 1)
                self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to move!")

        
    def add_task(self):
        task_description = self.task_entry.get()
        date = self.date_entry.get()

        # Adding date format validation
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Invalid Date Format", "The date format should be YYYY-MM-DD")
            return
    
        priority = self.priority.get()
        if task_description:
            task = Task(task_description, date, priority)
            self.task_list.append(task)
            self.update_task_display()
            self.save_tasks()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a task!")

            
    def view_task_details(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            task = self.task_list[selected_task_index]
            TaskDetailsWindow(self, task)
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to view details!")


    def edit_task(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            new_description = simpledialog.askstring("Edit Task", "Enter new task description:")
            if new_description:
                self.task_list[selected_task_index].description = new_description.strip()
                self.update_task_display()
                self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to edit!")


    def complete_task(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            self.task_list[selected_task_index].status = "Completed"  # Updating the status attribute
            self.update_task_display()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to mark as completed!")

    def delete_task(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            del self.task_list[selected_task_index]
            self.update_task_display()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to delete!")

    def update_task_display(self):
        self.tasks_listbox.delete(0, tk.END)
        for task in self.task_list:
            if task.status == "Completed":
                display_text = f"{task.description} ({task.status})"
            else:
                display_text = task.description

            self.tasks_listbox.insert(tk.END, display_text)
    
            priority = task.priority
            if priority == "High":
                self.tasks_listbox.itemconfig(tk.END, {'fg':'red'})
            elif priority == "Medium":
                self.tasks_listbox.itemconfig(tk.END, {'fg':'orange'})
            else:
                self.tasks_listbox.itemconfig(tk.END, {'fg':'green'})


    def save_tasks(self):
        with open(f"{self.category}_tasks.txt", "w") as file:
            for task in self.task_list:
                file.write(task.to_string() + "\n")

            

    def load_tasks(self):
        try:
            with open(f"{self.category}_tasks.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    task = Task.from_string(line.strip())  # Convert string to Task object
                    self.task_list.append(task)
            self.update_task_display()
        except FileNotFoundError:
            pass

        
class TaskDetailsWindow(tk.Toplevel):
    def __init__(self, parent, task):
        super().__init__(parent)
        self.title("Task Details")
        self.geometry("1000x600")  # Adjusted width to 1000 pixels and height to 600 pixels
        self.task = task
        self.parent = parent  # Save reference to the parent

        self.create_widgets()
    
    def create_widgets(self):
        ttk.Label(self, text="Progress:").grid(row=0, column=0, padx=20, pady=5, sticky="w")
        self.progress_var = tk.IntVar(value=self.task.progress)
        ttk.Entry(self, textvariable=self.progress_var, width=50).grid(row=0, column=1, padx=20, pady=5)

        # Adding a section to display and edit the date
        ttk.Label(self, text="Date:").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.date_var = tk.StringVar(value=self.task.date)
        ttk.Entry(self, textvariable=self.date_var, width=50).grid(row=1, column=1, padx=20, pady=5)
        
        # Setting up the subtasks label and listbox
        ttk.Label(self, text="Subtasks:").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.subtasks_listbox = tk.Listbox(self, width=50, height=10)
        self.subtasks_listbox.grid(row=2, column=1, padx=20, pady=5)
        for subtask in self.task.subtasks:
            self.subtasks_listbox.insert(tk.END, subtask)

        # Adding buttons to add and remove subtasks
        ttk.Button(self, text="Add", command=self.add_subtask).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(self, text="Remove", command=self.remove_subtask).grid(row=2, column=3, padx=5, pady=5)

        # Setting up the attachments section
        ttk.Label(self, text="Attachments:").grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.attachments_listbox = tk.Listbox(self, width=50, height=10)
        self.attachments_listbox.grid(row=3, column=1, padx=20, pady=5)
        for attachment in self.task.attachments:
            self.attachments_listbox.insert(tk.END, attachment)

        # Adding buttons to add and remove attachments
        ttk.Button(self, text="Add", command=self.add_attachment).grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(self, text="Remove", command=self.remove_attachment).grid(row=3, column=3, padx=5, pady=5)

        # Notes section
        ttk.Label(self, text="Notes:").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.notes_var = tk.StringVar(value=self.task.notes)
        ttk.Entry(self, textvariable=self.notes_var, width=50).grid(row=4, column=1, padx=20, pady=5)
        
        # Save button to save the task details
        ttk.Button(self, text="Save", command=self.save_task_details).grid(row=5, column=1, padx=20, pady=20)

    def add_subtask(self):
        subtask = simpledialog.askstring("Add Subtask", "Enter subtask:")
        if subtask:
            self.subtasks_listbox.insert(tk.END, subtask)
            self.task.subtasks.append(subtask)

    def remove_subtask(self):
        selected_subtask_index = self.subtasks_listbox.curselection()
        if selected_subtask_index:
            self.subtasks_listbox.delete(selected_subtask_index)
            del self.task.subtasks[selected_subtask_index[0]]

    def add_attachment(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.attachments_listbox.insert(tk.END, filepath)
            self.task.attachments.append(filepath)

    def remove_attachment(self):
        selected_attachment_index = self.attachments_listbox.curselection()
        if selected_attachment_index:
            self.attachments_listbox.delete(selected_attachment_index)
            del self.task.attachments[selected_attachment_index[0]]

    def save_task_details(self):
        if not validate_date(self.date_var.get()):  # Validate the date format
            messagebox.showwarning("Invalid Date Format", "The date format should be YYYY-MM-DD")
            return

        progress_value = self.progress_var.get()
        if progress_value < 0 or progress_value > 100:  # Validate the progress value
            messagebox.showwarning("Invalid Progress Value", "The progress value should be between 0 and 100")
            return

        self.task.progress = progress_value
        self.task.date = self.date_var.get()
        self.task.subtasks = list(self.subtasks_listbox.get(0, tk.END))
        self.task.notes = self.notes_var.get()
        self.task.attachments = list(self.attachments_listbox.get(0, tk.END))
        
        # Adding the last modified timestamp to the task. You also need to add this attribute to the Task class.
        self.task.last_modified_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.parent.save_tasks()
        self.destroy()

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Task Managers")
        self.geometry("300x400")

        # Fetch and set the background image
        url = "https://static.scientificamerican.com/sciam/cache/file/B4A25793-4E05-462B-96F1D8C17425675E_source.jpg"  # Replace with the actual URL of the image you want to use
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((300, 400), Image.LANCZOS)  # Adjust size to match the window size
        self.background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        ttk.Label(self, text="Task Manager Categories", font=("Arial", 24), background="white").pack(pady=20)

        self.categories = ['Learning', 'Coding', 'Cleaning', 'Personal']
        for category in self.categories:
            button = tk.Button(
                self, 
                text=f"Open {category} Tasks", 
                command=lambda cat=category: self.open_task_window(cat), 
                bg='#ffffff',  # Set a light background color
                fg='black',  # Set text color to black
                borderwidth=1,  # Set border width to 1
                relief="solid",  # Set border style to solid
                font=("Arial", 14)  # Set font style and size
            )
            button.pack(pady=10, padx=20, fill=tk.X)  # Pack each button with padding and make it fill the available horizontal space

    def open_task_window(self, category):
        IndividualTaskManager(category)

if __name__ == "__main__":
    main_app = MainApp()
    main_app.mainloop()