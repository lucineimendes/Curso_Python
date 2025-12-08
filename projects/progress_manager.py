"""
Módulo para gerenciamento de progresso do usuário.

Este módulo gerencia o progresso do usuário através dos cursos,
lições e exercícios, incluindo estatísticas e histórico.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProgressManager:
    """
    Gerencia o progresso do usuário através dos cursos.

    Armazena informações sobre lições completadas, exercícios resolvidos,
    tempo gasto e estatísticas gerais.
    """

    def __init__(self, data_dir_path_str="data"):
        """
        Inicializa o ProgressManager.

        Args:
            data_dir_path_str (str): Caminho para o diretório de dados.
        """
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / data_dir_path_str
        self.progress_file = self.data_dir / "user_progress.json"

        self._ensure_progress_file_exists()
        self.progress_data = self._load_progress()
        logger.info(f"ProgressManager inicializado. Dados em: {self.progress_file}")

    def _ensure_progress_file_exists(self):
        """Garante que o arquivo de progresso existe."""
        try:
            if not self.progress_file.exists():
                initial_data = {
                    "users": {},
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                }
                with open(self.progress_file, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=4)
                logger.info(f"Arquivo de progresso criado em: {self.progress_file}")
        except OSError as e:
            logger.error(f"Erro ao criar arquivo de progresso: {e}", exc_info=True)

    def _load_progress(self) -> dict:
        """Carrega dados de progresso do arquivo JSON."""
        if not self.progress_file.exists():
            return {"users": {}}

        try:
            with open(self.progress_file, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON de '{self.progress_file}'", exc_info=True)
            return {"users": {}}
        except OSError as e:
            logger.error(f"Erro de I/O ao ler '{self.progress_file}': {e}", exc_info=True)
            return {"users": {}}

    def _save_progress(self):
        """Salva dados de progresso no arquivo JSON."""
        try:
            self.progress_data["last_updated"] = datetime.now().isoformat()
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self.progress_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Progresso salvo em {self.progress_file}")
        except OSError as e:
            logger.error(f"Erro ao salvar progresso: {e}", exc_info=True)

    def get_user_progress(self, user_id: str = "default") -> dict:
        """
        Retorna o progresso de um usuário específico.

        Args:
            user_id (str): ID do usuário.

        Returns:
            dict: Dados de progresso do usuário.
        """
        if user_id not in self.progress_data.get("users", {}):
            self.progress_data.setdefault("users", {})[user_id] = {
                "courses": {},
                "total_lessons_completed": 0,
                "total_exercises_completed": 0,
                "achievements": [],
                "achievement_stats": {"perfect_exercises_count": 0, "lessons_in_day": 0, "last_lesson_date": None},
                "created_at": datetime.now().isoformat(),
            }
            self._save_progress()

        return self.progress_data["users"][user_id]

    def get_course_progress(self, user_id: str, course_id: str) -> dict:
        """
        Retorna o progresso de um curso específico.

        Args:
            user_id (str): ID do usuário.
            course_id (str): ID do curso.

        Returns:
            dict: Progresso do curso.
        """
        user_progress = self.get_user_progress(user_id)

        if course_id not in user_progress.get("courses", {}):
            user_progress.setdefault("courses", {})[course_id] = {
                "lessons": {},
                "exercises": {},
                "started_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "completed": False,
            }
            self._save_progress()

        return user_progress["courses"][course_id]

    def mark_lesson_complete(self, user_id: str, course_id: str, lesson_id: str) -> dict:
        """
        Marca uma lição como completa.

        Args:
            user_id (str): ID do usuário.
            course_id (str): ID do curso.
            lesson_id (str): ID da lição.

        Returns:
            dict: Progresso atualizado do curso.
        """
        course_progress = self.get_course_progress(user_id, course_id)

        if lesson_id not in course_progress["lessons"]:
            course_progress["lessons"][lesson_id] = {
                "completed": True,
                "completed_at": datetime.now().isoformat(),
                "times_viewed": 1,
            }

            # Atualizar contador global
            user_progress = self.get_user_progress(user_id)
            user_progress["total_lessons_completed"] = user_progress.get("total_lessons_completed", 0) + 1

            # Atualizar estatísticas de conquistas (lições por dia)
            stats = user_progress.setdefault(
                "achievement_stats", {"perfect_exercises_count": 0, "lessons_in_day": 0, "last_lesson_date": None}
            )

            today = datetime.now().date().isoformat()
            if stats.get("last_lesson_date") != today:
                stats["lessons_in_day"] = 1
                stats["last_lesson_date"] = today
            else:
                stats["lessons_in_day"] = stats.get("lessons_in_day", 0) + 1

        else:
            course_progress["lessons"][lesson_id]["completed"] = True
            course_progress["lessons"][lesson_id]["completed_at"] = datetime.now().isoformat()

        course_progress["last_accessed"] = datetime.now().isoformat()
        self._save_progress()

        logger.info(f"Lição '{lesson_id}' marcada como completa para usuário '{user_id}'")
        return course_progress

    def mark_exercise_attempt(self, user_id: str, course_id: str, exercise_id: str, success: bool = False) -> dict:
        """
        Registra uma tentativa de exercício (sucesso ou falha).

        Args:
            user_id (str): ID do usuário.
            course_id (str): ID do curso.
            exercise_id (str): ID do exercício.
            success (bool): Se a tentativa foi bem-sucedida.

        Returns:
            dict: Progresso atualizado do curso com estatísticas de tentativas.
        """
        course_progress = self.get_course_progress(user_id, course_id)

        if exercise_id not in course_progress["exercises"]:
            course_progress["exercises"][exercise_id] = {
                "completed": False,
                "completed_at": None,
                "attempts": 0,
                "successful_attempts": 0,
                "failed_attempts": 0,
                "first_attempt_success": False,
                "last_attempt_at": None,
            }

        exercise_data = course_progress["exercises"][exercise_id]
        exercise_data["attempts"] = exercise_data.get("attempts", 0) + 1
        exercise_data["last_attempt_at"] = datetime.now().isoformat()

        if success:
            exercise_data["successful_attempts"] = exercise_data.get("successful_attempts", 0) + 1

            # Marcar como completo na primeira tentativa bem-sucedida
            if not exercise_data.get("completed", False):
                exercise_data["completed"] = True
                exercise_data["completed_at"] = datetime.now().isoformat()
                exercise_data["first_attempt_success"] = exercise_data["attempts"] == 1

                # Atualizar contador global
                user_progress = self.get_user_progress(user_id)
                user_progress["total_exercises_completed"] = user_progress.get("total_exercises_completed", 0) + 1

                # Atualizar estatísticas de conquistas (exercícios perfeitos)
                if exercise_data["first_attempt_success"]:
                    stats = user_progress.setdefault(
                        "achievement_stats",
                        {"perfect_exercises_count": 0, "lessons_in_day": 0, "last_lesson_date": None},
                    )
                    stats["perfect_exercises_count"] = stats.get("perfect_exercises_count", 0) + 1
        else:
            exercise_data["failed_attempts"] = exercise_data.get("failed_attempts", 0) + 1

        course_progress["last_accessed"] = datetime.now().isoformat()
        self._save_progress()

        logger.info(
            f"Tentativa de exercício '{exercise_id}' registrada - Sucesso: {success}, Total tentativas: {exercise_data['attempts']}"
        )
        return course_progress

    def mark_exercise_complete(
        self, user_id: str, course_id: str, exercise_id: str, success: bool = True, attempts: int = 1
    ) -> dict:
        """
        Marca um exercício como completo (método legado, use mark_exercise_attempt).

        Args:
            user_id (str): ID do usuário.
            course_id (str): ID do curso.
            exercise_id (str): ID do exercício.
            success (bool): Se o exercício foi completado com sucesso.
            attempts (int): Número de tentativas.

        Returns:
            dict: Progresso atualizado do curso.
        """
        return self.mark_exercise_attempt(user_id, course_id, exercise_id, success)

    def _mark_exercise_complete_old(
        self, user_id: str, course_id: str, exercise_id: str, success: bool = True, attempts: int = 1
    ) -> dict:
        """Método antigo mantido para compatibilidade."""
        course_progress = self.get_course_progress(user_id, course_id)

        if exercise_id not in course_progress["exercises"]:
            course_progress["exercises"][exercise_id] = {
                "completed": success,
                "completed_at": datetime.now().isoformat() if success else None,
                "attempts": attempts,
                "first_attempt_success": success and attempts == 1,
            }

            if success:
                user_progress = self.get_user_progress(user_id)
                user_progress["total_exercises_completed"] = user_progress.get("total_exercises_completed", 0) + 1
        else:
            exercise_data = course_progress["exercises"][exercise_id]
            exercise_data["attempts"] = exercise_data.get("attempts", 0) + attempts

            if success and not exercise_data.get("completed", False):
                exercise_data["completed"] = True
                exercise_data["completed_at"] = datetime.now().isoformat()

                user_progress = self.get_user_progress(user_id)
                user_progress["total_exercises_completed"] = user_progress.get("total_exercises_completed", 0) + 1

        course_progress["last_accessed"] = datetime.now().isoformat()
        self._save_progress()

        logger.info(f"Exercício '{exercise_id}' atualizado para usuário '{user_id}'")
        return course_progress

    def get_course_statistics(self, user_id: str, course_id: str, total_lessons: int, total_exercises: int) -> dict:
        """
        Calcula estatísticas de progresso de um curso.

        Args:
            user_id (str): ID do usuário.
            course_id (str): ID do curso.
            total_lessons (int): Total de lições no curso.
            total_exercises (int): Total de exercícios no curso.

        Returns:
            dict: Estatísticas do curso.
        """
        course_progress = self.get_course_progress(user_id, course_id)

        completed_lessons = sum(
            1 for lesson in course_progress.get("lessons", {}).values() if lesson.get("completed", False)
        )

        completed_exercises = sum(
            1 for exercise in course_progress.get("exercises", {}).values() if exercise.get("completed", False)
        )

        lessons_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        exercises_percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        overall_percentage = (lessons_percentage + exercises_percentage) / 2

        return {
            "course_id": course_id,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "lessons_percentage": round(lessons_percentage, 2),
            "completed_exercises": completed_exercises,
            "total_exercises": total_exercises,
            "exercises_percentage": round(exercises_percentage, 2),
            "overall_percentage": round(overall_percentage, 2),
            "is_complete": completed_lessons == total_lessons and completed_exercises == total_exercises,
            "started_at": course_progress.get("started_at"),
            "last_accessed": course_progress.get("last_accessed"),
        }

    def get_all_statistics(self, user_id: str = "default") -> dict:
        """
        Retorna estatísticas gerais do usuário.

        Args:
            user_id (str): ID do usuário.

        Returns:
            dict: Estatísticas gerais.
        """
        user_progress = self.get_user_progress(user_id)

        total_courses = len(user_progress.get("courses", {}))
        completed_courses = sum(
            1 for course in user_progress.get("courses", {}).values() if course.get("completed", False)
        )

        return {
            "user_id": user_id,
            "total_courses_started": total_courses,
            "total_courses_completed": completed_courses,
            "total_lessons_completed": user_progress.get("total_lessons_completed", 0),
            "total_exercises_completed": user_progress.get("total_exercises_completed", 0),
            "achievements_count": len(user_progress.get("achievements", [])),
            "created_at": user_progress.get("created_at"),
        }

    def unlock_achievement(self, user_id: str, achievement_id: str) -> bool:
        """
        Desbloqueia uma conquista para o usuário.

        Args:
            user_id (str): ID do usuário.
            achievement_id (str): ID da conquista.

        Returns:
            bool: True se a conquista foi desbloqueada (era nova), False se já possuía.
        """
        user_progress = self.get_user_progress(user_id)
        achievements = user_progress.setdefault("achievements", [])

        # Verifica se já possui a conquista
        for ach in achievements:
            if ach["id"] == achievement_id:
                return False

        # Adiciona nova conquista
        achievements.append({"id": achievement_id, "unlocked_at": datetime.now().isoformat()})
        self._save_progress()
        logger.info(f"Conquista '{achievement_id}' desbloqueada para usuário '{user_id}'")
        return True

    def get_unlocked_achievements(self, user_id: str) -> List[Dict]:
        """
        Retorna lista de conquistas desbloqueadas do usuário.

        Args:
            user_id (str): ID do usuário.

        Returns:
            List[Dict]: Lista de conquistas desbloqueadas.
        """
        user_progress = self.get_user_progress(user_id)
        return user_progress.get("achievements", [])
