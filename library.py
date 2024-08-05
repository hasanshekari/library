import sys
import sqlite3
from PyQt5.QtCore import Qt
import jdatetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QMessageBox,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QCheckBox, QTabWidget
)


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')  # اتصال به پایگاه داده
        self.cursor = self.conn.cursor()
        self.create_database()
        self.main_window = MainWindow()
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
                category TEXT NOT NULL,
                status TEXT DEFAULT 'موجود'  -- اضافه کردن فیلد وضعیت
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                membership_code TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                membership_date TEXT NOT NULL,
                phone TEXT  -- اضافه کردن فیلد شماره تلفن
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setGeometry(100, 100, 400, 600)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setLayoutDirection(Qt.RightToLeft)  # تنظیم جهت به راست به چپ
        self.book_tab = BookTab()
        self.member_tab = MemberTab()
        self.lending_tab = LendingTab()
        self.report_tab = ReportTab()

        self.tabs.addTab(self.book_tab, "کتاب‌ها")
        self.tabs.addTab(self.member_tab, "اعضا")
        self.tabs.addTab(self.lending_tab, "امانت‌ها")
        self.tabs.addTab(self.report_tab, "گزارش")

        self.tabs.currentChanged.connect(self.book_tab.show_books)
        self.setCentralWidget(self.tabs)

class BookTab(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.initUI()

    def initUI(self):
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle('مدیریت کتاب‌ها')
        self.resize(400, 600)
        layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو...")
        self.search_input.textChanged.connect(self.search_books)
        layout.addWidget(self.search_input)

        self.book_form = QWidget()
        form_layout = QHBoxLayout()

        self.book_id = QLineEdit()
        self.book_title = QLineEdit()
        self.book_author = QLineEdit()
        self.book_category = QLineEdit()
        self.book_status = QLineEdit()  # اضافه کردن فیلد وضعیت کتاب

        form_layout.addWidget(QLabel('شناسه کتاب:'))
        form_layout.addWidget(self.book_id)
        form_layout.addWidget(QLabel('نام کتاب:'))
        form_layout.addWidget(self.book_title)
        form_layout.addWidget(QLabel('نویسنده:'))
        form_layout.addWidget(self.book_author)
        form_layout.addWidget(QLabel('دسته بندی:'))
        form_layout.addWidget(self.book_category)
        form_layout.addWidget(QLabel('وضعیت:'))  # اضافه کردن لیبل وضعیت کتاب
        self.book_status.setText("موجود")
        self.book_status.setDisabled(True)
        form_layout.addWidget(self.book_status)
        self.book_form.setLayout(form_layout)
        layout.addWidget(self.book_form)

        self.book_form = QWidget()
        form_layout = QHBoxLayout()
        self.add_book_button = QPushButton('ثبت کتاب')
        self.add_book_button.clicked.connect(self.add_book)
        form_layout.addWidget(self.add_book_button)

        self.update_book_button = QPushButton('ویرایش کتاب')
        self.update_book_button.clicked.connect(self.update_book)
        form_layout.addWidget(self.update_book_button)

        self.delete_book_button = QPushButton('حذف کتاب')
        self.delete_book_button.clicked.connect(self.delete_book)
        form_layout.addWidget(self.delete_book_button)

        self.book_form.setLayout(form_layout)
        layout.addWidget(self.book_form)

        self.book_table = QTableWidget()
        self.book_table.setColumnCount(5)  # افزایش تعداد ستون‌ها به 5
        self.book_table.setHorizontalHeaderLabels(['ID', 'نام کتاب', 'نویسنده', 'دسته بندی', 'وضعیت'])  # اضافه کردن ستون وضعیت
        self.book_table.setLayoutDirection(Qt.RightToLeft)
        self.book_table.cellClicked.connect(self.load_book)
        layout.addWidget(self.book_table)

        self.setLayout(layout)
        self.show_books()

    def search_books(self):
        search_text = self.search_input.text().strip()
        query = f"SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ?"
        self.cursor.execute(query, ('%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%'))
        books = self.cursor.fetchall()
        self.book_table.setRowCount(0)
        for row in books:
            row_position = self.book_table.rowCount()
            self.book_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.book_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def add_book(self):
        title = self.book_title.text().strip()
        author = self.book_author.text().strip()
        category = self.book_category.text().strip()
        status ='موجود'  # اضافه کردن وضعیت پیش‌فرض

        if title and author:
            try:
                self.cursor.execute("INSERT INTO books (title, author, category, status) VALUES (?, ?, ?, ?)",
                                    (title, author, category, status))
                self.conn.commit()
                self.show_books()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "خطای ثبت", "نام کتاب و نویسنده می بایست تکمیل باشد")

    def update_book(self):
        book_id = self.book_id.text().strip()
        title = self.book_title.text().strip()
        author = self.book_author.text().strip()
        category = self.book_category.text().strip()
        status = self.book_status.text().strip()  # اضافه کردن وضعیت

        if book_id and title and author:
            try:
                self.cursor.execute("UPDATE books SET title=?, author=?, category=?, status=? WHERE id=?",
                                    (title, author, category, status, book_id))
                self.conn.commit()
                self.show_books()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "خطای ویرایش", "لطفا نام نویسنده و نام کتاب را تکمیل نمایید")

    def delete_book(self):
        book_id = self.book_id.text().strip()

        if book_id:
            try:
                reply = QMessageBox.question(self, 'تأیید حذف', 'آیا مطمئن هستید که می‌خواهید حذف کنید؟',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
                    self.conn.commit()
                    self.show_books()
                    self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "خطای حذف", "هیچ کتابی برای حذف انتخاب نشده است.")

    def load_book(self, row, column):
        self.book_id.setText(self.book_table.item(row, 0).text())
        self.book_title.setText(self.book_table.item(row, 1).text())
        self.book_author.setText(self.book_table.item(row, 2).text())
        self.book_category.setText(self.book_table.item(row, 3).text())
        self.book_status.setText(self.book_table.item(row, 4).text())  # اضافه کردن فیلد وضعیت

    def clear_fields(self):
        self.book_id.clear()
        self.book_title.clear()
        self.book_author.clear()
        self.book_category.clear()
        self.book_status.clear()  # اضافه کردن فیلد وضعیت

    def show_books(self):
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        self.book_table.setRowCount(0)
        for row in books:
            row_position = self.book_table.rowCount()
            self.book_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.book_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

class MemberTab(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.current_date = jdatetime.date.today().strftime("%Y-%m-%d")

        self.initUI()

    def initUI(self):
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle('مدیریت اعضا')
        self.resize(400, 600)
        layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو...")
        self.search_input.textChanged.connect(self.search_member)
        layout.addWidget(self.search_input)

        self.member_form = QWidget()
        form_layout = QHBoxLayout()

        self.member_id = QLineEdit()
        self.member_code = QLineEdit()
        self.member_first_name = QLineEdit()
        self.member_last_name = QLineEdit()
        self.member_date = QLineEdit()
        self.member_phone = QLineEdit()  # اضافه کردن فیلد شماره تلفن

        form_layout.addWidget(QLabel('کد عضویت:'))
        form_layout.addWidget(self.member_code)
        form_layout.addWidget(QLabel('نام:'))
        form_layout.addWidget(self.member_first_name)
        form_layout.addWidget(QLabel('نام خانوادگی:'))
        form_layout.addWidget(self.member_last_name)
        form_layout.addWidget(QLabel('تاریخ عضویت:'))
        self.member_date.setText(self.current_date)

        form_layout.addWidget(self.member_date)
        form_layout.addWidget(QLabel('شماره تلفن:'))  # اضافه کردن لیبل شماره تلفن
        form_layout.addWidget(self.member_phone)
        self.member_form.setLayout(form_layout)
        layout.addWidget(self.member_form)

        self.member_form = QWidget()
        form_layout = QHBoxLayout()
        self.add_member_button = QPushButton('ثبت عضو')
        self.add_member_button.clicked.connect(self.add_member)
        form_layout.addWidget(self.add_member_button)

        self.update_member_button = QPushButton('ویرایش عضو')
        self.update_member_button.clicked.connect(self.update_member)
        form_layout.addWidget(self.update_member_button)

        self.delete_member_button = QPushButton('حذف عضو')
        self.delete_member_button.clicked.connect(self.delete_member)
        form_layout.addWidget(self.delete_member_button)

        self.member_form.setLayout(form_layout)
        layout.addWidget(self.member_form)

        self.member_table = QTableWidget()
        self.member_table.setColumnCount(6)  # افزایش تعداد ستون‌ها به 6
        self.member_table.setHorizontalHeaderLabels(['ID', 'کد عضویت', 'نام', 'نام خانوادگی', 'تاریخ عضویت', 'شماره تلفن'])  # اضافه کردن ستون شماره تلفن
        self.member_table.setLayoutDirection(Qt.RightToLeft)
        self.member_table.cellClicked.connect(self.load_member)
        layout.addWidget(self.member_table)

        self.setLayout(layout)
        self.show_members()

    def search_member(self):
        search_text = self.search_input.text().strip()
        query = f"SELECT * FROM members WHERE membership_code LIKE ? OR first_name LIKE ? OR last_name LIKE ?"
        self.cursor.execute(query, ('%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%'))
        members = self.cursor.fetchall()
        self.member_table.setRowCount(0)
        for row in members:
            row_position = self.member_table.rowCount()
            self.member_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.member_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def add_member(self):
        code = self.member_code.text().strip()
        first_name = self.member_first_name.text().strip()
        last_name = self.member_last_name.text().strip()
        date = self.member_date.text().strip()
        phone = self.member_phone.text().strip()  # اضافه کردن شماره تلفن

        if code and first_name and last_name and date:
            try:
                # بررسی تکراری بودن کد عضویت
                self.cursor.execute("SELECT COUNT(*) FROM members WHERE membership_code = ?", (code,))
                result = self.cursor.fetchone()

                if result[0] > 0:
                    QMessageBox.warning(self, "خطای ثبت عضو",
                                        "کد عضویت وارد شده قبلا وارد شده است، کد دیگری انتخاب نمایید")
                else:
                    self.cursor.execute(
                        "INSERT INTO members (membership_code, first_name, last_name, membership_date, phone) VALUES (?, ?, ?, ?, ?)",
                        (code, first_name, last_name, date, phone)
                    )
                    self.conn.commit()
                    self.show_members()
                    self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "خطای ثبت", "لطفا مشخصات عضو و تاریخ عضویت را وارد نمایید")

    def update_member(self):
        member_id = self.member_id.text().strip()
        code = self.member_code.text().strip()
        first_name = self.member_first_name.text().strip()
        last_name = self.member_last_name.text().strip()
        date = self.member_date.text().strip()
        phone = self.member_phone.text().strip()  # اضافه کردن شماره تلفن

        if member_id and code and first_name and last_name and date:
            try:
                self.cursor.execute("UPDATE members SET membership_code=?, first_name=?, last_name=?, membership_date=?, phone=? WHERE id=?",
                                    (code, first_name, last_name, date, phone, member_id))
                self.conn.commit()
                self.show_members()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def delete_member(self):
        member_id = self.member_id.text().strip()

        if member_id:
            try:
                reply = QMessageBox.question(self, 'تأیید حذف', 'آیا مطمئن هستید که می‌خواهید حذف کنید؟',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.cursor.execute("DELETE FROM members WHERE id=?", (member_id,))
                    self.conn.commit()
                    self.show_members()
                    self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def load_member(self, row, column):
        self.member_id.setText(self.member_table.item(row, 0).text())
        self.member_code.setText(self.member_table.item(row, 1).text())
        self.member_first_name.setText(self.member_table.item(row, 2).text())
        self.member_last_name.setText(self.member_table.item(row, 3).text())
        self.member_date.setText(self.member_table.item(row, 4).text())
        self.member_phone.setText(self.member_table.item(row, 5).text())  # اضافه کردن فیلد شماره تلفن

    def clear_fields(self):
        self.member_id.clear()
        self.member_code.clear()
        self.member_first_name.clear()
        self.member_last_name.clear()
        self.member_date.setText(self.current_date)
        self.member_phone.clear()  # اضافه کردن فیلد شماره تلفن

    def show_members(self):
        self.cursor.execute("SELECT * FROM members")
        members = self.cursor.fetchall()
        self.member_table.setRowCount(0)
        for row in members:
            row_position = self.member_table.rowCount()
            self.member_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.member_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

class LendingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.initUI()
        self.current_date = jdatetime.date.today().strftime("%Y-%m-%d")

    def initUI(self):
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle('مدیریت امانت‌ها')
        self.resize(400, 600)
        layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو...")
        self.search_input.textChanged.connect(self.search_lendings)
        layout.addWidget(self.search_input)

        self.lending_form = QWidget()
        form_layout = QHBoxLayout()

        self.lending_id = QLineEdit()
        self.lending_member_id = QLineEdit()
        self.lending_book_id = QLineEdit()
        self.lending_date = QLineEdit()
        self.return_date = QLineEdit()
        form_layout.addWidget(QLabel('شناسه کتاب:'))
        form_layout.addWidget(self.lending_book_id)
        self.lending_book_id.editingFinished.connect(self.check_book_status)

        form_layout.addWidget(QLabel('شناسه عضو:'))
        form_layout.addWidget(self.lending_member_id)
        form_layout.addWidget(QLabel('تاریخ امانت:'))
        form_layout.addWidget(self.lending_date)
        form_layout.addWidget(QLabel('تاریخ بازگشت:'))
        form_layout.addWidget(self.return_date)

        self.lending_form.setLayout(form_layout)
        layout.addWidget(self.lending_form)

        self.lending_form = QWidget()
        form_layout = QHBoxLayout()
        self.add_lending_button = QPushButton('ثبت امانت')
        self.add_lending_button.clicked.connect(self.add_lending)
        form_layout.addWidget(self.add_lending_button)

        self.return_lending_button = QPushButton('بازگشت کتاب')
        self.return_lending_button.clicked.connect(self.return_lending)
        form_layout.addWidget(self.return_lending_button)

        self.delete_lending_button = QPushButton('حذف امانت')
        self.delete_lending_button.clicked.connect(self.delete_lending)
        form_layout.addWidget(self.delete_lending_button)

        self.lending_form.setLayout(form_layout)
        layout.addWidget(self.lending_form)

        self.lending_table = QTableWidget()
        self.lending_table.setColumnCount(7)
        self.lending_table.setHorizontalHeaderLabels(['ID', 'عضو ID', 'کتاب ID', 'تاریخ امانت', 'تاریخ بازگشت', 'نام عضو', 'نام کتاب'])
        self.lending_table.setLayoutDirection(Qt.RightToLeft)
        self.lending_table.cellClicked.connect(self.load_lending)
        layout.addWidget(self.lending_table)

        self.setLayout(layout)
        self.show_lendings()

    def search_lendings(self):
        search_text = self.search_input.text().strip()
        query = f"SELECT l.*, m.first_name || ' ' || m.last_name AS member_name, b.title AS book_title FROM lendings l LEFT JOIN members m ON l.member_id = m.id LEFT JOIN books b ON l.book_id = b.id WHERE m.first_name LIKE ? OR m.last_name LIKE ? OR b.title LIKE ?"
        self.cursor.execute(query, ('%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%'))
        lendings = self.cursor.fetchall()
        self.lending_table.setRowCount(0)
        for row in lendings:
            row_position = self.lending_table.rowCount()
            self.lending_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.lending_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def add_lending(self):
        member_id = self.lending_member_id.text().strip()
        book_id = self.lending_book_id.text().strip()
        lending_date = self.lending_date.text().strip()
        return_date = self.return_date.text().strip()

        if member_id and book_id and lending_date and not return_date:
            try:
                # Check if the book is available
                self.cursor.execute("SELECT status FROM books WHERE id=?", (book_id,))
                book_status = self.cursor.fetchone()
                if book_status and book_status[0] == 'موجود':
                    self.cursor.execute("INSERT INTO lendings (member_id, book_id, loan_date, return_date) VALUES (?, ?, ?, ?)",
                                        (member_id, book_id, lending_date, return_date))
                    self.cursor.execute("UPDATE books SET status='امانت' WHERE id=?", (book_id,))
                    self.conn.commit()
                    self.show_lendings()
                    self.clear_fields()
                    self.return_date.setDisabled(False)

                else:
                    QMessageBox.warning(self, "Book Status Error", "کتاب در حال حاضر به امانت گرفته شده است.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields  not return date.")

    def return_lending(self):
        book_id = self.lending_book_id.text().strip()
        id=self.lending_id.text().strip()
        self.return_date.setText(self.current_date)
        return_date = self.return_date.text().strip()
        if  book_id and return_date :
            try:
                self.cursor.execute("UPDATE books SET status='موجود' WHERE id=?", (book_id,))
                self.cursor.execute("UPDATE lendings SET return_date=?  WHERE id=?", (return_date,id))

                self.conn.commit()
                self.show_lendings()
                self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def check_book_status(self):
        book_id = self.lending_book_id.text().strip()
        if book_id:
            try:
                self.cursor.execute("SELECT status FROM books WHERE id=?", (book_id,))
                result = self.cursor.fetchone()
                if result:
                    status = result[0]
                    current_date = jdatetime.date.today().strftime("%Y-%m-%d")
                    if status == "موجود":
                        self.lending_date.setText(current_date)
                        self.return_date.setDisabled(True)
                        self.return_date.clear()
                    elif status == "امانت":
                        self.cursor.execute(
                            "SELECT loan_date, member_id,id FROM lendings WHERE book_id=? AND (return_date IS NULL OR return_date = '')",
                            (book_id,))

                        lending_info = self.cursor.fetchone()

                        self.lending_date.setDisabled(True)
                        self.lending_date.setText(lending_info[0])
                        self.lending_member_id.setText(str(lending_info[1]))
                        self.lending_id.setText(str(lending_info[2]))

                        self.return_date.setDisabled(False)
                        self.return_date.setText(current_date)
                else:
                    QMessageBox.warning(self, "Book Not Found", "No book found with this ID.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

    def delete_lending(self):
        lending_id = self.lending_id.text().strip()
        book_id = self.lending_book_id.text().strip()

        if lending_id and book_id:
            try:
                reply = QMessageBox.question(self, 'تأیید حذف', 'آیا مطمئن هستید که می‌خواهید حذف کنید؟',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.cursor.execute("DELETE FROM lendings WHERE id=?", (lending_id,))
                    self.cursor.execute("UPDATE books SET status='موجود' WHERE id=?", (book_id,))
                    self.conn.commit()
                    self.show_lendings()
                    self.clear_fields()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")

    def load_lending(self, row, column):
        self.lending_id.setText(self.lending_table.item(row, 0).text())
        self.lending_member_id.setText(self.lending_table.item(row, 1).text())
        self.lending_book_id.setText(self.lending_table.item(row, 2).text())
        self.lending_date.setText(self.lending_table.item(row, 3).text())
        self.return_date.setText(self.lending_table.item(row, 4).text())

    def clear_fields(self):
        self.lending_id.clear()
        self.lending_member_id.clear()
        self.lending_book_id.clear()
        self.lending_date.clear()
        self.return_date.clear()

    def show_lendings(self):
        self.cursor.execute("SELECT l.*, m.first_name || ' ' || m.last_name AS member_name, b.title AS book_title FROM lendings l LEFT JOIN members m ON l.member_id = m.id LEFT JOIN books b ON l.book_id = b.id")
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


class ReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.initUI()

    def initUI(self):
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle('گزارش‌ها')
        self.resize(400, 600)
        layout = QVBoxLayout()

        self.report_form = QWidget()
        form_layout = QVBoxLayout()

        self.member_filter = QLineEdit()
        self.member_filter.setPlaceholderText("فیلتر بر اساس عضو...")
        form_layout.addWidget(self.member_filter)

        self.book_filter = QLineEdit()
        self.book_filter.setPlaceholderText("فیلتر بر اساس کتاب...")
        form_layout.addWidget(self.book_filter)

        self.date_filter_from = QLineEdit()
        self.date_filter_from.setPlaceholderText("تاریخ از...")
        form_layout.addWidget(self.date_filter_from)

        self.date_filter_to = QLineEdit()
        self.date_filter_to.setPlaceholderText("تاریخ تا...")
        form_layout.addWidget(self.date_filter_to)

        self.search_button = QPushButton('جستجو')
        self.search_button.clicked.connect(self.generate_report)
        form_layout.addWidget(self.search_button)

        self.report_form.setLayout(form_layout)
        layout.addWidget(self.report_form)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels(['ID', 'عضو ID', 'کتاب ID', 'تاریخ امانت', 'تاریخ بازگشت', 'وضعیت'])
        self.report_table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.report_table)

        self.setLayout(layout)

    def generate_report(self):
        member_filter = self.member_filter.text().strip()
        book_filter = self.book_filter.text().strip()
        date_from = self.date_filter_from.text().strip()
        date_to = self.date_filter_to.text().strip()

        query = f"""
            SELECT l.id, l.member_id, l.book_id, l.loan_date, l.return_date, 
                   CASE WHEN l.return_date IS NULL THEN 'امانت' ELSE 'موجود' END as status
            FROM lendings l
            LEFT JOIN members m ON l.member_id = m.id
            LEFT JOIN books b ON l.book_id = b.id
            WHERE (m.first_name LIKE ? OR m.last_name LIKE ? OR ? = '')
              AND (b.title LIKE ? OR ? = '')
              AND (l.loan_date BETWEEN ? AND ? OR ? = '' OR ? = '')
        """

        params = (
            '%' + member_filter + '%',
            '%' + member_filter + '%',
            member_filter,
            '%' + book_filter + '%',
            book_filter,
            date_from,
            date_to,
            date_from,
            date_to
        )

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        self.report_table.setRowCount(0)
        for row in results:
            row_position = self.report_table.rowCount()
            self.report_table.insertRow(row_position)
            for col, item in enumerate(row):
                self.report_table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)  # تنظیم جهت برنامه به راست به چپ
    mainWin = LoginForm()
    mainWin.show()
    sys.exit(app.exec_())
