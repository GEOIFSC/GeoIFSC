"""
Pacote principal do GeoIFSC.

Plugin QGIS para funcionalidades geoespaciais do IFSC.
"""

__version__ = "1.0.0"
__author__ = "GeoIFSC Team"


def classFactory(iface):
    """
    Factory function para o plugin QGIS.
    
    Esta função é chamada pelo QGIS para criar uma instância do plugin.
    
    Args:
        iface: Interface do QGIS
        
    Returns:
        Instância do plugin GeoIFSC
    """
    from .geoifsc_plugin import GeoIFSCPlugin
    return GeoIFSCPlugin(iface)
