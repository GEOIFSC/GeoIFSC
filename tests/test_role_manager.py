import pytest
from unittest.mock import MagicMock

from geoifsc.db_manager import DBManager
from geoifsc.role_manager import RoleManager


def make_conn():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    return conn, cur


def test_create_user_commits():
    conn, cur = make_conn()
    dao = DBManager(conn)
    dao.insert_user = MagicMock()
    manager = RoleManager(dao)

    manager.create_user("user1", "pw")

    dao.insert_user.assert_called_with("user1", "pw")
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_create_user_rollback_on_error():
    conn, cur = make_conn()
    dao = DBManager(conn)
    dao.insert_user = MagicMock(side_effect=Exception("fail"))
    manager = RoleManager(dao)

    with pytest.raises(Exception):
        manager.create_user("user1", "pw")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
