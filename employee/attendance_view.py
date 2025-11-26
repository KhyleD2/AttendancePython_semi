import tkinter as tk
from tkinter import messagebox, Canvas
from datetime import datetime
import math

class AttendanceView:
    def __init__(self, parent_frame, db, employee):
        self.parent_frame = parent_frame
        self.db = db
        self.employee = employee
        self.render()
    
    def render(self):
        # Clear parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
            
        self.parent_frame.configure(bg="#F5F7FA")
        
        main_container = tk.Frame(self.parent_frame, bg="#F5F7FA")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        center_frame = tk.Frame(main_container, bg="#F5F7FA")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Fetch today's status to decide which buttons to show
        today_status = self.db.get_today_attendance_status(self.employee['id'])

        main_card = tk.Frame(center_frame, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=900, height=950)
        main_card.pack()
        # Allow height to adjust automatically
        # main_card.pack_propagate(False) 

        # ========== HEADER ==========
        header = tk.Frame(main_card, bg="white")
        header.pack(fill=tk.X, padx=80, pady=(50, 30))

        tk.Label(header, text="A T T E N D A N C E   S Y S T E M",
                 font=("Segoe UI", 13, "bold"), fg="#6B7280", bg="white").pack()

        tk.Label(header,
                 text=f"{self.employee['first_name']} {self.employee['last_name']}",
                 font=("Segoe UI", 26, "bold"),
                 fg="#1F2937",
                 bg="white").pack(pady=(15, 8))

        tk.Label(header,
                 text=f"{self.employee['position']} • {self.employee['department']}",
                 font=("Segoe UI", 13),
                 fg="#6B7280",
                 bg="white").pack()

        # ========== CLOCK ==========
        clock_container = tk.Frame(main_card, bg="white")
        clock_container.pack(pady=20)

        self.clock_canvas = Canvas(clock_container, width=350, height=350, bg="white", highlightthickness=0)
        self.clock_canvas.pack()

        self.draw_clock_face()

        self.digital_time = tk.Label(main_card, text="", font=("Segoe UI", 36, "bold"), fg="#1F2937", bg="white")
        self.digital_time.pack(pady=(15, 8))

        self.date_label = tk.Label(main_card, text="", font=("Segoe UI", 14), fg="#6B7280", bg="white")
        self.date_label.pack(pady=(0, 30))

        # ========== STATUS SECTION ==========
        status_section = tk.Frame(main_card, bg="white")
        status_section.pack(fill=tk.X, padx=80, pady=(0, 40))

        # LOGIC:
        # 1. No record for today -> Show CLOCK IN
        # 2. Record exists but NO clock_out time -> Show CLOCK OUT (Working)
        # 3. Record exists AND has clock_out time -> Show COMPLETED
        
        if today_status:
            # Check if they have already clocked out
            if today_status['clock_out']:
                self.create_completed_status(status_section, today_status)
            else:
                # They are currently working
                self.create_working_status(status_section, today_status)
        else:
            # No record yet today
            self.create_ready_status(status_section)

        self.update_clock()

    # ====================== CLOCK FACE ===========================
    def draw_clock_face(self):
        center = 175
        
        self.clock_canvas.create_oval(25, 25, 325, 325, outline="#D1D5DB", width=4)
        self.clock_canvas.create_oval(35, 35, 315, 315, fill="#F9FAFB", outline="#E5E7EB", width=3)
        self.clock_canvas.create_oval(168, 168, 182, 182, fill="#3B82F6", outline="#3B82F6")

        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = center + 120 * math.cos(angle)
            y1 = center + 120 * math.sin(angle)

            if i % 3 == 0:
                x2 = center + 95 * math.cos(angle)
                y2 = center + 95 * math.sin(angle)
                width = 4
                color = "#3B82F6"
            else:
                x2 = center + 105 * math.cos(angle)
                y2 = center + 105 * math.sin(angle)
                width = 3
                color = "#9CA3AF"

            self.clock_canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

        for i in range(12):
            hour = 12 if i == 0 else i
            angle = math.radians(i * 30 - 90)
            x = center + 80 * math.cos(angle)
            y = center + 80 * math.sin(angle)

            self.clock_canvas.create_text(x, y, text=str(hour), font=("Segoe UI", 16, "bold"), fill="#374151")

    # ====================== CLOCK UPDATE ===========================
    def update_clock(self):
        try:
            now = datetime.now()

            self.clock_canvas.delete("hands")
            center = 175

            hours = now.hour % 12
            minutes = now.minute
            seconds = now.second

            hour_angle = math.radians((hours * 30 + minutes * 0.5) - 90)
            hour_x = center + 60 * math.cos(hour_angle)
            hour_y = center + 60 * math.sin(hour_angle)
            self.clock_canvas.create_line(center, center, hour_x, hour_y,
                                          fill="#1F2937", width=8, tags="hands", capstyle=tk.ROUND)

            minute_angle = math.radians((minutes * 6) - 90)
            minute_x = center + 85 * math.cos(minute_angle)
            minute_y = center + 85 * math.sin(minute_angle)
            self.clock_canvas.create_line(center, center, minute_x, minute_y,
                                          fill="#3B82F6", width=6, tags="hands", capstyle=tk.ROUND)

            second_angle = math.radians((seconds * 6) - 90)
            second_x = center + 105 * math.cos(second_angle)
            second_y = center + 105 * math.sin(second_angle)
            self.clock_canvas.create_line(center, center, second_x, second_y,
                                          fill="#EF4444", width=3, tags="hands", capstyle=tk.ROUND)

            self.digital_time.config(text=now.strftime("%I:%M:%S %p"))
            self.date_label.config(text=now.strftime("%A, %B %d, %Y"))

            self.parent_frame.after(1000, self.update_clock)
        except Exception:
            pass # Handle window close

    # ====================== STATUS TEMPLATES ===========================
    def create_completed_status(self, parent, today_status):
        """Displays when user has already clocked out for the day"""
        status_card = tk.Frame(parent, bg="#D1FAE5", highlightbackground="#10B981", highlightthickness=2)
        status_card.pack(fill=tk.X, pady=10)

        tk.Label(status_card, text="A T T E N D A N C E   C O M P L E T E D",
                 font=("Segoe UI", 13, "bold"), fg="#065F46", bg="#D1FAE5").pack(pady=(15, 12))

        times_frame = tk.Frame(status_card, bg="#D1FAE5")
        times_frame.pack(pady=(0, 15))

        # Handle time formatting safely
        clock_in_time = "---"
        if today_status.get('clock_in'):
             if hasattr(today_status['clock_in'], 'strftime'):
                 clock_in_time = today_status['clock_in'].strftime("%I:%M %p")
             else:
                 clock_in_time = str(today_status['clock_in'])

        clock_out_time = "---"
        if today_status.get('clock_out'):
             if hasattr(today_status['clock_out'], 'strftime'):
                 clock_out_time = today_status['clock_out'].strftime("%I:%M %p")
             else:
                 clock_out_time = str(today_status['clock_out'])

        in_frame = tk.Frame(times_frame, bg="#D1FAE5")
        in_frame.pack(side=tk.LEFT, padx=25)

        tk.Label(in_frame, text="CLOCK IN", font=("Segoe UI", 9, "bold"), fg="#059669", bg="#D1FAE5").pack()
        tk.Label(in_frame, text=clock_in_time, font=("Segoe UI", 16, "bold"), fg="#065F46", bg="#D1FAE5").pack()

        tk.Frame(times_frame, bg="#10B981", width=2, height=45).pack(side=tk.LEFT, padx=15)

        out_frame = tk.Frame(times_frame, bg="#D1FAE5")
        out_frame.pack(side=tk.LEFT, padx=25)

        tk.Label(out_frame, text="CLOCK OUT", font=("Segoe UI", 9, "bold"), fg="#059669", bg="#D1FAE5").pack()
        tk.Label(out_frame, text=clock_out_time, font=("Segoe UI", 16, "bold"), fg="#065F46", bg="#D1FAE5").pack()

    def create_working_status(self, parent, today_status):
        """Displays when user is clocked in but NOT clocked out"""
        status_card = tk.Frame(parent, bg="#FEF3C7", highlightbackground="#F59E0B", highlightthickness=2)
        status_card.pack(fill=tk.X, pady=(0, 20))

        tk.Label(status_card, text="C U R R E N T L Y   W O R K I N G",
                 font=("Segoe UI", 12, "bold"), fg="#92400E", bg="#FEF3C7").pack(pady=(15, 5))

        # Handle time format
        clock_in_time = "---"
        if today_status.get('clock_in'):
             if hasattr(today_status['clock_in'], 'strftime'):
                 clock_in_time = today_status['clock_in'].strftime("%I:%M %p")
             else:
                 clock_in_time = str(today_status['clock_in'])

        tk.Label(status_card, text=f"You clocked in at {clock_in_time}",
                 font=("Segoe UI", 11), fg="#92400E", bg="#FEF3C7").pack(pady=(0, 15))

        # --- CLOCK OUT BUTTON ---
        # This button must be OUTSIDE the status card so it's clearly clickable
        # We create a big red button below the yellow status card
        btn = tk.Button(parent, text="STOP WORK / CLOCK OUT", font=("Segoe UI", 14, "bold"),
                        bg="#EF4444", fg="white", activebackground="#DC2626", activeforeground="white",
                        relief=tk.FLAT, cursor="hand2",
                        pady=15,
                        command=self.clock_out)
        btn.pack(fill=tk.X, pady=10)

    def create_ready_status(self, parent):
        """Displays when user hasn't started yet"""
        tk.Label(parent, text="Ready to begin your workday?",
                 font=("Segoe UI", 13), fg="#6B7280", bg="white").pack(pady=(10, 20))

        # --- CLOCK IN BUTTON ---
        btn = tk.Button(parent, text="START WORK / CLOCK IN", font=("Segoe UI", 14, "bold"),
                        bg="#10B981", fg="white", activebackground="#059669", activeforeground="white",
                        relief=tk.FLAT, cursor="hand2",
                        pady=15,
                        command=self.clock_in)
        btn.pack(fill=tk.X, pady=10)

    # ====================== ACTION BUTTONS ===========================
    def clock_in(self):
        success, message = self.db.clock_in(self.employee['id'])
        if success:
            messagebox.showinfo("Clock In Successful", message)
            self.render() # Re-render to show the "Working" status
        else:
            messagebox.showerror("Clock In Failed", message)

    def clock_out(self):
        if messagebox.askyesno("Confirm Clock Out",
                               "Are you sure you want to clock out?\nThis will end your work session for today."):
            success, message = self.db.clock_out(self.employee['id'])
            if success:
                messagebox.showinfo("Clock Out Successful", message)
                self.render() # Re-render to show the "Completed" status
            else:
                messagebox.showerror("Clock Out Failed", message)