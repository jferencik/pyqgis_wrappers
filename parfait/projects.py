from wrappers.layer_wrappers import map_layers
from qgis.core.contextmanagers import qgisapp
from qgis.core import QgsProject, QgsMapLayerRegistry, QgsMapSettings
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from PyQt4.QtCore import QFileInfo
from PyQt4.QtXml import QDomDocument


class Project(object):
    """
    A wrapper for handling project based logic.
    note: This class really just talks to the QgsProject.instance() object.  QGIS can still
    only open and load a single project at a time. QgsProject is still a bad singleton object.
    """
    def __init__(self, bridge=None):
        self.bridge = bridge

    def __enter__(self):
        return self

    @classmethod
    def from_file(cls, filename, canvas):
        """
        Load a project file from a path.
        :param filename: The path to the project file.
        :param canvas: (optional) Passing a canvas will auto add layers to the canvas when the load is
        loaded.
        :return: A Project object which wraps QgsProject.instance()
        """
        QgsProject.instance().clear()
        bridge = None
        if canvas:
            bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(), canvas)
        QgsProject.instance().read(QFileInfo(filename))
        if bridge:
            bridge.setCanvasLayers()
        return cls(bridge)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Close the current project.
        """
        QgsProject.instance().clear()
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        if self.bridge:
            self.bridge.clear()

    @property
    def map_settings(self):
        """
        Return the settings that have been set for the map canvas.
        @return: A QgsMapSettings instance with the settings read from the project.
        """
        xml = open(QgsProject.instance().fileName()).read()
        doc = QDomDocument()
        doc.setContent(xml)
        canvasnodes = doc.elementsByTagName("mapcanvas")
        node = canvasnodes.at(0).toElement()
        settings = QgsMapSettings()
        settings.readXML(node)
        return settings


def open_project(projectfile, canvas=None):
    """
    Open a QGIS project file
    :param projectfile: The path to the project file to load.
    :param canvas: (optional) Canvas object.
    :return: A Project object wrapper with handy functions for doing project related stuff.
    """
    return Project.from_file(projectfile, canvas)
