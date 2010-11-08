#! /usr/bin/python

# pmaya.py - BYU pipeline tool for maya
# Created by James Jackson (james_jackson@byu.edu) 1 Sept 2010
# Updated by James Jackson (james_jackson@byu.edu) 20 Sept 2010

#http://www.harshj.com/2009/05/14/pyqt-signals-slots-and-layouts-tutorial/
#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qmessagebox.html

#TODO:
# - Project-specific configuration files
# - New Asset Wizard
# - Check that maya opened appropriately
# - Better file list (with modification times and sorting columns)
# - Checkin single window for selecting destination and log message
# - Safeguard against checking out of your users folder
# - Quit menu item

import os
import sys
from PyQt4 import QtGui, QtCore
from lib.controller import Controller


def main():
    profile_path = os.path.join(os.environ['HOME'], '.pmaya')

    app = QtGui.QApplication(sys.argv)
    controller = Controller(app)
    controller.loadProfile(profile_path)
    app.exec_()
    controller.saveProfile(profile_path)


if __name__ == '__main__':
    main()
