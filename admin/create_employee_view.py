import tkinter as tk
from tkinter import messagebox
from config import COLORS, ROLE_EMPLOYEE

class CreateEmployeeView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.employee_entries = {}
        self.render()
    
    def render(self):
        # --- Background ---
        self.parent_frame.configure(bg="#F0F2F5")

        # --- Header with blue background ---
        header_frame = tk.Frame(self.parent_frame, bg="#072446")
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=0)

        tk.Label(
            header_frame,
            text="Create New Employee",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#072446"
        ).pack(side=tk.LEFT, padx=40, pady=20)

        # --- Main container ---
        container = tk.Frame(self.parent_frame, bg="#F0F2F5")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))

        # --- White card (bigger) ---
        card = tk.Frame(container, bg="white", padx=60, pady=50)
        card.pack(fill=tk.BOTH, expand=True)

        # Ensure proper grid behavior
        for col in range(2):
            card.columnconfigure(col, weight=1)

        # --- FORM INPUTS (no section headers) ---
        self.create_input(card, "First Name", "first_name", 0, 0)
        self.create_input(card, "Last Name", "last_name", 0, 1)

        self.create_input(card, "Email Address", "email", 1, 0)
        self.create_input(card, "Phone Number", "phone", 1, 1)

        self.create_input(card, "Department", "department", 2, 0)
        self.create_input(card, "Job Position", "position", 2, 1)

        self.create_input(card, "Hire Date (YYYY-MM-DD)", "hire_date", 3, 0)
        # Empty cell for layout
        tk.Frame(card, bg="white").grid(row=3, column=1)

        self.create_input(card, "Username", "username", 4, 0)
        self.create_input(card, "Password", "password", 4, 1, is_password=True)

        # --- SUBMIT BUTTON SECTION ---
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(30, 0), sticky="e")

        tk.Button(
            btn_frame, text="Register Employee",
            font=("Segoe UI", 11, "bold"),
            bg="#10B981", fg="white",
            activebackground="#059669", activeforeground="white",
            relief=tk.FLAT, cursor="hand2",
            pady=12, width=20,
            command=self.create_employee
        ).pack(side=tk.RIGHT)

    # -------------------------
    #       Helper Methods
    # -------------------------

    def create_section_header(self, parent, text, row):
        tk.Label(
            parent, text=text,
            font=("Segoe UI", 9, "bold"),
            fg="#9CA3AF", bg="white"
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 20))

    def create_divider(self, parent, row):
        tk.Frame(parent, bg="#E5E7EB", height=1).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=25
        )

    def create_input(self, parent, label_text, key, row, col, is_password=False):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=col, sticky="ew", padx=15, pady=12)

        tk.Label(
            frame, text=label_text,
            font=("Segoe UI", 10, "bold"),
            fg="#1a1a1a", bg="white"
        ).pack(anchor="w", pady=(0, 8))

        wrapper = tk.Frame(frame, bg="#F3F4F6", padx=12, pady=10)
        wrapper.pack(fill=tk.X)

        entry = tk.Entry(
            wrapper,
            font=("Segoe UI", 11),
            bg="#F3F4F6",
            bd=0,
            show="•" if is_password else ""
        )
        entry.pack(fill=tk.X)
        self.employee_entries[key] = entry

    def create_employee(self):
        values = {k: v.get().strip() for k, v in self.employee_entries.items()}

        if not all(values.values()):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        emp_id = self.db.create_employee(
            values['first_name'], values['last_name'], values['email'],
            values['phone'], values['department'], values['position'],
            values['hire_date']
        )

        if emp_id:
            user_created = self.db.create_user(
                values['username'], values['password'], ROLE_EMPLOYEE, emp_id
            )

            if user_created:
                messagebox.showinfo("Success", f"Employee {values['first_name']} created successfully!")
                for entry in self.employee_entries.values():
                    entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Employee created but failed to create user account.")

        else:
            messagebox.showerror("Error", "Failed to create employee (Database Error).")