import os
import shutil
import tempfile
import stat
import pytest

from qgis.core import QgsApplication

# Cria um dummy QgsApplication.prefixPath
class DummyQgs:
    @staticmethod
    def prefixPath():
        return str(apps_dir / "qgis-ltr")

@pytest.fixture(autouse=True)
def setup_qgis_prefix(monkeypatch, tmp_path):
    # Monta estrutura: tmp/apps/qgis-ltr, tmp/apps/bin, tmp/bin
    global apps_dir, root_dir, bin1, bin2
    apps_dir = tmp_path / "apps"
    root_dir = tmp_path
    (apps_dir / "qgis-ltr").mkdir(parents=True)
    bin1 = apps_dir / "bin"
    bin2 = root_dir / "bin"
    bin1.mkdir()
    bin2.mkdir()
    # cria executáveis dummy
    exe1 = bin1 / "raster2pgsql.exe"
    exe2 = bin1 / "psql.exe"
    for exe in (exe1, exe2):
        exe.write_text("dummy")
        exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    # monkeypatch QgisApplication and os.path.isdir
    monkeypatch.setattr(QgsApplication, "prefixPath", DummyQgs.prefixPath)
    monkeypatch.setattr(os.path, "isdir", lambda p: str(p) in (str(bin1), str(bin2)))
    # garante que PATH não contenha nossos bins inicialmente
    monkeypatch.setenv("PATH", os.pathsep.join(os.environ.get("PATH", "").split(os.pathsep)))
    yield

def test_path_injection_and_logging(monkeypatch, caplog):
    import geoifsc.raster_uploader_service as rus
    s = rus.RasterUploaderService()
    # o primeiro caminho injetado deve ser bin1
    assert str(bin1) in os.environ["PATH"].split(os.pathsep)[0]
    # verifica log
    assert any("Adicionado ao PATH" in rec.getMessage() for rec in caplog.records)

def test_find_executables(monkeypatch):
    import geoifsc.raster_uploader_service as rus
    s = rus.RasterUploaderService()
    p = s.find_raster2pgsql()
    assert p and p.lower().endswith("raster2pgsql.exe")
    p2 = s.find_psql()
    assert p2 and p2.lower().endswith("psql.exe")
