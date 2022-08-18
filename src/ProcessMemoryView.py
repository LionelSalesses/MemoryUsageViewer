from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ProcessMemoryWidget import ProcessMemoryWidget
from TotalMemoryWidget import TotalMemoryWidget


class ProcessMemoryView(QWidget):
    def __init__(self, smemProxy, app, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.processMemoryWidget = ProcessMemoryWidget(app, smemProxy, self)
        self.totalMemoryWidget = TotalMemoryWidget(app, self)
        self.layout.addWidget(self.processMemoryWidget)
        self.layout.addWidget(self.totalMemoryWidget)

    
    def refresh(self, smemData, humanReadable, fullCommandLine):
        self.processMemoryWidget.refresh(smemData, humanReadable, fullCommandLine)
        self.totalMemoryWidget.refresh(smemData, humanReadable)
        self.updateTotalMemWidgetSize()
    
    def updateTotalMemWidgetSize(self):
        # Get process memory widget columns size
        columnSizes = [
            self.processMemoryWidget.horizontalHeader().sectionSize(c)
            for c in range(self.processMemoryWidget.horizontalHeader().count())
        ]
        if len(columnSizes):  # Before smem data loading the process memory widget is empty
            self.totalMemoryWidget.updateSize(columnSizes)
    
    def resizeEvent(self, event):
        self.updateTotalMemWidgetSize()
