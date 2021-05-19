"""
Main function to run the program.
"""
import sys

from PyQt5.QtWidgets import QApplication

from userInterface import MainWindow

app = QApplication(sys.argv) #Creates an app

#--Makes and shows an main window.
widget = MainWindow(app)
widget.show()

#Starts the code
sys.exit(app.exec_())
