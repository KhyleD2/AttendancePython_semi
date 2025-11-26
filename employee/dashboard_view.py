import tkinter as tk
from tkinter import Canvas, Frame, Label, Button
from datetime import datetime, timedelta
import calendar

class DashboardView:
    def __init__(self, parent_frame, db, employee):
        self.parent_frame = parent_frame
        self.db = db
        self.employee = employee
        self.render()
    
    def render(self):
        # Clear the parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
            
        # Main background
        self.parent_frame.configure(bg="#F5F7FA")

        # Create main container with canvas for scrolling
        main_container = Frame(self.parent_frame, bg="#F5F7FA")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = Label(
            main_container,
            text="My Dashboard",
            font=("Segoe UI", 28, "bold"),
            fg="#1F2937",
            bg="#F5F7FA"
        )
        title_label.pack(anchor=tk.W, padx=40, pady=(30, 20))

        # Content frame
        content_frame = Frame(main_container, bg="#F5F7FA")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))

        # Main grid layout
        # Left side - Calendar
        left_frame = Frame(content_frame, bg="#F5F7FA")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        # Right side - Clock Out & Announcements & Other Cards
        right_frame = Frame(content_frame, bg="#F5F7FA")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(15, 0))
        right_frame.config(width=400)

        # Create components
        self.create_calendar_card(left_frame)
        self.create_bottom_cards(left_frame)
        
        self.create_clock_card(right_frame)
        self.create_announcements_card(right_frame)
        self.create_celebrations_card(right_frame)

    def create_calendar_card(self, parent):
        """Calendar card showing the month view"""
        card = Frame(parent, bg="white", relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Add subtle shadow effect with border
        card.config(highlightbackground="#E5E7EB", highlightthickness=1)

        # Header with month/year
        header_frame = Frame(card, bg="white")
        header_frame.pack(fill=tk.X, padx=25, pady=(20, 15))

        now = datetime.now()
        month_year = now.strftime("%B %Y")
        
        # Navigation arrows (non-functional for demo)
        nav_frame = Frame(header_frame, bg="white")
        nav_frame.pack(side=tk.LEFT)
        
        Label(nav_frame, text="<", font=("Segoe UI", 14), fg="#6B7280", bg="white").pack(side=tk.LEFT, padx=5)
        Label(nav_frame, text=month_year, font=("Segoe UI", 16, "bold"), fg="#1F2937", bg="white").pack(side=tk.LEFT, padx=10)
        Label(nav_frame, text=">", font=("Segoe UI", 14), fg="#6B7280", bg="white").pack(side=tk.LEFT, padx=5)

        # Calendar grid
        cal_container = Frame(card, bg="white")
        cal_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

        # Days of week header with colored background
        days_header = Frame(cal_container, bg="#3B82F6", height=40)
        days_header.pack(fill=tk.X)

        days = ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat"]
        for day in days:
            Label(
                days_header,
                text=day,
                font=("Segoe UI", 11, "bold"),
                fg="white",
                bg="#3B82F6",
                width=10
            ).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)

        # Get calendar data
        year = now.year
        month = now.month
        cal = calendar.monthcalendar(year, month)
        
        # Demo data for attendance status
        attendance_data = {
            1: "Full Day", 2: "Full Day", 3: "Full Day", 4: "Pending REQ (Full Day)", 5: "Absent",
            6: "Full Day", 8: "Full Day", 9: "Full Day", 10: "Holiday", 11: "Full Day",
            12: "Full Day", 15: "Pending REQ (Full Day)", 16: "Absent", 17: "Full Day",
            18: "Full Day", 19: "Full Day", 20: "Full Day", 23: "Absent", 24: "Full Day",
            25: "Full Day", 26: "Full Day"
        }

        # Calendar rows
        for week in cal:
            week_frame = Frame(cal_container, bg="white")
            week_frame.pack(fill=tk.X)

            for day in week:
                day_cell = Frame(week_frame, bg="white", relief=tk.FLAT, bd=1, highlightbackground="#E5E7EB", highlightthickness=1)
                day_cell.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=0, pady=0)

                if day == 0:
                    # Empty cell
                    Label(day_cell, text="", bg="white", height=4).pack()
                else:
                    cell_content = Frame(day_cell, bg="white")
                    cell_content.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

                    # Day number
                    Label(
                        cell_content,
                        text=str(day),
                        font=("Segoe UI", 12, "bold"),
                        fg="#1F2937",
                        bg="white"
                    ).pack(anchor=tk.NW)

                    # Status
                    if day in attendance_data:
                        status = attendance_data[day]
                        
                        if status == "Full Day":
                            status_bg = "#DBEAFE"
                            status_fg = "#1E40AF"
                        elif status == "Half Day":
                            status_bg = "#FEF3C7"
                            status_fg = "#92400E"
                        elif status == "Absent":
                            status_bg = "#FEE2E2"
                            status_fg = "#991B1B"
                        elif "Pending" in status:
                            status_bg = "#F3E8FF"
                            status_fg = "#6B21A8"
                        elif status == "Holiday":
                            status_bg = "#E0E7FF"
                            status_fg = "#3730A3"
                        else:
                            status_bg = "#F3F4F6"
                            status_fg = "#6B7280"

                        status_label = Label(
                            cell_content,
                            text=status,
                            font=("Segoe UI", 8),
                            fg=status_fg,
                            bg=status_bg,
                            padx=4,
                            pady=2
                        )
                        status_label.pack(anchor=tk.CENTER, pady=(5, 0))

                    # Highlight today
                    if day == now.day:
                        day_cell.config(highlightbackground="#3B82F6", highlightthickness=2)

    def create_bottom_cards(self, parent):
        """Create bottom row cards"""
        bottom_row = Frame(parent, bg="#F5F7FA")
        bottom_row.pack(fill=tk.X)

        # Upcoming holidays card
        holidays_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        holidays_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        Label(
            holidays_card,
            text="Upcoming holidays",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=20, pady=(20, 15))

        # Holiday items
        holidays = [
            ("Christmas", "Dec 25, Monday", "Restricted"),
            ("New Year", "Jan 01, Wednesday", "National")
        ]

        for holiday, date, type_label in holidays:
            holiday_item = Frame(holidays_card, bg="white")
            holiday_item.pack(fill=tk.X, padx=20, pady=(0, 15))

            Label(
                holiday_item,
                text=holiday,
                font=("Segoe UI", 13, "bold"),
                fg="#1F2937",
                bg="white"
            ).pack(anchor=tk.W)

            info_frame = Frame(holiday_item, bg="white")
            info_frame.pack(fill=tk.X)

            Label(
                info_frame,
                text=date,
                font=("Segoe UI", 10),
                fg="#9CA3AF",
                bg="white"
            ).pack(side=tk.LEFT)

            Label(
                info_frame,
                text=type_label,
                font=("Segoe UI", 10),
                fg="#9CA3AF",
                bg="white"
            ).pack(side=tk.RIGHT)

        # Working hours card
        working_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        working_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 10))

        header = Frame(working_card, bg="white")
        header.pack(fill=tk.X, padx=20, pady=(20, 15))

        Label(
            header,
            text="Working hours",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(side=tk.LEFT)

        Label(
            header,
            text="7:30 hrs",
            font=("Segoe UI", 14),
            fg="#6B7280",
            bg="white"
        ).pack(side=tk.RIGHT)

        # Simple bar chart
        chart_frame = Frame(working_card, bg="white")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        days_hours = [
            ("Sun", 0, "#9CA3AF"),
            ("Mon", 5, "#3B82F6"),
            ("Tue", 4, "#FBBF24"),
            ("Wed", 6, "#10B981"),
            ("Thur", 3, "#3B82F6"),
            ("Fri", 2, "#9CA3AF")
        ]

        bars_frame = Frame(chart_frame, bg="white")
        bars_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        for day, hours, color in days_hours:
            bar_container = Frame(bars_frame, bg="white")
            bar_container.pack(side=tk.LEFT, expand=True, fill=tk.X)

            # Bar
            bar_height = hours * 20
            if bar_height > 0:
                bar = Frame(bar_container, bg=color, width=40, height=bar_height)
                bar.pack(pady=(120 - bar_height, 0))

        # Day labels
        labels_frame = Frame(chart_frame, bg="white")
        labels_frame.pack(fill=tk.X)

        for day, hours, color in days_hours:
            Label(
                labels_frame,
                text=day,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(side=tk.LEFT, expand=True)

        # Attendance summary card
        summary_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        summary_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        Label(
            summary_card,
            text="Attendance summary",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=20, pady=(20, 15))

        # Summary items
        summary_items = [
            ("01", "Present", "#10B981"),
            ("02", "Absent", "#EF4444"),
            ("04", "Leave", "#8B5CF6"),
            ("04", "Holidays", "#F59E0B")
        ]

        items_grid = Frame(summary_card, bg="white")
        items_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        for i, (count, label, color) in enumerate(summary_items):
            item_frame = Frame(items_grid, bg="white")
            if i < 2:
                item_frame.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            else:
                item_frame.grid(row=1, column=i-2, padx=10, pady=10, sticky="w")

            count_label = Label(
                item_frame,
                text=count,
                font=("Segoe UI", 20, "bold"),
                fg="white",
                bg=color,
                width=3,
                height=1
            )
            count_label.pack()

            Label(
                item_frame,
                text=label,
                font=("Segoe UI", 11),
                fg="#6B7280",
                bg="white"
            ).pack(pady=(5, 0))

        # Leave balance at bottom
        Label(
            summary_card,
            text="Leave balance",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))

        balance_frame = Frame(summary_card, bg="white")
        balance_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        Label(
            balance_frame,
            text="14",
            font=("Segoe UI", 32, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(side=tk.LEFT)

        sub_frame = Frame(balance_frame, bg="white")
        sub_frame.pack(side=tk.LEFT, padx=10)

        Label(
            sub_frame,
            text="Paid Leave",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W)

        Label(
            sub_frame,
            text="6",
            font=("Segoe UI", 12, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W)

    def create_clock_card(self, parent):
        """Clock in/out card"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))
        card.pack_propagate(False)

        Label(
            card,
            text="Let's get to work",
            font=("Segoe UI", 20, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(20, 5))

        # Mood selector
        mood_frame = Frame(card, bg="white")
        mood_frame.pack(fill=tk.X, padx=25, pady=(0, 15))

        Label(
            mood_frame,
            text="😊 Today's Mood",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(side=tk.LEFT)

        Label(
            mood_frame,
            text="⌄",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(side=tk.RIGHT)

        # Date and time
        now = datetime.now()
        Label(
            card,
            text=now.strftime("Mon, %d, %Y"),
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W, padx=25)

        Label(
            card,
            text=now.strftime("%I:%M:%S %p"),
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(5, 15))

        # Progress bar (demo)
        progress_container = Frame(card, bg="#E5E7EB", height=8)
        progress_container.pack(fill=tk.X, padx=25, pady=(0, 5))
        
        progress_bar = Frame(progress_container, bg="#10B981", width=200, height=8)
        progress_bar.pack(side=tk.LEFT)

        # Shift time
        Label(
            card,
            text="Shift  9:30am - 6:30pm",
            font=("Segoe UI", 10),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.CENTER, pady=(5, 15))

        # Clock Out button
        clock_btn = Button(
            card,
            text="Clock Out",
            font=("Segoe UI", 13, "bold"),
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            pady=15,
            command=lambda: print("Clock Out clicked")
        )
        clock_btn.pack(fill=tk.X, padx=25, pady=(0, 20))

    def create_announcements_card(self, parent):
        """Announcements card"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))

        Label(
            card,
            text="Announcements",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(20, 15))

        announcements = [
            ("Townhall | Fun Activity", "Nov 21, Friday"),
            ("New product update", "Nov 22, Monday")
        ]

        for title, date in announcements:
            item = Frame(card, bg="#F9FAFB")
            item.pack(fill=tk.X, padx=25, pady=(0, 10))

            # Icon
            icon_label = Label(
                item,
                text="📢",
                font=("Segoe UI", 20),
                bg="#3B82F6",
                fg="white",
                width=2,
                height=1
            )
            icon_label.pack(side=tk.LEFT, padx=(10, 15), pady=10)

            text_frame = Frame(item, bg="#F9FAFB")
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10)

            Label(
                text_frame,
                text=title,
                font=("Segoe UI", 12, "bold"),
                fg="#1F2937",
                bg="#F9FAFB"
            ).pack(anchor=tk.W)

            Label(
                text_frame,
                text=date,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="#F9FAFB"
            ).pack(anchor=tk.W)

        # Add padding at bottom
        Frame(card, bg="white", height=20).pack()

    def create_celebrations_card(self, parent):
        """Celebrations card"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))

        header = Frame(card, bg="white")
        header.pack(fill=tk.X, padx=25, pady=(20, 15))

        Label(
            header,
            text="Celebrations",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(side=tk.LEFT)

        Label(
            header,
            text="All Celebrations  ⌄",
            font=("Segoe UI", 10),
            fg="#6B7280",
            bg="white"
        ).pack(side=tk.RIGHT)

        celebrations = [
            ("Lydia Westervelt", "Birthday", "01", "Dec"),
            ("Ria Vetrovs", "Work Anniversary", "06", "Dec"),
            ("Kim Soo-hyun", "Marriage Anniversary", "08", "Dec")
        ]

        for name, event, day, month in celebrations:
            item = Frame(card, bg="white")
            item.pack(fill=tk.X, padx=25, pady=(0, 15))

            # Profile circle (placeholder)
            profile = Label(
                item,
                text="👤",
                font=("Segoe UI", 20),
                bg="#E5E7EB",
                width=2,
                height=1
            )
            profile.pack(side=tk.LEFT, padx=(0, 15))

            # Text info
            text_frame = Frame(item, bg="white")
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            Label(
                text_frame,
                text=name,
                font=("Segoe UI", 12, "bold"),
                fg="#1F2937",
                bg="white"
            ).pack(anchor=tk.W)

            Label(
                text_frame,
                text=event,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(anchor=tk.W)

            # Date badge
            date_badge = Frame(item, bg="#3B82F6")
            date_badge.pack(side=tk.RIGHT)

            Label(
                date_badge,
                text=day,
                font=("Segoe UI", 14, "bold"),
                fg="white",
                bg="#3B82F6",
                padx=10,
                pady=2
            ).pack()

            Label(
                date_badge,
                text=month,
                font=("Segoe UI", 9),
                fg="white",
                bg="#3B82F6",
                padx=10,
                pady=2
            ).pack()

        # Add padding at bottom
        Frame(card, bg="white", height=20).pack()