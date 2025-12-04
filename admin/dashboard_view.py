import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from config import COLORS


class DashboardView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.render()

    def render(self):
        # --- 1. Background Setup ---
        self.parent_frame.configure(bg=COLORS['bg_main'])
        
        # --- 2. Header Section ---
        header_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="Dashboard Overview", 
                 font=("Segoe UI", 24, "bold"), 
                 fg="#2c3e50", bg=COLORS['bg_main']).pack(side=tk.LEFT)

        current_date = datetime.now().strftime("%A, %B %d, %Y")
        tk.Label(header_frame, text=current_date, 
                 font=("Segoe UI", 12), 
                 fg="#7f8c8d", bg=COLORS['bg_main']).pack(side=tk.RIGHT, pady=10)

        # --- 3. Stats Cards Section (4 Cards) ---
        stats_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        stats_container.pack(fill=tk.X, pady=(0, 15))

        try:
            stats = self.db.get_dashboard_stats()
        except:
            stats = {
                'total_employees': 0,
                'present_today': 0,
                'on_leave': 0,
                'late_employees': 0
            }

        for i in range(4):
            stats_container.columnconfigure(i, weight=1)

        self.create_stat_card(stats_container, 0, "Total Employees", stats.get('total_employees', 0), "#3498db", "👥")
        self.create_stat_card(stats_container, 1, "Present Today", stats.get('present_today', 0), "#2ecc71", "✔")
        self.create_stat_card(stats_container, 2, "On Leave", stats.get('on_leave', 0), "#f39c12", "📋")
        self.create_stat_card(stats_container, 3, "Late Employees", stats.get('late_employees', 0), "#e74c3c", "⏰")

        # --- 4. Main Content Section ---
        main_content = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        main_content.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left Side: Graph
        left_frame = tk.Frame(main_content, bg="white", padx=2, pady=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right Side: Upcoming Holidays
        right_frame = tk.Frame(main_content, bg="white", padx=15, pady=15)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0), ipadx=10)

        # Render Chart
        self.render_attendance_chart(left_frame)

        # Render Upcoming Holidays
        self.render_upcoming_holidays(right_frame)

    def create_stat_card(self, parent, col_index, title, value, color, icon):
        card = tk.Frame(parent, bg="white", padx=20, pady=20)
        card.grid(row=0, column=col_index, sticky="ew", padx=10)
        
        strip = tk.Frame(card, bg=color, width=6)
        strip.place(relx=0, rely=0, relheight=1, anchor="nw")
        
        content = tk.Frame(card, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=(10, 0))
        
        header_row = tk.Frame(content, bg="white")
        header_row.pack(fill=tk.X)
        tk.Label(header_row, text=title.upper(), font=("Segoe UI", 9, "bold"), fg="#95a5a6", bg="white").pack(side=tk.LEFT)
        tk.Label(header_row, text=icon, font=("Segoe UI", 20), fg=color, bg="white").pack(side=tk.RIGHT)
        tk.Label(content, text=str(value), font=("Segoe UI", 32, "bold"), fg="#2c3e50", bg="white").pack(anchor="e", pady=(5, 0))

    def render_attendance_chart(self, parent):
        """Renders attendance chart with daily, weekly, monthly toggles"""
        
        # Frame for title and toggle buttons
        chart_header = tk.Frame(parent, bg="white")
        chart_header.pack(fill=tk.X, padx=15, pady=(15, 0))
        
        tk.Label(chart_header, text="Attendance Overview", 
                 font=("Segoe UI", 14, "bold"), 
                 fg="#2c3e50", bg="white").pack(side=tk.LEFT)
        
        # Toggle buttons frame
        toggle_frame = tk.Frame(chart_header, bg="white")
        toggle_frame.pack(side=tk.RIGHT)
        
        self.chart_view = tk.StringVar(value="daily")
        
        tk.Radiobutton(toggle_frame, text="Daily", variable=self.chart_view, value="daily", 
                       bg="white", fg="#2c3e50", font=("Segoe UI", 9),
                       command=lambda: self.update_chart(parent)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(toggle_frame, text="Weekly", variable=self.chart_view, value="weekly", 
                       bg="white", fg="#2c3e50", font=("Segoe UI", 9),
                       command=lambda: self.update_chart(parent)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(toggle_frame, text="Monthly", variable=self.chart_view, value="monthly", 
                       bg="white", fg="#2c3e50", font=("Segoe UI", 9),
                       command=lambda: self.update_chart(parent)).pack(side=tk.LEFT, padx=5)
        
        # Chart container
        self.chart_frame = tk.Frame(parent, bg="white")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Initial chart
        self.update_chart(parent)

    def update_chart(self, parent):
        """Updates the chart based on selected view"""
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        view_type = self.chart_view.get()
        
        # Get data based on view type
        if view_type == "daily":
            labels, present, absent, leave = self.get_daily_data()
            title = "Daily Attendance (Last 7 Days)"
        elif view_type == "weekly":
            labels, present, absent, leave = self.get_weekly_data()
            title = "Weekly Attendance (Last 4 Weeks)"
        else:  # monthly
            labels, present, absent, leave = self.get_monthly_data()
            title = "Monthly Attendance (Last 6 Months)"
        
        # Get total employees to set dynamic Y-axis max
        try:
            stats = self.db.get_dashboard_stats()
            total_employees = stats.get('total_employees', 100)
        except:
            total_employees = 100
        
        # Set Y-axis max to be 20% higher than total employees for better visualization
        y_max = int(total_employees * 1.2) if total_employees > 0 else 100
        
        # Create figure
        fig = Figure(figsize=(8, 4), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)
        
        x = range(len(labels))
        width = 0.25
        
        bars1 = ax.bar([i - width for i in x], present, width, label="Present", color="#2ecc71")
        bars2 = ax.bar(x, absent, width, label="Absent", color="#e74c3c")
        bars3 = ax.bar([i + width for i in x], leave, width, label="Leave", color="#f39c12")
        
        ax.set_xlabel("Date", fontsize=10, fontweight="bold")
        ax.set_ylabel("Count", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=12, fontweight="bold", color="#2c3e50")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
        ax.set_ylim(0, y_max)  # Dynamic Y-axis based on total employees
        
        # Set Y-axis to show only whole numbers (no decimals)
        import matplotlib.ticker as ticker
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.set_facecolor("white")
        
        fig.tight_layout()
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_daily_data(self):
        """Fetch daily attendance data for last 7 days - REAL DATA ONLY"""
        try:
            data = self.db.get_daily_attendance_stats(days=7)
            
            # Generate all 7 dates (even if no data for those dates)
            all_dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
            
            # Create dictionary from real data
            data_dict = {d['date']: d for d in data} if data else {}
            
            # Build arrays with real data or 0 if no records
            labels = all_dates
            present = [data_dict.get(date, {}).get('present', 0) for date in labels]
            absent = [data_dict.get(date, {}).get('absent', 0) for date in labels]
            leave = [data_dict.get(date, {}).get('leave', 0) for date in labels]
            
            print(f"DEBUG - Daily Data: labels={labels}, present={present}, absent={absent}")
            
            return labels, present, absent, leave
        except Exception as e:
            print(f"Error loading daily data: {e}")
            # If error, return empty data (0 for all)
            dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
            return dates, [0]*7, [0]*7, [0]*7

    def get_weekly_data(self):
        """Fetch weekly attendance data for last 4 weeks - REAL DATA ONLY"""
        try:
            data = self.db.get_weekly_attendance_stats(weeks=4)
            
            if not data:
                return ["W1", "W2", "W3", "W4"], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
            
            labels = [d['week'] for d in data]
            present = [d['present'] for d in data]
            absent = [d['absent'] for d in data]
            leave = [d['leave'] for d in data]
            return labels, present, absent, leave
        except Exception as e:
            print(f"Error fetching weekly stats: {e}")
            return ["W1", "W2", "W3", "W4"], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]

    def get_monthly_data(self):
        """Fetch monthly attendance data for last 6 months - REAL DATA ONLY"""
        try:
            data = self.db.get_monthly_attendance_stats(months=6)
            
            if not data:
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
                return months, [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]
            
            labels = [d['month'] for d in data]
            present = [d['present'] for d in data]
            absent = [d['absent'] for d in data]
            leave = [d['leave'] for d in data]
            return labels, present, absent, leave
        except Exception as e:
            print(f"Error fetching monthly stats: {e}")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            return months, [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]

    def render_upcoming_holidays(self, parent):
        """Renders upcoming holidays section"""
        tk.Label(parent, text="Upcoming Holidays", 
                 font=("Segoe UI", 12, "bold"), 
                 fg="#2c3e50", bg="white").pack(anchor="w", pady=(0, 10))
        
        try:
            holidays = self.db.get_upcoming_holidays(limit=5)
            print(f"DEBUG - Holidays fetched: {holidays}")
        except Exception as e:
            print(f"Error fetching holidays: {e}")
            holidays = []
        
        if not holidays:
            tk.Label(parent, text="No upcoming holidays", 
                     font=("Segoe UI", 10), 
                     fg="#7f8c8d", bg="white").pack(anchor="w", pady=5)
            return
        
        for holiday in holidays:
            holiday_item = tk.Frame(parent, bg="#f7f9fa", padx=10, pady=8)
            holiday_item.pack(fill=tk.X, pady=5)
            
            # Date indicator
            date_label = tk.Label(holiday_item, text="●", font=("Segoe UI", 12), fg="#f39c12", bg="#f7f9fa")
            date_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Holiday details
            details_frame = tk.Frame(holiday_item, bg="#f7f9fa")
            details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            tk.Label(details_frame, text=holiday.get('name', 'N/A'), 
                     font=("Segoe UI", 10, "bold"), 
                     fg="#2c3e50", bg="#f7f9fa").pack(anchor="w")
            tk.Label(details_frame, text=holiday.get('date', 'N/A'), 
                     font=("Segoe UI", 9), 
                     fg="#7f8c8d", bg="#f7f9fa").pack(anchor="w")