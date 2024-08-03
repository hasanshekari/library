import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QMessageBox)


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')  # اتصال به پایگاه داده
        self.cursor = self.conn.cursor()
        self.create_database()
        self.main_window = Library()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 280, 100)
        self.layout = QVBoxLayout()
        self.label_username = QLabel("Username:")
        self.entry_username = QLineEdit()
        self.label_password = QLabel("Password:")
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.check_login)
        self.layout.addWidget(self.label_username)
        self.layout.addWidget(self.entry_username)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.entry_password)
        self.layout.addWidget(self.button_login)
        self.setLayout(self.layout)

    def create_database(self):
        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS books (  
                id INTEGER PRIMARY KEY,   
                title TEXT NOT NULL,   
                author TEXT NOT NULL,   
                category TEXT NOT NULL  
            )  
        ''')

        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS members (  
                id INTEGER PRIMARY KEY,   
                membership_code TEXT NOT NULL,   
                first_name TEXT NOT NULL,   
                last_name TEXT NOT NULL,   
                membership_date TEXT NOT NULL  
            )  
        ''')

        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS lendings (  
                id INTEGER PRIMARY KEY,   
                member_id INTEGER,   
                book_id INTEGER,   
                loan_date TEXT NOT NULL,  
                return_date TEXT,  
                FOREIGN KEY(member_id) REFERENCES members(id),  
                FOREIGN KEY(book_id) REFERENCES books(id)  
            )  
        ''')

        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS users (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                username TEXT NOT NULL,  
                password TEXT NOT NULL  
            )  
        ''')

        self.conn.commit()

    def check_login(self):
        username = self.entry_username.text()
        password = self.entry_password.text()

        # اعتبارسنجی نام کاربری و رمز عبور
        if self.conn:
            try:
                self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
                user = self.cursor.fetchone()
                if user:
                    mainWin.close()
                    self.main_window.show()
                else:
                    QMessageBox.warning(self, "Login Failed", "Username or Password is incorrect.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Connection Error", "Database connection is closed.")


class Library(QWidget):
    def __init__(self):
        super().__init__()
        self.book_window = LibraryManager()
        self.setWindowTitle("مدیریت کتابخانه")
        self.setGeometry(100, 100, 300, 200)

        # ایجاد یک ویجت و لایه عمودی
        layout = QVBoxLayout()

        # ایجاد دکمه‌ها
        self.book_button = QPushButton("کتاب")
        self.member_button = QPushButton("اعضا")
        self.lending_button = QPushButton("فرم امانت کتاب")

        # اضافه کردن دکمه‌ها به لایه
        layout.addWidget(self.book_button)
        layout.addWidget(self.member_button)
        layout.addWidget(self.lending_button)

        # اتصال سیگنال به slot
        self.book_button.clicked.connect(self.open_book_form)
        self.member_button.clicked.connect(self.open_member_form)
        self.lending_button.clicked.connect(self.open_lending_form)

        # تنظیم لایه برای ویجت
        self.setLayout(layout)

        # تنظیم پس‌زمینه
        self.setStyleSheet("background-color: #f0f0f0;")

    def open_book_form(self):
        #self.close()
        self.book_window.show()

    def open_member_form(self):
        #self.close()
        self.member_window = MemberManager()
        self.member_window.show()

    def open_lending_form(self):
        #self.close()
        self.lending_window = LendingManager()
        self.lending_window.show()


class LibraryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')  # اتصال به پایگاه داده
        self.cursor = self.conn.cursor()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Library Management System')
        self.resize(600, 400)
        self.layout = QVBoxLayout()
        # Register Book
        self.book_form = QWidget()
        self.book_layout = QVBoxLayout()
        self.book_title = QLineEdit(self)
        self.book_author = QLineEdit(self)
        self.category_checkboxes = {
            "علمی": QCheckBox("علمی"),
            "مذهبی": QCheckBox("مذهبی"),
            "داستان": QCheckBox("داستان"),
            "سایر": QCheckBox("سایر"),
        }
        self.book_layout.addWidget(QLabel('نام کتاب:'))
        self.book_layout.addWidget(self.book_title)
        self.book_layout.addWidget(QLabel('نویسنده:'))
        self.book_layout.addWidget(self.book_author)
        for checkbox in self.category_checkboxes.values():
            self.book_layout.addWidget(checkbox)

        self.add_book_button = QPushButton('ثبت کتاب', self)
        self.add_book_button.clicked.connect(self.add_book)
        self.book_layout.addWidget(self.add_book_button)
        self.book_form.setLayout(self.book_layout)
        self.layout.addWidget(self.book_form)
        # Table to display books
        self.book_table = QTableWidget(self)
        self.book_table.setColumnCount(4)
        self.book_table.setHorizontalHeaderLabels(['ID', 'نام کتاب', 'نویسنده', 'دسته بندی'])
        self.layout.addWidget(self.book_table)
        self.setLayout(self.layout)
        self.show_books()

    def add_book(self):
        title = self.book_title.text().strip()  # استفاده از strip برای پاک‌سازی فضاهای اضافی
        author = self.book_author.text().strip()
        categories = [name for name, checkbox in self.category_checkboxes.items() if checkbox.isChecked()]

        if title and author and categories:
            try:
                self.cursor.execute("INSERT INTO books (title, author, category) VALUES (?, ?, ?)",
                                    (title, author, ', '.join(categories)))
                self.conn.commit()
                self.show_books()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def clear_fields(self):
        self.book_title.clear()
        self.book_author.clear()
        for checkbox in self.category_checkboxes.values():
            checkbox.setChecked(False)
        self.book_title.clear()
        self.book_author.clear()
        for checkbox in self.category_checkboxes.values():
            checkbox.setChecked(False)

    def show_books(self):
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        self.book_table.setRowCount(0)
        for row in books:
            row_position = self.book_table.rowCount()
            self.book_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.book_table.setItem(row_position, col, QTableWidgetItem(str(item)))
        # self.conn.close()


class MemberManager(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('مدیریت اعضا')
        self.resize(400, 300)
        layout = QVBoxLayout()

        self.membership_code = QLineEdit(self)
        self.first_name = QLineEdit(self)
        self.last_name = QLineEdit(self)
        self.membership_date = QLineEdit(self)

        layout.addWidget(QLabel("کد عضویت:"))
        layout.addWidget(self.membership_code)
        layout.addWidget(QLabel("نام:"))
        layout.addWidget(self.first_name)
        layout.addWidget(QLabel("نام خانوادگی:"))
        layout.addWidget(self.last_name)
        layout.addWidget(QLabel("تاریخ عضویت:"))
        layout.addWidget(self.membership_date)

        self.add_member_button = QPushButton('ثبت عضو', self)
        self.add_member_button.clicked.connect(self.add_member)
        layout.addWidget(self.add_member_button)

        self.member_table = QTableWidget(self)
        self.member_table.setColumnCount(4)
        self.member_table.setHorizontalHeaderLabels(['ID', 'کد عضویت', 'نام', 'نام خانوادگی'])
        layout.addWidget(self.member_table)

        self.setLayout(layout)
        self.show_members()

    def add_member(self):
        membership_code = self.membership_code.text().strip()
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        membership_date = self.membership_date.text().strip()

        if membership_code and first_name and last_name and membership_date:
            try:
                self.cursor.execute("INSERT INTO members (membership_code, first_name, last_name, membership_date) VALUES (?, ?, ?, ?)",
                                    (membership_code, first_name, last_name, membership_date))
                self.conn.commit()
                self.show_members()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def clear_fields(self):
        self.membership_code.clear()
        self.first_name.clear()
        self.last_name.clear()
        self.membership_date.clear()

    def show_members(self):
        self.cursor.execute("SELECT * FROM members")
        members = self.cursor.fetchall()
        self.member_table.setRowCount(0)  # تنظیم تعداد ردیف‌ها به صفر
        for row in members:
            row_position = self.member_table.rowCount()  # تعداد ردیف‌های فعلی
            self.member_table.insertRow(row_position)  # افزودن ردیف جدید
            for col, item in enumerate(row):  # استفاده از `row` به جای `row.self`
                self.member_table.setItem(row_position, col, QTableWidgetItem(str(item)))  #                # افزودن آیتم به جدول


    def closeEvent(self, event):
        self.conn.close()  # اینجا دقت کنید که self.conn باید تعریف شده باشد
        event.accept()


class LendingManager(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('امانت کتاب')
        self.resize(400, 300)
        layout = QVBoxLayout()

        self.member_membership_code = QLineEdit(self)
        self.book_id = QLineEdit(self)
        self.lending_date = QLineEdit(self)

        layout.addWidget(QLabel("کد عضویت:"))
        layout.addWidget(self.member_membership_code)
        layout.addWidget(QLabel("شناسه کتاب:"))
        layout.addWidget(self.book_id)
        layout.addWidget(QLabel("تاریخ امانت:"))
        layout.addWidget(self.lending_date)

        self.lend_book_button = QPushButton('امانت کتاب', self)
        self.lend_book_button.clicked.connect(self.lend_book)
        layout.addWidget(self.lend_book_button)

        self.lending_table = QTableWidget(self)
        self.lending_table.setColumnCount(3)
        self.lending_table.setHorizontalHeaderLabels(['کد عضویت', 'شناسه کتاب', 'تاریخ امانت'])
        layout.addWidget(self.lending_table)

        self.setLayout(layout)
        self.show_lendings()

    def lend_book(self):
        member_membership_code = self.member_membership_code.text().strip()
        book_id = self.book_id.text().strip()
        lending_date = self.lending_date.text().strip()

        if member_membership_code and book_id and lending_date:
            try:
                self.cursor.execute("INSERT INTO lendings (membership_code, book_id, lending_date) VALUES (?, ?, ?)",
                                    (member_membership_code, book_id, lending_date))
                self.conn.commit()
                self.show_lendings()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def clear_fields(self):
        self.member_membership_code.clear()
        self.book_id.clear()
        self.lending_date.clear()

    def show_lendings(self):
        self.cursor.execute("SELECT * FROM lendings")
        lendings = self.cursor.fetchall()
        self.lending_table.setRowCount(0)
        for row in lendings:
            row_position = self.lending_table.rowCount()
            self.lending_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.lending_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == '__main__':


    app = QApplication(sys.argv)
    mainWin = LoginForm()
    mainWin.show()
    sys.exit(app.exec_())

