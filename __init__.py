"""
Arquivo principal do plugin GeoIFSC.
"""

try:
    from .src.geoifsc.geoifsc_plugin import classFactory
except Exception:  # pragma: no cover - plugin deps podem faltar em testes
    def classFactory(iface):  # type: ignore
        return None
