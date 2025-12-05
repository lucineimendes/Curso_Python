"""
Testes baseados em propriedades para o sistema de conquistas.

Este módulo contém testes de propriedades usando Hypothesis para validar
o comportamento do AchievementManager em relação às propriedades de corretude
definidas no documento de design.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from hypothesis import HealthCheck, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from projects.achievement_manager import AchievementManager  # noqa: E402

# Estratégias de geração de dados para Hypothesis

# Tipos de condição válidos
VALID_CONDITION_TYPES = [
    "lesson_count",
    "exercise_count",
    "perfect_exercises",
    "lessons_in_day",
    "course_complete",
    "all_courses_complete",
    "exercise_after_attempts",
]

# Tipos que requerem 'value'
CONDITIONS_WITH_VALUE = [
    "lesson_count",
    "exercise_count",
    "perfect_exercises",
    "lessons_in_day",
    "exercise_after_attempts",
]


@st.composite
def valid_unlock_condition(draw):
    """Gera uma condição de desbloqueio válida."""
    condition_type = draw(st.sampled_from(VALID_CONDITION_TYPES))

    condition = {"type": condition_type}

    if condition_type in CONDITIONS_WITH_VALUE:
        condition["value"] = draw(st.integers(min_value=1, max_value=100))
    elif condition_type == "course_complete":
        condition["course_id"] = draw(st.sampled_from(["python-basico", "python-intermediario", "python-avancado"]))

    return condition


@st.composite
def valid_achievement(draw):
    """Gera uma definição de conquista válida."""
    achievement_id = draw(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="_-"),
        )
    )

    return {
        "id": achievement_id,
        "name": draw(st.text(min_size=1, max_size=100)),
        "description": draw(st.text(min_size=1, max_size=200)),
        "icon": draw(st.text(min_size=1, max_size=10)),
        "category": draw(st.sampled_from(["beginner", "skill", "dedication", "completion", "mastery", "progress"])),
        "unlock_condition": draw(valid_unlock_condition()),
    }


@st.composite
def invalid_achievement(draw):
    """Gera uma definição de conquista inválida (faltando campos obrigatórios)."""
    # Começar com uma conquista válida
    achievement = draw(valid_achievement())

    # Escolher qual campo remover ou invalidar
    invalidation_strategy = draw(
        st.sampled_from(
            [
                "remove_id",
                "remove_name",
                "remove_description",
                "remove_icon",
                "remove_unlock_condition",
                "empty_id",
                "empty_name",
                "invalid_unlock_condition_type",
                "missing_unlock_condition_type",
                "missing_value_for_count_condition",
                "missing_course_id_for_course_complete",
                "invalid_value_type",
            ]
        )
    )

    if invalidation_strategy == "remove_id":
        del achievement["id"]
    elif invalidation_strategy == "remove_name":
        del achievement["name"]
    elif invalidation_strategy == "remove_description":
        del achievement["description"]
    elif invalidation_strategy == "remove_icon":
        del achievement["icon"]
    elif invalidation_strategy == "remove_unlock_condition":
        del achievement["unlock_condition"]
    elif invalidation_strategy == "empty_id":
        achievement["id"] = ""
    elif invalidation_strategy == "empty_name":
        achievement["name"] = ""
    elif invalidation_strategy == "invalid_unlock_condition_type":
        achievement["unlock_condition"]["type"] = "invalid_type"
    elif invalidation_strategy == "missing_unlock_condition_type":
        del achievement["unlock_condition"]["type"]
    elif invalidation_strategy == "missing_value_for_count_condition":
        # Escolher um tipo que requer value
        achievement["unlock_condition"]["type"] = draw(st.sampled_from(CONDITIONS_WITH_VALUE))
        if "value" in achievement["unlock_condition"]:
            del achievement["unlock_condition"]["value"]
    elif invalidation_strategy == "missing_course_id_for_course_complete":
        achievement["unlock_condition"]["type"] = "course_complete"
        if "course_id" in achievement["unlock_condition"]:
            del achievement["unlock_condition"]["course_id"]
    elif invalidation_strategy == "invalid_value_type":
        achievement["unlock_condition"]["type"] = draw(st.sampled_from(CONDITIONS_WITH_VALUE))
        achievement["unlock_condition"]["value"] = "not_a_number"

    return achievement


# **Feature: achievements-badges, Property 9: Validação de definição de conquista**
# **Valida: Requisitos 5.2, 5.3**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(achievement=invalid_achievement())
def test_property_9_invalid_achievement_validation(achievement):
    """
    Propriedade 9: Validação de definição de conquista.

    Para qualquer definição de conquista que está faltando campos obrigatórios
    (id, name, description, icon, unlock_condition), a função de validação deve rejeitá-la.

    **Feature: achievements-badges, Property 9: Validação de definição de conquista**
    **Valida: Requisitos 5.2, 5.3**
    """
    # Criar um diretório temporário para cada teste
    tmp_dir = tempfile.mkdtemp()
    try:
        # Criar um AchievementManager temporário
        manager = AchievementManager(data_dir_path_str=tmp_dir)

        # A conquista inválida deve ser rejeitada
        is_valid = manager._validate_achievement(achievement)

        assert not is_valid, f"Conquista inválida foi aceita: {achievement}"
    finally:
        # Limpar o diretório temporário
        shutil.rmtree(tmp_dir, ignore_errors=True)


# **Feature: achievements-badges, Property 9: Validação de definição de conquista**
# **Valida: Requisitos 5.2, 5.3**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(achievement=valid_achievement())
def test_property_9_valid_achievement_validation(achievement):
    """
    Propriedade 9: Validação de definição de conquista (caso positivo).

    Para qualquer definição de conquista válida com todos os campos obrigatórios,
    a função de validação deve aceitá-la.

    **Feature: achievements-badges, Property 9: Validação de definição de conquista**
    **Valida: Requisitos 5.2, 5.3**
    """
    # Criar um diretório temporário para cada teste
    tmp_dir = tempfile.mkdtemp()
    try:
        # Criar um AchievementManager temporário
        manager = AchievementManager(data_dir_path_str=tmp_dir)

        # A conquista válida deve ser aceita
        is_valid = manager._validate_achievement(achievement)

        assert is_valid, f"Conquista válida foi rejeitada: {achievement}"
    finally:
        # Limpar o diretório temporário
        shutil.rmtree(tmp_dir, ignore_errors=True)


# **Feature: achievements-badges, Property 4: Completude de dados de conquista**
# **Valida: Requisitos 1.3, 6.5**
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(achievements=st.lists(valid_achievement(), min_size=1, max_size=20))
def test_property_4_achievement_data_completeness(achievements):
    """
    Propriedade 4: Completude de dados de conquista.

    Para qualquer conquista sendo renderizada ou retornada pela API,
    a estrutura de dados deve conter todos os campos obrigatórios:
    id, name, description, icon e unlock_condition.

    **Feature: achievements-badges, Property 4: Completude de dados de conquista**
    **Valida: Requisitos 1.3, 6.5**
    """
    # Criar diretório de dados temporário
    tmp_dir = tempfile.mkdtemp()
    try:
        data_dir = Path(tmp_dir) / "data"
        data_dir.mkdir()

        # Criar arquivo de conquistas com as conquistas geradas
        achievements_file = data_dir / "achievements.json"
        with open(achievements_file, "w", encoding="utf-8") as f:
            json.dump({"achievements": achievements}, f, ensure_ascii=False, indent=4)

        # Criar AchievementManager e carregar conquistas
        manager = AchievementManager(data_dir_path_str=str(data_dir))

        # Obter todas as conquistas
        loaded_achievements = manager.get_all_achievements()

        # Verificar que todas as conquistas carregadas têm os campos obrigatórios
        required_fields = ["id", "name", "description", "icon", "unlock_condition"]

        for achievement in loaded_achievements:
            for field in required_fields:
                assert (
                    field in achievement
                ), f"Conquista '{achievement.get('id', 'desconhecido')}' está faltando campo obrigatório: {field}"
                assert achievement[
                    field
                ], f"Conquista '{achievement.get('id', 'desconhecido')}' tem campo vazio: {field}"

            # Verificar estrutura de unlock_condition
            unlock_condition = achievement["unlock_condition"]
            assert isinstance(
                unlock_condition, dict
            ), f"unlock_condition não é um dicionário para conquista '{achievement['id']}'"
            assert (
                "type" in unlock_condition
            ), f"unlock_condition está faltando 'type' para conquista '{achievement['id']}'"
    finally:
        # Limpar o diretório temporário
        shutil.rmtree(tmp_dir, ignore_errors=True)
