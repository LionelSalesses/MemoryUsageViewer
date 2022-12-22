from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from TableWidget import TableWidget
from Tools import formatNumberToHumanReadable, getCommandName


class MemoryAmountWidgetItem(QTableWidgetItem):
    def __init__(self, value: int, humanReadable : bool):
        super().__init__()
        self.value = value
        self.humanReadable = humanReadable
        self.setData(Qt.ToolTipRole, value)
        if self.humanReadable:
            self.setData(Qt.DisplayRole, formatNumberToHumanReadable(value))
        else:
            self.setData(Qt.DisplayRole, value)
        self.setData(Qt.UserRole, value)

    def __lt__(self, other: QTableWidgetItem):
        value = other.data(Qt.UserRole)
        return self.value < value


class ProcessMemoryWidget(TableWidget):
    def __init__(self, app, smemProxy, parent):
        super().__init__(app, parent)
        self.smemProxy = smemProxy
        self.headerToolTips = {
            'RSS': 
                'RSS is Resident Set Size. It counts the total amount of memory occupied by this process, ' 
                'including private and shared portions.', 
            'PSS':
                'PSS is the Propotional Set Size. It counts the memory privately allocated for this '
                'process plus the proportion of shared memory with one or more other processes', 
            'USS':
                'USS is the Unique Set Size. It counts only the memory privately allocated for this '
                'process. Memory occupied by shared libraries is not counted.'
        }
    
    def setupHeaderTooltips(self):
        if self.columnCount() > 0:
            for c in range(self.columnCount()):
                headerItem = self.horizontalHeaderItem(c)
                assert headerItem is not None
                if headerItem.text() in self.headerToolTips:
                    headerItem.setToolTip(self.headerToolTips[headerItem.text()])

    def refresh(self, smemData, humanReadable, fullCommandLine):
        self.clearContents()
        self.setSortingEnabled(False)  # Disable sorting before setting data
        
        data, headers = smemData
        # Resize the table
        self.setRowCount(len(data))
        self.setColumnCount(len(headers))
        
        # Add header
        self.setHorizontalHeaderLabels(headers)
        self.setupHeaderTooltips()
        # Adjust column size. First column is stretched, other columns are resized to content
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for c in range(len(headers)-1):
            self.horizontalHeader().setSectionResizeMode(c+1, QHeaderView.ResizeToContents)
        
        # Populate
        for row, rowData in enumerate(data):
            for col, value in enumerate(rowData):
                if headers[col] in ['RSS', 'PSS', 'USS']:
                    tableItem = MemoryAmountWidgetItem(value, humanReadable)
                else:
                    tableItem = QTableWidgetItem()
                    tableItem.setData(Qt.ToolTipRole, value)
                    if headers[col] == 'Command line' and not fullCommandLine:
                        tableItem.setData(Qt.DisplayRole, getCommandName(value))
                    else:
                        tableItem.setData(Qt.DisplayRole, value)
                self.setItem(row, col, tableItem)
        
        # Resize to content. Hiding is necessary to get it work. See:
        # https://stackoverflow.com/questions/3433664/how-to-make-sure-columns-in-qtableview-are-resized-to-the-maximum
        self.setVisible(False)
        self.resizeColumnsToContents() # Recompute columns size
        self.setSortingEnabled(True)   # Re-enable sorting
        self.setVisible(True)

