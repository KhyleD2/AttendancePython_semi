import tkinter as tk
from tkinter import Canvas
import math
from config import COLORS

class ReportsView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.render()
    
    def render(self):
        # --- Background ---
        self.parent_frame.configure(bg="#F0F2F5")

        # --- Header with blue background ---
        header_frame = tk.Frame(self.parent_frame, bg="#4A90E2")
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=0)

        tk.Label(
            header_frame,
            text="Reports & Analytics",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#4A90E2"
        ).pack(side=tk.LEFT, padx=40, pady=20)

        # --- Scrollable container ---
        main_canvas = Canvas(self.parent_frame, bg="#F0F2F5", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.parent_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#F0F2F5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=1400)
        main_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        container = scrollable_frame

        # --- Stats Cards Row ---
        stats_row = tk.Frame(container, bg="#F0F2F5")
        stats_row.pack(fill=tk.X, pady=(0, 20))

        stats_data = [
            ("Total Employees", "45", "#3B82F6"),
            ("Present Today", "38", "#10B981"),
            ("Absent Today", "7", "#EF4444"),
            ("Attendance Rate", "84.4%", "#8B5CF6")
        ]

        for i, (title, value, color) in enumerate(stats_data):
            self.create_stat_card(stats_row, title, value, color, i)

        # --- First Row: Donut Chart + Weekly Trend ---
        row1 = tk.Frame(container, bg="#F0F2F5")
        row1.pack(fill=tk.X, pady=(0, 20))

        # Department Distribution Donut Chart
        donut_card = tk.Frame(row1, bg="white")
        donut_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            donut_card,
            text="Department Distribution",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        self.create_department_donut(donut_card)

        # Weekly Attendance Trend Bar Chart
        weekly_card = tk.Frame(row1, bg="white")
        weekly_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            weekly_card,
            text="Weekly Attendance Trend",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        self.create_weekly_bar_chart(weekly_card)

        # --- Second Row: Monthly Line Chart + Top Performers ---
        row2 = tk.Frame(container, bg="#F0F2F5")
        row2.pack(fill=tk.X, pady=(0, 20))

        # Monthly Attendance Line Chart
        monthly_card = tk.Frame(row2, bg="white")
        monthly_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            monthly_card,
            text="Monthly Attendance Trend",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        self.create_monthly_line_chart(monthly_card)

        # Top Performers
        top_card = tk.Frame(row2, bg="white")
        top_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            top_card,
            text="Top 5 Best Attendance",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        self.create_top_performers(top_card)

    def create_stat_card(self, parent, title, value, color, index):
        card = tk.Frame(parent, bg="white", highlightthickness=0)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if index == 0 else 10, 0))

        color_bar = tk.Frame(card, bg=color, width=4)
        color_bar.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(card, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content,
            text=title,
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text=value,
            font=("Segoe UI", 28, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(anchor=tk.W, pady=(5, 0))

    def create_department_donut(self, parent):
        chart_frame = tk.Frame(parent, bg="white")
        chart_frame.pack(pady=20)

        # Department data with unique colors
        departments = [
            ("IT", 12, "#3B82F6"),
            ("HR", 8, "#10B981"),
            ("Finance", 10, "#F59E0B"),
            ("Sales", 15, "#EF4444"),
            ("Marketing", 6, "#8B5CF6"),
            ("Operations", 9, "#06B6D4")
        ]

        total = sum(count for _, count, _ in departments)

        # Canvas for donut
        canvas = Canvas(chart_frame, width=300, height=300, bg="white", highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=30)

        center_x, center_y = 150, 150
        radius = 110
        inner_radius = 70

        # Draw donut segments
        start_angle = 0
        for dept, count, color in departments:
            extent = (count / total) * 360
            self.draw_donut_arc(canvas, center_x, center_y, radius, inner_radius, 
                               start_angle, extent, color)
            start_angle += extent

        # Center text
        canvas.create_text(
            center_x, center_y - 10,
            text=str(total),
            font=("Segoe UI", 32, "bold"),
            fill="#1a1a1a"
        )
        canvas.create_text(
            center_x, center_y + 20,
            text="Employees",
            font=("Segoe UI", 12),
            fill="#6B7280"
        )

        # Legend
        legend_frame = tk.Frame(chart_frame, bg="white")
        legend_frame.pack(side=tk.LEFT, padx=20, pady=20)

        for dept, count, color in departments:
            item_frame = tk.Frame(legend_frame, bg="white")
            item_frame.pack(anchor=tk.W, pady=8)

            # Color box
            color_box = tk.Frame(item_frame, bg=color, width=16, height=16)
            color_box.pack(side=tk.LEFT, padx=(0, 10))

            # Department name and count
            tk.Label(
                item_frame,
                text=f"{dept}",
                font=("Segoe UI", 11, "bold"),
                fg="#1a1a1a",
                bg="white"
            ).pack(side=tk.LEFT)

            tk.Label(
                item_frame,
                text=f"({count})",
                font=("Segoe UI", 11),
                fg="#6B7280",
                bg="white"
            ).pack(side=tk.LEFT, padx=(5, 0))

    def create_weekly_bar_chart(self, parent):
        canvas = Canvas(parent, width=600, height=300, bg="white", highlightthickness=0)
        canvas.pack(pady=20, padx=30)

        # Demo data: Last 7 days
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        attendance = [42, 40, 38, 41, 39, 35, 32]

        # Chart dimensions
        margin = 50
        chart_width = 600 - 2 * margin
        chart_height = 250
        max_value = 45
        bar_width = chart_width / len(days) - 20

        # Draw bars
        for i, (day, value) in enumerate(zip(days, attendance)):
            x = margin + i * (chart_width / len(days)) + 10
            bar_height = (value / max_value) * chart_height
            y = 250 - bar_height

            # Bar
            canvas.create_rectangle(
                x, y, x + bar_width, 250,
                fill="#3B82F6", outline=""
            )

            # Value on top
            canvas.create_text(
                x + bar_width/2, y - 10,
                text=str(value),
                font=("Segoe UI", 10, "bold"),
                fill="#1a1a1a"
            )

            # Day label
            canvas.create_text(
                x + bar_width/2, 270,
                text=day,
                font=("Segoe UI", 10),
                fill="#6B7280"
            )

    def create_monthly_line_chart(self, parent):
        canvas = Canvas(parent, width=600, height=300, bg="white", highlightthickness=0)
        canvas.pack(pady=20, padx=30)

        # Demo data: 4 weeks
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
        rates = [88, 85, 82, 84]

        # Chart dimensions
        margin = 50
        chart_width = 600 - 2 * margin
        chart_height = 220
        max_rate = 100

        # Calculate points
        points = []
        for i, rate in enumerate(rates):
            x = margin + (i / (len(rates) - 1)) * chart_width
            y = margin + chart_height - (rate / max_rate) * chart_height
            points.append((x, y))

        # Draw line
        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill="#10B981", width=3, smooth=True
            )

        # Draw points and labels
        for i, (point, rate, week) in enumerate(zip(points, rates, weeks)):
            # Circle
            canvas.create_oval(
                point[0]-6, point[1]-6,
                point[0]+6, point[1]+6,
                fill="#10B981", outline="white", width=2
            )

            # Rate value
            canvas.create_text(
                point[0], point[1] - 20,
                text=f"{rate}%",
                font=("Segoe UI", 11, "bold"),
                fill="#1a1a1a"
            )

            # Week label
            canvas.create_text(
                point[0], 280,
                text=week,
                font=("Segoe UI", 10),
                fill="#6B7280"
            )

    def create_top_performers(self, parent):
        # Demo data
        employees = [
            ("John Smith", "IT", "100%", "#10B981"),
            ("Sarah Johnson", "HR", "98%", "#10B981"),
            ("Mike Davis", "Sales", "97%", "#10B981"),
            ("Emily Brown", "Finance", "96%", "#10B981"),
            ("David Wilson", "Marketing", "95%", "#3B82F6")
        ]

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        for i, (name, dept, rate, color) in enumerate(employees, 1):
            row = tk.Frame(list_frame, bg="#F9FAFB")
            row.pack(fill=tk.X, pady=5)

            # Rank
            tk.Label(
                row,
                text=f"#{i}",
                font=("Segoe UI", 12, "bold"),
                fg="#6B7280",
                bg="#F9FAFB",
                width=3
            ).pack(side=tk.LEFT, padx=10, pady=15)

            # Name and dept
            info_frame = tk.Frame(row, bg="#F9FAFB")
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                info_frame,
                text=name,
                font=("Segoe UI", 11, "bold"),
                fg="#1a1a1a",
                bg="#F9FAFB"
            ).pack(anchor=tk.W)

            tk.Label(
                info_frame,
                text=dept,
                font=("Segoe UI", 9),
                fg="#6B7280",
                bg="#F9FAFB"
            ).pack(anchor=tk.W)

            # Rate badge
            badge = tk.Frame(row, bg=color)
            badge.pack(side=tk.RIGHT, padx=15)

            tk.Label(
                badge,
                text=rate,
                font=("Segoe UI", 11, "bold"),
                fg="white",
                bg=color
            ).pack(padx=12, pady=8)

    def draw_donut_arc(self, canvas, center_x, center_y, radius, inner_radius, start_angle, extent, color):
        if extent <= 0:
            return

        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(start_angle + extent - 90)

        points = []
        steps = max(2, int(extent / 2))
        
        for i in range(steps + 1):
            angle = start_rad + (end_rad - start_rad) * i / steps
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))

        for i in range(steps, -1, -1):
            angle = start_rad + (end_rad - start_rad) * i / steps
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            points.append((x, y))

        flat_points = [coord for point in points for coord in point]
        canvas.create_polygon(flat_points, fill=color, outline=color, smooth=True)