"""
Plugin principal do GeoIFSC.

Este módulo implementa o plugin principal para QGIS.
"""

import os
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QTranslator, QCoreApplication, QLocale
import builtins, sys
from qgis.core import QgsMessageLog, Qgis

from .raster_upload_dialog import RasterUploadDialog


class GeoIFSCPlugin:
    """Plugin principal do GeoIFSC."""
    
    def __init__(self, iface):
        """Inicializa o plugin.
        
        Args:
            iface: Interface do QGIS
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Inicializa tradutor
        locale = QLocale.system().name()[:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            f'GeoIFSC_{locale}.qm'
        )
        
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
        
        # Variáveis de menu e ações
        self.menu = None
        self.actions = []
    
    def initGui(self):
        """Inicializa interface gráfica do plugin."""
        # Cria menu principal
        self.menu = QMenu("GeoIFSC", self.iface.mainWindow().menuBar())
        
        # Submenu Banco de dados
        db_menu = QMenu("Banco de dados", self.menu)
        self.menu.addMenu(db_menu)
        
        # Ação: Enviar Raster → PostGIS
        raster_action = QAction(
            QIcon(os.path.join(self.plugin_dir, "icon.png")),
            "Enviar Raster → PostGIS",
            self.iface.mainWindow()
        )
        raster_action.triggered.connect(self.run_raster_upload)
        raster_action.setStatusTip("Envia arquivos raster para banco PostGIS")
        
        db_menu.addAction(raster_action)
        self.actions.append(raster_action)
        
        # Adiciona menu à barra de menus
        menubar = self.iface.mainWindow().menuBar()
        menubar.addMenu(self.menu)
        # Redireciona print e exceções não tratadas para o log do QGIS
        def _qgis_print(*args, **kwargs):
            QgsMessageLog.logMessage(" ".join(str(a) for a in args), "GeoIFSC", Qgis.Info)
        builtins.print = _qgis_print
        def _qgis_excepthook(exctype, value, tb):
            QgsMessageLog.logMessage(f"Unhandled exception: {value}", "GeoIFSC", Qgis.Critical)
        sys.excepthook = _qgis_excepthook
    
    def unload(self):
        """Remove o plugin da interface."""
        if self.menu:
            # Remove menu da barra de menus
            menubar = self.iface.mainWindow().menuBar()
            menubar.removeAction(self.menu.menuAction())
            
            # Limpa ações
            for action in self.actions:
                self.iface.removePluginMenu("GeoIFSC", action)
            
            self.menu = None
            self.actions = []
    
    def run_raster_upload(self):
        """Executa diálogo de upload de raster de forma não bloqueante para manter o console acessível."""
        try:
            # Armazena referência para não ser coletado e abre de forma não modal
            self.dialog = RasterUploadDialog()
            self.dialog.show()
        except Exception as e:
            from qgis.core import QgsMessageLog, Qgis
            QgsMessageLog.logMessage(
                f"Erro ao abrir diálogo de upload: {e}",
                "GeoIFSC",
                Qgis.Critical
            )
