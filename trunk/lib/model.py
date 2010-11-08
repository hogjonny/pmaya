import os
import shutil
import subprocess
from pprint import pprint
from project import Project
from cotool import CheckoutTool

class Model:
    def __init__(self):
        self.workspace_paths = []
        self.files = []
        self.project = None


    def loadProjects(self, projs):
        self.workspace_paths = projs
        if projs:
            self.project = Project(self.workspace_paths[0])
        print 'DEBUG: '
        self.refreshFileList()


    def selectProject(self, proj):
        """The selected project is always the first item in the list. If proj
            is not already in the project list, it will be added"""

        #update project list
        if proj in self.workspace_paths:
            self.workspace_paths.remove(proj)
        self.workspace_paths.insert(0, proj)

        self.project = Project(self.workspace_paths[0])
        self.refreshFileList()

        #load project's configuration file


    def open(self, path):
        print 'Opening maya on file: %s' % path

        proj = self.project.getProject()

        #use tcsh shell since that is what BYU uses for its maya env
        cmd = 'tcsh -c \''

        #check for .cshrc file in proj root
        if os.path.exists(os.path.join(proj, '.cshrc')):
            cmd += 'source %s; ' % (os.path.join(proj, '.cshrc'))

        #maya command
        cmd += 'maya -file %s -proj %s' % (path, proj)

        #check for startup script
        startup_script = self.project.getMelStartupScript()
        if os.path.exists(startup_script):
            cmd += ' -script %s' % startup_script

        #close command string
        cmd += '\''

        #open maya
        print 'CMD:', cmd
        subprocess.Popen(cmd, shell=True)


    def _createFileDirectories(self, path):
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        misc = os.path.join(dirname, self.project.getMiscDirname())
        if not os.path.exists(misc):
            os.makedirs(misc)


    def createFile(self, path):
        print 'Creating new maya file: %s' % path

        #make directory if it does not already exist
        self._createFileDirectories(path)

        cmd = 'maya -batch -command \'file -rename "%s"; file -f -save\'' % path
        print 'CMD:', cmd
        subprocess.Popen(cmd, shell=True)

        #TODO raise exception if not created


    def copyFile(self, src, dest):
        print 'Copying file %s to %s' % (src, dest)

        #make directory if it does not already exist
        self._createFileDirectories(dest)

        shutil.copy(src, dest)


    def checkout(self, src, dest):
        print 'Checking out file: "%s" to "%s".' % (src, dest)
        CheckoutTool().checkout(src, dest)
        self.refreshFileList()


    def checkin(self, src, dest, msg):
        print 'Checking in file: "%s" to "%s".' % (src, dest)
        print 'Log msg: %s' % msg
        
        #set up checkout tool
        co_tool = CheckoutTool()
        if self.project.getBackupDirname():
            co_tool.backup_dirname = self.project.getBackupDirname()

        co_tool.checkin(src, dest, msg)
        self.refreshFileList()


    def remove(self, path):
        os.remove(path)
        self.refreshFileList()


    def refreshFileList(self):
        if not self.project:
            return

        co_dir = self.project.getCheckoutDir()

        print 'Refreshing file list from dir: %s' % co_dir

        if not os.path.exists(co_dir):
            os.makedirs(co_dir)

        self.files = [os.path.join(co_dir, x) for x in os.listdir(co_dir) if 
            x.endswith('.mb') or x.endswith('.ma')]
        self.files.sort()
