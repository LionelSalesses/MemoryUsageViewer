from PyQt5.QtWidgets import QApplication
from MemoryUsageViewer import MemoryUsageViewer


if __name__ == "__main__":
    app = QApplication([])
    w = MemoryUsageViewer(app)
    w.show()
    app.exec_()

