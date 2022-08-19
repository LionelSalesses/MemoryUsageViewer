from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from TableWidget import TableWidget
from Tools import formatNumberToHumanReadable


class TotalMemoryWidget(TableWidget):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        
        self.countedQuantities = ['RSS', 'PSS', 'USS']
        # Disable horizontal header
        self.horizontalHeader().setVisible(False)
        # Disable scroll bar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def countTotalMemory(self, smemData):
        data, headers = smemData
        totals = [0]*len(self.countedQuantities)
        for i, c in enumerate([headers.index(q) for q in self.countedQuantities]):
            for p in range(len(data)):
                totals[i] += data[p][c]
        return totals
    
    def updateSize(self, columnSizes):
        # Adjust column width to match process memory widget columns
        self.setColumnWidth(0, columnSizes[0]+columnSizes[1])  # Cmd line + pid columns
        self.setColumnWidth(1, columnSizes[2])  # RSS
        self.setColumnWidth(2, columnSizes[3])  # PSS
        self.setColumnWidth(3, columnSizes[4])  # USS
        
        self.setMaximumWidth(self.horizontalHeader().length())
        self.setMaximumHeight(self.verticalHeader().length())
    
    def refresh(self, smemData, humanReadable):
        _, headers = smemData
        totals = self.countTotalMemory(smemData)
        self.clearContents()
        
        # Resize the table
        self.setRowCount(1)
        self.setColumnCount(len(self.countedQuantities)+1)
        
        rowData = ["Total", *totals]
        # Populate
        for col, value in enumerate(rowData):
            tableItem = QTableWidgetItem()
            tableItem.setData(Qt.EditRole, value)
            tableItem.setData(Qt.ToolTipRole, value)
            if col >= 1 and humanReadable:
                tableItem.setData(Qt.DisplayRole, formatNumberToHumanReadable(value))
            self.setItem(0, col, tableItem)

