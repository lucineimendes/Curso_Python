"""
Módulo para gerenciamento de conquistas e badges.

Este módulo gerencia o sistema de conquistas, incluindo carregamento de definições,
validação, verificação de condições de desbloqueio e persistência de conquistas desbloqueadas.

Refatorado seguindo princípios SOLID:
- Single Responsibility: Cada classe tem uma responsabilidade única
- Open/Closed: Extensível via Strategy Pattern
- Dependency Inversion: Depende de abstrações (validators, evaluators)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

try:
    from .condition_evaluator import ConditionEvaluator
    from .condition_validator import AchievementValidator
except ImportError:
    # Fallback para execução direta ou testes
    from condition_evaluator import ConditionEvaluator
    from condition_validator import AchievementValidator

logger = logging.getLogger(__name__)


class AchievementManager:
    """
    Gerencia conquistas e badges do sistema.

    Responsabilidades:
    - Carregar definições de conquistas do JSON
    - Verificar condições de desbloqueio
    - Persistir conquistas desbloqueadas
    - Fornecer dados de conquistas para a API
    """

    def __init__(self, data_dir_path_str="data", validator=None, evaluator=None):
        """
        Inicializa o AchievementManager.

        Args:
            data_dir_path_str (str): Caminho para o diretório de dados.
            validator: Validador de conquistas (Dependency Injection).
            evaluator: Avaliador de condições (Dependency Injection).
        """
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / data_dir_path_str
        self.achievements_file = self.data_dir / "achievements.json"

        # Dependency Injection: permite substituir validators/evaluators para testes
        self._validator = validator or AchievementValidator()
        self._evaluator = evaluator or ConditionEvaluator()

        self.achievements = self.load_achievements()
        logger.info(
            f"AchievementManager inicializado. {len(self.achievements)} conquistas carregadas de: {self.achievements_file}"
        )

    def load_achievements(self) -> List[Dict]:
        """
        Carrega definições de conquistas do arquivo JSON.

        Returns:
            List[Dict]: Lista de definições de conquistas válidas.
        """
        if not self.achievements_file.exists():
            logger.warning(f"Arquivo de conquistas '{self.achievements_file}' não encontrado. Retornando lista vazia.")
            return []

        try:
            with open(self.achievements_file, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "achievements" not in data:
                logger.error(
                    f"Formato inválido em {self.achievements_file}. Esperava objeto com chave 'achievements'. Retornando lista vazia."
                )
                return []

            achievements_list = data.get("achievements", [])
            if not isinstance(achievements_list, list):
                logger.error("Formato inválido: 'achievements' não é uma lista. Retornando lista vazia.")
                return []

            # Validar e filtrar conquistas
            valid_achievements = []
            for achievement in achievements_list:
                if self._validate_achievement(achievement):
                    valid_achievements.append(achievement)
                else:
                    logger.warning(f"Conquista inválida ignorada: {achievement.get('id', 'ID desconhecido')}")

            logger.info(f"{len(valid_achievements)} conquistas válidas carregadas de {len(achievements_list)} total.")
            return valid_achievements

        except json.JSONDecodeError:
            logger.error(
                f"Erro ao decodificar JSON de '{self.achievements_file}'. Retornando lista vazia.",
                exc_info=True,
            )
            return []
        except OSError as e:
            logger.error(
                f"Erro de I/O ao ler '{self.achievements_file}': {e}. Retornando lista vazia.",
                exc_info=True,
            )
            return []

    def get_all_achievements(self) -> List[Dict]:
        """
        Retorna todas as definições de conquistas disponíveis.

        Returns:
            List[Dict]: Lista de todas as conquistas carregadas.
        """
        return self.achievements

    def _validate_achievement(self, achievement: Dict) -> bool:
        """
        Valida se uma definição de conquista contém todos os campos obrigatórios.

        Delegado para AchievementValidator (Single Responsibility Principle).

        Args:
            achievement (Dict): Definição de conquista a ser validada.

        Returns:
            bool: True se a conquista é válida, False caso contrário.
        """
        return self._validator.validate_achievement(achievement)

    def _evaluate_condition(self, condition: Dict, progress_data: Dict) -> bool:
        """
        Avalia se uma condição de desbloqueio foi satisfeita.

        Delegado para ConditionEvaluator (Strategy Pattern + Dependency Inversion).

        Args:
            condition (Dict): Condição de desbloqueio da conquista.
            progress_data (Dict): Dados de progresso do usuário.

        Returns:
            bool: True se a condição foi satisfeita, False caso contrário.
        """
        return self._evaluator.evaluate(condition, progress_data)
