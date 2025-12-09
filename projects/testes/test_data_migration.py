"""
Testes unitários para migração de dados de progresso do usuário.

Testa que a migração adiciona campos achievements e achievement_stats
preservando dados existentes e tratando campos faltando.
"""

import json

import pytest


@pytest.fixture
def migration_module():
    """Importa o módulo de migração."""
    from projects import data_migration

    return data_migration


@pytest.fixture
def sample_old_progress():
    """Dados de progresso no formato antigo (sem achievements)."""
    return {
        "users": {
            "user1": {
                "courses": {
                    "python-basico": {
                        "lessons": {
                            "intro-programacao-python": {
                                "completed": True,
                                "completed_at": "2025-12-08T12:52:10.183678",
                                "times_viewed": 1,
                            }
                        },
                        "exercises": {
                            "ex-introducao-1": {
                                "completed": True,
                                "completed_at": "2025-12-03T17:50:39.333443",
                                "attempts": 1,
                                "first_attempt_success": True,
                            }
                        },
                        "started_at": "2025-12-03T17:48:26.625604",
                        "last_accessed": "2025-12-08T12:53:26.560025",
                        "completed": False,
                    }
                },
                "total_lessons_completed": 1,
                "total_exercises_completed": 1,
                "created_at": "2025-12-03T17:48:26.625209",
            }
        }
    }


@pytest.fixture
def sample_partial_progress():
    """Dados de progresso com alguns campos faltando."""
    return {
        "users": {
            "user2": {
                "courses": {},
                "total_lessons_completed": 5,
                "total_exercises_completed": 3,
                "achievements": [],  # Tem achievements mas não tem achievement_stats
                "created_at": "2025-12-01T10:00:00.000000",
            },
            "user3": {
                "courses": {},
                "total_lessons_completed": 2,
                "total_exercises_completed": 1,
                "achievement_stats": {  # Tem achievement_stats mas não tem achievements
                    "perfect_exercises_count": 1,
                    "lessons_in_day": 0,
                    "last_activity_date": None,
                },
                "created_at": "2025-12-02T10:00:00.000000",
            },
        }
    }


def test_migrate_adds_achievements_field(migration_module, sample_old_progress):
    """Testa que migração adiciona campo achievements."""
    migrated = migration_module.migrate_user_progress(sample_old_progress)

    assert "achievements" in migrated["users"]["user1"]
    assert isinstance(migrated["users"]["user1"]["achievements"], list)
    assert migrated["users"]["user1"]["achievements"] == []


def test_migrate_adds_achievement_stats_field(migration_module, sample_old_progress):
    """Testa que migração adiciona campo achievement_stats."""
    migrated = migration_module.migrate_user_progress(sample_old_progress)

    assert "achievement_stats" in migrated["users"]["user1"]
    assert isinstance(migrated["users"]["user1"]["achievement_stats"], dict)

    stats = migrated["users"]["user1"]["achievement_stats"]
    assert stats["perfect_exercises_count"] == 0
    assert stats["lessons_in_day"] == 0
    assert stats["last_activity_date"] is None


def test_migrate_preserves_existing_data(migration_module, sample_old_progress):
    """Testa que migração preserva dados existentes."""
    original_courses = sample_old_progress["users"]["user1"]["courses"]
    original_lessons = sample_old_progress["users"]["user1"]["total_lessons_completed"]
    original_exercises = sample_old_progress["users"]["user1"]["total_exercises_completed"]

    migrated = migration_module.migrate_user_progress(sample_old_progress)

    assert migrated["users"]["user1"]["courses"] == original_courses
    assert migrated["users"]["user1"]["total_lessons_completed"] == original_lessons
    assert migrated["users"]["user1"]["total_exercises_completed"] == original_exercises
    assert migrated["users"]["user1"]["created_at"] == sample_old_progress["users"]["user1"]["created_at"]


def test_migrate_handles_missing_achievements(migration_module, sample_partial_progress):
    """Testa que migração trata campo achievements faltando."""
    migrated = migration_module.migrate_user_progress(sample_partial_progress)

    # user3 não tinha achievements
    assert "achievements" in migrated["users"]["user3"]
    assert isinstance(migrated["users"]["user3"]["achievements"], list)
    assert migrated["users"]["user3"]["achievements"] == []


def test_migrate_handles_missing_achievement_stats(migration_module, sample_partial_progress):
    """Testa que migração trata campo achievement_stats faltando."""
    migrated = migration_module.migrate_user_progress(sample_partial_progress)

    # user2 não tinha achievement_stats
    assert "achievement_stats" in migrated["users"]["user2"]
    assert isinstance(migrated["users"]["user2"]["achievement_stats"], dict)

    stats = migrated["users"]["user2"]["achievement_stats"]
    assert stats["perfect_exercises_count"] == 0
    assert stats["lessons_in_day"] == 0
    assert stats["last_activity_date"] is None


def test_migrate_preserves_existing_achievements(migration_module):
    """Testa que migração preserva conquistas já existentes."""
    data = {
        "users": {
            "user_with_achievements": {
                "courses": {},
                "total_lessons_completed": 10,
                "total_exercises_completed": 5,
                "achievements": [
                    {"id": "first_lesson", "unlocked_at": "2025-12-01T10:00:00.000000"},
                    {"id": "first_exercise", "unlocked_at": "2025-12-01T11:00:00.000000"},
                ],
                "achievement_stats": {
                    "perfect_exercises_count": 3,
                    "lessons_in_day": 2,
                    "last_activity_date": "2025-12-08",
                },
                "created_at": "2025-12-01T09:00:00.000000",
            }
        }
    }

    migrated = migration_module.migrate_user_progress(data)

    # Conquistas devem ser preservadas
    assert len(migrated["users"]["user_with_achievements"]["achievements"]) == 2
    assert migrated["users"]["user_with_achievements"]["achievements"][0]["id"] == "first_lesson"
    assert migrated["users"]["user_with_achievements"]["achievements"][1]["id"] == "first_exercise"

    # Stats devem ser preservadas
    stats = migrated["users"]["user_with_achievements"]["achievement_stats"]
    assert stats["perfect_exercises_count"] == 3
    assert stats["lessons_in_day"] == 2
    assert stats["last_activity_date"] == "2025-12-08"


def test_migrate_handles_empty_users(migration_module):
    """Testa que migração trata estrutura sem usuários."""
    data = {"users": {}}
    migrated = migration_module.migrate_user_progress(data)

    assert migrated == {"users": {}}


def test_migrate_handles_multiple_users(migration_module, sample_old_progress):
    """Testa que migração processa múltiplos usuários."""
    # Adicionar mais usuários
    sample_old_progress["users"]["user2"] = {
        "courses": {},
        "total_lessons_completed": 0,
        "total_exercises_completed": 0,
        "created_at": "2025-12-08T10:00:00.000000",
    }
    sample_old_progress["users"]["user3"] = {
        "courses": {},
        "total_lessons_completed": 3,
        "total_exercises_completed": 2,
        "created_at": "2025-12-07T10:00:00.000000",
    }

    migrated = migration_module.migrate_user_progress(sample_old_progress)

    # Todos os usuários devem ter os campos
    for user_id in ["user1", "user2", "user3"]:
        assert "achievements" in migrated["users"][user_id]
        assert "achievement_stats" in migrated["users"][user_id]


def test_migrate_is_idempotent(migration_module, sample_old_progress):
    """Testa que migração pode ser executada múltiplas vezes sem problemas."""
    migrated_once = migration_module.migrate_user_progress(sample_old_progress)
    migrated_twice = migration_module.migrate_user_progress(migrated_once)

    # Resultado deve ser o mesmo
    assert migrated_once == migrated_twice


def test_migrate_file_creates_backup(migration_module, tmp_path):
    """Testa que migrate_file cria backup antes de migrar."""
    # Criar arquivo de progresso temporário
    progress_file = tmp_path / "user_progress.json"
    original_data = {
        "users": {
            "test_user": {
                "courses": {},
                "total_lessons_completed": 1,
                "total_exercises_completed": 1,
                "created_at": "2025-12-08T10:00:00.000000",
            }
        }
    }

    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(original_data, f, indent=4)

    # Executar migração
    migration_module.migrate_file(str(progress_file))

    # Verificar que backup foi criado
    backup_file = tmp_path / "user_progress.json.backup"
    assert backup_file.exists()

    # Verificar que backup contém dados originais
    with open(backup_file, encoding="utf-8") as f:
        backup_data = json.load(f)

    assert backup_data == original_data


def test_migrate_file_updates_original(migration_module, tmp_path):
    """Testa que migrate_file atualiza o arquivo original."""
    # Criar arquivo de progresso temporário
    progress_file = tmp_path / "user_progress.json"
    original_data = {
        "users": {
            "test_user": {
                "courses": {},
                "total_lessons_completed": 1,
                "total_exercises_completed": 1,
                "created_at": "2025-12-08T10:00:00.000000",
            }
        }
    }

    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(original_data, f, indent=4)

    # Executar migração
    migration_module.migrate_file(str(progress_file))

    # Verificar que arquivo foi atualizado
    with open(progress_file, encoding="utf-8") as f:
        migrated_data = json.load(f)

    assert "achievements" in migrated_data["users"]["test_user"]
    assert "achievement_stats" in migrated_data["users"]["test_user"]


def test_migrate_file_handles_nonexistent_file(migration_module, tmp_path):
    """Testa que migrate_file trata arquivo inexistente graciosamente."""
    nonexistent_file = tmp_path / "nonexistent.json"

    # Não deve lançar exceção
    result = migration_module.migrate_file(str(nonexistent_file))
    assert result is False


def test_migrate_file_handles_corrupted_json(migration_module, tmp_path):
    """Testa que migrate_file trata JSON corrompido graciosamente."""
    corrupted_file = tmp_path / "corrupted.json"

    with open(corrupted_file, "w", encoding="utf-8") as f:
        f.write("{invalid json content")

    # Não deve lançar exceção
    result = migration_module.migrate_file(str(corrupted_file))
    assert result is False
