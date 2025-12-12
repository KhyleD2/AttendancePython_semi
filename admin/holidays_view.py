"""
Holidays Management View for Admin
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database

try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False
    print("Warning: tkcalendar not installed. Using basic date entry.")


class HolidaysView:
    """Holidays management interface"""
    
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.render()
        
    def render(self):
        """Render the holidays management view"""
        # Configure parent frame
        self.parent_frame.configure(bg='#f0f0f0')
        
        # Header Section
        header_frame = tk.Frame(self.parent_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="Manage Holidays",
            font=('Segoe UI', 24, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(side='left')
        
        # Button frame
        button_frame = tk.Frame(header_frame, bg='#f0f0f0')
        button_frame.pack(side='right')
        
        add_btn = tk.Button(
            button_frame,
            text="➕ Add New Holiday",
            font=('Segoe UI', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            cursor='hand2',
            padx=20,
            pady=8,
            relief=tk.FLAT,
            command=self.add_holiday
        )
        add_btn.pack(side='left', padx=5)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=('Segoe UI', 11),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            padx=20,
            pady=8,
            relief=tk.FLAT,
            command=self.load_holidays
        )
        refresh_btn.pack(side='left', padx=5)
        
        # Main content frame with notebook (tabs)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.pack(fill='both', expand=True, pady=10)
        
        # Upcoming holidays tab
        self.upcoming_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.upcoming_frame, text='📅 Upcoming Holidays')
        
        # Past holidays tab
        self.past_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.past_frame, text='📜 Past Holidays')
        
        # Load holidays
        self.load_holidays()
        
    def load_holidays(self):
        """Load and display holidays"""
        # Clear existing content
        for widget in self.upcoming_frame.winfo_children():
            widget.destroy()
        for widget in self.past_frame.winfo_children():
            widget.destroy()
        
        try:
            query = """
                SELECT id, name, holiday_date, created_at 
                FROM holidays 
                ORDER BY holiday_date ASC
            """
            holidays = self.db.execute_query(query, fetch=True)
            
            if not holidays:
                holidays = []
            
            today = datetime.now().date()
            upcoming = [h for h in holidays if h['holiday_date'] >= today]
            past = [h for h in holidays if h['holiday_date'] < today]
            past.reverse()  # Most recent first
            
            # Display upcoming holidays
            self.display_holidays_list(self.upcoming_frame, upcoming, is_upcoming=True)
            
            # Display past holidays
            self.display_holidays_list(self.past_frame, past, is_upcoming=False)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading holidays: {str(e)}")
    
    def display_holidays_list(self, parent_frame, holidays, is_upcoming=True):
        """Display holidays in a scrollable list"""
        # Create canvas and scrollbar
        canvas = tk.Canvas(parent_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        if not holidays:
            no_data_label = tk.Label(
                scrollable_frame,
                text=f"No {'upcoming' if is_upcoming else 'past'} holidays found.",
                font=('Segoe UI', 12),
                bg='white',
                fg='#7f8c8d'
            )
            no_data_label.pack(pady=50)
            return
        
        # Display each holiday
        today = datetime.now().date()
        for holiday in holidays:
            self.create_holiday_card(scrollable_frame, holiday, today, is_upcoming)
    
    def create_holiday_card(self, parent, holiday, today, is_upcoming):
        """Create a card for each holiday"""
        card = tk.Frame(parent, bg='white', relief='solid', borderwidth=1, highlightbackground='#e0e0e0', highlightthickness=1)
        card.pack(fill='x', padx=15, pady=8)
        
        # Content frame with padding
        content_frame = tk.Frame(card, bg='white')
        content_frame.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Left side - Holiday info
        info_frame = tk.Frame(content_frame, bg='white')
        info_frame.pack(side='left', fill='x', expand=True)
        
        # Holiday name
        name_label = tk.Label(
            info_frame,
            text=holiday['name'],
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            anchor='w'
        )
        name_label.pack(anchor='w')
        
        # Holiday date
        date_str = holiday['holiday_date'].strftime('%B %d, %Y')
        date_label = tk.Label(
            info_frame,
            text=f"📅 {date_str}",
            font=('Segoe UI', 11),
            bg='white',
            fg='#34495e',
            anchor='w'
        )
        date_label.pack(anchor='w', pady=(5, 0))
        
        # Days info (for upcoming holidays)
        if is_upcoming:
            days_left = (holiday['holiday_date'] - today).days
            if days_left == 0:
                days_text = "🎉 Today!"
                days_color = '#e74c3c'
            elif days_left == 1:
                days_text = "⏰ Tomorrow"
                days_color = '#f39c12'
            else:
                days_text = f"⏳ In {days_left} days"
                days_color = '#3498db'
            
            days_label = tk.Label(
                info_frame,
                text=days_text,
                font=('Segoe UI', 10, 'italic'),
                bg='white',
                fg=days_color,
                anchor='w'
            )
            days_label.pack(anchor='w', pady=(3, 0))
        
        # Right side - Action buttons
        action_frame = tk.Frame(content_frame, bg='white')
        action_frame.pack(side='right')
        
        edit_btn = tk.Button(
            action_frame,
            text="✏️ Edit",
            font=('Segoe UI', 9),
            bg='#f39c12',
            fg='white',
            cursor='hand2',
            padx=15,
            pady=5,
            relief=tk.FLAT,
            command=lambda: self.edit_holiday(holiday)
        )
        edit_btn.pack(side='left', padx=3)
        
        delete_btn = tk.Button(
            action_frame,
            text="🗑️ Delete",
            font=('Segoe UI', 9),
            bg='#e74c3c',
            fg='white',
            cursor='hand2',
            padx=15,
            pady=5,
            relief=tk.FLAT,
            command=lambda: self.delete_holiday(holiday)
        )
        delete_btn.pack(side='left', padx=3)
    
    def add_holiday(self):
        """Open dialog to add new holiday"""
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Add New Holiday")
        dialog.geometry("500x300")
        dialog.configure(bg='#ecf0f1')
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (150)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Title
        title_frame = tk.Frame(dialog, bg='#3498db', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Add New Holiday",
            font=('Segoe UI', 16, 'bold'),
            bg='#3498db',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Form frame
        form_frame = tk.Frame(dialog, bg='#ecf0f1')
        form_frame.pack(padx=40, pady=25, fill='both', expand=True)
        
        # Holiday name
        tk.Label(
            form_frame,
            text="Holiday Name:",
            font=('Segoe UI', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).grid(row=0, column=0, sticky='w', pady=10)
        
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=30)
        name_entry.grid(row=0, column=1, pady=10, padx=10, sticky='ew')
        name_entry.focus()
        
        # Holiday date
        tk.Label(
            form_frame,
            text="Date:",
            font=('Segoe UI', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).grid(row=1, column=0, sticky='w', pady=10)
        
        if HAS_CALENDAR:
            date_entry = DateEntry(
                form_frame,
                font=('Segoe UI', 11),
                width=27,
                background='#3498db',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
        else:
            date_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=30)
            date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            tk.Label(
                form_frame,
                text="(Format: YYYY-MM-DD)",
                font=('Segoe UI', 8, 'italic'),
                bg='#ecf0f1',
                fg='#7f8c8d'
            ).grid(row=2, column=1, sticky='w')
        
        date_entry.grid(row=1, column=1, pady=10, padx=10, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#ecf0f1')
        button_frame.pack(pady=15)
        
        def save_holiday():
            name = name_entry.get().strip()
            
            try:
                if HAS_CALENDAR:
                    date_value = date_entry.get_date().strftime('%Y-%m-%d')
                else:
                    date_value = date_entry.get().strip()
                    # Validate date format
                    datetime.strptime(date_value, '%Y-%m-%d')
            except:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format", parent=dialog)
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter holiday name", parent=dialog)
                return
            
            try:
                # Check for duplicate
                check_query = "SELECT id FROM holidays WHERE holiday_date = %s"
                existing = self.db.execute_query(check_query, (date_value,), fetch=True)
                
                if existing:
                    messagebox.showwarning("Duplicate", "A holiday already exists on this date!", parent=dialog)
                    return
                
                insert_query = """
                    INSERT INTO holidays (name, holiday_date)
                    VALUES (%s, %s)
                """
                self.db.execute_query(insert_query, (name, date_value))
                
                messagebox.showinfo("Success", f"Holiday '{name}' added successfully!", parent=dialog)
                dialog.destroy()
                self.load_holidays()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error adding holiday: {str(e)}", parent=dialog)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save Holiday",
            font=('Segoe UI', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            cursor='hand2',
            padx=25,
            pady=8,
            relief=tk.FLAT,
            command=save_holiday
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            font=('Segoe UI', 11),
            bg='#95a5a6',
            fg='white',
            cursor='hand2',
            padx=25,
            pady=8,
            relief=tk.FLAT,
            command=dialog.destroy
        )
        cancel_btn.pack(side='left', padx=5)
    
    def edit_holiday(self, holiday):
        """Open dialog to edit holiday"""
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Edit Holiday")
        dialog.geometry("500x300")
        dialog.configure(bg='#ecf0f1')
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (150)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Title
        title_frame = tk.Frame(dialog, bg='#f39c12', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Edit Holiday",
            font=('Segoe UI', 16, 'bold'),
            bg='#f39c12',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Form frame
        form_frame = tk.Frame(dialog, bg='#ecf0f1')
        form_frame.pack(padx=40, pady=25, fill='both', expand=True)
        
        # Holiday name
        tk.Label(
            form_frame,
            text="Holiday Name:",
            font=('Segoe UI', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).grid(row=0, column=0, sticky='w', pady=10)
        
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=30)
        name_entry.insert(0, holiday['name'])
        name_entry.grid(row=0, column=1, pady=10, padx=10, sticky='ew')
        name_entry.focus()
        
        # Holiday date
        tk.Label(
            form_frame,
            text="Date:",
            font=('Segoe UI', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).grid(row=1, column=0, sticky='w', pady=10)
        
        if HAS_CALENDAR:
            date_entry = DateEntry(
                form_frame,
                font=('Segoe UI', 11),
                width=27,
                background='#f39c12',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            date_entry.set_date(holiday['holiday_date'])
        else:
            date_entry = tk.Entry(form_frame, font=('Segoe UI', 11), width=30)
            date_entry.insert(0, holiday['holiday_date'].strftime('%Y-%m-%d'))
            tk.Label(
                form_frame,
                text="(Format: YYYY-MM-DD)",
                font=('Segoe UI', 8, 'italic'),
                bg='#ecf0f1',
                fg='#7f8c8d'
            ).grid(row=2, column=1, sticky='w')
        
        date_entry.grid(row=1, column=1, pady=10, padx=10, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#ecf0f1')
        button_frame.pack(pady=15)
        
        def update_holiday():
            name = name_entry.get().strip()
            
            try:
                if HAS_CALENDAR:
                    date_value = date_entry.get_date().strftime('%Y-%m-%d')
                else:
                    date_value = date_entry.get().strip()
                    datetime.strptime(date_value, '%Y-%m-%d')
            except:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format", parent=dialog)
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter holiday name", parent=dialog)
                return
            
            try:
                update_query = """
                    UPDATE holidays 
                    SET name = %s, holiday_date = %s
                    WHERE id = %s
                """
                self.db.execute_query(update_query, (name, date_value, holiday['id']))
                
                messagebox.showinfo("Success", f"Holiday '{name}' updated successfully!", parent=dialog)
                dialog.destroy()
                self.load_holidays()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error updating holiday: {str(e)}", parent=dialog)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Update",
            font=('Segoe UI', 11, 'bold'),
            bg='#f39c12',
            fg='white',
            cursor='hand2',
            padx=25,
            pady=8,
            relief=tk.FLAT,
            command=update_holiday
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            font=('Segoe UI', 11),
            bg='#95a5a6',
            fg='white',
            cursor='hand2',
            padx=25,
            pady=8,
            relief=tk.FLAT,
            command=dialog.destroy
        )
        cancel_btn.pack(side='left', padx=5)
    
    def delete_holiday(self, holiday):
        """Delete a holiday"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{holiday['name']}'?\n\nDate: {holiday['holiday_date'].strftime('%B %d, %Y')}\n\nThis action cannot be undone."
        )
        
        if not result:
            return
        
        try:
            delete_query = "DELETE FROM holidays WHERE id = %s"
            self.db.execute_query(delete_query, (holiday['id'],))
            
            messagebox.showinfo("Success", f"Holiday '{holiday['name']}' deleted successfully!")
            self.load_holidays()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting holiday: {str(e)}")