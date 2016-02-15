    from maya import cmds
    from maya import mel
    from maya import OpenMayaUI as omui 
    from PySide import QtGui, QtCore
    from PySide.QtCore import * 
    from PySide.QtGui import * 
    from shiboken import wrapInstance

#import FabricEngine.Core


mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

#contextID = cmds.FabricCanvasGetContextID()
#client = FabricEngine.Core.createClient({'contextID':contextID})
#host = client.DFG.host

class CheckableComboBox(QtGui.QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

class MetaHeaderView(QtGui.QHeaderView):

    def __init__(self,orientation,parent=None):
        super(MetaHeaderView, self).__init__(orientation,parent)
        self.setMovable(True)
        self.setClickable(True)
        # This block sets up the edit line by making setting the parent
        # to the Headers Viewport.
        self.line = QtGui.QLineEdit(parent=self.viewport())  #Create
        self.line.setAlignment(QtCore.Qt.AlignTop) # Set the Alignmnet
        self.line.setHidden(True) # Hide it till its needed
        # This is needed because I am having a werid issue that I believe has
        # to do with it losing focus after editing is done.
        self.line.blockSignals(True)
        self.sectionedit = 0
        # Connects to double click
        self.sectionDoubleClicked.connect(self.editHeader)
        self.line.editingFinished.connect(self.doneEditing)

    def doneEditing(self):
        # This block signals needs to happen first otherwise I have lose focus
        # problems again when there are no rows
        self.line.blockSignals(True)
        self.line.setHidden(True)
        newname = str(self.line.text())
        self.model().setHeaderData(self.sectionedit, Qt.Orientation.Vertical, newname)
        self.line.setText('')
        self.setCurrentIndex(QtCore.QModelIndex())

    def editHeader(self,section):
        print self.geometry().width()
        text = self.model().headerData(section, Qt.Orientation.Vertical)
        # This block sets up the geometry for the line edit
        edit_geometry = self.line.geometry()
        edit_geometry.setHeight(self.sectionSize(section))
        edit_geometry.setWidth(self.geometry().width())
        edit_geometry.moveBottom(self.sectionViewportPosition(section) + self.sectionSize(section)-1)
        self.line.setGeometry(edit_geometry)
        
        #print self.model().headerData(section, Qt.Orientation.Vertical)
        self.line.setText(text)
        self.line.setHidden(False) # Make it visiable
        self.line.blockSignals(False) # Let it send signals
        self.line.setFocus()
        self.line.selectAll()
        self.sectionedit = section


class CreateRbfEditor(QWidget):    
    def __init__(self, canvasNodes,*args, **kwargs):        
        super(CreateRbfEditor, self).__init__(*args, **kwargs)

        self.canvasNodes = canvasNodes
        
        #Parent widget under Maya main window        
        self.setParent(mayaMainWindow)        
        self.setWindowFlags(Qt.Window)   
        
        #Set the object name     
        self.setObjectName('RbfEditor_uniqueId')        
        self.setWindowTitle('RBF Editor')        
        
        self.actions()     
        self.initUI()
        self._updateWidgetSize()    
        self.cmd = 'polyCone'

        
    def initUI(self):
        #Create combo box (drop-down menu) and add menu items 
        self.combo = QComboBox(self)
        if self.canvasNodes is None or len(self.canvasNodes) == 0:
            self.combo.addItem('no RBF node')
        else:
            for i in self.canvasNodes:      
                self.combo.addItem(i)        
        
        #self.combo.setCurrentIndex(0)        
        #self.combo.move(20, 20)        
        #self.combo.activated[str].connect(self.combo_onActivated)        

        #Create combo box (drop-down menu) and add menu items 
        self.poseAtt = QComboBox(self)
        self.poseAtt.addItem('Translate')
        self.poseAtt.addItem('Scaling')
        self.poseAtt.addItem('Euler')
        self.poseAtt.addItem('Quaternion')
        self.poseAtt.setCurrentIndex(0)        
        self.poseAtt.move(20, 45)        
        #self.poseAtt.activated[str].connect(self.driverAtt_onActivated) 

        #Create 'Create' button
        self.addButton = QPushButton('Add Pose', self)
        self.addButton.setGeometry(50, 50, 75, 20)       
        self.addButton.move(self._rightPos(self.poseName, 5)[0] , self._rightPos(self.poseName, 5)[1])        
        self.addButton.clicked.connect(self.addButton_onClicked)

        self.valuesAtt = QComboBox(self)
        self.valuesAtt.addItem('Translate')
        self.valuesAtt.addItem('Scaling')
        self.valuesAtt.addItem('Euler')
        self.valuesAtt.addItem('Quaternion')
        self.valuesAtt.setCurrentIndex(0)        
        self.valuesAtt.move(60, 45)        
        #self.valuesAtt.activated[str].connect(self.driverAtt_onActivated) 

        #Create line edit box  
        self.poseName = QLineEdit(self)             
        self.poseName.move(20, 70)        

        self.ComboBox = CheckableComboBox()
        self.combo.move(20, 20) 
        for i in range(3):
            self.ComboBox.addItem("Combobox Item " + str(i))
            item = self.ComboBox.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

        #Create 'Create' button
        self.addButton = QPushButton('Add Pose', self)
        self.addButton.setGeometry(50, 50, 75, 20)       
        self.addButton.move(self._rightPos(self.poseName, 5)[0] , self._rightPos(self.poseName, 5)[1])        
        self.addButton.clicked.connect(self.addButton_onClicked)
        
        #Create 'Delete' button
        self.delButton = QPushButton('Delete Pose', self)
        self.delButton.setGeometry(50, 50, 75, 20)      
        self.delButton.move(self._rightPos(self.addButton, 5)[0] , self._rightPos(self.addButton, 5)[1])
        self.delButton.clicked.connect(self.delButton_onClicked)                   

        #Create a table
        self.table = QTableWidget(self)
        vheader = MetaHeaderView(Qt.Orientation.Vertical)
        self.table.setVerticalHeader(vheader)
        self.table.vHeader = ['D','E','F']
        self.table.setColumnCount(2)
        self.table.setRowCount(len(self.table.vHeader))
        self.table.verticalHeader().setVisible(1)
        self.table.horizontalHeader().setVisible(0)
        self.table.setAlternatingRowColors(True)
        self.table.setVerticalHeaderLabels(self.table.vHeader)
        self.table.setItem( 0, 0, QTableWidgetItem( 'test' ) )        
        self.table.itemClicked.connect(self.table_onClicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.openMenu)


    def _rightPos(self, widget, spacing):
        x = widget.pos().x() + widget.width() + spacing
        y = widget.pos().y()
        return [x, y]


    def _updateWidgetSize(self):
        self.table.setGeometry(20, 110, self.table.horizontalHeader().length() + 20, self.table.verticalHeader().length() + 25)
        self.setGeometry(50, 50, self.table.horizontalHeader().length() + 60, self.table.verticalHeader().length() + 100)        


    def floatAsItem(self, value):
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, value)
        return item

    
    #Change commmand string when combo box changes
    def combo_onActivated(self, text):        
        self.cmd = 'poly' + text + '()'            


    #Change commmand string when combo box changes
    def driverAtt_onActivated(self, text):        
        self.cmd = 'poly' + text + '()'  

    
    # Add a new position
    def addButton_onClicked(self):
        if(len(self.poseName.text()) > 0):
            rowPosition = self.table.rowCount()       
            self.table.insertRow(rowPosition)
            self.table.setVerticalHeaderItem(rowPosition, QtGui.QTableWidgetItem(self.poseName.text()))
            self.poseName.setText('')
            self.table.setItem(rowPosition , 0, self.floatAsItem(0.5))
            self._updateWidgetSize()

        
    # Delete selected row
    def delButton_onClicked(self):
        selectedRows =  self.table.selectionModel().selectedRows() 
        #for item in self.table.selectedRanges():
        for item in selectedRows:
            print "delete row:", item.row()
            self.table.removeRow(item.row())
               
        
    #test table is clicked    
    def table_onClicked(self):
        print 'toto'

    
    # setup Menu    
    def openMenu(self, position):       
        indexes = self.table.selectedItems()
        print indexes[0].row()
        
        menu = QMenu()       
        menu.addAction(self.renameAct)
        menu.addAction(self.deleteAct)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))

    
    # setup menu actions  
    def actions(self):
        self.renameAct = QtGui.QAction("&Rename Pose", self,
                shortcut=Qt.Key_F2,
                statusTip="rename the current pose",
                triggered=self.renamePose)
                
        self.deleteAct = QtGui.QAction("&Delete Pose", self,
                shortcut=QtGui.QKeySequence.Delete,
                statusTip="delete the current pose",
                triggered=self.deletePose)

    
    # menu actions
    def renamePose(self):
        print 'rename'
        #self.table.verticalHeader().

        
    def deletePose(self):
        print 'delete'
        #self.table.verticalHeader().
    
    
                           
view = CreateRbfEditor(None)
view.show()