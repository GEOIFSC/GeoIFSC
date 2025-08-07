import sys
import types
import os

# Ensure src directory is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Stub qgis modules if not available
if 'qgis' not in sys.modules:
    qgis = types.ModuleType('qgis')
    core = types.ModuleType('qgis.core')
    pyqt = types.ModuleType('qgis.PyQt')
    qtwidgets = types.ModuleType('qgis.PyQt.QtWidgets')
    qtgui = types.ModuleType('qgis.PyQt.QtGui')
    qtcore = types.ModuleType('qgis.PyQt.QtCore')

    class QAction: pass
    class QMenu: pass
    class QIcon: pass
    class QTranslator: pass
    class QCoreApplication:
        @staticmethod
        def installTranslator(t):
            pass
        @staticmethod
        def translate(ctx, text):
            return text
    class QLocale:
        @staticmethod
        def system():
            class L:
                def name(self):
                    return 'en_US'
            return L()

    class QgsMessageLog: pass
    class Qgis: pass
    class QgsApplication:
        @staticmethod
        def prefixPath():
            return ''

    qtwidgets.QAction = QAction
    qtwidgets.QMenu = QMenu
    qtgui.QIcon = QIcon
    qtcore.QTranslator = QTranslator
    qtcore.QCoreApplication = QCoreApplication
    qtcore.QLocale = QLocale

    core.QgsMessageLog = QgsMessageLog
    core.Qgis = Qgis
    core.QgsApplication = QgsApplication

    qgis.core = core
    pyqt.QtWidgets = qtwidgets
    pyqt.QtGui = qtgui
    pyqt.QtCore = qtcore
    qgis.PyQt = pyqt

    sys.modules['qgis'] = qgis
    sys.modules['qgis.core'] = core
    sys.modules['qgis.PyQt'] = pyqt
    sys.modules['qgis.PyQt.QtWidgets'] = qtwidgets
    sys.modules['qgis.PyQt.QtGui'] = qtgui
    sys.modules['qgis.PyQt.QtCore'] = qtcore

# Stub PyQt5 if not available
if 'PyQt5' not in sys.modules:
    class StubModule(types.ModuleType):
        def __getattr__(self, name):
            val = type(name, (), {})
            setattr(self, name, val)
            return val

    pyqt5 = types.ModuleType('PyQt5')
    QtWidgets5 = StubModule('PyQt5.QtWidgets')
    QtGui5 = StubModule('PyQt5.QtGui')
    QtCore5 = StubModule('PyQt5.QtCore')

    QtGui5.QIcon = QIcon
    def pyqtSignal(*args, **kwargs):
        class _Sig:
            def connect(self, *a, **k):
                pass
            def emit(self, *a, **k):
                pass
        return _Sig()

    QtCore5.QObject = object
    QtCore5.pyqtSignal = pyqtSignal

    pyqt5.QtWidgets = QtWidgets5
    pyqt5.QtGui = QtGui5
    pyqt5.QtCore = QtCore5
    sys.modules['PyQt5'] = pyqt5
    sys.modules['PyQt5.QtWidgets'] = QtWidgets5
    sys.modules['PyQt5.QtGui'] = QtGui5
    sys.modules['PyQt5.QtCore'] = QtCore5
