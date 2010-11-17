import os
from pprint import pprint

from globals import VERSION
from model import Model
from viewer import Viewer, Dialogs, UIAbortException


class Controller:
    def __init__(self, app):
        self.app = app
        self.view = Viewer(self)
        self.model = Model()
        self.view.show()

        self.refreshGui()


    def event(self, event):
        print 'Handing event', event

        try:
            if event == 'PROJ_SELECT':
                self._selectProject()
            elif event == 'ABOUT_MENU_ITEM':
                self._aboutMenuItem()
            elif event == 'QUIT_MENU_ITEM':
                self._quitMenuItem()

            #these events need a project to be specified already
            else:
                if not self.model.project:
                    return

                if event == 'NEW_BUTTON':
                    self._newButton()
                elif event == 'OPEN_BUTTON':
                    self._openButton()
                elif event == 'CHECKIN_BUTTON':
                    self._checkinButton()
                elif event == 'CHECKOUT_BUTTON':
                    self._checkoutButton()
                elif event == 'DELETE_BUTTON':
                    self._deleteButton()
                elif event == 'REFRESH_BUTTON':
                    self._refreshButton()
                elif event == 'NEW_FILE_MENU_ITEM':
                    self._newFileMenuItem()

        except UIAbortException, e:
            pass

        self.refreshGui()


    def _selectProject(self):
        selected = self.view.proj_selector.getSelected()

        if selected == 'Select New...':
            dialogs = Dialogs(self.view)
            start_dir = os.path.join(os.environ['HOME'], 'maya', 'projects')
            filters = ['Maya Project File (workspace.mel)']

            selected = dialogs.fileDialog(start_dir, filters)

        if not os.path.exists(selected):
            #user is trying to load an invalid project
            return

        self.model.selectProject(selected)

    
    def _newButton(self):
        dialogs = Dialogs(self.view)

        #prompt for a file name
        filename = dialogs.fileTextPrompt('Enter name of the new maya file:')
        print 'Chosen name:', filename

        if not filename.endswith('.mb'):
            filename += '.mb'

        full_path = os.path.join(self.model.project.getCheckoutDir(), filename)
        print 'Full path:', full_path

        self.model.createFile(full_path)
        self.refreshGui()

        #report
        msg = 'The file "%s" was successfully created.' % filename
        msg += '\n\nTo edit it in maya, select it in your list and'
        msg += ' click "Open...".'

        dialogs.infoPrompt(msg)


    def _openButton(self):
        """Opens Maya on the specified file"""
        #get the specified file
        selected_file = self.view.list.getSelected()

        if selected_file:
            self.model.open(selected_file)
            return

        #prompt if they really want to open maya
        dialogs = Dialogs(self.view)

        msg = 'No file selected!'
        msg += '\n\nAre you sure you want to open maya without a file?'
        dialogs.confirmPrompt(msg)

        self.model.open()


    def _checkoutButton(self):
        dialogs = Dialogs(self.view)

        #open a file dialog
        start_dir = self.model.project.getScenesDir()
        filters = self.model.project.getDialogFilters()

        selected = dialogs.fileDialog(start_dir, filters)

        #prompt to overwrite
        dest_file = os.path.join(self.model.project.getCheckoutDir(), 
            os.path.basename(selected))

        if os.path.exists(dest_file):
            msg = 'The file "%s" already exists in your checkout folder.' \
                % os.path.basename(dest_file)
            msg += '\n\nAre you sure you want to overwrite it?'
            dialogs.confirmPrompt(msg)

        #checkout the file
        self.model.checkout(selected, dest_file)
        self.refreshGui()

        #report
        msg = 'The file was successfully checked out.'
        msg += '\n\nTo open it in maya, select it in your list and'
        msg += ' click "Open...".'

        dialogs.infoPrompt(msg)
            

    def _checkinButton(self):
        dialogs = Dialogs(self.view)

        src_file = self.view.list.getSelected()

        if not src_file:
            #nothing selected so do nothing
            return

        print 'Checking in file: %s' % src_file

        #get the destination location
        start_dir = self.model.project.getScenesDir()
        filters = self.model.project.getDialogFilters()

        dest_file = dialogs.fileDialog(start_dir, filters, 
            doSaveButton=True)

        print 'DEST IS:', dest_file

        #confirm if it does not yet exist
        if not os.path.exists(dest_file):
            msg = 'The file "%s" does not yet exist.' % dest_file
            msg += '\n\nAre you sure you want to check in to a new location?'

            dialogs.confirmPrompt(msg)

        #prompt for a log message
        log_msg = dialogs.textPrompt('Enter a log message:')

        #confirm
        msg = 'Please confirm:\n\n'
        msg += 'Checking in:\n%s\n\n' % src_file
        msg += 'To: \n%s\n\n' % dest_file
        msg += 'Log message:\n%s\n\n' % log_msg
        msg += 'Does this look okay?\n'
        dialogs.confirmPrompt(msg)

        #check in
        self.model.checkin(src_file, dest_file, log_msg)
        self.refreshGui()

        #report
        msg = 'The file was successfully checked in.'
        msg += '\n\nTo continue working on it, you will have to check'
        msg += ' it out again.'

        dialogs.infoPrompt(msg)


    def _deleteButton(self):
        dialogs = Dialogs(self.view)

        src_file = self.view.list.getSelected()

        if not src_file:
            #nothing selected so do nothing
            return

        print 'Removing file: %s' % src_file

        #confirm
        msg = 'Remove "%s" from your checked out folder?\n' % src_file
        dialogs.confirmPrompt(msg)

        self.model.remove(src_file)
        self.refreshGui()


    def _refreshButton(self):
        self.model.refreshFileList()
        self.refreshGui()


    def _newFileWizard(self):
        """Wizard that prompts the user to get the path of a new file"""

        dialogs = Dialogs(self.view)

        #get category
        category = dialogs.radioButtonDialog('Pick a category:' , 
            self.model.project.config['NEW_FILE_CATEGORIES'])

        #get name of asset/shot (loop until valid input)
        name = dialogs.fileTextPrompt('Enter name:')

        #get task
        tasks = self.model.project.config['NEW_FILE_TASKS'][category][:]
        tasks.append('Other')

        task = dialogs.radioButtonDialog('Pick a task:' , tasks)

        if task == 'Other':
            task = dialogs.textPrompt('Enter task:')

        #get the path of the file we are creating
        category_dir = self.model.project.config['NEW_FILE_PATHS'][category]
        result = os.path.join(category_dir, name, '%s_%s.mb' % (name, task))

        #ask to overwrite
        print 'EXISTS:', result, os.path.exists(result)
        if os.path.exists(result):
            msg = 'The file "%s" already exists. Overwrite?' % result
            dialogs.confirmPrompt(msg)

        #confirm all settings
        msg = 'You have selected:'
        msg += '\n\n\tCategory: %s' % category
        msg += '\n\tName: %s' % name
        msg += '\n\tTask: %s' % task
        msg += '\n\nThis will create a file in this location: '
        msg += '\n%s' % result
        msg += '\n\nDoes this look okay?'
        dialogs.confirmPrompt(msg)

        return result


    def _newFileMenuItem(self):
        """Prompts and then creates a new file"""

        dialogs = Dialogs(self.view)

        path = self._newFileWizard()

        #see if we want to make a blank scene or not
        msg = 'How should the new file be created?'
        BLANK = 'Make a blank maya scene'
        EXISTING = 'Use a copy of an existing file'

        choice = dialogs.radioButtonDialog(msg, [BLANK, EXISTING])

        if choice == BLANK:
            msg = 'Final confirmation:'
            msg += '\n\nCreate blank maya file at "%s"?' % path
            dialogs.confirmPrompt(msg)
            self.model.createFile(path)

        elif choice == EXISTING:
            src_path = dialogs.fileDialog(
                self.model.project.getScenesDir(),
                self.model.project.getDialogFilters())

            msg = 'Please confirm:'
            msg += '\n\nCopy "%s" to new file "%s"?' % (src_path, path)
            dialogs.confirmPrompt(msg)
            self.model.copyFile(src_path, path)

        msg = 'New file successfully created!'
        msg += '\n\nLocation: %s' % path
        msg += '\n\nPlease check out your new file to begin work on it.'
        dialogs.infoPrompt(msg)


    def _quitMenuItem(self):
        self.app.quit()


    def _aboutMenuItem(self):
        #TODO make this a more spiffy "About..." dialog
        msg = 'Pmaya version: %s\n\n' % VERSION
        msg += 'Written by: James Jackson\n'
        msg += 'Email: james_jackson@byu.edu'

        dialogs = Dialogs(self.view)
        dialogs.infoPrompt(msg)


    def refreshGui(self):
        #project selector
        self.view.proj_selector.load(self.model.workspace_paths)

        #file list
        self.view.list.load(self.model.files)


    def loadProfile(self, path):
        if not os.path.exists(path):
            return

        f = open(path, 'r')
        cfg = eval(f.read())
        f.close()
        print cfg

        self.model.loadProjects(cfg['projects'])
        self.refreshGui()


    def saveProfile(self, path):
        cfg = {}
        cfg['projects'] = self.model.workspace_paths
        cfg['version'] = VERSION

        f = open(path, 'w')
        pprint(cfg, stream=f)
        f.close()
