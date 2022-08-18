from PyQt5.QtWidgets import QTableWidget, QMenu, QAbstractItemView, QAbstractScrollArea, QSizePolicy
from PyQt5.QtCore import Qt


class TableWidget(QTableWidget):
    def __init__(self, app, parent):
        super().__init__(parent)
        self.app = app
        # Configure table widget
        self.verticalHeader().setVisible(False)                 # Disable vertical header
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Disable cell editing
        # Size policy
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.handleContextMenu)
    
    def handleContextMenu(self, pos):
        # Create context menu on fly. We need to do this way because the 'Copy' action must know the
        # clicked cell.
        menu = QMenu(self)
        menu.addAction("Copy")
        menu.exec_(self.mapToGlobal(pos))
        
        # Get clicked cell content
        row = self.rowAt(pos.y())
        col = self.columnAt(pos.x())
        cell = self.item(row, col)
        cellText = cell.text()
                
        clipBoard = self.app.clipboard().setText(cellText)
        print("Copied '" + cellText + "' to clipboard")
