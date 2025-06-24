from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .wu_simulator_dock import WUSimulatorPlugin
from . import resources  # This ensures the compiled resources are loaded

class WUSimulator:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.plugin = None

    def initGui(self):
        self.action = QAction(QIcon(":/icon.png"), "WU-Simulator", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("WU-Simulator", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.plugin:
            self.plugin.unload()
        if self.action:
            self.iface.removePluginMenu("WU-Simulator", self.action)
            self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.plugin:
            self.plugin = WUSimulatorPlugin(self.iface)
        self.plugin.initGui()
