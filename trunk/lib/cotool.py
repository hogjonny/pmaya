import os
import shutil
import datetime
from getpass import getuser

class CheckoutTool:
    """Handles checking in and checking out of files"""

    def __init__(self):
        self.backup_dirname = 'backup'

    def _getBkpPath(self, path):
        """Returns the version and path of the lowest non-existing backup path
            defined as "backup/<basename>.<version>.<extension>"
            (for example: "backup/izzy.1.mb")"""

        #set up some other paths that we are going to use later
        dirname, basename = os.path.split(path)
        backupDir = os.path.join(dirname, self.backup_dirname)

        #set up the directories that we are going to use
        root, ext = os.path.splitext(basename)

        #find the version number that we need
        version = 1
        while True:
            path = '%s/%s.%s%s' % (backupDir, root, version, ext)

            if not os.path.exists(path):
                break

            version += 1

        return version, path


    def _writeLog(self, logFile, version, msg):
        """Writes an entry into this files backup log"""

        #write into the log file
        f = open(logFile, 'a')
        f.write('-----------------------\n')
        f.write('version: %s\n' % version)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write('user: %s\n' % getuser())
        f.write('date: %s\n' % now)
        f.write('\n%s\n\n' % msg)
        f.close()


    def checkin(self, src, dest, msg):
        """Checks in a file and writes to its log. Note: unlike other pipeline
            I have done, the latest version of the file is located within the 
            "backup" folder AND outside."""

        #get the version and backup location
        version, bkpPath = self._getBkpPath(dest)

        #make sure the backup directory exists
        backupDir = os.path.dirname(bkpPath)
        if not os.path.exists(backupDir):
            os.makedirs(backupDir)

        #backup the file first
        shutil.copy(src, bkpPath)

        #then overwrite the base file
        shutil.move(src, dest)

        #and write to the log file
        log_file = backupDir + '/' + os.path.basename(dest) + '.log'
        self._writeLog(log_file, version, msg)


    def checkout(self, src, dest):
        """Checks out src to PATH (really just copies)"""
        shutil.copy(src, dest)
