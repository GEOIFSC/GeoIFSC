"""Camada de serviços para gerenciamento de roles."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .db_manager import DBManager
from .models import User


class RoleManager:
    """Regras de negócio para gerenciamento de usuários e grupos."""

    def __init__(self, dao: DBManager, logger: Optional[logging.Logger] = None):
        self.dao = dao
        self.logger = logger or logging.getLogger(__name__)

    # ---------------------- Operações de Usuário ----------------------

    def create_user(self, username: str, password: str) -> str:
        """Cria um novo usuário e persiste a transação."""
        try:
            self.dao.insert_user(username, password)
            self.dao.conn.commit()
            self.logger.info("Usuário %s criado", username)
            return username
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao criar usuário %s", username)
            raise

    def get_user(self, username: str) -> Optional[User]:
        """Obtém dados de um usuário."""
        return self.dao.find_user_by_name(username)

    def list_users(self) -> List[str]:
        """Lista usuários registrados."""
        return self.dao.list_users()

    def update_user(self, username: str, **updates: Any) -> bool:
        """Atualiza atributos de um usuário."""
        try:
            self.dao.update_user(username, **updates)
            self.dao.conn.commit()
            self.logger.info("Usuário %s atualizado", username)
            return True
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao atualizar usuário %s", username)
            raise

    def delete_user(self, username: str) -> bool:
        """Exclui usuário."""
        try:
            self.dao.delete_user(username)
            self.dao.conn.commit()
            self.logger.info("Usuário %s removido", username)
            return True
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao remover usuário %s", username)
            raise

    def change_password(self, username: str, new_password: str) -> bool:
        """Altera a senha de um usuário."""
        try:
            self.dao.update_user(username, password=new_password)
            self.dao.conn.commit()
            self.logger.info("Senha alterada para %s", username)
            return True
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao alterar senha de %s", username)
            raise

    # ---------------------- Operações de Grupo ----------------------

    def create_group(self, group_name: str) -> str:
        """Cria um grupo."""
        try:
            self.dao.create_group(group_name)
            self.dao.conn.commit()
            self.logger.info("Grupo %s criado", group_name)
            return group_name
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao criar grupo %s", group_name)
            raise

    def add_user_to_group(self, username: str, group_name: str) -> None:
        """Adiciona usuário ao grupo."""
        try:
            self.dao.add_user_to_group(username, group_name)
            self.dao.conn.commit()
            self.logger.info("%s adicionado a %s", username, group_name)
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao adicionar %s ao grupo %s", username, group_name)
            raise

    def remove_user_from_group(self, username: str, group_name: str) -> None:
        """Remove usuário do grupo."""
        try:
            self.dao.remove_user_from_group(username, group_name)
            self.dao.conn.commit()
            self.logger.info("%s removido de %s", username, group_name)
        except Exception:
            self.dao.conn.rollback()
            self.logger.exception("Falha ao remover %s do grupo %s", username, group_name)
            raise

    def list_group_members(self, group_name: str) -> List[str]:
        """Lista membros de um grupo."""
        return self.dao.list_group_members(group_name)
