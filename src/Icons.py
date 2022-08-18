from PyQt5.QtGui import QIcon
from os.path import join, dirname


def getIconPath(iconName):
    srcDirectory = dirname(__file__)
    projectDirectory = dirname(srcDirectory)
    iconAbsolutePath = join(projectDirectory, 'icons', iconName)
    return iconAbsolutePath


def getIcon(iconName):
    iconPath = getIconPath(iconName)
    return QIcon(iconPath)
