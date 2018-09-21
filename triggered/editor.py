import sys

from PyQt5.QtWidgets import *

class LevelView(QGraphicsView):

    def __init__(self, scene, parent):
        super(LevelView, self).__init__(parent)

        self.setObjectName("View")
        self.setScene(scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)

class EditorWindow(QMainWindow):

    def __init__(self):
        super(EditorWindow, self).__init__()
        self.setWindowTitle("Level Editor")
        self.initUi()

    def initUi(self):
        self.setMinimumSize(400, 400)

        # -- central widget
        self.centralWidget = QFrame()
        self.centralWidget.setObjectName("Central")
        self.setCentralWidget(self.centralWidget)

        # -- layout
        self.centralLayout = QHBoxLayout(self.centralWidget)

        # -- Graphics View
        self.scene = QGraphicsScene()
        self.scene.setObjectName("Scene")
        self.scene.setSceneRect(0, 0, 1000, 1000)

        self.view = LevelView(self.scene, self)
        self.centralLayout.addWidget(self.view)

        # Color.
        self.initColor()

    def initColor(self):
        windowCss = '''
        QFrame {
            background-color: rgb(90,90,90);
            border: 1px solid rgb(90,70,30);
        }'''
        self.setStyleSheet(windowCss)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = EditorWindow()
    win.show()

    sys.exit(app.exec_())
