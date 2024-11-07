import sys
import psycopg2
import re
import resources_icon
from PyQt5 import QtCore,QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime, date

class ButtonWidget(QWidget):
    def __init__(self, parent=None):
        super(ButtonWidget, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        
        self.editButton = QPushButton('Edit', self)
        self.saveButton = QPushButton('Save', self)
        self.deleteButton = QPushButton('Delete', self)
        self.addButton = QPushButton('Add', self)
        
        self.layout.addWidget(self.editButton)
        self.layout.addWidget(self.saveButton)
        self.layout.addWidget(self.deleteButton)
        self.layout.addWidget(self.addButton)
        
        self.saveButton.setVisible(False)      
        self.setLayout(self.layout)

        # Set the stylesheet for the entire widget
        self.deleteButton.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                border-radius: 3px;
                background-color: #d00000;
            }
            QPushButton:hover {
                background-color: #9d0208;
            }
            QPushButton:pressed {
                background-color: #d00000;
            }
        """)
        self.editButton.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                border-radius: 3px;
                background-color: #00a6fb;
            }
            QPushButton:hover {
                background-color: #0582ca;
            }
            QPushButton:pressed {
                background-color: #00a6fb;
            }
        """)
        self.saveButton.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                border-radius: 3px;
                background-color: #70e000;
            }
            QPushButton:hover {
                background-color: #38b000;
            }
            QPushButton:pressed {
                background-color: #70e000;
            }
        """)
        self.addButton.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                border-radius: 3px;
                background-color: #1e88e5;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1e88e5;
            }
        """)

class NotifUi(QFrame):
    def __init__(self, parent):
        super(NotifUi, self).__init__(parent)
        uic.loadUi('venv\\notification.ui', self)
        self.setGeometry(parent.width() - 570, 60, 481, 280)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.connect_to_database()
        self.notiflistView = self.findChild(QtWidgets.QListView, 'notiflistView')  
        self.clearButton = self.findChild(QtWidgets.QPushButton, 'clearButton')
        self.clearButton.clicked.connect(self.proceed)

    def connect_to_database(self): #database connection
        try:
            self.connection = psycopg2.connect(
                dbname="Saku",
                user="postgres",
                password="francis0001",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def proceed(self):
        try:
            self.cursor.execute("DELETE FROM notifications")
            self.connection.commit()
            print("All notifications cleared.")
            self.populate_notifications()  # Refresh the notifications list
        except Exception as e:
            print(f"Error clearing notifications: {e}")

    def populate_notifications(self):
        try:
            self.cursor.execute("SELECT notification_id, message, date_created FROM notifications ORDER BY notification_id DESC")
            notifications = self.cursor.fetchall()
            model = QtGui.QStandardItemModel(self.notiflistView)
            
            for notification_id, message, date_created in notifications:
                item = QtGui.QStandardItem(f"({date_created}):  {message}")
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                model.appendRow(item)
            
            self.notiflistView.setModel(model)
        except Exception as e:
            print(f"Error retrieving notifications: {e}")

class LogoutUI(QFrame):
    def __init__(self):
        super(LogoutUI,self).__init__()     
        uic.loadUi('venv\\Logout.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint)  
        self.yesButton = self.findChild(QtWidgets.QPushButton, 'yesButton')
        self.yesButton.clicked.connect(sys.exit) 

        self.noButton = self.findChild(QtWidgets.QPushButton, 'noButton')
        self.noButton.clicked.connect(self.close)

class AdminUI(QMainWindow): #AdminUI  Class
    def __init__(self):
        super(AdminUI, self).__init__()
        uic.loadUi("venv\\Admin.ui", self)
        # self.username = username  # Store the username of admin
        self.connect_buttons()
        self.setDateTime()
        self.update_notification_count()
        self.connect_to_database()
        self.currentPageIndex = None
        self.pageHistory = []
        
    def load_ui(self, ui_file, setup_func=None):
        uic.loadUi(ui_file, self)
        if setup_func:
            setup_func()
    
    def connect_to_database(self): #database connection
        try:
            self.connection = psycopg2.connect(
                dbname="Saku",
                user="postgres",
                password="francis0001",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def setup_main_window(self): #window size set up
        self.setFixedSize(1200, 700)

    def set_stacked_widget_index(self, index): #Method for stacked widget
        if hasattr(self, 'stackedWidget'):
            self.stackedWidget.setCurrentIndex(index)
        else:
            print("StackedWidget not found!")
            
    def connect_buttons(self):  #set up buttons for admin dashboard
        self.stackedWidget = self.findChild(QtWidgets.QStackedWidget, 'stackedWidget')
        self.prod_menu()
        self.salesReport_menu()
        self.dailysales_menu()
        self.monthlysales_menu()
        self.purchase_menu()

        #Products Buttons
        self.notificationButton = self.findChild(QtWidgets.QToolButton, 'notificationButton')
        self.logoutButton = self.findChild(QtWidgets.QToolButton, 'logoutButton') 
        self.dashboardButton = self.findChild(QtWidgets.QToolButton, 'dashboardButton')       
        self.tiresAddProdButton = self.findChild(QtWidgets.QPushButton, 'tiresAddProdButton')
        self.oilsAddProdButton = self.findChild(QtWidgets.QPushButton, 'oilsAddProdButton')
        self.batteriesAddProdButton = self.findChild(QtWidgets.QPushButton, 'batteriesAddProdButton')
        self.selectImageButton = self.findChild(QtWidgets.QPushButton, 'selectImageButton')
        if self.selectImageButton:
            self.selectImageButton.clicked.connect(self.select_image)

        #notif, logout, dashbaord,products
        if self.notificationButton:
            self.notiflistView = None
            self.notificationButton.clicked.connect(self.notification)
        if self.logoutButton:
            self.logoutButton.clicked.connect(self.logout)
        if self.dashboardButton:
            self.dashboardButton.clicked.connect(self.handle_dashboard)
        if self.tiresAddProdButton or self.oilsAddProdButton or self.batteriesAddProdButton:
            self.tiresAddProdButton.clicked.connect(self.handle_addProduct)
            self.oilsAddProdButton.clicked.connect(self.handle_addProduct)
            self.batteriesAddProdButton.clicked.connect(self.handle_addProduct)

        #Sale Buttons
        self.salesButton = self.findChild(QtWidgets.QToolButton, 'salesButton')
        self.salesAddButton = self.findChild(QtWidgets.QPushButton, 'salesAddButton')
        self.clearAllButton = self.findChild(QtWidgets.QPushButton, 'clearAllButton')      
        if self.salesButton:
            self.salesButton.clicked.connect(self.handle_sales)
        if self.salesAddButton:
            self.salesAddButton.clicked.connect(self.handle_salesAdd)
        if self.clearAllButton:
            self.clearAllButton.clicked.connect(self.confirm_delete_all_sales)
        
        #Supplier Buttons
        self.supplierButton = self.findChild(QtWidgets.QToolButton, 'supplierButton')
        self.suppliersAddButton = self.findChild(QtWidgets.QPushButton, 'suppliersAddButton')
        if self.supplierButton:
            self.supplierButton.clicked.connect(self.handle_supplier)
        if self.suppliersAddButton:
            self.suppliersAddButton.clicked.connect(self.handle_supplierAdd)

        #Purchase Buttons
        self.purchaseButton = self.findChild(QtWidgets.QToolButton, 'purchaseButton')
        self.purchaseAddButton = self.findChild(QtWidgets.QPushButton, 'purchaseAddButton')
        self.clearAllPurchase = self.findChild(QtWidgets.QPushButton, 'clearAllPurchase')
        if self.purchaseButton:
            self.purchaseButton.clicked.connect(self.handle_purchase)
        if self.purchaseAddButton:
            self.purchaseAddButton.clicked.connect(self.handle_purchaseAdd)
        if self.clearAllPurchase:
            self.clearAllPurchase.clicked.connect(self.confirm_delete_all_purchase)

        #Account Buttons
        self.accountButton = self.findChild(QtWidgets.QPushButton, 'accountButton')
        self.accountUpdateButton = self.findChild(QtWidgets.QPushButton, 'updateButton')
        self.accountChangeButton = self.findChild(QtWidgets.QPushButton, 'changeButton')
        self.updateAccButton = self.findChild(QtWidgets.QPushButton, 'updateAccButton')
        self.updatePassButton = self.findChild(QtWidgets.QPushButton, 'updatePassButton')
        
        if self.accountButton:
            self.accountButton.clicked.connect(self.handle_account)
        if self.accountUpdateButton:
            self.accountUpdateButton.clicked.connect(self.handle_accountUpdate)
        if self.accountChangeButton:
            self.accountChangeButton.clicked.connect(self.handle_accountChangepass)
        if self.updateAccButton.clicked:
            self.updateAccButton.clicked.connect(self.accountUpdate)
        if self.updatePassButton.clicked:
            self.updatePassButton.clicked.connect(self.accountChangepass)
        #cancel buttons
        self.cancelButtons = [
            self.findChild(QtWidgets.QPushButton, button_name)
            for button_name in ['cancelItemButton', 'cancelSalesButton', 'cancelSupplierButton',
                                'cancelPurchaseButton', 'cancelAccButton', 'cancelPassButton']
        ]
        for button in self.cancelButtons:
            if button:
                button.clicked.connect(self.goBack)

    def show_login_ui(self):
        self.setCentralWidget(LoginUI())

    def setDateTime(self): # Update the date and time every second using a QTimer
        self.dateLabel = self.findChild(QtWidgets.QLabel, 'dateLabel')
        self.dateLabel.customContextMenuRequested.connect(self.updateDateTime)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)

    def updateDateTime(self):  # Get the current date,time and format
        currentDateTime = QDateTime.currentDateTime()
        formattedDateTime = currentDateTime.toString("MMM d, yyyy, h:mm:ss ap")
        self.dateLabel.setText(formattedDateTime)
    
    def closeEvent(self, event): # Disconnect the timer's timeout signal from the updateDateTime slot      
        self.timer.timeout.disconnect(self.updateDateTime)
        event.accept()

    def notification(self):
        self.update_notification_count()
        if self.notiflistView is None:
            self.notiflistView = NotifUi(self)
            self.notiflistView.hide()

        self.notiflistView.populate_notifications()
        self.toggle_notif()


    def add_notification(self, message, product_id=None): # insert notifications
        self.connect_to_database()
        try:
            if product_id is not None:
                self.cursor.execute("INSERT INTO notifications (message, product_id) VALUES (%s, %s)", (message, product_id))
            else:
                self.cursor.execute("INSERT INTO notifications (message) VALUES (%s)", (message,))
            self.connection.commit()
            print("Notification added successfully!")
        except Exception as e:
            print(f"Error adding notification: {e}")

    def update_notification_count(self): #count the stored notifications
        self.connect_to_database()
        self.notiflabel = self.findChild(QtWidgets.QLabel, 'notiflabel')
        try:
            self.cursor.execute("SELECT COUNT(*) FROM notifications")
            count = self.cursor.fetchone()[0]
            self.notiflabel.setText(f"{count}")
            self.notiflabel.setAlignment(Qt.AlignCenter)
            
            if count > 0:
                self.notiflabel.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
            else:
                self.notiflabel.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
                
        except Exception as e:
            print(f"Error updating notification count: {e}")
    
    def toggle_notif(self): #toggle the notification
        if self.notiflistView.isVisible():
            self.notiflistView.hide()
        else:
            self.notiflistView.show()
    
    def logout(self):
        self.log = LogoutUI()
        self.log.show()
    
    def prod_menu(self):  #Setup Product category menu
        menu = QMenu()
        actions = [
            ("Tires", self.handle_tires),                                            
            ("Oils", self.handle_oils),
            ("Batteries", self.handle_batteries)      
        ]
        for text, func in actions:
            action = QAction(text, self)
            action.triggered.connect(func)
            menu.addAction(action)
        self.productButton.setMenu(menu)
    
    def set_header_color(self): #set table headers
        header = self.tableWidget.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section { 
                background-color: #333; 
                color: white; 
                font-size: 15px; 
                border: 1px solid #6c6c6c;
            }
        """)

    ################################ DASHBOARD ##########################################
    def handle_dashboard(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'trendTableWidget')
        self.set_header_color()
        self.set_stacked_widget_index(0)
        self.setCurrentPage(0)
        self.update_dashboard()

    def update_dashboard(self):
        self.connect_to_database()
        
        try:    # Query to get the highest selling products for the current month
            query = """
                SELECT p.product_id, p.product_name, p.product_type, p.product_size, p.product_sellingprice, 
                    SUM(s.sales_quantity) AS total_qty, SUM(s.sales_quantity * p.product_sellingprice) AS total_sale
                FROM sales s
                JOIN product p ON s.product_id = p.product_id
                WHERE DATE_TRUNC('month', s.sales_date) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY p.product_id, p.product_name, p.product_type, p.product_size, p.product_sellingprice
                ORDER BY total_qty DESC
                LIMIT 10
            """
            print(f"Executing query: {query}")  # Debug print
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            print(f"Fetched records: {records}")  # Debug print

            self.tableWidget.setRowCount(len(records))
            self.tableWidget.setColumnCount(7)  # Updated column count
            headers = ["Product ID", "Product", "Type", "Size", "Selling Price", "Quantity Sold", "Total Sale"]
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            for rowIndex, rowData in enumerate(records):
                self.tableWidget.setRowHeight(rowIndex, 80)
                print(f"Processing row: {rowIndex}, Data: {rowData}")  # Debug print
                for colIndex, colData in enumerate(rowData):
                    if colIndex == 1:  # Product column
                        colData = colData.title()
                    elif colIndex == 2:  # Size column
                        colData = colData.title()
                    elif colIndex == 3:  # Size column
                        colData = colData.upper()
                    elif colIndex in [4, 6]:  # Format the price and total sale columns
                        colData = f"₱ {colData:,.2f}"
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)
            
            # Update total number of products
            product_count_query = "SELECT COUNT(*) FROM product"
            self.cursor.execute(product_count_query)
            product_count = self.cursor.fetchone()[0]
            print(f"Total number of products: {product_count}")  # Debug print

            self.numProductLabel = self.findChild(QtWidgets.QLabel, 'numProductLabel')
            self.numProductLabel.setText(f"{product_count}")
            
            # Update total sales
            total_sales_query = "SELECT SUM(sales_quantity * product_sellingprice) FROM sales JOIN product ON sales.product_id = product.product_id"
            self.cursor.execute(total_sales_query)
            total_sales = self.cursor.fetchone()[0]
            if total_sales is not None:
                total_sales_formatted = f"₱ {total_sales:,.2f}"
            else:
                total_sales_formatted = "₱ 0.00"
            print(f"Total sales: {total_sales_formatted}")  # Debug print
            self.numSalesLabel = self.findChild(QtWidgets.QLabel, 'numSalesLabel')
            self.numSalesLabel.setText(total_sales_formatted)

        except Exception as e:
            print(f"Dashboard : Error executing query: {e}")

    ############################## PRODUCTS ###############################################        

    def handle_tires(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'tiresTableWidget')
        self.set_stacked_widget_index(1)
        self.setCurrentPage(1)
        self.currentPageIndex = 1
        self.connect_to_database()
        self.update_notification_count()
        try:
            self.cursor.execute("""
                SELECT p.product_id, p.product_name, p.image_path, p.product_type, p.product_size, p.product_stock, p.product_sellingprice, s.company_name
                FROM PRODUCT p
                JOIN SUPPLIER s ON p.supplier_id = s.supplier_id
                WHERE p.product_type = 'tire'
            """)
            records = self.cursor.fetchall()
            self.populate_table(records)
        except Exception as e:
            print(f"Tire - Error executing query: {e}")

    def handle_oils(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'oilsTableWidget')
        self.set_stacked_widget_index(2)
        self.setCurrentPage(2)
        self.currentPageIndex = 2
        self.connect_to_database()
        self.update_notification_count()
        try:
            self.cursor.execute("""
                SELECT p.product_id, p.product_name, p.image_path, p.product_type, p.product_size, p.product_stock, p.product_sellingprice, s.company_name
                FROM PRODUCT p
                JOIN SUPPLIER s ON p.supplier_id = s.supplier_id
                WHERE p.product_type = 'oil'
            """)
            records = self.cursor.fetchall()
            self.populate_table(records)
        except Exception as e:
            print(f"Oil - Error executing query: {e}")

    def handle_batteries(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'batteriesTableWidget')
        self.set_stacked_widget_index(3)
        self.setCurrentPage(3)
        self.currentPageIndex = 3
        self.connect_to_database()
        self.update_notification_count()
        try:
            self.cursor.execute("""
                SELECT p.product_id, p.product_name, p.image_path, p.product_type, p.product_size, p.product_stock, p.product_sellingprice, s.company_name
                FROM PRODUCT p
                JOIN SUPPLIER s ON p.supplier_id = s.supplier_id
                WHERE p.product_type = 'battery'
            """)
            records = self.cursor.fetchall()
            self.populate_table(records)
        except Exception as e:
            print(f"Battery - Error executing query: {e}")

    def populate_table(self, records):
        self.tableWidget.setRowCount(len(records))
        self.tableWidget.setColumnCount(9)
        headers = ["Product ID", "Product", "Image", "Type", "Size", "In Stock", "Price", "Supplier", "Actions"]
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.set_header_color()

        for rowIndex, rowData in enumerate(records):
            self.tableWidget.setRowHeight(rowIndex, 100)  # Set fixed row height for larger images
            for colIndex, colData in enumerate(rowData):
                if colIndex == 1:  # Product column
                    colData = colData.title()
                elif colIndex == 3:  # Type column
                    colData = colData.title()
                elif colIndex == 4:  # Size column
                    colData = colData.upper()
                elif colIndex == 7:  # Supplier column
                    colData = colData.title()
                elif colIndex == 6:  # Format the price column
                    colData = f"₱ {colData:,.2f}"
                if colIndex == 2:  # Display the image in the image column (index 2)
                    image_path = colData
                    if image_path:
                        label = QLabel()
                        pixmap = QPixmap(image_path)
                        label.setPixmap(pixmap.scaled(140, 140, QtCore.Qt.KeepAspectRatio))
                        self.tableWidget.setCellWidget(rowIndex, 2, label)
                    else:
                        item = QTableWidgetItem("No Image")
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                        self.tableWidget.setItem(rowIndex, 2, item)
                else:
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)

            # Add the ButtonWidget in the last column (index 8)
            buttonWidget = ButtonWidget()
            buttonWidget.addButton.setVisible(False)
            buttonWidget.editButton.clicked.connect(lambda _, r=rowIndex: self.edit_row(r))
            buttonWidget.saveButton.clicked.connect(lambda _, r=rowIndex: self.save_row(r))
            buttonWidget.deleteButton.clicked.connect(self.get_product_delete_lambda(rowIndex))

            self.tableWidget.setCellWidget(rowIndex, 8, buttonWidget)

    def edit_row(self, rowIndex):
        print("Edit clicked")
        buttonWidget = self.tableWidget.cellWidget(rowIndex, 8)
        if buttonWidget:
            buttonWidget.editButton.setVisible(False)
            buttonWidget.saveButton.setVisible(True)
        # Columns to be made editable (indices: product_name, product_size, product_stock, product_price)
        editable_columns = [1, 4, 5, 6]
        
        for col in editable_columns:
            item = self.tableWidget.item(rowIndex, col)
            if item:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                print("Editable column", col, "flags:", item.flags())       
        self.tableWidget.update()

    def save_row(self, rowIndex):
        buttonWidget = self.tableWidget.cellWidget(rowIndex, 8)
        if buttonWidget:
            buttonWidget.editButton.setVisible(True)
            buttonWidget.saveButton.setVisible(False)

        # Define the editable columns (indices: product_name, product_size, product_stock, product_price)
        editable_columns = [1, 4, 5, 6]
        updated_data = []
        
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(rowIndex, col)
            if item:
                if col in editable_columns:  # Make the specific columns non-editable again
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                if col == 6:  # Remove currency symbol and format number correctly
                    updated_data.append(item.text().replace('₱ ', '').replace(',', ''))
                else:
                    updated_data.append(item.text())

        product_id = updated_data[0]
        product_name = updated_data[1].lower()
        product_size = updated_data[3].lower()
        product_stock = updated_data[4]
        product_price = updated_data[5]

        # Ensure all fields are filled
        if not all([product_name, product_size, product_stock, product_price]):
            QtWidgets.QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            self.refresh_table()
            return

        # Check if product_stock is a valid integer and not negative
        if not product_stock.isdigit() or int(product_stock) <= 0:
            QtWidgets.QMessageBox.warning(self, "Input Error", f"Invalid quantity: {product_stock}")
            self.refresh_table()
            return

        # Check if product selling price is a valid number (allowing decimals) and not negative
        try:
            price = float(product_price)
            if price < 0:
                raise ValueError(f"Price cannot be negative: {product_price}")
        except ValueError as ve:
            QtWidgets.QMessageBox.warning(self, "Input Error", f"Invalid price: {product_price}")
            self.refresh_table()
            return

        try:
            # Retrieve uneditable fields: product_type and supplier_id
            self.cursor.execute("""
                SELECT product_type, supplier_id FROM PRODUCT
                WHERE product_id = %s
            """, (product_id,))
            result = self.cursor.fetchone()
            if not result:
                QtWidgets.QMessageBox.warning(self, "Database Error", "there is an error while editing please try again later.")
                self.refresh_table()
                return
            
            product_type = result[0]
            supplier_id = result[1]

            # Check if the product with the edited details already exists in the database
            self.cursor.execute("""
                SELECT 1 FROM PRODUCT 
                WHERE product_name = %s AND product_type = %s AND product_size = %s AND supplier_id = %s AND product_id != %s
            """, (product_name, product_type, product_size, supplier_id, product_id))
            if self.cursor.fetchone():
                QtWidgets.QMessageBox.warning(self, "Unable to edit", f"Product '{product_name.title()}' of type '{product_type.title()}' and size '{product_size.upper()}' with the same supplier already exists.")
                self.refresh_table()
                return

            # Update the product details in the database
            self.cursor.execute("""
                UPDATE PRODUCT SET
                product_name = %s, product_size = %s,
                product_stock = %s, product_sellingprice = %s
                WHERE product_id = %s
            """, (product_name, product_size, product_stock, product_price, product_id))
            self.connection.commit()
            QMessageBox.information(self, "Update Successful", "Product details updated successfully!")
            print("Update Successful")
        except Exception as e:
            print(f"Products Error updating database: {e}")
        # Refresh the table after saving
        self.refresh_table()

    #Method for reverting the changes if there are invalid inputs caught
    def refresh_table(self):
        if self.currentPageIndex == 1:
            self.handle_tires()
        elif self.currentPageIndex == 2:
            self.handle_oils()
        elif self.currentPageIndex == 3:
            self.handle_batteries()

    def get_product_delete_lambda(self, rowIndex):
        return lambda: self.delete_row(rowIndex)

    def delete_row(self, rowIndex):
        code_item = self.tableWidget.item(rowIndex, 0)
        if code_item:
            product_id = code_item.text()
            try:
                self.cursor.execute("SELECT product_name FROM PRODUCT WHERE product_id = %s", (product_id,))
                product_name = self.cursor.fetchone()[0]
                prod_name = product_name.title()
                # Now delete the product (which will cascade delete related notifications)
                self.cursor.execute("DELETE FROM PRODUCT WHERE product_id = %s", (product_id,))
                self.connection.commit()

                self.tableWidget.removeRow(rowIndex)
                QtWidgets.QMessageBox.information(self, "Product Deleted", f"Product Id {product_id} has been deleted.")
                
                # Optionally, add a notification about the deletion without specifying product_id
                self.add_notification(f"Product '{prod_name}' (ID: {product_id}) has been deleted from the inventory.", None)
                
            except Exception as e:
                print(f"Error deleting product: {e}")

    def handle_addProduct(self):
        self.set_stacked_widget_index(4)
        self.setCurrentPage(4)
        self.additemButton = self.findChild(QtWidgets.QPushButton, 'addItemButton')
        # Check if the signal is already connected
        if not hasattr(self, 'is_additemButton_connected'):
            self.additemButton.clicked.connect(self.addproduct)
            self.is_additemButton_connected = True

        self.productSupplierInput = self.findChild(QtWidgets.QComboBox, 'productSupplier')
        # Fetch and populate suppliers
        self.populate_suppliers()

    def addproduct(self):
        self.connect_to_database()

        self.productNameInput = self.findChild(QtWidgets.QLineEdit, 'productName')
        self.productTypeInput = self.findChild(QtWidgets.QComboBox, 'productType')
        self.productSizeInput = self.findChild(QtWidgets.QLineEdit, 'productSize')
        self.productQuantityInput = self.findChild(QtWidgets.QLineEdit, 'productQuantity')
        self.productBuyingPriceInput = self.findChild(QtWidgets.QLineEdit, 'productBuyingPrice')
        self.productSellingPriceInput = self.findChild(QtWidgets.QLineEdit, 'productSellingPrice')
        self.productReorderLevelInput = self.findChild(QtWidgets.QLineEdit, 'productReorderLevel')
        self.productSupplierInput = self.findChild(QtWidgets.QComboBox, 'productSupplier')
        self.imagePathLineEdit = self.findChild(QtWidgets.QLineEdit, 'imagePathLineEdit')

        product_name = self.productNameInput.text().lower()
        product_type = self.productTypeInput.currentText().lower()
        product_size = self.productSizeInput.text().lower()
        product_quantity = self.productQuantityInput.text()
        product_buying_price = self.productBuyingPriceInput.text()
        product_selling_price = self.productSellingPriceInput.text()
        product_reorder_level = self.productReorderLevelInput.text()
        product_supplier_name = self.productSupplierInput.currentText().lower()
        image_path = self.imagePathLineEdit.text()

        if not all([product_name, product_type, product_size, product_quantity, product_buying_price, product_selling_price, product_reorder_level, product_supplier_name, image_path]):
            QtWidgets.QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return       
        if not product_quantity.isdigit() or int(product_quantity) <= 0:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Product quantity must be a number greater than zero.")
            return
        if not product_reorder_level.isdigit() or int(product_reorder_level) <= 0:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Product reorder level must be a number greater than zero.")
            return
        try:
            product_buying_price = float(product_buying_price)
            if product_buying_price < 0:
                QtWidgets.QMessageBox.warning(self, "Input Error", "Product buying price cannot be less than zero.")
                return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Product buying price must be a number.")
            return

        try:
            product_selling_price = float(product_selling_price)
            if product_selling_price < 0:
                QtWidgets.QMessageBox.warning(self, "Input Error", "Product selling price cannot be less than zero.")
                return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Product selling price must be a number.")
            return

        # Get the supplier ID from the dictionary
        supplier = product_supplier_name.title()
        product_supplier_id = self.supplier_dict.get(product_supplier_name.title())

        if not product_supplier_id:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Invalid supplier selected.")
            return

        try:
            # Check if the supplier's product type matches the selected product type
            self.cursor.execute("""
                SELECT product_type FROM supplier WHERE supplier_id = %s
            """, (product_supplier_id,))
            result = self.cursor.fetchone()

            if result and result[0].lower() != product_type:
                QtWidgets.QMessageBox.warning(self, "Input Error", f"Supplier '{supplier}' does not supply products of type '{product_type.title()}'.")
                return
            
            # Check if the product with the same name, type, and size already exists
            self.cursor.execute("""
                SELECT 1 FROM product 
                WHERE product_name = %s AND product_type = %s AND product_size = %s AND supplier_id = %s
            """, (product_name, product_type, product_size, product_supplier_id))
            if self.cursor.fetchone():
                QtWidgets.QMessageBox.warning(self, "Input Error", f"Product '{product_name.title()}' of type '{product_type.title()}' and size '{product_size.upper()}' with supplier company name'{supplier}' already exists.")
                return

            # Insert new product
            self.cursor.execute("""
                INSERT INTO PRODUCT (PRODUCT_NAME, PRODUCT_TYPE, PRODUCT_SIZE, PRODUCT_STOCK, 
                                    PRODUCT_BUYINGPRICE, PRODUCT_SELLINGPRICE, PRODUCT_REORDER, 
                                    SUPPLIER_ID, IMAGE_PATH)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING product_id
            """, (product_name, product_type, product_size, product_quantity, product_buying_price, 
                product_selling_price, product_reorder_level, product_supplier_id, image_path))
            product_id = self.cursor.fetchone()[0]
            self.connection.commit()
            prod_name = product_name.title()
            print("Product added successfully!")
            QtWidgets.QMessageBox.information(self, "Successful", f"Product '{prod_name}' added successfully!")
            # Add notification
            self.add_notification(f"Product '{prod_name}' added to the inventory.", product_id)

            # Clear the input fields after successful addition
            self.productNameInput.clear()
            self.productSizeInput.clear()
            self.productQuantityInput.clear()
            self.productBuyingPriceInput.clear()
            self.productSellingPriceInput.clear()
            self.productReorderLevelInput.clear()
            self.imagePathLineEdit.clear()
            #Proceed to specific product pages after successfull insertion
            if product_type == 'tire':
                self.handle_tires()
            elif product_type == 'oil':
                self.handle_oils()
            elif product_type == 'battery':
                self.handle_batteries()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Invalid Input", f"Failed adding Product: {e}")
            print(f"Error adding product: {e}")
    #populate the combo box drop down with the company names
    def populate_suppliers(self):
        try:
            self.cursor.execute("SELECT supplier_id, company_name FROM SUPPLIER")
            suppliers = self.cursor.fetchall()
            self.productSupplierInput.clear()
            self.supplier_dict = {}  # Dictionary to map supplier names to IDs

            if not suppliers:
                QtWidgets.QMessageBox.warning(self, "No Suppliers", "No suppliers found. Please add a supplier before adding a product.")
                self.handle_supplierAdd()
                return

            for supplier in suppliers:
                supplier_id, supplier_name = supplier
                # Convert supplier name to title case before adding it to the combo box
                supplier_name_title = supplier_name.title()
                self.productSupplierInput.addItem(supplier_name_title)
                self.supplier_dict[supplier_name_title] = supplier_id
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching suppliers: {e}")
            print(f"Error fetching suppliers: {e}")


    #method to select files(images only)
    def select_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_path:
            self.imagePathLineEdit.setText(file_path)

    ##################################### SALES ######################################

    def handle_sales(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'salesTableWidget')
        self.set_stacked_widget_index(5)
        self.setCurrentPage(5)
        self.connect_to_database()
        self.update_notification_count()
        try:
            self.cursor.execute("""
                SELECT s.sales_id, p.product_name, p.product_type, p.product_size, s.sales_quantity,p.product_sellingprice, s.sales_quantity * p.product_sellingprice AS total, s.sales_date
                FROM SALES s
                JOIN PRODUCT p ON s.product_id = p.product_id
                ORDER BY s.sales_id DESC
            """)
            records = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(records))
            self.tableWidget.setColumnCount(9)
            headers = ["Sales ID", "Product", "Type", "Size", "Quantity", "Selling Price", "Total Sale", "Date", "Actions"]
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()

            for rowIndex, rowData in enumerate(records):
                self.tableWidget.setRowHeight(rowIndex, 80)
                for colIndex, colData in enumerate(rowData):
                    if colIndex == 1:  # Product column
                        colData = colData.title()
                    elif colIndex == 2:  # Type column
                        colData = colData.title()
                    elif colIndex == 3:  # Size column
                        colData = colData.upper()
                    elif colIndex in [5, 6]:  # Format the price and total sale columns
                        colData = f"₱ {colData:,.2f}"
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)

                # Add Action button
                buttonWidget = ButtonWidget()
                buttonWidget.editButton.setVisible(False)
                buttonWidget.addButton.setVisible(False)            
                buttonWidget.deleteButton.clicked.connect(self.get_sales_delete_lambda(rowIndex))
                self.tableWidget.setCellWidget(rowIndex, 8, buttonWidget)

        except Exception as e:
            print(f"Sales Error executing query: {e}")

    def confirm_delete_all_sales(self):
        self.connect_to_database()
        # Check if there are any records in SALES table
        self.cursor.execute("SELECT COUNT(*) FROM SALES")
        count = self.cursor.fetchone()[0]

        if count == 0:
            QMessageBox.information(self, "Empty Sales", "There are no sales records to delete.")
        else:
            reply = QMessageBox.question(self, 'Confirm Deletion', 
                                        "Are you sure you want to delete all sales records?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.delete_all_sales()

    def delete_all_sales(self):
        self.connect_to_database()
        try:
            self.cursor.execute("DELETE FROM SALES")
            self.connection.commit()
            QMessageBox.information(self, "Deletion Successful", "All sales records have been deleted successfully!")
            self.handle_sales()
        except Exception as e:
            print(f"Error deleting row: {e}")

    #method to secure correct ron index to delete
    def get_sales_delete_lambda(self, rowIndex):
        return lambda: self.sales_delete_row(rowIndex)
    # delete the selected row
    def sales_delete_row(self, rowIndex):
        code_item = self.tableWidget.item(rowIndex, 0)
        if code_item:
            code = code_item.text()
            try:
                self.cursor.execute("DELETE FROM SALES WHERE sales_id= %s", (code,))
                self.connection.commit()
                self.tableWidget.removeRow(rowIndex)
                QMessageBox.information(self, "Sales Deleted", f"Sales Code {code} has been deleted.")
            except Exception as e:
                print(f"Error deleting row: {e}")
    
    def handle_salesAdd(self):
        self.connect_to_database()
        self.update_notification_count()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'searchtableWidget')
        headers = ["Code", "Product", "Type", "Size", "Quantity", "Price", "Total", "Actions"]
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.set_stacked_widget_index(6)
        self.setCurrentPage(6)
        self.salesfindButton = self.findChild(QtWidgets.QPushButton, 'findButton')
        self.salesfindButton.clicked.connect(self.search_item)

        try:
            query = "SELECT product_id, product_name, product_type, product_size, product_sellingprice FROM product"
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            headers = ["Product ID", "Product Name", "Product Type", "Product Size", "Price", "Quantity", "Total", "Action"]
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(headers))
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            for row_number, row_data in enumerate(results):
                self.tableWidget.setRowHeight(row_number, 80)
                for column_number, data in enumerate(row_data):
                    if column_number == 1:  # Product Name
                        data = data.title()
                    elif column_number == 2:  # Product Type
                        data = data.title()
                    elif column_number == 3:  # Product Size
                        data = data.upper()
                    elif column_number == 4:  # Product Price
                        data = f"₱ {data:,.2f}"
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(row_number, column_number, item)
                
                # Add Quantity and Total columns
                quantity_item = QtWidgets.QTableWidgetItem("1")  # Set default quantity to 1
                quantity_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row_number, 5, quantity_item)

                # Calculate total based on default quantity
                price = float(self.tableWidget.item(row_number, 4).text().replace('₱ ', '').replace(',', ''))
                total = price * 1  # Quantity is set to 1
                total_item = QtWidgets.QTableWidgetItem(f"₱ {total:,.2f}")
                total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                self.tableWidget.setItem(row_number, 6, total_item)

                # Add Action button
                button_widget = ButtonWidget()                
                button_widget.editButton.setVisible(False)
                button_widget.deleteButton.setVisible(False)
                button_widget.addButton.clicked.connect(lambda _, r=row_number: self.add_to_sales(r))
                self.tableWidget.setCellWidget(row_number, 7, button_widget)
            
            # Connect itemChanged signal to update_total function
            self.tableWidget.itemChanged.connect(self.update_total)
            
        except Exception as e:
            print(f" Search Item Error executing query: {e}")

    def search_item(self):
        self.connect_to_database()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'searchtableWidget')
        self.searchLineEdit = self.findChild(QtWidgets.QLineEdit, 'searchLineEdit')
        product = self.searchLineEdit.text()
        search_product = product.lower()
        
        try:
            query = "SELECT product_id, product_name, product_type, product_size, product_sellingprice FROM product WHERE product_name LIKE %s"
            self.cursor.execute(query, (f'%{search_product}%',))
            results = self.cursor.fetchall()

            # Check if results are empty
            if not results:
                QMessageBox.information(self, "Search Failed", f"Product {product} was not found.")
                return
            
            # Set up the table
            headers = ["Product ID", "Product Name", "Product Type", "Product Size", "Price", "Quantity", "Total", "Action"]
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(headers))
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            for row_number, row_data in enumerate(results):
                self.tableWidget.setRowHeight(row_number, 80)
                for column_number, data in enumerate(row_data):
                    if column_number == 1:  # Product Name
                        data = data.title()
                    elif column_number == 2:  # Product Type
                        data = data.title()
                    elif column_number == 3:  # Product Size
                        data = data.upper()
                    elif column_number == 4:  # Product Price
                        data = f"₱ {data:,.2f}"
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(row_number, column_number, item)
                
                # Add Quantity and Total columns
                quantity_item = QtWidgets.QTableWidgetItem("1")  # Set default quantity to 1
                quantity_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row_number, 5, quantity_item)

                # Calculate total based on default quantity
                price = float(self.tableWidget.item(row_number, 4).text().replace('₱ ', '').replace(',', ''))
                total = price * 1  # Quantity is set to 1
                total_item = QtWidgets.QTableWidgetItem(f"₱ {total:,.2f}")
                total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                self.tableWidget.setItem(row_number, 6, total_item)

                # Add Action button
                button_widget = ButtonWidget()                
                button_widget.editButton.setVisible(False)
                button_widget.deleteButton.setVisible(False)
                button_widget.addButton.clicked.connect(self.get_sales_add_lambda(row_number))
                self.tableWidget.setCellWidget(row_number, 7, button_widget)
            
            # Connect itemChanged signal to update_total function
            self.tableWidget.itemChanged.connect(self.update_total)
            
        except Exception as e:
            print(f" Search Item Error executing query: {e}")
    
    def get_sales_add_lambda(self, row):
        return lambda: self.add_to_sales(row)
    #method to update the total depends on the quantity inputted
    def update_total(self, item):
        row = item.row()
        column = item.column()

        if column == 5:  # Quantity column
            try:
                price = float(self.tableWidget.item(row, 4).text().replace('₱ ', '').replace(',', ''))
                quantity = item.text()
                if quantity:
                    quantity = int(quantity)
                    if quantity < 1:
                        QMessageBox.warning(self, "Invalid Quantity", "Negative or Zero quantity is not allowed.")
                        item.setText("1")  # Reset to default quantity
                        total = price * 1
                    else:
                        total = price * quantity
                    self.tableWidget.setItem(row, 6, QTableWidgetItem(f"₱ {total:,.2f}"))
                else:
                    self.tableWidget.setItem(row, 6, QTableWidgetItem(""))
            except ValueError:
                self.tableWidget.setItem(row, 6, QTableWidgetItem(""))

    def add_to_sales(self, row):
        try:
            product_id = self.tableWidget.item(row, 0).text()
            quantity_text = self.tableWidget.item(row, 5).text()

            if not all([product_id, quantity_text]):
                QtWidgets.QMessageBox.warning(self, "Input Error", "Quantity field must be filled.")
                return

            # Check if quantity_text is valid and can be converted to an integer
            if not quantity_text.isdigit():
                raise ValueError(f"Invalid quantity: {quantity_text}")
            
            quantity = int(quantity_text)

            # Fetch the current stock from the database
            stock_query = """
                SELECT product_stock, product_name, product_reorder FROM product WHERE product_id = %s
            """
            self.cursor.execute(stock_query, (product_id,))
            stock_result = self.cursor.fetchone()

            if stock_result is None:
                QtWidgets.QMessageBox.warning(self, "Error", "Product not found.")
                return

            current_stock, product_name, product_reorder_level = stock_result
            prod_name = product_name.title()

            # Check if the quantity is greater than the available stock
            if quantity > current_stock:
                QtWidgets.QMessageBox.warning(self, "Insufficient Stock", f"Not enough stock available. Only {current_stock} units left.")
                return
            
            current_date = datetime.now().strftime('%Y-%m-%d')
            # Insert into sales table
            insert_query = """
                INSERT INTO sales (product_id, sales_quantity, sales_date)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(insert_query, (product_id, quantity, current_date))

            # Update product table to reduce stock quantity
            update_query = """
                UPDATE product
                SET product_stock = product_stock - %s
                WHERE product_id = %s
            """
            self.cursor.execute(update_query, (quantity, product_id))
            self.connection.commit()

            # Check product status
            new_stock = current_stock - quantity
            self.check_product_status(product_id, prod_name, new_stock, product_reorder_level)
            
            self.tableWidget.removeRow(row)
            self.searchLineEdit.clear()
            QtWidgets.QMessageBox.information(self, "Successful", f"Sales added successfully!")
            # Check if the new stock has reached or below the reorder level
            if new_stock <= product_reorder_level:
                QtWidgets.QMessageBox.warning(self, "Reorder Level Reached", f"Product: {prod_name} has reached its reorder level ({product_reorder_level}).")
            self.handle_sales()
            if new_stock == 0:
                QtWidgets.QMessageBox.warning(self, "Out of Stock", f"Product: {prod_name} is now out of stock.")
            self.handle_sales()

        except ValueError as ve:
            print(f"Value error: {ve}")
            QtWidgets.QMessageBox.warning(self, "Warning", f"Value error:' {ve} ', Input must be an Integer")
        except Exception as e:
            print(f"Error inserting into sales table or updating product stock: {e}")

    def check_product_status(self, product_id, product_name, product_quantity, product_reorder_level):
        if int(product_quantity) <= 0:
            self.add_notification(f"Product '{product_name}' (ID: {product_id}) is out of stock.", product_id)
        elif int(product_quantity) <= int(product_reorder_level):
            self.add_notification(f"Product '{product_name}' (ID: {product_id}) has reached its reorder level( {product_reorder_level} ), Only {product_quantity} units left.", product_id)

    # Setup sales menu
    def salesReport_menu(self):
        menu = QMenu()
        actions = [
            ("Daily Sales", self.handle_dailySales),                                            
            ("Monthly Sales", self.handle_monthlySales)         
        ]
        for text, func in actions:
            action = QAction(text, self)
            action.triggered.connect(func)
            menu.addAction(action)
        self.reportButton.setMenu(menu)
    
    def handle_dailySales(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'dailyTableWidget')
        self.set_header_color()
        self.set_stacked_widget_index(8)
        self.setCurrentPage(8)
        self.update_daily_sales("All") # Default to show all sales

    def update_daily_sales(self, filter_category):
        self.connect_to_database()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'dailyTableWidget')
        
        try:
            base_query = """
                SELECT p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice, 
                    SUM(s.sales_quantity) AS total_qty, SUM(s.sales_quantity * p.product_sellingprice) AS total_sale
                FROM sales s
                JOIN product p ON s.product_id = p.product_id
                WHERE DATE(s.sales_date) = CURRENT_DATE
            """
            
            if filter_category == "Tire":
                query = base_query + " AND p.product_type = 'tire' GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice"
                print(f"Executing Tire query: {query}")  # Debug print
            elif filter_category == "Oil":
                query = base_query + " AND p.product_type = 'oil' GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice"
                print(f"Executing Oil query: {query}")  # Debug print
            elif filter_category == "Battery":
                query = base_query + " AND p.product_type = 'battery' GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice"
                print(f"Executing Battery query: {query}")  # Debug print
            else:
                query = base_query + " GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice ORDER BY total_qty DESC"
            
            print(f"Executing query: {query}")  # Debug print
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            print(f"Fetched records: {records}")  # Debug print

            self.tableWidget.setRowCount(len(records))
            self.tableWidget.setColumnCount(7)  # Updated column count
            headers = ["Product", "Type", "Size", "Buying Price", "Selling Price", "Total Qty", "Total"]
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            total_sales = 0
            total_profit = 0
            
            for rowIndex, rowData in enumerate(records):
                self.tableWidget.setRowHeight(rowIndex, 80)
                print(f"Processing row: {rowIndex}, Data: {rowData}")  # Debug print
                for colIndex, colData in enumerate(rowData):
                    if colIndex == 0:  # Product column
                        colData = colData.title()
                    elif colIndex == 1:  # Type column
                        colData = colData.title()
                    elif colIndex == 2:  # Size column
                        colData = colData.upper()
                    elif colIndex in [3,4,6]:  # Format the price and total sale columns
                        colData = f"₱ {colData:,.2f}"
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)
                    
                total_sales += rowData[6]  # Sum up the total sales
                total_profit += (rowData[6] - rowData[3] * rowData[5])  # Calculate profit (Total Sale - (Buying Price * Total Quantity))
            
            # Update total and profit labels
            self.dailyTotalLabel = self.findChild(QtWidgets.QLabel, 'dailyTotalLabel')
            self.dailyProfitLabel = self.findChild(QtWidgets.QLabel, 'dailyProfitLabel')
            
            print(f"Total Sales: {total_sales}, Total Profit: {total_profit}")  # Debug print
            self.dailyTotalLabel.setText(f"₱ {total_sales:,.2f}")
            self.dailyProfitLabel.setText(f"₱ {total_profit:,.2f}")
            
        except Exception as e:
            print(f"Daily Sales Error executing query: {e}")

    # Functions to filter by different categories
    def filterByAll(self):
        self.update_daily_sales("All")
    def filterByTire(self):
        self.update_daily_sales("Tire")
    def filterByOil(self):
        self.update_daily_sales("Oil")
    def filterByBattery(self):
        self.update_daily_sales("Battery")
    # Setup sales menu
    def dailysales_menu(self):
        menu = QMenu()
        actions = [
            ("All", self.filterByAll),
            ("Tire", self.filterByTire),
            ("Oil", self.filterByOil),
            ("Battery", self.filterByBattery)
        ]
        for text, func in actions:
            action = QAction(text, self)
            action.triggered.connect(func)
            menu.addAction(action)
        self.dailySalesFilter.setMenu(menu)

    def handle_monthlySales(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'monthlyTableWidget')
        self.set_header_color()
        self.set_stacked_widget_index(7)  
        self.setCurrentPage(7)
        self.update_monthly_sales("All")  # Default to show all sales

    def update_monthly_sales(self, filter_category):
        self.connect_to_database()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'monthlyTableWidget')
        
        try:
            base_query = """
                SELECT p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice, 
                    SUM(s.sales_quantity) AS total_qty, SUM(s.sales_quantity * p.product_sellingprice) AS total_sale
                FROM sales s
                JOIN product p ON s.product_id = p.product_id
                WHERE DATE_TRUNC('month', s.sales_date) = DATE_TRUNC('month', CURRENT_DATE)
            """
            if filter_category == "Tire":
                query = base_query + " AND p.product_type = 'tire' GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice"
                print(f"Executing Tire query: {query}")  # Debug print
            elif filter_category == "Oil":
                query = base_query + " AND p.product_type = 'oil' GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice"
                print(f"Executing Oil query: {query}")  # Debug print
            elif filter_category == "Battery":
                query = base_query + " AND p.product_type = 'battery' GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice"
                print(f"Executing Battery query: {query}")  # Debug print
            else:
                query = base_query + " GROUP BY p.product_name, p.product_type, p.product_size, p.product_buyingprice, p.product_sellingprice ORDER BY total_qty DESC"
            
            print(f"Executing query: {query}")  # Debug print
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            print(f"Fetched records: {records}")  # Debug print

            self.tableWidget.setRowCount(len(records))
            self.tableWidget.setColumnCount(7)  # Updated column count
            headers = ["Product", "Type", "Size", "Buying Price", "Selling Price", "Total Qty", "Total"]
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            total_sales = 0
            total_profit = 0
            
            for rowIndex, rowData in enumerate(records):
                self.tableWidget.setRowHeight(rowIndex, 80)
                print(f"Processing row: {rowIndex}, Data: {rowData}")  # Debug print
                for colIndex, colData in enumerate(rowData):
                    if colIndex == 0:  # Product column
                        colData = colData.title()
                    elif colIndex == 1:  # Type column
                        colData = colData.title()
                    elif colIndex == 2:  # Size column
                        colData = colData.upper()
                    elif colIndex in [3,4,6]:  # Format the price and total sale columns
                        colData = f"₱ {colData:,.2f}"
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)
                    
                total_sales += rowData[6]  # Sum up the total sales
                total_profit += (rowData[6] - rowData[3] * rowData[5])  # Calculate profit (Total Sale - (Buying Price * Total Quantity))
            
            # Update total and profit labels
            self.monthlyTotalLabel = self.findChild(QtWidgets.QLabel, 'monthlyTotalLabel')
            self.monthlyProfitLabel = self.findChild(QtWidgets.QLabel, 'monthlyProfitLabel')
            
            print(f"Total Sales: {total_sales}, Total Profit: {total_profit}")  # Debug print
            self.monthlyTotalLabel.setText(f"₱ {total_sales:,.2f}")
            self.monthlyProfitLabel.setText(f"₱ {total_profit:,.2f}")
            
        except Exception as e:
            print(f"Monthly Sales Error executing query: {e}")

    # Functions to filter by different categories
    def filterByAllMonthly(self):
        self.update_monthly_sales("All")

    def filterByTireMonthly(self):
        self.update_monthly_sales("Tire")

    def filterByOilMonthly(self):
        self.update_monthly_sales("Oil")

    def filterByBatteryMonthly(self):
        self.update_monthly_sales("Battery")

    # Setup sales menu
    def monthlysales_menu(self):
        menu = QMenu()
        actions = [
            ("All", self.filterByAllMonthly),
            ("Tire", self.filterByTireMonthly),
            ("Oil", self.filterByOilMonthly),
            ("Battery", self.filterByBatteryMonthly)
        ]
        for text, func in actions:
            action = QAction(text, self)
            action.triggered.connect(func)
            menu.addAction(action)
        self.monthlySalesFilter.setMenu(menu)

    ################################### SUPPLIER #############################################

    def handle_supplier(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'suppliersTableWidget')
        self.set_stacked_widget_index(9)
        self.setCurrentPage(9)
        self.connect_to_database()
        try:
            self.cursor.execute("""
                SELECT s.supplier_id, s.company_name, c.contact_name, c.title, c.phone, s.address, s.city, s.province, c.email, s.product_type
                FROM supplier s
                JOIN contact c ON s.contact_id = c.contact_id
            """)
            records = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(records))
            self.tableWidget.setColumnCount(11)
            headers = ["Supplier ID", "Company Name", "Contact Name", "Title", "Phone", "Address", "City", "Province", "Email", "Product", "Action"]
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()

            for rowIndex, rowData in enumerate(records):
                self.tableWidget.setRowHeight(rowIndex, 80)
                for colIndex, colData in enumerate(rowData):
                    if colIndex == 1:  # company column
                        colData = colData.title()
                    elif colIndex == 2:  # contact name column
                        colData = colData.title()
                    elif colIndex == 3:  # title column
                        colData = colData.title()
                    elif colIndex == 5:  # address column
                        colData = colData.title()
                    elif colIndex == 6:  # city column
                        colData = colData.title()
                    elif colIndex == 7:  # province column
                        colData = colData.title()
                    elif colIndex == 8:  # email column
                        colData = colData.lower()
                    elif colIndex == 9:  # product column
                        colData = colData.title()
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)
                    
                # Add the ButtonWidget in the last column (index 10)
                buttonWidget = ButtonWidget()
                buttonWidget.addButton.setVisible(False)
                buttonWidget.editButton.clicked.connect(lambda _, r=rowIndex: self.supplier_edit_row(r))
                buttonWidget.saveButton.clicked.connect(lambda _, r=rowIndex: self.supplier_save_row(r))
                buttonWidget.deleteButton.clicked.connect(self.get_supplier_delete_lambda(rowIndex))

                self.tableWidget.setCellWidget(rowIndex, 10, buttonWidget)
        except Exception as e:
            print(f"Supplier Error executing query: {e}")

    def supplier_edit_row(self, rowIndex):
        print("edit clicked")
        buttonWidget = self.tableWidget.cellWidget(rowIndex, 10)
        if buttonWidget:
            buttonWidget.editButton.setVisible(False)
            buttonWidget.saveButton.setVisible(True)

        # Columns to be made editable (indices: contact_name, title, phone, address, city, province, email)
        editable_columns = [2, 3, 4, 5, 6, 7, 8]
        
        for col in editable_columns:
            item = self.tableWidget.item(rowIndex, col)
            if item:
                item.setFlags(item.flags() | Qt.ItemIsEditable)

    def supplier_save_row(self, rowIndex):
        buttonWidget = self.tableWidget.cellWidget(rowIndex, 10)
        if buttonWidget:
            buttonWidget.editButton.setVisible(True)
            buttonWidget.saveButton.setVisible(False)

        # Columns to be saved (indices: contact_name, title, phone, address, city, province, email)
        editable_columns = [2, 3, 4, 5, 6, 7, 8]
        updated_data = []
        
        for col in range(self.tableWidget.columnCount() - 1):  # Exclude the last column (Action buttons)
            item = self.tableWidget.item(rowIndex, col)
            if item:           
                if col in editable_columns:  # Make the specific columns non-editable again
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)              
                # Convert to lowercase if the column is editable and does not contain digits
                text = item.text()
                if col in editable_columns and not re.search(r'\d', text):
                    text = text.lower()
                updated_data.append(item.text())

        # Debug print statements to check the content of updated_data
        print(f"Updated Data: {updated_data}")

        if len(updated_data) < 10:  # Check if we have all the expected columns
            print("Error: Missing data columns")
            self.revert_changes_supplier(rowIndex)
            return
        
        # Check if any field is blank
        if any(not field.strip() for field in updated_data):
            QtWidgets.QMessageBox.warning(self, "Edit error", "All fields must be filled.")
            self.revert_changes_supplier(rowIndex)
            return

        supplier_id = updated_data[0]
        contact_name = updated_data[2]
        title = updated_data[3]
        phone = updated_data[4]
        address = updated_data[5]
        city = updated_data[6]
        province = updated_data[7]
        email = updated_data[8]

        # Regular expression to match both formats
        phone_pattern = r'^(09\d{9}|\+639\d{9})$'
        if not re.match(phone_pattern, phone):
            QtWidgets.QMessageBox.warning(self, "Invalid Phone Number", "Phone number must be either 11 digits starting with '09' or start with '+63' followed by 9 digits.")
            self.revert_changes_supplier(rowIndex)
            return

        # Regular expression to match a valid email address
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            QtWidgets.QMessageBox.warning(self, "Invalid Email Address", "Please enter a valid email address.")
            self.revert_changes_supplier(rowIndex)
            return

        # Validate that name and title do not contain numbers
        if re.search(r'\d', contact_name) or re.search(r'\d', title):
            QtWidgets.QMessageBox.warning(self, "Input Error", "Contact name and title should not contain numbers.")
            self.revert_changes_supplier(rowIndex)
            return

        try:
            # Update the contact information first
            self.cursor.execute("""
                UPDATE contact SET contact_name = %s, title = %s, phone = %s, email = %s
                WHERE contact_id = (
                    SELECT contact_id FROM supplier WHERE supplier_id = %s
                )
            """, (contact_name, title, phone, email, supplier_id))
            
            # Update the supplier information
            self.cursor.execute("""
                UPDATE supplier SET address = %s, city = %s, province = %s, product_type = %s
                WHERE supplier_id = %s
            """, (address, city, province, updated_data[9], supplier_id))
            
            self.connection.commit()
            QMessageBox.information(self, "Update Successful", "Supplier details updated successfully!")
            print("Update Successful!")
        except Exception as e:
            print(f"Supplier Error updating database: {e}")
            self.revert_changes_supplier(rowIndex)
            QtWidgets.QMessageBox.critical(self, "Database Error", f"An error occurred while updating the database: {e}")

    def revert_changes_supplier(self, rowIndex):
        try:
            supplier_id = self.tableWidget.item(rowIndex, 0).text()  # Get supplier_id
            self.cursor.execute("""
                SELECT s.supplier_id, s.company_name, c.contact_name, c.title, c.phone, s.address, s.city, s.province, c.email, s.product_type
                FROM supplier s
                JOIN contact c ON s.contact_id = c.contact_id
                WHERE s.supplier_id = %s
            """, (supplier_id,))
            supplier = self.cursor.fetchone()

            if supplier:
                for col in range(self.tableWidget.columnCount() - 1):  # Exclude the last column (Action buttons)
                    item = self.tableWidget.item(rowIndex, col)
                    if item:
                        # Convert company name and product type to title case
                        if col == 1:  # company_name column
                            item.setText(str(supplier[col]).title())
                        elif col == 9:  # product_type column
                            item.setText(str(supplier[col]).title())
                        else:
                            item.setText(str(supplier[col]))
                        # Ensure the specific columns are not editable
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                print("Changes reverted successfully")
            else:
                print("Supplier not found")
        except Exception as e:
            print(f"Supplier Error reverting changes: {e}")
            QtWidgets.QMessageBox.critical(self, "Database Error", f"An error occurred while reverting the data: {e}")

    def get_supplier_delete_lambda(self, rowIndex):
        return lambda: self.supplier_delete_row(rowIndex)

    def supplier_delete_row(self, rowIndex):
        supplier_id_item = self.tableWidget.item(rowIndex, 0)
        if supplier_id_item:
            supplier_id = supplier_id_item.text()
            try:
                # Get the contact_id associated with this supplier
                self.cursor.execute("SELECT contact_id FROM supplier WHERE supplier_id = %s", (supplier_id,))
                contact_id = self.cursor.fetchone()
                if not contact_id:
                    raise ValueError("Contact ID not found for the supplier.")
                
                contact_id = contact_id[0]

                # Delete the supplier
                self.cursor.execute("DELETE FROM supplier WHERE supplier_id = %s", (supplier_id,))

                # Delete the contact associated with this supplier
                self.cursor.execute("DELETE FROM contact WHERE contact_id = %s", (contact_id,))
                
                self.connection.commit()
                self.tableWidget.removeRow(rowIndex)
                QtWidgets.QMessageBox.information(self, "Supplier Deleted", f"Supplier with ID {supplier_id} has been deleted.")
            except Exception as e:
                print(f"Supplier Error deleting row: {e}")
                QtWidgets.QMessageBox.critical(self, "Database Error", f"An error occurred while deleting the supplier: {e}")

    def handle_supplierAdd(self):
        self.set_stacked_widget_index(10)
        self.setCurrentPage(10)
        self.supplierAddButton = self.findChild(QtWidgets.QPushButton, 'addSupplierButton')
        # Check if the signal is already connected
        if not hasattr(self, 'is_addsupplierButton_connected'):
            self.supplierAddButton.clicked.connect(self.supplierAdd)
            self.is_addsupplierButton_connected = True            
        
    def supplierAdd(self):
        self.connect_to_database()

        self.companyNameInput = self.findChild(QtWidgets.QLineEdit, 'companyName')
        self.contactNameInput = self.findChild(QtWidgets.QLineEdit, 'contactName')
        self.titleInput = self.findChild(QtWidgets.QLineEdit, 'title')
        self.phoneInput = self.findChild(QtWidgets.QLineEdit, 'phone')
        self.addressInput = self.findChild(QtWidgets.QLineEdit, 'address')
        self.cityInput = self.findChild(QtWidgets.QLineEdit, 'city')
        self.provinceInput = self.findChild(QtWidgets.QLineEdit, 'province')
        self.emailInput = self.findChild(QtWidgets.QLineEdit, 'email')
        self.productInput = self.findChild(QtWidgets.QComboBox, 'product')
        
        company = self.companyNameInput.text()
        company_name = company.lower()
        contact_name = self.contactNameInput.text().lower()
        title = self.titleInput.text().lower()
        phone = self.phoneInput.text()
        address = self.addressInput.text().lower()
        city = self.cityInput.text().lower()
        province = self.provinceInput.text().lower()
        email = self.emailInput.text().lower()
        product = self.productInput.currentText().lower()

        # All fields must be filled
        if not all([company_name, contact_name, title, phone, address, city, province, email, product]):
            QtWidgets.QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return      
        if any(char.isdigit() for char in contact_name):
            QtWidgets.QMessageBox.warning(self, "Input Error", "Invalid Contact Name. Name should not contain numbers.")
            return
        if any(char.isdigit() for char in title):
            QtWidgets.QMessageBox.warning(self, "Input Error", "Invalid Title Input. Title should not contain numbers.")
            return
        
        # Regular expression to match both formats
        phone_pattern = r'^(09\d{9}|\+639\d{9})$'
        if not re.match(phone_pattern, phone):
            QtWidgets.QMessageBox.warning(self, "Invalid Phone Number", "Phone number must be either 11 digits starting with '09' or start with '+63' followed by 9 digits.")
            return

        # Regular expression to match a valid email address
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            QtWidgets.QMessageBox.warning(self, "Invalid Email Address", "Please enter a valid email address.")
            return

        try:
            # Check if the company name already exists
            self.cursor.execute("SELECT 1 FROM supplier WHERE company_name = %s", (company_name,))
            if self.cursor.fetchone():
                QtWidgets.QMessageBox.warning(self, "Input Error", f"Company '{company}' already exists.")
                return

            # Check if the contact name already exists
            self.cursor.execute("SELECT contact_id FROM contact WHERE contact_name = %s", (contact_name,))
            contact_row = self.cursor.fetchone()
            if contact_row:
                # contact_id = contact_row[0]
                QtWidgets.QMessageBox.warning(self, "Input Error", f"Contact name '{contact_name}' already exists.")
                return
            else:
                # Insert new contact
                self.cursor.execute("""
                    INSERT INTO contact (contact_name, title, phone, email)
                    VALUES (%s, %s, %s, %s) RETURNING contact_id
                """, (contact_name, title, phone, email))
                contact_id = self.cursor.fetchone()[0]

            # Insert new supplier
            self.cursor.execute("""
                INSERT INTO supplier (company_name, address, city, province, product_type, contact_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (company_name, address, city, province, product, contact_id))
            self.connection.commit()
            print("Supplier added successfully!")
            QtWidgets.QMessageBox.information(self, "Successful", f"Supplier: {company} added successfully!")

            # Clear the input fields after successful addition
            self.companyNameInput.clear()
            self.contactNameInput.clear()
            self.titleInput.clear()
            self.phoneInput.clear()
            self.addressInput.clear()
            self.cityInput.clear()
            self.provinceInput.clear()
            self.emailInput.clear()
            self.handle_supplier()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Input Error", f"Failed adding Supplier: {e}")
            print(f"Error adding Supplier: {e}")

    ########################################  PURCHASE  ############################################    

    def handle_purchase(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'purchasingTableWidget')
        self.set_header_color()
        self.set_stacked_widget_index(11)
        self.setCurrentPage(11)
        self.update_purchase_table("All")  # Default to show all purchases
    
    def update_purchase_table(self, filter_category):
        self.connect_to_database()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'purchasingTableWidget')
        try:
            base_query = """
                SELECT b.purchase_date, b.purchase_id, p.product_name, p.product_type, p.product_size, b.purchase_quantity,
                    p.product_buyingprice, b.purchase_quantity * p.product_buyingprice AS total, s.company_name
                FROM PURCHASE b
                JOIN PRODUCT p ON b.product_id = p.product_id
                JOIN SUPPLIER s ON p.supplier_id = s.supplier_id
            """
            if filter_category == "Tire":
                query = base_query + " WHERE p.product_type = 'tire' ORDER BY b.purchase_id DESC"
                print("Tire category selected")
            elif filter_category == "Oil":
                query = base_query + " WHERE p.product_type = 'oil'  ORDER BY b.purchase_id DESC"
                print("Oil category selected")
            elif filter_category == "Battery":
                query = base_query + " WHERE p.product_type = 'battery' ORDER BY b.purchase_id DESC"
                print("Battery category selected")
            else:
                query = base_query + " ORDER BY b.purchase_id DESC"
            
            print(f"Executing query: {query}")  # Debug print
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            print(f"Fetched records: {records}")  # Debug print

            self.tableWidget.setRowCount(len(records))
            self.tableWidget.setColumnCount(10)
            headers = ["Date", "Purchase ID", "Product", "Type", "Size", "Quantity", "Buying Price", "Total", "Supplier", "Actions"]
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()

            total_spend = 0

            for rowIndex, rowData in enumerate(records):
                self.tableWidget.setRowHeight(rowIndex, 80)
                for colIndex, colData in enumerate(rowData):
                    if colIndex == 2:  # Product column
                        colData = colData.title()
                    elif colIndex == 3:  # Type column
                        colData = colData.title()
                    elif colIndex == 4:  # Size column
                        colData = colData.upper()
                    elif colIndex in [6, 7]:  # Format the price and total columns
                        colData = f"₱ {colData:,.2f}"
                    elif colIndex == 8:  # Supplier column (company name)
                        colData = colData.title()
                    
                    item = QTableWidgetItem(str(colData))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(rowIndex, colIndex, item)

                total_spend += rowData[7]  # Sum up the total spend

                # Add Action button
                buttonWidget = ButtonWidget()
                buttonWidget.editButton.setVisible(False)
                buttonWidget.addButton.setVisible(False)
                buttonWidget.deleteButton.clicked.connect(self.get_purchase_delete_lambda(rowIndex))
                self.tableWidget.setCellWidget(rowIndex, 9, buttonWidget)

            # Update total spend label
            self.totalSpendLabel = self.findChild(QtWidgets.QLabel, 'totalSpendLabel')
            print(f"Total Spend: {total_spend}")  # Debug print
            self.totalSpendLabel.setText(f"₱ {total_spend:,.2f}")

        except Exception as e:
            print(f"Purchase Error executing query: {e}")
    
    def confirm_delete_all_purchase(self):
        self.connect_to_database()
        # Check if there are any records in purchase table
        self.cursor.execute("SELECT COUNT(*) FROM purchase")
        count = self.cursor.fetchone()[0]

        if count == 0:
            QMessageBox.information(self, "Empty Purchase", "There are no purchase records to delete.")
        else:
            reply = QMessageBox.question(self, 'Confirm Deletion', 
                                        "Are you sure you want to delete all purchase records?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.delete_all_Purchase()

    def delete_all_Purchase(self):
        self.connect_to_database()
        try:
            self.cursor.execute("DELETE FROM purchase")
            self.connection.commit()
            QMessageBox.information(self, "Deletion Successful", "All purchase records have been deleted successfully!")
            self.handle_purchase()
        except Exception as e:
            print(f"Error deleting row: {e}")

    def get_purchase_delete_lambda(self, rowIndex):
        return lambda: self.purchase_delete_row(rowIndex)

    def purchase_delete_row(self, rowIndex):
        purchase_id_item = self.tableWidget.item(rowIndex, 1)
        if purchase_id_item:
            purchase_id = purchase_id_item.text()
            try:
                self.cursor.execute("DELETE FROM PURCHASE WHERE purchase_id = %s", (purchase_id,))
                self.connection.commit()
                self.tableWidget.removeRow(rowIndex)
                QMessageBox.information(self, "Purchase Deleted", f"Purchase with ID {purchase_id} has been deleted.")
            except Exception as e:
                print(f"Purchase Error deleting row: {e}")
                QtWidgets.QMessageBox.critical(self, "Database Error", f"An error occurred while deleting the purchase: {e}")

    # Functions to filter by different categories
    def purchase_filterByAll(self):
        self.update_purchase_table("All")

    def purchase_filterByTire(self):
        self.update_purchase_table("Tire")

    def purchase_filterByOil(self):
        self.update_purchase_table("Oil")

    def purchase_filterByBattery(self):
        self.update_purchase_table("Battery")

    def purchase_menu(self):
        menu = QMenu()
        actions = [
            ("All", self.purchase_filterByAll),
            ("Tire", self.purchase_filterByTire),
            ("Oil", self.purchase_filterByOil),
            ("Battery", self.purchase_filterByBattery)
        ]
        for text, func in actions:
            action = QAction(text, self)
            action.triggered.connect(func)
            menu.addAction(action)
        self.purchaseFilter.setMenu(menu)

    def handle_purchaseAdd(self):
        self.connect_to_database()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'addpurchaseTableWidget')
        headers = ["Product ID", "Product Name", "Product Type", "Product Size", "Buying Price", "Quantity", "Total", "Supplier", "Action"]
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.set_stacked_widget_index(12)
        self.setCurrentPage(12)
        self.purchasefindButton = self.findChild(QtWidgets.QPushButton, 'findproduct')
        self.purchasefindButton.clicked.connect(self.search_item_purchase)

        try:
            query = """
                SELECT p.product_id, p.product_name, p.product_type, p.product_size, p.product_buyingprice, s.company_name
                FROM product p
                JOIN supplier s ON p.supplier_id = s.supplier_id
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            # Set up the table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(headers))
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            for row_number, row_data in enumerate(results):
                self.tableWidget.setRowHeight(row_number, 50)
                for column_number, data in enumerate(row_data):
                    if column_number == 1:  # Product Name
                        data = data.title()
                    elif column_number == 2:  # Product Type
                        data = data.title()
                    elif column_number == 3:  # Product Size
                        data = data.upper()
                    elif column_number == 4:  # Product Price
                        data = f"₱ {data:,.2f}"
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(row_number, column_number, item)
                
                # Add Quantity and Total columns
                quantity_item = QtWidgets.QTableWidgetItem("1")  # Set default quantity to 1
                quantity_item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                quantity_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row_number, 5, quantity_item)
                
                price = float(self.tableWidget.item(row_number, 4).text().replace('₱ ', '').replace(',', ''))
                total = price * 1  # Quantity is set to 1
                total_item = QTableWidgetItem(f"₱ {total:,.2f}")
                total_item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                self.tableWidget.setItem(row_number, 6, total_item)


                supplier_id = str(row_data[5]).title()  # Convert to title case
                supplier_item = QTableWidgetItem(supplier_id)  
                supplier_item.setTextAlignment(Qt.AlignCenter)  
                supplier_item.setFlags(QtCore.Qt.ItemIsEnabled)  
                self.tableWidget.setItem(row_number, 7, supplier_item)  

                # Add Action button
                button_widget = ButtonWidget()                
                button_widget.editButton.setVisible(False)
                button_widget.deleteButton.setVisible(False)
                button_widget.addButton.clicked.connect(lambda _, r=row_number: self.add_to_purchase(r))
                self.tableWidget.setCellWidget(row_number, 8, button_widget)
            
            # Connect itemChanged signal to update_total function
            self.tableWidget.itemChanged.connect(self.update_total_purchase)
            
        except Exception as e:
            print(f"Search Item Purchase Error executing query: {e}")

    def search_item_purchase(self):
        self.connect_to_database()
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'addpurchaseTableWidget')
        self.searchproduct = self.findChild(QtWidgets.QLineEdit, 'searchproduct')
        product = self.searchproduct.text()
        searchproduct = product.lower()
        
        try:
            query = """
            SELECT p.product_id, p.product_name, p.product_type, p.product_size, p.product_buyingprice, s.company_name
            FROM product p
            JOIN supplier s ON p.supplier_id = s.supplier_id
            WHERE p.product_name LIKE %s
            """
            self.cursor.execute(query, (f'%{searchproduct}%',))
            results = self.cursor.fetchall()

            # Check if results are empty
            if not results:
                QMessageBox.information(self, "Search Failed", f"Product {product} was not found.")
                return
            
            # Set up the table
            headers = ["Product ID", "Product Name", "Product Type", "Product Size", "Buying Price", "Quantity", "Total", "Supplier", "Action"]
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(headers))
            self.tableWidget.setHorizontalHeaderLabels(headers)
            self.set_header_color()
            
            for row_number, row_data in enumerate(results):
                self.tableWidget.setRowHeight(row_number, 50)
                for column_number, data in enumerate(row_data):
                    if column_number == 1:  # Product Name
                        data = data.title()
                    elif column_number == 2:  # Product Type
                        data = data.title()
                    elif column_number == 3:  # Product Size
                        data = data.upper()
                    elif column_number == 4:  # Product Price
                        data = f"₱ {data:,.2f}"
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make the item uneditable
                    self.tableWidget.setItem(row_number, column_number, item)
                
                # Add Quantity and Total columns
                quantity_item = QtWidgets.QTableWidgetItem("1")  # Set default quantity to 1
                quantity_item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                quantity_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row_number, 5, quantity_item)
                
                price = float(self.tableWidget.item(row_number, 4).text().replace('₱ ', '').replace(',', ''))
                total = price * 1  # Quantity is set to 1
                total_item = QTableWidgetItem(f"₱ {total:,.2f}")
                total_item.setTextAlignment(Qt.AlignCenter)  # Align the text to the center
                total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                self.tableWidget.setItem(row_number, 6, total_item)

                supplier_id = str(row_data[5]).title()  # Convert to title case
                supplier_item = QTableWidgetItem(supplier_id)  
                supplier_item.setTextAlignment(Qt.AlignCenter)  
                supplier_item.setFlags(QtCore.Qt.ItemIsEnabled)  
                self.tableWidget.setItem(row_number, 7, supplier_item) 

                # Add Action button
                button_widget = ButtonWidget()                
                button_widget.editButton.setVisible(False)
                button_widget.deleteButton.setVisible(False)
                button_widget.addButton.clicked.connect(lambda _, r=row_number: self.add_to_purchase(r))
                self.tableWidget.setCellWidget(row_number, 8, button_widget)
            
            # Connect itemChanged signal to update_total function
            self.tableWidget.itemChanged.connect(self.update_total_purchase)
            
        except Exception as e:
            print(f"Search Item Purchase Error executing query: {e}")

    def update_total_purchase(self, item):
        row = item.row()
        column = item.column()
        if column == 5:  # Quantity column
            try:
                price = float(self.tableWidget.item(row, 4).text().replace('₱ ', '').replace(',', ''))
                quantity_text = item.text()
                if quantity_text:
                    quantity = int(quantity_text)
                    if quantity < 1:
                        QMessageBox.warning(self, "Invalid Quantity", "Negative or zero quantity is not allowed.")
                        item.setText("1")  # Reset to default quantity
                        total = price * 1
                    else:
                        total = price * quantity
                    total_item = QTableWidgetItem(f"₱ {total:,.2f}")
                    total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                    self.tableWidget.setItem(row, 6, total_item)
                else:
                    total_item = QTableWidgetItem("")
                    total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                    self.tableWidget.setItem(row, 6, total_item)
            except ValueError:
                total_item = QTableWidgetItem("")
                total_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make total uneditable
                self.tableWidget.setItem(row, 6, total_item)

    def add_to_purchase(self, row):
        try:
            product_id = self.tableWidget.item(row, 0).text()
            quantity_text = self.tableWidget.item(row, 5).text()

            if not all([product_id, quantity_text]):
                QtWidgets.QMessageBox.warning(self, "Input Error", "All fields must be filled.")
                return

            # Check if quantity_text is valid and can be converted to an integer
            if not quantity_text.isdigit():
                raise ValueError(f"Invalid quantity: {quantity_text}")
            quantity = int(quantity_text)
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            admin_query = """
                SELECT ADMIN_USERNAME FROM ADMIN
            """
            self.cursor.execute(admin_query)
            admin_username = self.cursor.fetchall()[0]

            # Insert into purchase table with username
            query = """
                INSERT INTO purchase (product_id, purchase_quantity, purchase_date, admin_username)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (product_id, quantity, current_date, admin_username))
            self.connection.commit()

            # Update product quantity
            update_query = """
                UPDATE product SET product_stock = product_stock + %s 
                WHERE product_id = %s
            """
            self.cursor.execute(update_query, (quantity, product_id))
            self.connection.commit()

            # Remove the row from the table widget
            self.tableWidget.removeRow(row)
            self.searchproduct.clear()
            QtWidgets.QMessageBox.information(self, "Successful", "Purchase added successfully!")
            self.handle_purchase()

        except ValueError as ve:
            print(f"Purchase Value error: {ve}")
            QtWidgets.QMessageBox.warning(self, "Warning", f"Value error:' {ve} ', Input must be an Integer")
        except Exception as e:
            print(f"Error processing purchase: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error processing purchase: {e}")


    def handle_account(self):
        self.set_stacked_widget_index(13)
        self.setCurrentPage(13)
        self.connect_to_database()

        try:
            query = "SELECT ADMIN_USERNAME, ADMIN_NAME FROM ADMIN"
            self.cursor.execute(query)
            admin_data = self.cursor.fetchone()

            if admin_data:
                admin_username, admin_name = admin_data
                self.nameLabel.setText(admin_name.title())
                self.usernameLabel.setText(admin_username.title())
            else:
                print("No admin data found")
        except Exception as e:
            print(f"Error fetching admin data: {e}")

    def handle_accountUpdate(self):
        self.set_stacked_widget_index(14)
        self.setCurrentPage(14)

    def accountUpdate(self):
        self.connect_to_database()
        try:
            new_admin_username = self.usernameLineEdit.text()
            new_admin_name = self.nameLineEdit.text()

            admin_username = new_admin_username.lower()
            admin_name = new_admin_name.lower()
            if not all([new_admin_username,new_admin_name]):
                QMessageBox.information(self, "Input Error", "Please fill all the fields")
                return

            query = """
                UPDATE ADMIN SET
                ADMIN_USERNAME = %s,
                ADMIN_NAME = %s
            """
            self.cursor.execute(query, (admin_username, admin_name))
            self.connection.commit()
            QMessageBox.information(self, "Success", "Username and name updated successfully!")
            self.usernameLineEdit.clear()
            self.nameLineEdit.clear()
            self.handle_account()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Update Failed: {e}")


    def handle_accountChangepass(self):
        self.set_stacked_widget_index(15)
        self.setCurrentPage(15)
        
    
    def accountChangepass(self):
        self.connect_to_database()
        try:
            # Get the new password and confirmation password from the input fields
            new_admin_password = self.passwordLineEdit.text()
            confirm_password = self.confirmLineEdit.text()

            # Check if the new password and confirm password fields are not empty
            if new_admin_password and confirm_password:
                # Check if the new password matches the confirmation password
                if new_admin_password == confirm_password:
                    # SQL query to update the admin's password
                    query = """
                        UPDATE ADMIN SET
                        ADMIN_PASSWORD = %s
                    """
                    # Execute the update query with the new password
                    self.cursor.execute(query, (new_admin_password,))
                    # Commit the transaction
                    self.connection.commit()
                    if self.cursor.rowcount > 0:                       
                        QMessageBox.information(self, "Successful", "Password updated successfully!")
                        self.passwordLineEdit.clear()
                        self.confirmLineEdit.clear()
                        self.goBack()
                    else:
                        QMessageBox.warning(self, "Warning", "No changes made. Please check your input.")
                else:
                    QMessageBox.warning(self, "Warning", "Password doesn't match")
            else:
                QMessageBox.warning(self, "Warning", "Please input both new password and confirm password.")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error updating database: {e}")
    
    def goBack(self):
        if len(self.pageHistory) > 1:  
            self.pageHistory.pop()  
            previousIndex = self.pageHistory[-1]  
            self.stackedWidget.setCurrentIndex(previousIndex)
    
    def setCurrentPage(self, index):
        current_index = self.stackedWidget.currentIndex()
        self.pageHistory.append(current_index)  
        self.stackedWidget.setCurrentIndex(index)  

# Login UI class
class LoginUI(QMainWindow):
    def __init__(self):
        super(LoginUI, self).__init__()
        uic.loadUi("venv\\Login.ui", self)
        self.connect_to_database()  # Connect to the database
        self.usernameEdit = self.findChild(QLineEdit, 'usernameEdit')
        self.passwordEdit = self.findChild(QLineEdit, 'passwordEdit')
        self.loginButton = self.findChild(QtWidgets.QPushButton, 'loginButton')
        self.loginButton.clicked.connect(self.login)

        self.forgotButton = self.findChild(QtWidgets.QPushButton, 'forgotButton')
        self.forgotButton.clicked.connect(self.show_forgotpass)
        
        self.forgotpassUI = ForgotPasswordUi(self)
        self.forgotpassUI.hide()

    def connect_to_database(self):
        # Database connection method
        try:
            self.connection = psycopg2.connect(
                dbname="Saku",
                user="postgres",
                password="francis0001",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            self.connection.commit()
            print("Database connection successful")
        except Exception as e:
            print(f"Error connecting to database: {e}")

    # Login Verification
    def login(self):
        username = self.usernameEdit.text().lower()
        password = self.passwordEdit.text()
        try:
            # Query to fetch the user data from the database
            query = "SELECT ADMIN_PASSWORD FROM ADMIN WHERE ADMIN_USERNAME = %s"
            self.cursor.execute(query, (username,))
            result = self.cursor.fetchone()

            if result:
                stored_password = result[0]
                if password == stored_password:
                    self.messageBox = self.display_message("Logged in Successfully!", QMessageBox.Information)
                    self.admin_ui = AdminUI()  # Pass the username to AdminUI
                    self.setCentralWidget(self.admin_ui)  # Set AdminUI as the central widget
                    self.admin_ui.handle_dashboard()  # Call handle_dashboard method to load the data  
                else:
                    self.show_invalid_credentials()
            else:
                self.show_invalid_credentials()
        except Exception as e:
            print(f"Error querying the database: {e}")
            self.show_invalid_credentials()
    
    def show_invalid_credentials(self):
        self.loginLabel2.setText('"Invalid username or password"')
        self.loginLabel2.setStyleSheet("color: red; font-style: italic; border:none;")
    
    def show_forgotpass(self):
        self.forgotpassUI.move(
            (self.width() - self.forgotpassUI.width()) // 2,
            (self.height() - self.forgotpassUI.height()) // 2
        )
        self.forgotpassUI.show()
    
    # Dialog
    def display_message(self, text, icon):
        msg = QMessageBox()
        msg.setText(text)
        msg.setIcon(icon)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Custom style
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ADB5BD;
                border: 1px solid black;
                border-radius: 10px;
            }
            QLabel {
                color: black;
                font-family: 'Segoe UI Light';
                font-size: 12pt;
            }
        """)
        msg.setStandardButtons(QMessageBox.NoButton)
        msg.show()
        # Automatically close the message box after 1000 milliseconds (1 second)
        QTimer.singleShot(900, msg.deleteLater)
        return msg  

class ForgotPasswordUi(QFrame):
    def __init__(self, parent):
        super(ForgotPasswordUi, self).__init__(parent)
        uic.loadUi('venv\\ForgotPassword.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.connect_to_database()
        self.confirmButton = self.findChild(QtWidgets.QPushButton, 'confirmButton')
        self.confirmButton.clicked.connect(self.accountRecover)
        self.backButton = self.findChild(QtWidgets.QPushButton, 'backButton')
        self.backButton.clicked.connect(self.back)

    def connect_to_database(self):
        # Database connection method
        try:
            self.connection = psycopg2.connect(
                dbname="Saku",
                user="postgres",
                password="francis0001",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            self.connection.commit()
            print("Database connection successful")
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def accountRecover(self):
        self.connect_to_database()
        self.username = self.findChild(QLineEdit, 'usernameEdit')
        self.newpassword = self.findChild(QLineEdit, 'newpasswordEdit')
        self.confirmpassword = self.findChild(QLineEdit, 'confirmpasswordEdit')

        username = self.username.text().lower()
        newpassword = self.newpassword.text()
        confirmpassword = self.confirmpassword.text()

        try:
            # Check if the username exists in the database
            query = "SELECT 1 FROM ADMIN WHERE ADMIN_USERNAME = %s"
            self.cursor.execute(query, (username,))
            result = self.cursor.fetchone()

            if result:
                if newpassword == confirmpassword:
                    try:
                        update_query = """
                            UPDATE ADMIN SET
                            ADMIN_PASSWORD = %s
                            WHERE ADMIN_USERNAME = %s
                        """
                        # Execute the update query with the new password
                        self.cursor.execute(update_query, (newpassword, username))
                        self.connection.commit()
                        QMessageBox.information(self, "Success", "New Password updated successfully!")
                        self.back()
                    except Exception as e:
                        print(f"Error updating the password: {e}")
                        self.show_warning_message("An error occurred while updating the password.")
                else:
                    self.show_warning_message("Passwords do not match.")
            else:
                self.show_warning_message("Username does not exist.")
        except Exception as e:
            print(f"Error querying the database: {e}")
            self.show_warning_message("An error occurred while verifying the username.")

    def show_warning_message(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.handle_warning_message)
        msg.show()

    def handle_warning_message(self):
        self.show()

    def back(self):
        self.hide()

#Main Class
class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setup_main_window()
        self.show_login_ui()
    
    def setup_main_window(self):
        self.setFixedSize(1200, 730)
        #tracks the height and width of desktop screen
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        # Move the main window to the center of the screen
        self.move(center_x, center_y)
        self.setWindowTitle("Saku Automotive Batteries Trading Shop")
        icon = QIcon("venv\\Images\\SakuLogo.png")  
        self.setWindowIcon(icon)

    def show_login_ui(self):
        self.setCentralWidget(LoginUI())
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())