"""
Painel de Ajuda para o plugin GeoIFSC.

Este módulo contém a classe HelpPanel, responsável por exibir o conteúdo de ajuda
e informações sobre o plugin GeoIFSC.
"""

from .geoifsc_utils import find_executable, get_postgres_possible_paths


class HelpPanel:
    def __init__(self):
        # ...código existente...

    def display_help(self):
        # ...código existente...
        self._add_note(
            "Este plugin inclui raster2pgsql.exe e psql.exe dentro de sua pasta bin/. "
            "Não é necessário instalar PostgreSQL/PostGIS externamente."
        )

    def _add_note(self, note: str):
        """
        Adiciona uma nota na interface do painel de ajuda.

        Args:
            note: O texto da nota a ser exibida
        """
        # ...código para adicionar nota na UI...