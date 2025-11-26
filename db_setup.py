# db_setup.py
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def setup_database():
    """Create database and tables if they don't exist"""
    try:
        # Connect without specifying database
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        print(f"Database '{DB_CONFIG['database']}' created/verified successfully")
        
        # Create employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                phone VARCHAR(20),
                department VARCHAR(100),
                position VARCHAR(100),
                hire_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Table 'employees' created successfully")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'employee', 'hr_manager') NOT NULL,
                employee_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
            )
        """)
        print("Table 'users' created successfully")
        
        # Create attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT NOT NULL,
                clock_in DATETIME NOT NULL,
                clock_out DATETIME,
                date DATE NOT NULL,
                status ENUM('present', 'absent', 'late') DEFAULT 'present',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)
        print("Table 'attendance' created successfully")
        
        # Create departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Table 'departments' created successfully")
        
        # Insert default admin if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (username, password, role) 
                VALUES ('admin', 'admin123', 'admin')
            """)
            print("Default admin user created (username: admin, password: admin123)")
        
        # Insert sample departments
        departments = ['IT', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations']
        for dept in departments:
            cursor.execute("INSERT IGNORE INTO departments (name) VALUES (%s)", (dept,))
        print("Sample departments added")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✓ Database setup completed successfully!")
        return True
        
    except Error as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    print("Setting up database...")
    setup_database()