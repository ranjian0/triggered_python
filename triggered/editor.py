import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

class EditorWindow(QMainWindow):

    def __init__(self):
        super(EditorWindow, self).__init__()
        self.setWindowTitle("Level Editor")
        self.initUi()

    def initUi(self):
        self.setMinimumSize(400, 400)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = EditorWindow()
    win.show()

    sys.exit(app.exec_())
