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

    def get_user_achievements(self, user_id: str, progress_manager) -> Dict:
        """
        Retorna conquistas do usuário com status de desbloqueio.

        Args:
            user_id (str): ID do usuário.
            progress_manager: Instância do ProgressManager para acessar dados do usuário.

        Returns:
            Dict: Dicionário contendo:
                - unlocked: Lista de conquistas desbloqueadas com timestamps
                - locked: Lista de conquistas bloqueadas
                - stats: Estatísticas (total, unlocked, percentage)
        """
        user_progress = progress_manager.get_user_progress(user_id)
        unlocked_achievements_data = user_progress.get("achievements", [])
        unlocked_ids = {a["id"] for a in unlocked_achievements_data}

        unlocked = []
        locked = []

        for achievement in self.achievements:
            ach_id = achievement["id"]
            if ach_id in unlocked_ids:
                # Encontrar dados de desbloqueio
                unlock_data = next((a for a in unlocked_achievements_data if a["id"] == ach_id), None)
                unlocked_at = unlock_data.get("unlocked_at") if unlock_data else None

                unlocked.append({**achievement, "unlocked": True, "unlocked_at": unlocked_at})
            else:
                locked.append({**achievement, "unlocked": False})

        # Ordenar conquistas desbloqueadas por timestamp (ordem cronológica)
        unlocked.sort(key=lambda x: x.get("unlocked_at", ""))

        total = len(self.achievements)
        unlocked_count = len(unlocked)
        percentage = (unlocked_count / total * 100) if total > 0 else 0.0

        return {
            "unlocked": unlocked,
            "locked": locked,
            "stats": {"total": total, "unlocked": unlocked_count, "percentage": round(percentage, 2)},
        }

    def unlock_achievement(self, user_id: str, achievement_id: str, progress_manager) -> bool:
        """
        Desbloqueia uma conquista específica para um usuário.

        Args:
            user_id (str): ID do usuário.
            achievement_id (str): ID da conquista a ser desbloqueada.
            progress_manager: Instância do ProgressManager para persistir o desbloqueio.

        Returns:
            bool: True se desbloqueou (era nova), False se já estava desbloqueada.
        """
        # Verificar se a conquista existe
        achievement_exists = any(a["id"] == achievement_id for a in self.achievements)
        if not achievement_exists:
            logger.warning(
                f"Tentativa de desbloquear conquista inexistente: achievement_id='{achievement_id}', user_id='{user_id}'"
            )
            return False

        # Delegar para o ProgressManager que já implementa a persistência
        was_unlocked = progress_manager.unlock_achievement(user_id, achievement_id)

        if was_unlocked:
            # Obter nome da conquista para logging mais informativo
            achievement_name = next((a["name"] for a in self.achievements if a["id"] == achievement_id), achievement_id)
            logger.info(
                f"Conquista desbloqueada: achievement_id='{achievement_id}', "
                f"achievement_name='{achievement_name}', user_id='{user_id}'"
            )
        else:
            logger.debug(f"Conquista já estava desbloqueada: achievement_id='{achievement_id}', user_id='{user_id}'")

        return was_unlocked

    def check_unlocks(self, user_id: str, progress_manager) -> List[Dict]:
        """
        Verifica quais conquistas devem ser desbloqueadas baseado no progresso.

        Avalia todas as condições de desbloqueio e desbloqueia conquistas elegíveis.

        Args:
            user_id (str): ID do usuário.
            progress_manager: Instância do ProgressManager para acessar dados e salvar desbloqueios.

        Returns:
            List[Dict]: Lista de conquistas recém-desbloqueadas.
        """
        import time

        start_time = time.time()
        logger.debug(f"Iniciando verificação de conquistas para user_id='{user_id}'")

        user_progress = progress_manager.get_user_progress(user_id)
        # Obter lista de IDs já desbloqueados para otimização
        unlocked_ids = {a["id"] for a in user_progress.get("achievements", [])}

        newly_unlocked = []
        conditions_evaluated = 0

        for achievement in self.achievements:
            ach_id = achievement["id"]
            if ach_id in unlocked_ids:
                continue

            condition = achievement.get("unlock_condition")
            if not condition:
                logger.warning(f"Conquista sem condição de desbloqueio: achievement_id='{ach_id}', user_id='{user_id}'")
                continue

            conditions_evaluated += 1

            try:
                if self._evaluate_condition(condition, user_progress):
                    # Tenta desbloquear (retorna True se foi desbloqueado agora)
                    if self.unlock_achievement(user_id, ach_id, progress_manager):
                        # Adicionar timestamp ao achievement retornado
                        unlocked_achievement = {
                            **achievement,
                            "unlocked_at": progress_manager.get_user_progress(user_id)
                            .get("achievements", [])[-1]
                            .get("unlocked_at"),
                        }
                        newly_unlocked.append(unlocked_achievement)
                        unlocked_ids.add(ach_id)  # Atualiza conjunto local
            except Exception as e:
                logger.error(
                    f"Erro ao avaliar condição de conquista: achievement_id='{ach_id}', "
                    f"user_id='{user_id}', condition_type='{condition.get('type')}', error='{str(e)}'",
                    exc_info=True,
                )

        elapsed_time = time.time() - start_time
        logger.info(
            f"Verificação de conquistas concluída: user_id='{user_id}', "
            f"conditions_evaluated={conditions_evaluated}, newly_unlocked={len(newly_unlocked)}, "
            f"elapsed_time={elapsed_time:.3f}s"
        )

        return newly_unlocked

    def check_new_achievements(self, user_id: str, progress_manager) -> List[Dict]:
        """
        Verifica e desbloqueia novas conquistas para o usuário.

        Método legado - use check_unlocks() para nova implementação.

        Args:
            user_id (str): ID do usuário.
            progress_manager: Instância do ProgressManager para acessar dados e salvar desbloqueios.

        Returns:
            List[Dict]: Lista de conquistas recém-desbloqueadas.
        """
        return self.check_unlocks(user_id, progress_manager)

    def _is_course_complete(self, progress_data: Dict, course_id: str) -> bool:
        """
        Verifica se todas as lições em um curso estão completas.

        Args:
            progress_data (Dict): Dados de progresso do usuário.
            course_id (str): ID do curso a verificar.

        Returns:
            bool: True se todas as lições do curso estão completas, False caso contrário.
        """
        courses = progress_data.get("courses", {})
        course_progress = courses.get(course_id, {})

        # Um curso é considerado completo se tem o campo 'completed' como True
        # ou se todas as suas lições estão completas
        if course_progress.get("completed", False):
            return True

        # Verificar se todas as lições estão completas
        lessons = course_progress.get("lessons", {})
        if not lessons:
            return False

        # Todas as lições devem estar marcadas como completas
        return all(lesson.get("completed", False) for lesson in lessons.values())

    def _are_all_courses_complete(self, progress_data: Dict) -> bool:
        """
        Verifica se todos os três cursos estão completos.

        Args:
            progress_data (Dict): Dados de progresso do usuário.

        Returns:
            bool: True se todos os três cursos (básico, intermediário, avançado) estão completos.
        """
        required_courses = ["python-basico", "python-intermediario", "python-avancado"]

        for course_id in required_courses:
            if not self._is_course_complete(progress_data, course_id):
                return False

        return True

    def _has_exercise_after_attempts(self, progress_data: Dict, min_attempts: int) -> bool:
        """
        Verifica se o usuário completou algum exercício após um número mínimo de tentativas.

        Args:
            progress_data (Dict): Dados de progresso do usuário.
            min_attempts (int): Número mínimo de tentativas necessárias.

        Returns:
            bool: True se existe pelo menos um exercício completado após min_attempts tentativas.
        """
        courses = progress_data.get("courses", {})

        for course_progress in courses.values():
            exercises = course_progress.get("exercises", {})

            for exercise_data in exercises.values():
                # Verificar se o exercício está completo e teve pelo menos min_attempts tentativas
                if exercise_data.get("completed", False) and exercise_data.get("attempts", 0) >= min_attempts:
                    return True

        return False
