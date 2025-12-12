import tkinter as tk
from tkinter import ttk
from config import COLORS
from datetime import datetime, timedelta
from collections import defaultdict

class ReportsView:
    def __init__(self, parent_frame, db, employee):
        self.parent_frame = parent_frame
        self.db = db
        self.employee = employee
        self.current_filter = "All Time"  # Default filter
        
        # Clear parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        self.render()
    
    def calculate_kpis(self):
        """Calculate KPI metrics from attendance logs AND leave requests"""
        try:
            logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
            
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM leave_requests 
                WHERE employee_id = %s AND status = 'approved'
            """, (self.employee['id'],))
            approved_leaves = cursor.fetchall()
            cursor.close()
            
            total_days = len(logs)
            present_days = sum(1 for log in logs if log['status'] == 'present')
            late_days = sum(1 for log in logs if log['status'] == 'late')
            absent_days = sum(1 for log in logs if log['status'] == 'absent')
            leave_days = len(approved_leaves)
            
            attendance_rate = ((present_days + late_days) / total_days * 100) if total_days > 0 else 0
            
            return {
                'present': present_days,
                'late': late_days,
                'absent': absent_days,
                'leave': leave_days,
                'rate': attendance_rate
            }
        except Exception as e:
            print(f"Error calculating KPIs: {e}")
            return {'present': 0, 'late': 0, 'absent': 0, 'leave': 0, 'rate': 0}
    
    def get_week_label(self, date_obj):
        """Get week label in format 'Nov 24 - 30'"""
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        if start_of_week.month == end_of_week.month:
            return f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%d')}"
        else:
            return f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
    
    def get_weekly_attendance(self):
        """Get attendance data for the last 4 weeks"""
        try:
            logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
            weekly_data = defaultdict(lambda: {'present': 0, 'late': 0})
            
            for log in logs:
                if isinstance(log['date'], str):
                    date_obj = datetime.strptime(log['date'], "%Y-%m-%d")
                else:
                    date_obj = log['date']
                
                week_label = self.get_week_label(date_obj)
                
                if log['status'] == 'present':
                    weekly_data[week_label]['present'] += 1
                elif log['status'] == 'late':
                    weekly_data[week_label]['late'] += 1
            
            if weekly_data:
                sorted_weeks = sorted(weekly_data.keys(), 
                    key=lambda x: datetime.strptime(x.split(' - ')[0] + ' 2025', '%b %d %Y'))[-4:]
                return {week: weekly_data[week] for week in sorted_weeks}
            return {}
        except Exception as e:
            print(f"Error getting weekly attendance: {e}")
            return {}
    
    def get_week_options(self):
        """Get list of available weeks for filtering"""
        try:
            logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
            weeks = set()
            
            for log in logs:
                if isinstance(log['date'], str):
                    date_obj = datetime.strptime(log['date'], "%Y-%m-%d")
                else:
                    date_obj = log['date']
                week_label = self.get_week_label(date_obj)
                weeks.add(week_label)
            
            sorted_weeks = sorted(list(weeks), 
                key=lambda x: datetime.strptime(x.split(' - ')[0] + ' 2025', '%b %d %Y'))
            return ["All Time"] + sorted_weeks
        except Exception as e:
            print(f"Error getting week options: {e}")
            return ["All Time"]
    
    def filter_logs_by_week(self, logs, week_label):
        """Filter logs by selected week"""
        if week_label == "All Time":
            return logs
        
        try:
            # Parse week range
            parts = week_label.split(' - ')
            start_str = parts[0]
            
            filtered = []
            for log in logs:
                if isinstance(log['date'], str):
                    date_obj = datetime.strptime(log['date'], "%Y-%m-%d")
                else:
                    date_obj = log['date']
                
                log_week = self.get_week_label(date_obj)
                if log_week == week_label:
                    filtered.append(log)
            
            return filtered
        except Exception as e:
            print(f"Error filtering logs: {e}")
            return logs
    
    def create_gradient_card(self, parent, title, value, gradient_start, gradient_end, icon):
        """Create a modern gradient KPI card"""
        card_shadow = tk.Frame(parent, bg='#e0e0e0', highlightthickness=0)
        card = tk.Frame(card_shadow, bg=gradient_start, highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        icon_frame = tk.Frame(card, bg=gradient_start)
        icon_frame.pack(anchor=tk.NW, padx=20, pady=15)
        
        icon_circle = tk.Canvas(icon_frame, width=50, height=50, 
                               bg=gradient_start, highlightthickness=0)
        icon_circle.pack()
        icon_circle.create_oval(5, 5, 45, 45, fill=gradient_end, outline='')
        icon_circle.create_text(25, 25, text=icon, font=("Arial", 20), fill='white')
        
        content_frame = tk.Frame(card, bg=gradient_start)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(content_frame, text=title, font=("Arial", 10, "bold"),
                fg='white', bg=gradient_start, anchor=tk.W).pack(fill=tk.X)
        
        value_text = f"{value:.1f}%" if title == "Attendance Rate" else str(value)
        tk.Label(content_frame, text=value_text, font=("Arial", 36, "bold"),
                fg='white', bg=gradient_start, anchor=tk.W).pack(fill=tk.X, pady=(5, 0))
        
        return card_shadow
    
    def create_modern_chart(self, parent, data):
        """Create a modern bar chart without Y-axis numbers"""
        chart_frame = tk.Frame(parent, bg=COLORS['bg_white'], highlightthickness=0)
        
        header = tk.Frame(chart_frame, bg='#4A90E2', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Weekly Attendance Trend", 
                font=("Arial", 16, "bold"),
                fg='white', bg='#4A90E2').pack(side=tk.LEFT, padx=20, pady=12)
        
        # Filter dropdown for chart
        chart_filter_frame = tk.Frame(header, bg='#4A90E2')
        chart_filter_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(chart_filter_frame, text="Show:", font=("Arial", 10, "bold"),
                fg='white', bg='#4A90E2').pack(side=tk.LEFT, padx=(0, 10))
        
        self.chart_filter_var = tk.StringVar(value="Last 4 Weeks")
        chart_filter_options = ["Last 4 Weeks", "Last 8 Weeks", "Last 12 Weeks", "All Time"]
        
        chart_filter_dropdown = ttk.Combobox(chart_filter_frame, textvariable=self.chart_filter_var,
                                            values=chart_filter_options, state='readonly',
                                            width=15, font=("Arial", 10))
        chart_filter_dropdown.pack(side=tk.LEFT)
        
        canvas_frame = tk.Frame(chart_frame, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        canvas = tk.Canvas(canvas_frame, width=550, height=350, 
                          bg='white', highlightthickness=0)
        canvas.pack()
        
        # Store canvas for updates
        self.chart_canvas = canvas
        self.chart_canvas_frame = canvas_frame
        
        # Bind filter change
        chart_filter_dropdown.bind('<<ComboboxSelected>>', 
                                  lambda e: self.update_chart())
        
        if not data:
            canvas.create_text(275, 175, text="No attendance data yet",
                             font=("Arial", 14), fill=COLORS['text_gray'])
            return chart_frame
        
        self.draw_chart(canvas, data)
        
        return chart_frame
    
    def draw_chart(self, canvas, data):
        """Draw the chart on canvas"""
        margin_left = 30
        margin_right = 30
        margin_top = 50
        margin_bottom = 60
        chart_width = 550 - margin_left - margin_right
        chart_height = 350 - margin_top - margin_bottom
        
        weeks = list(data.keys())
        if not weeks:
            return
            
        max_value = max(sum(d.values()) for d in data.values()) or 1
        
        # Draw subtle grid lines (no Y-axis numbers)
        for i in range(6):
            y = margin_top + (chart_height / 5) * i
            canvas.create_line(margin_left, y, 550 - margin_right, y,
                             fill='#f0f0f0', width=1)
        
        bar_group_width = chart_width / len(weeks)
        bar_width = min(bar_group_width / 3, 60)
        spacing = bar_width * 0.3
        
        colors = {'present': '#4CAF50', 'late': '#FF9800'}
        
        x = margin_left + bar_group_width / 2 - bar_width
        
        for week in weeks:
            week_data = data[week]
            
            for i, (status, count) in enumerate(week_data.items()):
                if count > 0:
                    bar_height = (count / max_value) * chart_height
                    y1 = margin_top + chart_height - bar_height
                    y2 = margin_top + chart_height
                    x1 = x + (i * (bar_width + spacing))
                    x2 = x1 + bar_width
                    
                    radius = 8
                    self.create_rounded_rectangle(canvas, x1, y1, x2, y2,
                                                 radius, fill=colors[status])
                    
                    canvas.create_text((x1 + x2) / 2, y1 - 10,
                                     text=str(count), font=("Arial", 10, "bold"),
                                     fill=colors[status])
            
            canvas.create_text(x + bar_width / 2 + spacing / 2, 
                             margin_top + chart_height + 20,
                             text=week, font=("Arial", 9, "bold"),
                             fill=COLORS['text_dark'])
            
            x += bar_group_width
        
        # Legend
        legend_x = margin_left
        legend_y = 20
        for status, color in colors.items():
            canvas.create_oval(legend_x, legend_y, 
                             legend_x + 12, legend_y + 12,
                             fill=color, outline='')
            canvas.create_text(legend_x + 20, legend_y + 6,
                             text=status.capitalize(), font=("Arial", 10, "bold"),
                             fill=COLORS['text_dark'], anchor=tk.W)
            legend_x += 100
    
    def update_chart(self):
        """Update chart based on filter selection"""
        try:
            filter_value = self.chart_filter_var.get()
            
            # Get all weekly data
            logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
            weekly_data = defaultdict(lambda: {'present': 0, 'late': 0})
            
            for log in logs:
                if isinstance(log['date'], str):
                    date_obj = datetime.strptime(log['date'], "%Y-%m-%d")
                else:
                    date_obj = log['date']
                
                week_label = self.get_week_label(date_obj)
                
                if log['status'] == 'present':
                    weekly_data[week_label]['present'] += 1
                elif log['status'] == 'late':
                    weekly_data[week_label]['late'] += 1
            
            # Filter based on selection
            if weekly_data:
                sorted_weeks = sorted(weekly_data.keys(), 
                    key=lambda x: datetime.strptime(x.split(' - ')[0] + ' 2025', '%b %d %Y'))
                
                if filter_value == "Last 4 Weeks":
                    sorted_weeks = sorted_weeks[-4:]
                elif filter_value == "Last 8 Weeks":
                    sorted_weeks = sorted_weeks[-8:]
                elif filter_value == "Last 12 Weeks":
                    sorted_weeks = sorted_weeks[-12:]
                # else: All Time - use all weeks
                
                filtered_data = {week: weekly_data[week] for week in sorted_weeks}
            else:
                filtered_data = {}
            
            # Clear and redraw canvas
            self.chart_canvas.delete("all")
            if filtered_data:
                self.draw_chart(self.chart_canvas, filtered_data)
            else:
                self.chart_canvas.create_text(275, 175, text="No attendance data yet",
                                            font=("Arial", 14), fill=COLORS['text_gray'])
        except Exception as e:
            print(f"Error updating chart: {e}")
            import traceback
            traceback.print_exc()
    
    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Helper to create rounded rectangles"""
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
                  x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
                  x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def on_filter_change(self, event, tree):
        """Handle filter dropdown change"""
        selected_week = self.filter_var.get()
        self.current_filter = selected_week
        
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Get all logs
        logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
        
        # Filter logs
        filtered_logs = self.filter_logs_by_week(logs, selected_week)
        
        # Repopulate table
        for idx, log in enumerate(filtered_logs):
            clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "Active"
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", tk.END, values=(
                log['date'],
                log['clock_in'].strftime("%I:%M %p"),
                clock_out,
                log['status'].capitalize()
            ), tags=(tag,))
    
    def render(self):
        try:
            # Header
            header_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
            header_frame.pack(fill=tk.X, pady=(0, 25))
            
            tk.Label(header_frame, text="My Attendance Reports", 
                    font=("Arial", 24, "bold"), 
                    fg=COLORS['text_dark'], 
                    bg=COLORS['bg_main']).pack(side=tk.LEFT)
            
            # KPI Cards
            kpis = self.calculate_kpis()
            kpi_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
            kpi_container.pack(fill=tk.X, pady=(0, 25))
            
            card_data = [
                ("Total Present", kpis['present'], '#4CAF50', '#45a049', '✓'),
                ("Total Late", kpis['late'], '#FF9800', '#F57C00', '⏰'),
                ("Total Absent", kpis['absent'], '#9C27B0', '#7B1FA2', '✗'),
                ("Total Leave", kpis['leave'], '#E91E63', '#C2185B', '🏖'),
                ("Attendance Rate", kpis['rate'], '#2196F3', '#1976D2', '📈')
            ]
            
            for i, (title, value, color1, color2, icon) in enumerate(card_data):
                card = self.create_gradient_card(kpi_container, title, value, color1, color2, icon)
                card.grid(row=0, column=i, padx=6, sticky="nsew")
                kpi_container.grid_columnconfigure(i, weight=1, uniform="card")
            
            kpi_container.grid_rowconfigure(0, minsize=120)
            
            # SIDE BY SIDE LAYOUT
            content_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
            content_container.pack(fill=tk.BOTH, expand=True)
            
            # LEFT: Attendance History
            left_frame = tk.Frame(content_container, bg=COLORS['bg_white'])
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
            
            # RIGHT: Weekly Chart
            right_frame = tk.Frame(content_container, bg=COLORS['bg_white'])
            right_frame.grid(row=0, column=1, sticky="nsew")
            
            content_container.grid_columnconfigure(0, weight=1)
            content_container.grid_columnconfigure(1, weight=1)
            content_container.grid_rowconfigure(0, weight=1)
            
            # Attendance History Header
            history_header = tk.Frame(left_frame, bg='#4A90E2', height=50)
            history_header.pack(fill=tk.X)
            history_header.pack_propagate(False)
            
            tk.Label(history_header, text="Attendance History", 
                    font=("Arial", 16, "bold"),
                    fg='white', bg='#4A90E2').pack(side=tk.LEFT, padx=20, pady=12)
            
            # Filter dropdown
            filter_frame = tk.Frame(history_header, bg='#4A90E2')
            filter_frame.pack(side=tk.RIGHT, padx=20)
            
            tk.Label(filter_frame, text="Filter:", font=("Arial", 10, "bold"),
                    fg='white', bg='#4A90E2').pack(side=tk.LEFT, padx=(0, 10))
            
            self.filter_var = tk.StringVar(value="All Time")
            week_options = self.get_week_options()
            
            filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                          values=week_options, state='readonly',
                                          width=15, font=("Arial", 10))
            filter_dropdown.pack(side=tk.LEFT)
            
            # Table
            table_container = tk.Frame(left_frame, bg=COLORS['bg_white'])
            table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            columns = ("Date", "Clock In", "Clock Out", "Status")
            tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
            
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview", 
                           background='white',
                           foreground=COLORS['text_dark'],
                           fieldbackground='white',
                           rowheight=35,
                           font=("Arial", 10))
            style.configure("Treeview.Heading", 
                           background='#f8f9fa',
                           foreground=COLORS['text_dark'],
                           font=("Arial", 11, "bold"))
            style.map('Treeview', background=[('selected', '#E3F2FD')])
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor=tk.CENTER)
            
            scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            
            logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
            
            for idx, log in enumerate(logs):
                clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "Active"
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tree.insert("", tk.END, values=(
                    log['date'],
                    log['clock_in'].strftime("%I:%M %p"),
                    clock_out,
                    log['status'].capitalize()
                ), tags=(tag,))
            
            tree.tag_configure('evenrow', background='#f8f9fa')
            tree.tag_configure('oddrow', background='white')
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Bind filter change event
            filter_dropdown.bind('<<ComboboxSelected>>', lambda e: self.on_filter_change(e, tree))
            
            # Weekly Chart
            weekly_data = self.get_weekly_attendance()
            chart = self.create_modern_chart(right_frame, weekly_data)
            chart.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error rendering reports view: {e}")
            import traceback
            traceback.print_exc()