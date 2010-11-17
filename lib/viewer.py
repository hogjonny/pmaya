import os
import re
from PyQt4 import QtGui, QtCore

#TODO: viewer should have a link to model, not controller

class UIAbortException:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Dialogs:
    """This class is used to invoke dialogs from the controller"""

    def __init__(self, parent):
        self.parent = parent


    def radioButtonDialog(self, msg, items):
        """Raises a dialog allowing you to choose between ITEMS"""

        dialog = RadioButtonDialog(self.parent, msg, items)
        if not dialog.exec_() or not dialog.getSelection():
            raise UIAbortException('User aborted during radioButtonPrompt')

        return dialog.getSelection()


    def textPrompt(self, msg):
        """Raises a prompt for user input. Reprompts until valid input is given
            or the user aborts"""

        while True:
            result, ok = QtGui.QInputDialog.getText(self.parent, 
                'Input Dialog', msg)

            if not ok:
                raise UIAbortException('User aborted during textPrompt')

            if result:
                #TODO: insert prompt about bad input
                break

        return str(result)


    def fileTextPrompt(self, msg):
        """Raises a prompt for user input. Reprompts until valid input is given
            or the user aborts. Valid input for filenames cannot have spaces
            or punctuation except for underscores and periods"""

        while True:
            result = self.textPrompt(msg)

            if re.match('^[A-Za-z0-9_\.]*$', result):
                break

            error_msg = 'Invalid input detected.'
            error_msg += '\n\nPlease only use alphanumeric characters, '
            error_msg += '\nunderscores, and periods. (No spaces.)'
            self.infoPrompt(error_msg)

        return str(result)


    def confirmPrompt(self, msg):
        """Raises a UIAbortException if the MSG is not confirmed"""

        msg_box = QtGui.QMessageBox(self.parent)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Please Confirm:')
        msg_box.setStandardButtons(
            QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok)

        #TODO: figure out why this doesn't work
        #msg_box.setDefaultButton(QtGui.QMessageBox.Ok)

        if msg_box.exec_() != QtGui.QMessageBox.Ok:
            raise UIAbortException('User aborted during confirmPrompt')


    def infoPrompt(self, msg):
        msg_box = QtGui.QMessageBox(self.parent)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Info')
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)

        if msg_box.exec_() != QtGui.QMessageBox.Ok:
            raise UIAbortException('User aborted during infoPrompt')


    def fileDialog(self, start_dir, filters, doSaveButton=False):
        dialog = QtGui.QFileDialog()
        dialog.setFilters(filters)
        dialog.setDirectory(start_dir)
        dialog.setConfirmOverwrite(False)

        if doSaveButton:
            dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)

        if not dialog.exec_():
            raise UIAbortException('User aborted during confirmPrompt')

        return str(dialog.selectedFiles()[0])


class SideButtons:
    def __init__(self):

        #set up layouts
        self.layout = QtGui.QVBoxLayout()
        topbuttons_layout = QtGui.QVBoxLayout()
        self.layout.addLayout(topbuttons_layout, QtCore.Qt.AlignTop)
        bottombuttons_layout = QtGui.QVBoxLayout()
        self.layout.addLayout(bottombuttons_layout, QtCore.Qt.AlignBottom)

        #new button
        self.new_button = QtGui.QPushButton('New...')
        topbuttons_layout.addWidget(self.new_button)

        #open button
        self.open_button = QtGui.QPushButton('Open...')
        topbuttons_layout.addWidget(self.open_button)

        #delete button
        self.delete_button = QtGui.QPushButton('Remove...')
        topbuttons_layout.addWidget(self.delete_button)

        line = QtGui.QFrame()
        topbuttons_layout.addWidget(line)
        line.setFrameShape(QtGui.QFrame.HLine);
        line.setFrameShadow(QtGui.QFrame.Sunken);

        #checkin button
        self.checkin_button = QtGui.QPushButton('Check In...')
        topbuttons_layout.addWidget(self.checkin_button)

        #checkout button
        self.checkout_button = QtGui.QPushButton('Check Out...')
        topbuttons_layout.addWidget(self.checkout_button)

        #refresh button
        self.refresh_button = QtGui.QPushButton('Refresh List')
        topbuttons_layout.addWidget(self.refresh_button, 0, 
            QtCore.Qt.AlignBottom)


class FileList(QtGui.QListWidget):
    def __init__(self):
        QtGui.QListWidget.__init__(self)
        self.layout = QtGui.QVBoxLayout()

        #list widget
        self.setMinimumSize(350, 400)
        self.layout.addWidget(self)

        self.paths = {}


    def load(self, files):
        """refreshes the file list"""

        #only display basenames, but store the whole path for "getSelected()"
        self.paths.clear()
        for k,v in [(os.path.basename(x), x) for x in files]:
            self.paths[k] = v

        #now get the basenames sort them
        basenames = self.paths.keys()
        basenames.sort()

        #and display them on screen
        self.clear()
        for x in basenames:
            self.addItem(QtCore.QString(x))


    def getSelected(self):
        items = self.selectedItems()

        if not items:
            return None

        basename = str(self.selectedItems()[0].text())
        
        if not self.paths.has_key(basename):
            return None

        return self.paths[basename]


class ProjectSelector(QtGui.QComboBox):
    def __init__(self):
        QtGui.QComboBox.__init__(self)
        self.layout = QtGui.QHBoxLayout()

        #label
        text = QtCore.QString('Project:')
        label = QtGui.QLabel(text)
        label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.layout.addWidget(label)

        #project dropdown
        self.setFixedHeight(self.sizeHint().height())
        self.layout.addWidget(self)

        #load empty list by default
        self.paths = {}
        self.load([])


    def load(self, workspaces):
        self.clear() #clear elements in GUI list

        #add an empty element to GUI if the proj list is empty
        if len(workspaces) == 0:
            self.addItem('')

        #only display dirnames, but store the whole path for "getSelected()"
        self.paths.clear()
        for dirname, fullname in [(os.path.dirname(x), x) for x in workspaces]:
            self.addItem(dirname)
            self.paths[dirname] = fullname

        self.addItem('Select New...')
        self.setCurrentIndex(0)


    def getSelected(self):
        result = str(self.currentText())
        if self.paths.has_key(result):
            return self.paths[result]
        return result


class MenuBar(QtGui.QMenuBar):
    def __init__(self, controller, parent=None):
        QtGui.QMenuBar.__init__(self, parent)

        self.setGeometry(QtCore.QRect(0, 0, 800, 21))

        #file menu
        menuFile = QtGui.QMenu(self)
        menuFile.setTitle('File')

        #new asset/shot...
        menuFile.addAction('New File...', 
            lambda: controller.event('NEW_FILE_MENU_ITEM'))

        #quit action
        menuFile.addAction('Quit', 
            lambda: controller.event('QUIT_MENU_ITEM'), 
            QtGui.QKeySequence('Ctrl+q'))

        self.addAction(menuFile.menuAction())

        #help menu
        menuHelp = QtGui.QMenu(self)
        menuHelp.setTitle('Help')

        #about action
        menuHelp.addAction('About...',
            lambda: controller.event('ABOUT_MENU_ITEM'))

        self.addAction(menuHelp.menuAction())


class RadioButtonDialog(QtGui.QDialog):
    def __init__(self, parent, msg, items):
        QtGui.QDialog.__init__(self, parent)
        self.buttonGroup = QtGui.QButtonGroup()
        layout = QtGui.QVBoxLayout(self)

        #display message
        label = QtGui.QLabel(msg)
        layout.addWidget(label)

        #convert text to radio buttons
        buttons = [QtGui.QRadioButton(x) for x in items]
        buttons[0].setChecked(True)

        #add buttons to layout
        for button in buttons:
            layout.addWidget(button)
            self.buttonGroup.addButton(button)

        #Add "Ok" and "Cancel" buttons
        h_layout = QtGui.QHBoxLayout()
        layout.addLayout(h_layout)

        button = QtGui.QPushButton('Cancel')
        self.connect(button, QtCore.SIGNAL('clicked()'), self._cancelButton)
        h_layout.addWidget(button)

        button = QtGui.QPushButton('Ok')
        self.connect(button, QtCore.SIGNAL('clicked()'), self._okButton)
        h_layout.addWidget(button)

        self.selection = ''


    def _okButton(self):
        self.selection = str(self.buttonGroup.checkedButton().text())
        self.done(QtGui.QDialog.Accepted)


    def _cancelButton(self):
        self.selection = ''
        self.done(QtGui.QDialog.Rejected)

    def getSelection(self):
        return self.selection


class Viewer(QtGui.QWidget):
    def __init__(self, controller):
        QtGui.QWidget.__init__(self)

        layout = QtGui.QVBoxLayout(self)
        menubar = MenuBar(controller, self)
        layout.setMenuBar(menubar)

        layout.addSpacing(5)
        #set up project dropdown
        self.proj_selector = ProjectSelector()
        layout.addLayout(self.proj_selector.layout)
        self.connect(self.proj_selector, QtCore.SIGNAL('activated(int)'), 
            lambda: controller.event('PROJ_SELECT'))

        #separator
        separator = QtGui.QFrame()
        separator.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        separator.setFixedHeight(10)
        layout.addWidget(separator)
        layout.addSpacing(10)

        #label
        text = QtCore.QString('Currently checked out files:')
        label = QtGui.QLabel(text)
        layout.addWidget(label)

        #horizontal layout for list and buttons
        bottom_layout = QtGui.QHBoxLayout()
        layout.addLayout(bottom_layout)

        #set up filelist
        self.list = FileList()
        bottom_layout.addLayout(self.list.layout)

        #side buttons
        side_buttons = SideButtons()
        bottom_layout.addLayout(side_buttons.layout)

        self.connect(side_buttons.new_button,
            QtCore.SIGNAL('clicked()'),
            lambda: controller.event('NEW_BUTTON'))

        self.connect(side_buttons.open_button, 
            QtCore.SIGNAL('clicked()'), 
            lambda: controller.event('OPEN_BUTTON'))

        self.connect(side_buttons.delete_button, 
            QtCore.SIGNAL('clicked()'), 
            lambda: controller.event('DELETE_BUTTON'))

        self.connect(side_buttons.checkin_button, 
            QtCore.SIGNAL('clicked()'), 
            lambda: controller.event('CHECKIN_BUTTON'))

        self.connect(side_buttons.checkout_button, 
            QtCore.SIGNAL('clicked()'), 
            lambda: controller.event('CHECKOUT_BUTTON'))

        self.connect(side_buttons.refresh_button, 
            QtCore.SIGNAL('clicked()'), 
            lambda: controller.event('REFRESH_BUTTON'))

