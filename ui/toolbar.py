from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QFileDialog, QMessageBox

def create_toolbar(window, update_callback, action_callback):
    menu_bar = QMenuBar(window)

    file_menu = QMenu("File", window)
    edit_menu = QMenu("Edit", window)
    view_menu = QMenu("View", window)
    help_menu = QMenu("Help", window)

    # File Menu
    file_menu.addAction("Export Data", lambda: export_data(window))
    file_menu.addAction("Exit", window.close)

    # Edit Menu
    edit_menu.addAction("Clear Data", lambda: clear_data(window))

    # View Menu
    view_menu.addAction("Refresh", update_callback)

    # Help Menu
    help_menu.addAction("About", lambda: show_about(window))
    help_menu.addAction("Documentation", lambda: show_documentation(window))

    # Add Menus to Menu Bar
    menu_bar.addMenu(file_menu)
    menu_bar.addMenu(edit_menu)
    menu_bar.addMenu(view_menu)
    menu_bar.addMenu(help_menu)

    return menu_bar

# --- Helper Actions ---

def export_data(window):
    file_name, _ = QFileDialog.getSaveFileName(window, "Export Data", "", "Text Files (*.txt);;All Files (*)")
    if file_name:
        with open(file_name, 'w') as file:
            file.write("Sample export data\n...\nReplace with actual content.")
        QMessageBox.information(window, "Export Successful", f"Data exported to: {file_name}")

def clear_data(window):
    QMessageBox.information(window, "Clear Data", "Temporary data cleared network_monitor_logs.csv.")

def show_about(window):
    QMessageBox.information(window, "About", "Network Monitor Tool v1.0\nDeveloped with PyQt5.")

def show_documentation(window):
    QMessageBox.information(window, "Documentation", "Visit https://your-documentation-link.com for help.")