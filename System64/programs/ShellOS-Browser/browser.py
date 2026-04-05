import sys
import os
import re
import json
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolButton, QWidget, QVBoxLayout,
    QHBoxLayout, QMessageBox, QTabWidget, QSizePolicy, QDialog,
    QTableWidget, QTableWidgetItem, QProgressBar, QPushButton, QLabel,
    QHeaderView, QAbstractItemView, QMenu, QAction, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineDownloadItem
from PyQt5.QtGui import QDesktopServices, QIcon

APP_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(APP_SCRIPT_DIR)))

DEFAULT_DOWNLOAD_DIR = os.path.join(ROOT_DIR, "System64", "Documents", "Downloads")
DOWNLOADS_HISTORY_FILE = os.path.join(ROOT_DIR, "System64", "Documents", "downloads_history.json")

os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)

class DownloadsManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ShellOS Downloads")
        self.setGeometry(200, 200, 800, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinMaxButtonsHint)

        self.downloads = {} 
        self.history = self.load_downloads_history() 

        self.init_ui()
        self.load_history_into_table()
        self.apply_dark_stylesheet()

    def apply_dark_stylesheet(self):
        """Applies a dark stylesheet to the DownloadsManager window and its widgets."""
        self.setStyleSheet("""
            DownloadsManager {
                background-color: #212121;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                color: #e0e0e0; /* Default text color for the window */
            }
            QTableWidget {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                gridline-color: #3a3a3a;
                selection-background-color: #6272a4;
                selection-color: #ffffff;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #383838;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #3a3a3a;
                border-bottom: 2px solid #6272a4;
                font-weight: bold;
            }
            QProgressBar {
                text-align: center;
                color: #ffffff;
                background-color: #383838;
                border: 1px solid #555;
                border-radius: 7px;
            }
            QProgressBar::chunk {
                background-color: #6272a4;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #6272a4;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["File Name", "Status", "Progress", "Size", "Location", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) 
        self.table.setSelectionMode(QAbstractItemView.SingleSelection) 

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        main_layout.addWidget(self.table)

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if item:
            row = item.row()
            file_path_item = self.table.item(row, 4) 
            if file_path_item:
                file_path = file_path_item.text()
                menu = QMenu(self)

                open_action = QAction("Open File", self)
                open_action.triggered.connect(lambda: self.open_file_from_history(file_path))
                menu.addAction(open_action)

                open_folder_action = QAction("Open Containing Folder", self)
                open_folder_action.triggered.connect(lambda: self.open_folder_from_history(file_path))
                menu.addAction(open_folder_action)

                status_item = self.table.item(row, 1)
                is_active_download = False
                for dl_info in self.downloads.values():
                    if dl_info['row'] == row:
                        is_active_download = True
                        break

                if status_item and status_item.text() in ['Completed', 'Canceled', 'Failed'] and not is_active_download:
                    clear_action = QAction("Clear from History", self)
                    clear_action.triggered.connect(lambda: self.clear_item_from_history(row))
                    menu.addAction(clear_action)

                menu.exec_(self.table.mapToGlobal(pos))

    def clear_item_from_history(self, row_index):
        """Removes a download item from the history and table."""
        if 0 <= row_index < self.table.rowCount():
            file_path = self.table.item(row_index, 4).text() 
            item_removed = False
            for i, entry in enumerate(list(self.history)): 
                if entry.get('path') == file_path:
                    removed_entry = self.history.pop(i)
                    item_removed = True
                    QMessageBox.information(self, "History Cleared", f"'{os.path.basename(removed_entry.get('path', ''))}' removed from history.", parent=self)
                    break
            
            if item_removed:
                self.load_history_into_table()
                for dl_id, dl_info in self.downloads.copy().items(): 
                    self.add_download(dl_info['item'])
                self.save_downloads_history()
            else:
                QMessageBox.warning(self, "Error", "Could not find item in history or it's an active download.", parent=self)

    def load_downloads_history(self):
        if os.path.exists(DOWNLOADS_HISTORY_FILE):
            try:
                with open(DOWNLOADS_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error decoding downloads history file. Starting fresh.")
                return []
        return []

    def save_downloads_history(self):
        history_to_save = [
            item for item in self.history
            if item.get('state') in ['Completed', 'Canceled', 'Failed', 'Interrupted']
        ]
        try:
            with open(DOWNLOADS_HISTORY_FILE, 'w') as f:
                json.dump(history_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving downloads history: {e}")

    def load_history_into_table(self):
        self.table.setRowCount(0)
        for download_info in reversed(self.history):
            self.table.insertRow(0) 
            row_idx = 0 
            self.add_history_row(row_idx, download_info)

    def add_history_row(self, row_idx, download_info):
        file_name = os.path.basename(download_info.get('path', ''))
        status = download_info.get('state', 'Unknown')
        progress_text = ""
        size_text = self.format_bytes(download_info.get('total_bytes', 0))
        location = download_info.get('path', '')

        self.table.setItem(row_idx, 0, QTableWidgetItem(file_name))
        self.table.setItem(row_idx, 1, QTableWidgetItem(status))
        self.table.setItem(row_idx, 2, QTableWidgetItem(progress_text))
        self.table.setItem(row_idx, 3, QTableWidgetItem(size_text))
        self.table.setItem(row_idx, 4, QTableWidgetItem(location))

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setAlignment(Qt.AlignCenter)

        if status == 'Completed':
            open_file_btn = QPushButton("Open")
            open_file_btn.clicked.connect(lambda _, p=location: self.open_file_from_history(p))
            actions_layout.addWidget(open_file_btn)

            open_folder_btn = QPushButton("Folder")
            open_folder_btn.clicked.connect(lambda _, p=location: self.open_folder_from_history(p))
            actions_layout.addWidget(open_folder_btn)
        elif status in ['Canceled', 'Failed', 'Interrupted']:
            pass 

        self.table.setCellWidget(row_idx, 5, actions_widget)

    def add_download(self, download: QWebEngineDownloadItem):
        if download.id() in self.downloads:
            return

        history_entry_index = -1
        for i, entry in enumerate(self.history):
            if entry.get('path') == download.path() and entry.get('url') == download.url().toString():
                history_entry_index = i
                break

        if history_entry_index != -1:
            updated_entry = self.history.pop(history_entry_index)
            updated_entry['state'] = 'InProgress'
            self.history.insert(0, updated_entry)
        else:
            self.history.insert(0, {
                'id': download.id(),
                'path': download.path(),
                'total_bytes': download.totalBytes(),
                'state': 'InProgress',
                'url': download.url().toString()
            })
        
        self.load_history_into_table()

        current_row = 0
        self.downloads[download.id()] = {'item': download, 'row': current_row}

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        self.table.setCellWidget(current_row, 2, progress_bar)
        self.downloads[download.id()]['progress_bar'] = progress_bar

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setAlignment(Qt.AlignCenter)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(lambda: download.cancel())
        actions_layout.addWidget(cancel_btn)
        self.downloads[download.id()]['cancel_button'] = cancel_btn

        self.table.setCellWidget(current_row, 5, actions_widget)

        download.stateChanged.connect(lambda state: self.update_download_status(download, state))
        download.downloadProgress.connect(lambda received, total: self.update_download_progress(download, received, total))

        self.update_download_status(download, download.state())
        self.update_download_progress(download, download.receivedBytes(), download.totalBytes())


    def update_download_status(self, download: QWebEngineDownloadItem, state):
        row_info = self.downloads.get(download.id())
        if not row_info:
            return

        row_idx = row_info['row']
        status_item = self.table.item(row_idx, 1)
        progress_bar = row_info['progress_bar']
        cancel_btn = row_info.get('cancel_button')

        history_entry = next((item for item in self.history if item.get('id') == download.id()), None)

        status_text = ""
        if state == QWebEngineDownloadItem.DownloadRequested:
            status_text = "Requested"
        elif state == QWebEngineDownloadItem.DownloadInProgress:
            status_text = "Downloading"
        elif state == QWebEngineDownloadItem.DownloadCompleted:
            status_text = "Completed"
            if cancel_btn:
                cancel_btn.hide() 
            actions_widget = self.table.cellWidget(row_idx, 5)
            if actions_widget:
                while actions_widget.layout().count():
                    child = actions_widget.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                layout = actions_widget.layout()
                open_file_btn = QPushButton("Open")
                open_file_btn.clicked.connect(lambda: self.open_file(download.path()))
                layout.addWidget(open_file_btn)
                open_folder_btn = QPushButton("Folder")
                open_folder_btn.clicked.connect(lambda: self.open_folder(download.path()))
                layout.addWidget(open_folder_btn)
            if download.id() in self.downloads:
                del self.downloads[download.id()]
        elif state == QWebEngineDownloadItem.DownloadCancelled:
            status_text = "Canceled"
            if cancel_btn:
                cancel_btn.hide()
            if download.id() in self.downloads:
                del self.downloads[download.id()]
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            status_text = "Failed"
            if cancel_btn:
                cancel_btn.hide()
            if download.id() in self.downloads:
                del self.downloads[download.id()]

        status_item.setText(status_text)
        if history_entry:
            history_entry['state'] = status_text
        self.save_downloads_history()


    def update_download_progress(self, download: QWebEngineDownloadItem, received_bytes: int, total_bytes: int):
        row_info = self.downloads.get(download.id())
        if not row_info:
            return

        row_idx = row_info['row']
        progress_bar = row_info['progress_bar']

        if total_bytes > 0:
            percentage = int((received_bytes / total_bytes) * 100)
            progress_bar.setValue(percentage)
            size_text = f"{self.format_bytes(received_bytes)} / {self.format_bytes(total_bytes)}"
            self.table.item(row_idx, 3).setText(size_text)
        else:
            progress_bar.setValue(0)
            size_text = f"{self.format_bytes(received_bytes)} / Unknown"
            self.table.item(row_idx, 3).setText(size_text)

    def format_bytes(self, bytes_val):
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.2f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

    def open_file(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "File Not Found", f"The file '{os.path.basename(path)}' could not be found.")

    def open_folder(self, path):
        if os.path.exists(path):
            folder_path = os.path.dirname(path)
            if os.path.exists(folder_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            else:
                QMessageBox.warning(self, "Folder Not Found", f"The folder '{folder_path}' could not be found.")
        else:
            QMessageBox.warning(self, "File Not Found", f"The file '{os.path.basename(path)}' does not exist. Cannot open containing folder.")

    def open_file_from_history(self, file_path):
        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            QMessageBox.warning(self, "File Not Found", f"The file '{os.path.basename(file_path)}' could not be found. It may have been moved or deleted.")

    def open_folder_from_history(self, file_path):
        folder_path = os.path.dirname(file_path)
        if os.path.exists(folder_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            QMessageBox.warning(self, "Folder Not Found", f"The folder containing '{os.path.basename(file_path)}' could not be found. It may have been moved or deleted.")


class ShellOSBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShellOS Internet")
        self.setGeometry(100, 100, 1200, 800) 

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0) 
        self.main_layout.setSpacing(0) 
        self.apply_stylesheet()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.home_url = QUrl.fromLocalFile(os.path.join(script_dir, "home.html"))

        self.nav_bar = QWidget()
        self.nav_bar_layout = QHBoxLayout(self.nav_bar)
        self.nav_bar_layout.setContentsMargins(10, 10, 10, 10) 
        self.nav_bar_layout.setSpacing(5)
        self.nav_bar.setObjectName("NavBar")

        self.back_btn = QToolButton()
        self.back_btn.setText("◀")
        self.back_btn.setToolTip("Go back")
        self.back_btn.clicked.connect(lambda: self.tabs.currentWidget().back() if self.tabs.currentWidget() else None)
        self.back_btn.setObjectName("NavButton")

        self.forward_btn = QToolButton()
        self.forward_btn.setText("▶")
        self.forward_btn.setToolTip("Go forward")
        self.forward_btn.clicked.connect(lambda: self.tabs.currentWidget().forward() if self.tabs.currentWidget() else None)
        self.forward_btn.setObjectName("NavButton")

        self.reload_btn = QToolButton()
        self.reload_btn.setText("↻")
        self.reload_btn.setToolTip("Reload page")
        self.reload_btn.clicked.connect(lambda: self.tabs.currentWidget().reload() if self.tabs.currentWidget() else None)
        self.reload_btn.setObjectName("NavButton")

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search on Google...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setObjectName("UrlBar")

        self.new_tab_btn = QToolButton()
        self.new_tab_btn.setText("+")
        self.new_tab_btn.setToolTip("Open new tab")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.new_tab_btn.setObjectName("NavButton")

        self.downloads_btn = QToolButton()
        self.downloads_btn.setText("⬇")
        self.downloads_btn.setToolTip("Open Downloads")
        self.downloads_btn.clicked.connect(self.open_downloads_manager)
        self.downloads_btn.setObjectName("NavButton")

        self.nav_bar_layout.addWidget(self.back_btn)
        self.nav_bar_layout.addWidget(self.forward_btn)
        self.nav_bar_layout.addWidget(self.reload_btn)
        self.nav_bar_layout.addWidget(self.url_bar)
        self.nav_bar_layout.addWidget(self.new_tab_btn)
        self.nav_bar_layout.addWidget(self.downloads_btn) 

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setObjectName("BrowserTabs")

        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.addWidget(self.tabs, 1)

        self.downloads_manager = DownloadsManager(self)
        QWebEngineProfile.defaultProfile().downloadRequested.connect(self.handle_download_requested)

        self.add_new_tab(initial_load=True)


    def apply_stylesheet(self):
        """Applies a dark, modern stylesheet to the browser."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        x_png_path = os.path.join(script_dir, "X.png").replace("\\", "/")

        stylesheet = f"""
            /* Universal reset for margins and padding, borders */
            * {{
                margin: 0px;
                padding: 0px;
                border-width: 0px;
                border-style: none; /* Explicitly set border-style to none */
            }}

            QMainWindow {{
                background-color: #212121;
                border: none;
                padding: 0;
                margin: 0;
            }}

            QWidget#central_widget {{
                    background-color: #212121;
                    border: none;
                    padding: 0;
                    margin: 0;
            }}

            QWidget#NavBar {{
                background-color: #2c2c2c;
                border-bottom: 1px solid #3a3a3a;
                border-radius: 15px;
                margin: 5px;
            }}

            QLineEdit#UrlBar {{
                background-color: #383838;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 12px;
                padding: 8px 15px;
                font-size: 14px;
                selection-background-color: #6272a4;
            }}
            QLineEdit#UrlBar:focus {{
                border: 1px solid #6272a4;
                outline: none;
            }}

            QToolButton#NavButton {{
                background-color: #4a4a4a;
                color: #e0e0e0;
                border: none;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
                font-weight: bold;
                transition: background-color 0.2s ease, color 0.2s ease;
            }}
            QToolButton#NavButton:hover {{
                background-color: #5a5a5a;
            }}
            QToolButton#NavButton:pressed {{
                background-color: #6272a4;
                color: #ffffff;
            }}

            QTabWidget#BrowserTabs {{
                border: none;
                padding: 0;
                margin: 0;
                /* Crucial: Ensure the content area of the tab widget also fills its space */
                QTabBar::pane {{ /* The tab bar's "pane" is the area below the tabs where content sits */
                    border: none;
                    margin: 0;
                    padding: 0;
                    background-color: #212121; /* Match main background */
                }}
            }}

            QTabWidget#BrowserTabs::tab-bar {{
                alignment: left;
                background-color: #2c2c2c;
                border-top: 1px solid #3a3a3a;
                margin-left: 5px;
                margin-right: 5px;
                margin-bottom: 0;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}

            QTabWidget#BrowserTabs QTabBar::tab {{
                background-color: #383838;
                color: #e0e0e0;
                padding: 8px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
                margin-right: 2px;
                border: 1px solid #4a4a4a;
                border-bottom: none;
            }}

            QTabWidget#BrowserTabs QTabBar::tab:hover {{
                background-color: #4a4a4a;
            }}

            QTabWidget#BrowserTabs QTabBar::tab:selected {{
                background-color: #212121;
                color: #8be9fd;
                border: 1px solid #6272a4;
                border-bottom: 2px solid #6272a4;
                margin-bottom: -1px;
            }}

            QTabWidget#BrowserTabs QTabBar::close-button {{
                image: url({x_png_path});
                subcontrol-origin: padding;
                subcontrol-position: center;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin-left: 5px;
                padding: 2px;
            }}
            QTabWidget#BrowserTabs QTabBar::close-button:hover {{
                background-color: #e0e0e0;
                image: url({x_png_path});
            }}
            QTabWidget#BrowserTabs QTabBar::close-button:pressed {{
                    background-color: #d0d0d0;
                    image: url({x_png_path});
            }}

            QTabWidget#BrowserTabs QStackedWidget {{
                background-color: #212121;
                border: none;
                padding: 0;
                margin: 0;
            }}

            QWebEngineView {{
                border: none;
                padding: 0;
                margin: 0;
                background-color: #212121;
            }}
        """
        self.central_widget.setObjectName("central_widget")
        self.setStyleSheet(stylesheet)

    def add_new_tab(self, qurl=None, label="New Tab", initial_load=False):
        """Adds a new tab to the browser."""
        browser = QWebEngineView()
        browser.setUrl(self.home_url if qurl is None else qurl)

        browser.urlChanged.connect(self.update_url_bar_for_current_tab)
        browser.loadFinished.connect(self.update_title_for_current_tab)

        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)

        if initial_load and not os.path.exists(self.home_url.toLocalFile()):
            QMessageBox.critical(self, "Error", "home.html not found! Please ensure 'home.html' is in the same directory as the script.")
            browser.setUrl(QUrl("https://www.google.com/search?q=ShellOS+Browser"))


    def close_tab(self, index):
        """Closes the tab at the given index. Prevents closing the last tab."""
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    def navigate_to_url(self):
        """Navigates to the URL entered in the URL bar, or performs a Google search."""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return

        current_browser = self.tabs.currentWidget()
        if not current_browser:
            return

        domain_pattern = re.compile(
            r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
        )

        final_url = ""
        if url_text.startswith("http://") or url_text.startswith("https://"):
            final_url = url_text
        elif domain_pattern.match(url_text):
            final_url = "https://" + url_text
        else:
            final_url = "https://www.google.com/search?q=" + QUrl.toPercentEncoding(url_text).data().decode()

        current_browser.setUrl(QUrl(final_url))
        self.url_bar.setText(final_url)

    def update_url_bar_for_current_tab(self, qurl):
        """Updates the URL bar with the current page's URL if it's the active tab.
            Clears the URL bar if on the home page.
        """
        if self.sender() == self.tabs.currentWidget():
            if qurl == self.home_url:
                self.url_bar.clear()
            else:
                self.url_bar.setText(qurl.toString())

    def update_title_for_current_tab(self):
        """Updates the window title and tab title for the current page."""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            new_title = current_browser.title()
            current_url = current_browser.url()

            if current_url == self.home_url:
                display_title = "New Tab"
            else:
                display_title = new_title if new_title else "Loading..."

            self.setWindowTitle(f"ShellOS Internet - {display_title}")
            self.tabs.setTabText(self.tabs.currentIndex(), display_title)

    def current_tab_changed(self, index):
        """Handles changes in the active tab."""
        if index >= 0:
            current_browser = self.tabs.widget(index)
            if current_browser:
                current_url = current_browser.url()
                if current_url == self.home_url:
                    self.url_bar.clear()
                else:
                    self.url_bar.setText(current_url.toString())
                self.update_title_for_current_tab()
            else:
                self.url_bar.clear()
                self.setWindowTitle("ShellOS Internet")
        else:
            self.url_bar.clear()
            self.setWindowTitle("ShellOS Internet")

    def handle_download_requested(self, download: QWebEngineDownloadItem):
        """
        Handles a download request by prompting the user for a save location
        and initiating the download.
        """
        initial_file_name = os.path.basename(download.path())
        suggested_path = os.path.join(DEFAULT_DOWNLOAD_DIR, initial_file_name)
        suggested_path = os.path.normpath(suggested_path)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            suggested_path,
            f"All Files (*);;{os.path.splitext(initial_file_name)[1].lstrip('.') if os.path.splitext(initial_file_name)[1] else '.*'} (*{os.path.splitext(initial_file_name)[1]})"
        )

        if file_path:
            abs_file_path = os.path.abspath(file_path)
            if not abs_file_path.startswith(ROOT_DIR):
                QMessageBox.warning(self, "Access Denied", "Cannot save files outside the ShellOS directory for security reasons. Please choose a location within 'ShellOS'.")
                download.cancel()
                return

            download.setPath(abs_file_path)
            download.accept() 
            self.downloads_manager.add_download(download)
            self.downloads_manager.show()
            self.downloads_manager.activateWindow() 
        else:
            download.cancel() 

    def open_downloads_manager(self):
        """Opens the downloads manager window."""
        self.downloads_manager.show()
        self.downloads_manager.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setStyle("Fusion") 
    browser = ShellOSBrowser()
    browser.show()
    sys.exit(app.exec_())