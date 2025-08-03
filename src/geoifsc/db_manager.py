"""Data Access Object for PostgreSQL roles."""
from typing import List, Optional

import psycopg2
from psycopg2 import sql

from .models import User, Group


class DBManager:
    """Encapsula operações no banco para usuários e grupos."""

    def __init__(self, connection):
        if connection is None:
            raise ValueError("Conexão inválida")
        self.conn = connection

    # ---------------------- Métodos de Usuário ----------------------

    def find_user_by_name(self, username: str) -> Optional[User]:
        """Busca usuário pelo nome."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT rolname, rolvaliduntil, rolcanlogin
                FROM pg_roles
                WHERE rolname = %s
                """,
                (username,),
            )
            row = cur.fetchone()
            if row:
                return User(username=row[0], valid_until=row[1], can_login=row[2])
        return None

    def insert_user(self, username: str, password_hash: str) -> None:
        """Cria um novo usuário."""
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD %s").format(
                    sql.Identifier(username)
                ),
                [password_hash],
            )

    def update_user(self, username: str, **fields) -> None:
        """Atualiza atributos do usuário."""
        with self.conn.cursor() as cur:
            if "valid_until" in fields:
                cur.execute(
                    sql.SQL("ALTER ROLE {} VALID UNTIL %s").format(
                        sql.Identifier(username)
                    ),
                    [fields["valid_until"],],
                )
            if "can_login" in fields:
                action = "LOGIN" if fields["can_login"] else "NOLOGIN"
                cur.execute(
                    sql.SQL("ALTER ROLE {} %s").format(sql.Identifier(username)),
                    [sql.SQL(action)],
                )

    def delete_user(self, username: str) -> None:
        """Remove usuário."""
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL("DROP ROLE {}" ).format(sql.Identifier(username)))

    def list_users(self) -> List[str]:
        """Lista usuários de acordo com filtros padrão."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT rolname
                FROM pg_roles
                WHERE rolname NOT LIKE 'pg_%' AND rolname <> 'postgres'
                ORDER BY rolname
                """
            )
            return [row[0] for row in cur.fetchall()]

    # ---------------------- Métodos de Grupo ----------------------

    def create_group(self, group_name: str) -> None:
        """Cria grupo sem permissão de login."""
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE ROLE {} NOLOGIN").format(sql.Identifier(group_name))
            )

    def add_user_to_group(self, username: str, group_name: str) -> None:
        """Adiciona usuário ao grupo."""
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("GRANT {} TO {}" ).format(
                    sql.Identifier(group_name), sql.Identifier(username)
                )
            )

    def remove_user_from_group(self, username: str, group_name: str) -> None:
        """Remove usuário do grupo."""
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("REVOKE {} FROM {}" ).format(
                    sql.Identifier(group_name), sql.Identifier(username)
                )
            )

    def list_group_members(self, group_name: str) -> List[str]:
        """Lista membros de um grupo."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.rolname
                FROM pg_auth_members m
                JOIN pg_roles r ON m.member = r.oid
                JOIN pg_roles g ON m.roleid = g.oid
                WHERE g.rolname = %s
                ORDER BY r.rolname
                """,
                (group_name,),
            )
            return [row[0] for row in cur.fetchall()]
