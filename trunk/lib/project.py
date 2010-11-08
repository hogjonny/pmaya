import os
from pprint import pprint
from getpass import getuser

from globals import PMAYA_CONFIG_FILENAME

class Project:
    """This class is in charge of loading configuration information for a 
        project."""

    #TODO: simplify this module
    #   * make a clearly-defined config file with all settings and explanations
    #   * find better way to make the co_tool check in to a specific dirname
    #   * consider making this a simple dict. Bake all values in the dict 
    #       from the get go

    def __init__(self, workspace_path):
        #load path
        self.path = os.path.dirname(workspace_path)
        print 'Proj: %s' % self.path

        #load workspace
        self.workspace = self._loadWorkspace(workspace_path)
        print 'Workspace: '
        pprint(self.workspace)

        #load config
        config_path = os.path.join(self.path, PMAYA_CONFIG_FILENAME)
        self.config = self._loadConfig(config_path)
        print 'Config: '
        pprint(self.config)


    def _loadConfig(self, path=''):
        """Loads a pmaya configuration file (just a normal python dict)"""

        #CONFIGURATION FILE EXPLANATION:
        #   In order to facilitate projects with different settings, 
        #   configuration files will be used. The config file is really
        #   just a python dictionary that is saved to "$PROJ/.pmaya_cfg".
        #
        #   A project does not NEED to have a config file ready. If a config
        #   file is not found, default values will be used instead.
        #
        #   Here are explanations for each possible setting:
        #
        #    CHECK_OUT_DIR
        #       * The name of the directory used as the checkout destination
        #           for all users.
        #       * Note that if this path is not absolute, the actual location 
        #           will be relative to the root of the project. 
        #           (i.e. "$PROJ/<CHECK_OUT_DIRNAME>")
        #       * Default value is "users"
        #
        #    MEL_STARTUP_SCRIPT
        #       * This is the filename of a MEL script that will be sourced
        #           into maya whenever it is launched. 
        #       * Note that if this path is not absolute, it's actual location 
        #           will be relative to the MEL directory specified by the
        #           project's workspace.mel file.
        #           (i.e. $PROJ/<mel>/<MEL_STARTUP_SCRIPT>
        #       * The default value is "startup.mel"
        #
        #    TCSH_STARTUP_SCRIPT
        #       * This is the filename of a TCSH/CSH script that will be
        #           sourced into the shell right before maya is launched.
        #       * Note that if the specified value is not absolute, it's
        #           actual location will be relative to the root of the project
        #           (i.e. $PROJ/<TCSH_STARTUP_SCRIPT>
        #       * The default value is ".cshrc"
        #
        #    BACKUP_DIRNAME
        #       * This is the name of the directory where file backup's are
        #           stored when checking in.
        #       * Only specify a name for this value, not a full path, since
        #           it is always relative to the directory of the file being
        #           checked in.
        #       * The default value is "backup"
        #
        #    MISC_DIRNAME
        #       * When a new asset is created, there is a "misc" directory
        #           placed behind it for any misc files related to the maya
        #           files (such as texture images, cache data, etc.) 
        #       * This setting determines what the name of that directory 
        #           will be.
        #       * The default value is "misc"
        #
        #    DIALOG_FILTERS
        #       * This setting allows you to specify which filetypes can be
        #           selected in the check in and check out file dialogs.
        #       * The format of this setting should follow the exact guidelines
        #           used in the PyQt documentation for "QFileDialog.setFilters"
        #           (http://www.opendocs.net/pyqt/pyqt4/html/qfiledialog.html)
        #       * The default value is ['Maya Scene (*.mb *.ma)']
        #
        #   NEW_FILE_CATAGORIES
        #       * This setting allows you to specify the different catagories
        #           that can be specified for the new file dialogs. That way,
        #           you can use a simple description name (which appears in the
        #           gui), which will then map to a specific directory and 
        #           sub-types.
        #       * This setting should be stored as the following dictionary:
        #           <type> : [<dir>, [<subtypes>]]
        #           - <type> is the label that will appear in the GUI
        #           - <dir> is the directory where the new file will be stored.
        #               If the specified value is not an absolute path then it
        #               will be relative to the scenes directory of the current
        #               project.
        #           - [<subtypes>] is a list of strings that will make up part
        #               of the resulting filename.
        #       * The resulting new file will have the path: 
        #           "<dir>/<name>_<subtype>.mb"


        #load default values
        result = {  'CHECK_OUT_DIR' : 'users',
                    'MEL_STARTUP_SCRIPT' : 'startup.mel',
                    'TCSH_STARTUP_SCRIPT' : '.cshrc',
                    'BACKUP_DIRNAME' : 'backup',
                    'MISC_DIRNAME' : 'misc',
                    'DIALOG_FILTERS' : ['Maya Scene (*.mb *.ma)'],
                    'NEW_FILE_CATEGORIES' : ['Asset', 'Shot'],
                    'NEW_FILE_PATHS' : {
                        'Asset' : 'assets',
                        'Shot' : 'shots'
                    },
                    'NEW_FILE_TASKS' : {
                        'Asset' : ['model', 'shader', 'rig'],
                        'Shot' : ['layout', 'animation', 'lighting']
                    }
                }

        #load the project's config file
        if os.path.exists(path):
            f = open(path)
            tmp = eval(f.read())
            f.close()

            #and merge with the defaults
            result.update(tmp)

        #check config
        for category in result['NEW_FILE_CATEGORIES']:
            if not result['NEW_FILE_PATHS'].has_key(category) \
                or not result['NEW_FILE_TASKS'].has_key(category):

                raise Exception('Invalid config for this project!')

        #resolve any non-absolute paths
        abs_paths = {   'CHECK_OUT_DIR' : self.path,
                        'MEL_STARTUP_SCRIPT' : self.workspace['mel'],
                        'TCSH_STARTUP_SCRIPT' : self.path, 
                        'NEW_FILE_PATHS' : self.workspace['scene']
                        }

        for setting, abs_path in abs_paths.iteritems():
            if setting == 'NEW_FILE_PATHS':
                for k,v in result[setting].iteritems():
                    if not os.path.isabs(v):
                        new_path = os.path.join(abs_path, v)
                        result[setting][k] = new_path
                continue

            tmp_path = result[setting]
            if not os.path.isabs(result[setting]):
                result[setting] = os.path.join(abs_path, tmp_path)

        return result


    def _loadWorkspace(self, path=''):
        """Reads a workspace.mel file and returns directory maps as a dict"""

        def _stripArgument(string):
            """Removes semicolons and quotes from workspace file arguments"""
            result = string.strip()
            if result.endswith(';'):
                result = result[:-1]
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            return result

        #load default arguments
        result = {
            'scene' : self.path,
            'mel' : self.path
        }

        #load the workspace file if it is found
        if not os.path.exists(path):
            return result

        tmp = {}

        f = open(path)
        lines = [x.strip() for x in f.readlines()]
        f.close()

        for line in lines:
            if line.startswith('//'):
                continue

            args = line.split()

            if len(args) < 4 or args[0] != 'workspace' or args[1] != '-fr':
                continue

            key, val = [_stripArgument(x) for x in args[2:4]]
            tmp[key] = os.path.join(self.path, val)

        result.update(tmp)

        return result


    def getDialogFilters(self):
        """Get the type of files that can be selected in file dialogs. Must be
            of the format the QT uses for the QtDialog.setFilters method."""

        return self.config['DIALOG_FILTERS']


    def getMelStartupScript(self):
        return self.config['MEL_STARTUP_SCRIPT']


    def getTcshStartupScript(self):
        return self.config['TCSH_STARTUP_SCRIPT']


    def getBackupDirname(self):
        return self.config['BACKUP_DIRNAME']


    def getMiscDirname(self):
        return self.config['MISC_DIRNAME']


    def getProject(self):
        return self.path


    def getScenesDir(self):
        return self.workspace['scene']


    def getCheckoutDir(self):
        return os.path.join(self.config['CHECK_OUT_DIR'], getuser())


    def getMelDir(self):
        return self.workspace['mel']
