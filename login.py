# login.py
import tkinter as tk
from tkinter import messagebox
from database import Database
from config import COLORS

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Login - Attendance System")
        self.window.geometry("450x550")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS['bg_main'])
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.window.winfo_screenheight() // 2) - (550 // 2)
        self.window.geometry(f"450x550+{x}+{y}")
        
        self.db = Database()
        self.user_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main = tk.Frame(self.window, bg=COLORS['bg_main'])
        main.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Login card
        login_frame = tk.Frame(main, bg=COLORS['bg_white'], relief=tk.FLAT)
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add subtle shadow effect
        login_frame.config(highlightbackground=COLORS['border'], highlightthickness=1)
        
        # Inner padding
        inner = tk.Frame(login_frame, bg=COLORS['bg_white'])
        inner.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Logo/Icon
        logo = tk.Label(inner, text="👤", font=("Arial", 50), 
                       fg=COLORS['primary'], bg=COLORS['bg_white'])
        logo.pack(pady=(0, 10))
        
        # Title
        title = tk.Label(inner, text="Attendance System", 
                        font=("Arial", 24, "bold"), 
                        fg=COLORS['text_dark'], bg=COLORS['bg_white'])
        title.pack(pady=(0, 5))
        
        # Subtitle
        subtitle = tk.Label(inner, text="Sign in to continue", 
                           font=("Arial", 11), 
                           fg=COLORS['text_gray'], bg=COLORS['bg_white'])
        subtitle.pack(pady=(0, 30))
        
        # Username
        tk.Label(inner, text="Username", font=("Arial", 10, "bold"), 
                fg=COLORS['text_dark'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=(0, 5))
        
        username_frame = tk.Frame(inner, bg=COLORS['bg_white'], 
                                 highlightbackground=COLORS['border'], 
                                 highlightthickness=1)
        username_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.username_entry = tk.Entry(username_frame, font=("Arial", 11), 
                                       bg=COLORS['bg_white'], 
                                       fg=COLORS['text_dark'], 
                                       bd=0)
        self.username_entry.pack(fill=tk.X, padx=12, pady=10)
        
        # Password
        tk.Label(inner, text="Password", font=("Arial", 10, "bold"), 
                fg=COLORS['text_dark'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=(0, 5))
        
        password_frame = tk.Frame(inner, bg=COLORS['bg_white'], 
                                 highlightbackground=COLORS['border'], 
                                 highlightthickness=1)
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.password_entry = tk.Entry(password_frame, font=("Arial", 11), 
                                       show="●", bg=COLORS['bg_white'], 
                                       fg=COLORS['text_dark'], bd=0)
        self.password_entry.pack(fill=tk.X, padx=12, pady=10)
        
        # Admin checkbox
        self.is_admin_var = tk.BooleanVar()
        admin_check = tk.Checkbutton(inner, text="Login as Administrator", 
                                     variable=self.is_admin_var, 
                                     font=("Arial", 9), 
                                     fg=COLORS['text_gray'], 
                                     bg=COLORS['bg_white'], 
                                     activebackground=COLORS['bg_white'])
        admin_check.pack(pady=(0, 25))
        
        # Login button
        login_btn = tk.Button(inner, text="Sign In", 
                             font=("Arial", 11, "bold"),
                             bg=COLORS['primary'], 
                             fg="white", 
                             command=self.login,
                             cursor="hand2", 
                             relief=tk.FLAT, 
                             padx=40, 
                             pady=12,
                             activebackground=COLORS['primary_dark'])
        login_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.login())
        
        # Demo info
        info = tk.Label(inner, 
                       text="Demo: admin/admin123 or EMP001/pass123", 
                       font=("Arial", 9), 
                       fg=COLORS['text_gray'], 
                       bg=COLORS['bg_white'])
        info.pack()
        
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if not self.db.connect():
            messagebox.showerror("Error", "Could not connect to database.\nMake sure XAMPP MySQL is running!")
            return
        
        user = self.db.authenticate_user(username, password)
        
        if user:
            self.user_data = user
            self.window.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
    
    def run(self):
        self.window.mainloop()
        return self.user_data