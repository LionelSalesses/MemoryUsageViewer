from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QCheckBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from SmemProxy import SmemProxy
from OverlayWidget import OverlayWidget
from ProcessMemoryView import ProcessMemoryView
from Tools import getCommandName


class SmemProxyWorker(QObject):
    finished = pyqtSignal(list)
    
    def __init__(self, smemProxy):
        super().__init__()
        self.smemProxy = smemProxy

    def run(self):
        smemData = self.smemProxy.getData()
        self.finished.emit(list(smemData))


class MemoryUsageViewer(QMainWindow):
    AppName = "Memory usage viewer"
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.smemProxy = self.initSmemProxy()
        self.smemData = None
        self.filterText = ''
        
        # Options
        self.option_HumanReadableNumbers = True
        self.option_FullCommandLine = False
        
        self.initUI()
        self.resfreshProcessMemViewer()
    
    def initUI(self):
        self.setWindowTitle(self.AppName)
        self.centralWidget = QWidget(parent=self)
        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
        
        self.topBar = self.createTopBar(self.centralWidget)
        self.mainLayout.addWidget(self.topBar)
        
        self.processMemView = ProcessMemoryView(self.smemProxy, self.app, self.centralWidget)
        self.processMemView.setFocus()
        self.mainLayout.addWidget(self.processMemView)
        
        self.bottomBar = self.createBottomBar(self.centralWidget)
        self.mainLayout.addWidget(self.bottomBar)
        
        self.loadingOverlayWidget = OverlayWidget(parent=self.centralWidget)
        self.loadingOverlayWidget.hide()
        
        self.setCentralWidget(self.centralWidget)
        self.showMaximized()
    
    def showLoadingOverlay(self):
        assert not self.loadingOverlayWidget.isVisible()
        self.loadingOverlayWidget.move(0, 0)
        self.loadingOverlayWidget.resize(self.width(), self.height())
        self.loadingOverlayWidget.show()
    
    def hideLoadingOverlay(self):
        assert self.loadingOverlayWidget.isVisible()
        self.loadingOverlayWidget.hide()
    
    def resfreshProcessMemViewer(self):
        self.showLoadingOverlay()
        # Create worker
        smemProxyWorker = SmemProxyWorker(self.smemProxy)
        
        # Create worker thread
        smemWorkerThread = QThread()
        smemProxyWorker.moveToThread(smemWorkerThread)
        self.smemLoader = (smemProxyWorker, smemWorkerThread)
        
        smemWorkerThread.started.connect(smemProxyWorker.run)
        smemWorkerThread.finished.connect(smemWorkerThread.deleteLater)
        smemProxyWorker.finished.connect(smemProxyWorker.deleteLater)
        smemProxyWorker.finished.connect(smemWorkerThread.quit)
        smemProxyWorker.finished.connect(self.finalizeSmemDataLoading)
        
        # Start
        smemWorkerThread.start()
    
    def applyProcessFilter(self, smemData, fullCommandLine):
        if len(self.filterText) > 0:
            if not fullCommandLine:
                formatCmdLine = getCommandName
            else:
                formatCmdLine = lambda x:x
            data, headers = smemData
            filteredData = [
                row for row in data if self.filterText in formatCmdLine(row[0])
            ]
            return filteredData, headers
        return smemData
    
    def refreshProcessMemView(self):
        # Filter processes
        filteredSmemData = self.applyProcessFilter(self.smemData, self.option_FullCommandLine)
        self.processMemView.refresh(
            filteredSmemData,
            self.option_HumanReadableNumbers,
            self.option_FullCommandLine
        )
    
    def finalizeSmemDataLoading(self, smemData):
        # Save smem data
        self.smemData = smemData
        # Refresh view with loaded data
        self.refreshProcessMemView()
        # Hide loading overlay
        self.loadingOverlayWidget.hide()
    
    def resizeEvent(self, event):
        if self.loadingOverlayWidget.isVisible():
            self.loadingOverlayWidget.move(0, 0)
            self.loadingOverlayWidget.resize(self.width(), self.height())
    
    def createTopBar(self, parent):
        self.topBarWidget = QWidget(parent)
        self.topBarLayout = QHBoxLayout()
        self.topBarWidget.setLayout(self.topBarLayout)
        
        # Refresh button
        self.refreshButton = QPushButton(self.topBarWidget)
        self.topBarLayout.addWidget(self.refreshButton)
        self.refreshButton.setText('Refresh')
        #self.refreshButton.setIcon()  # TODO refresh icon
        self.refreshButton.clicked.connect(self.resfreshProcessMemViewer)
        
        # Filter text
        self.filterTextWidget = QLineEdit(self.topBarWidget)
        self.filterTextWidget.setPlaceholderText('Enter filter text')
        self.filterTextWidget.returnPressed.connect(self.onFilterClick)
        self.topBarLayout.addWidget(self.filterTextWidget)
        
        # Filter button
        self.filterButton = QPushButton(self.topBarWidget)
        self.topBarLayout.addWidget(self.filterButton)
        self.filterButton.setText('Filter')
        self.filterButton.clicked.connect(self.onFilterClick)
        
        return self.topBarWidget
    
    def onFilterClick(self):
        self.filterText = self.filterTextWidget.text()
        # Refresh process memory view without reload smem data
        self.refreshProcessMemView()
        
    def onHumanReadableCheckboxClick(self):
        self.option_HumanReadableNumbers = self.humandReadableNumCheckBox.isChecked()
        # Refresh process memory view without reload smem data
        self.refreshProcessMemView()
        
    def onFullCmdLineCheckboxClick(self):
        self.option_FullCommandLine = self.fullCmdLineCheckBox.isChecked()
        # Refresh process memory view without reload smem data
        self.refreshProcessMemView()
    
    def createBottomBar(self, parent):
        self.bottomBarWidget = QWidget(parent)
        self.bottomBarLayout = QHBoxLayout()
        self.bottomBarWidget.setLayout(self.bottomBarLayout)
        
        # 'Human readable numbers' option checkbox
        self.humandReadableNumCheckBox = QCheckBox(self.bottomBarWidget)
        self.bottomBarLayout.addWidget(self.humandReadableNumCheckBox)
        self.humandReadableNumCheckBox.setText('Human readable numbers')
        self.humandReadableNumCheckBox.clicked.connect(self.onHumanReadableCheckboxClick)
        self.humandReadableNumCheckBox.setChecked(self.option_HumanReadableNumbers)
        
        # 'Full command line' option checkbox
        self.fullCmdLineCheckBox = QCheckBox(self.bottomBarWidget)
        self.bottomBarLayout.addWidget(self.fullCmdLineCheckBox)
        self.fullCmdLineCheckBox.setText('Full command line')
        self.fullCmdLineCheckBox.clicked.connect(self.onFullCmdLineCheckboxClick)
        self.fullCmdLineCheckBox.setChecked(self.option_FullCommandLine)

        return self.bottomBarWidget
        
    
    def notifyError(self, severity, message):
        assert severity in ['ERROR', 'CRITICAL']
        if severity == 'CRITICAL':
            QMessageBox.critical(self, self.AppName, message)
            exit(1)
        elif severity == 'ERROR':
            QMessageBox.warning(self, self.AppName, message)
    
    def initSmemProxy(self):
        if not SmemProxy.checkSupport():
            self.notifyError(
                'CRITICAL',
                "Cannot find command 'smem' required by this application."
                "Make sure it is correctly installed."
            )
        smemProxy = SmemProxy()
        print("Initialized smem proxy")
        return smemProxy

