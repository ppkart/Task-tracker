import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, END, Canvas
import time
import json
import threading
import os
from datetime import datetime, timedelta

class TaskTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Tracker")
        self.root.geometry("400x600")
        self.root.configure(bg="#f0f4f8")

        self.tasks = []
        self.current_task = None
        self.start_time = None
        self.running = False
        self.task_notes = ""
        self.timeline_date = datetime.now()
        self.zoom_level = 1.0

        self.load_tasks()

        self.task_name_label = tk.Label(root, text="Task Name:", font=("Helvetica", 12), bg="#f0f4f8")
        self.task_name_label.pack(pady=10)

        task_name_frame = tk.Frame(root)
        task_name_frame.pack(pady=5)

        self.task_name_entry = tk.Entry(task_name_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.task_name_entry.pack(side=tk.LEFT)

        self.add_task_button = tk.Button(task_name_frame, text="Add Task", font=("Helvetica", 12), bg="#a3d2ca", fg="white", bd=2, relief="groove", command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=5)

        self.task_notes_label = tk.Label(root, text="Task Notes:", font=("Helvetica", 12), bg="#f0f4f8")
        self.task_notes_label.pack(pady=10)

        task_notes_frame = tk.Frame(root)
        task_notes_frame.pack(pady=5)

        self.task_notes_entry = tk.Entry(task_notes_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.task_notes_entry.pack(side=tk.LEFT)

        self.add_note_button = tk.Button(task_notes_frame, text="Add Note", font=("Helvetica", 12), bg="#a3d2ca", fg="white", bd=2, relief="groove", command=self.add_note)
        self.add_note_button.pack(side=tk.LEFT, padx=5)

        frame = tk.Frame(root)
        frame.pack(pady=10)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox = Listbox(frame, font=("Helvetica", 12), bd=2, relief="groove", yscrollcommand=scrollbar.set)
        self.task_listbox.pack()

        scrollbar.config(command=self.task_listbox.yview)

        for task in self.tasks:
            self.task_listbox.insert(END, task)

        self.start_task_button = tk.Button(root, text="Start Task", font=("Helvetica", 12), bg="#5eaaa8", fg="white", bd=2, relief="groove", command=self.start_task)
        self.start_task_button.pack(pady=5)

        self.end_task_button = tk.Button(root, text="End Task", font=("Helvetica", 12), bg="#ffb6b9", fg="white", bd=2, relief="groove", command=self.end_task)
        self.end_task_button.pack(pady=5)

        self.current_task_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f4f8")
        self.current_task_label.pack(pady=10)

        # Add a button to open the timeline window
        self.timeline_button = tk.Button(root, text="Show Timeline", font=("Helvetica", 12), bg="#a3d2ca", fg="white", bd=2, relief="groove", command=self.show_timeline)
        self.timeline_button.pack(pady=5)

    def add_task(self):
        task_name = self.task_name_entry.get()
        if task_name:
            self.tasks.append(task_name)
            self.task_listbox.insert(END, task_name)
            self.task_name_entry.delete(0, END)
            self.save_tasks()
        else:
            messagebox.showwarning("Input Error", "Please enter a task name.")

    def add_note(self):
        self.task_notes = self.task_notes_entry.get()
        messagebox.showinfo("Note Added", "Note added successfully!")

    def start_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            if self.current_task and self.start_time:
                # End the current running task before starting a new one
                self.end_task()
            self.current_task = self.tasks[selected_task_index[0]]
            self.start_time = time.time()
            self.running = True
            threading.Thread(target=self.update_timer).start()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to start.")

    def end_task(self):
        if self.current_task and self.start_time:
            end_time = time.time()
            duration = end_time - self.start_time
            log_entry = {
                "task": self.current_task,
                "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time)),
                "end_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)),
                "duration": duration,
                "notes": self.task_notes
            }
            with open("task_log.json", "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")
            self.current_task = None
            self.start_time = None
            self.running = False
            self.current_task_label.config(text="")
            self.task_notes_entry.delete(0, END)
            self.task_notes = ""
            # Update the timeline window if it's open
            if hasattr(self, 'timeline_window') and tk.Toplevel.winfo_exists(self.timeline_window):
                self.update_timeline()
        else:
            messagebox.showwarning("Timing Error", "No task is currently being timed.")

    def update_timer(self):
        while self.running:
            elapsed_time = time.time() - self.start_time
            elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.current_task_label.config(text=f"Current Task: {self.current_task} | Running Time: {elapsed_str}")
            time.sleep(1)

    def save_tasks(self):
        with open("tasks.txt", "w") as task_file:
            for task in self.tasks:
                task_file.write(task + "\n")

    def load_tasks(self):
        if os.path.exists("tasks.txt"):
            with open("tasks.txt", "r") as task_file:
                for line in task_file:
                    task = line.strip()
                    if task:
                        self.tasks.append(task)

    def show_timeline(self):
        # Create a new window for the timeline
        if hasattr(self, 'timeline_window') and tk.Toplevel.winfo_exists(self.timeline_window):
            return

        self.timeline_window = tk.Toplevel(self.root)
        self.timeline_window.title("Daily Timeline")

        control_frame = tk.Frame(self.timeline_window)
        control_frame.pack(fill=tk.X)

        prev_day_button = tk.Button(control_frame, text="Previous Day", command=self.prev_day)
        prev_day_button.pack(side=tk.LEFT, padx=5, pady=5)

        next_day_button = tk.Button(control_frame, text="Next Day", command=self.next_day)
        next_day_button.pack(side=tk.LEFT, padx=5, pady=5)

        canvas_frame = tk.Frame(self.timeline_window)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_scrollbar_y = Scrollbar(canvas_frame, orient=tk.VERTICAL)
        canvas_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = Canvas(canvas_frame, width=800, height=600, bg="#ffffff", yscrollcommand=canvas_scrollbar_y.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_scrollbar_y.config(command=self.canvas.yview)

        self.canvas.bind("<Control-MouseWheel>", self.zoom)
        self.canvas.bind("<MouseWheel>", self.scroll_y)

        summary_frame = tk.Frame(self.timeline_window, bg="#f0f4f8")
        summary_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.task_summary_label = tk.Label(summary_frame, text="", font=("Helvetica", 12), bg="#f0f4f8")
        self.task_summary_label.pack()

        self.update_timeline()

    def prev_day(self):
        self.timeline_date -= timedelta(days=1)
        self.update_timeline()

    def next_day(self):
        self.timeline_date += timedelta(days=1)
        self.update_timeline()

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_level *= 1.2
        else:
            self.zoom_level /= 1.2
        self.update_timeline()

    def scroll_y(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_timeline(self):
        self.canvas.delete("task_box")
        self.canvas.config(scrollregion=(0, 0, 800, int(600 * self.zoom_level)))
        date_str = self.timeline_date.strftime('%Y-%m-%d')
        self.canvas.create_text(400, 10, text=f"Timeline for {date_str}", font=("Helvetica", 14), tags="task_box")

        task_durations = {}

        for hour in range(25):
            y_position = hour * 24 * self.zoom_level
            self.canvas.create_line(50, y_position + 20, 750, y_position + 20, fill="#d3d3d3", tags="task_box")
            self.canvas.create_text(30, y_position + 20, text=f"{hour:02d}:00", anchor="e", tags="task_box")

        with open("task_log.json", "r") as log_file:
            for line in log_file:
                if line.strip():  # Skip empty lines
                    try:
                        log_entry = json.loads(line)
                        start_time = datetime.strptime(log_entry["start_time"], '%Y-%m-%d %H:%M:%S')
                        end_time = datetime.strptime(log_entry["end_time"], '%Y-%m-%d %H:%M:%S')
                        if start_time.strftime('%Y-%m-%d') == date_str:
                            start_y = start_time.hour * 24 * self.zoom_level + start_time.minute * 0.4 * self.zoom_level + 20
                            end_y = end_time.hour * 24 * self.zoom_level + end_time.minute * 0.4 * self.zoom_level + 20
                            self.canvas.create_rectangle(50, start_y, 750, end_y, fill="#a3d2ca", tags="task_box")
                            self.canvas.create_text(400, (start_y + end_y) / 2, text=log_entry["task"], tags="task_box")

                            task_duration = end_time - start_time
                            if log_entry["task"] in task_durations:
                                task_durations[log_entry["task"]] += task_duration
                            else:
                                task_durations[log_entry["task"]] = task_duration
                    except json.JSONDecodeError:
                        continue

        summary_text = "Task Summary:\n"
        total_work_seconds = 0
        total_break_seconds = 0

        for task, duration in task_durations.items():
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            summary_text += f"{task}: {int(hours)}h {int(minutes)}m\n"
            if task in ["Taukoilua", "Lounas", "Päikyt"]:
                total_break_seconds += duration.total_seconds()
            else:
                total_work_seconds += duration.total_seconds()

        total_work_str = time.strftime('%H:%M:%S', time.gmtime(total_work_seconds))
        total_break_str = time.strftime('%H:%M:%S', time.gmtime(total_break_seconds))

        summary_text += f"\nTotal Work: {total_work_str}\nTotal Break: {total_break_str}\n"

        self.task_summary_label.config(text=summary_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTracker(root)
    root.mainloop()