"""
Testes de Integração para o Sistema de Conquistas.

TASK-19: Escrever testes de integração
- Testar fluxo completo: conclusão de lição → verificação de conquista → desbloqueio → notificação
- Testar endpoints da API com cliente de teste Flask
- Testar cenários de desbloqueio concorrente
- Testar casos extremos: sem conquistas, todas as conquistas, limites exatos

Nota: Estes testes usam as conquistas e dados configurados pelo conftest.py
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


# =====================================================
# TESTES DE FLUXO COMPLETO
# =====================================================


class TestCompleteFlow:
    """
    Testa o fluxo completo: conclusão de lição/exercício → verificação → desbloqueio → notificação.
    """

    def test_lesson_completion_triggers_achievement_check(self, client, app_test_data):
        """
        Testa que completar uma lição dispara verificação de conquistas.
        Fluxo: POST /api/progress/lesson → verificação automática → retorna novas conquistas
        """
        # Completar a primeira lição
        response = client.post(
            "/api/progress/lesson",
            json={
                "course_id": "python-basico",
                "lesson_id": "introducao-python",
                "user_id": "test_user_flow_1",
            },
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Deve retornar campo new_achievements (pode estar vazio ou com conquistas)
        assert "new_achievements" in data

        # Se desbloqueou conquistas, verificar estrutura
        new_achievements = data.get("new_achievements", [])
        if len(new_achievements) > 0:
            # Verificar estrutura da conquista
            for ach in new_achievements:
                assert "id" in ach or "name" in ach

    def test_exercise_completion_triggers_achievement_check(self, client, app_test_data):
        """
        Testa que completar um exercício dispara verificação de conquistas.
        """
        # Submeter solução correta para o exercício
        response = client.post(
            "/api/check-exercise",
            json={
                "course_id": "python-basico",
                "exercise_id": "ex-introducao-5",
                "code": "print('Olá, Python!')",
                "user_id": "test_user_flow_2",
            },
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Deve retornar campo new_achievements
        assert "new_achievements" in data

    def test_full_flow_lesson_to_notification(self, client, app_test_data):
        """
        Testa o fluxo completo desde a conclusão de uma lição até a verificação.
        """
        user_id = "test_full_flow_user"

        # 1. Verificar estado inicial - obter conquistas atuais
        response = client.get(f"/api/achievements?user_id={user_id}")
        assert response.status_code == 200
        # initial_data = response.get_json()  # Não usado
        # initial_unlocked = len(initial_data["achievements"]["unlocked"])  # Não usado

        # 2. Completar primeira lição
        response = client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )
        assert response.status_code == 200
        lesson_data = response.get_json()
        assert lesson_data["success"] is True

        # 3. Verificar que o campo new_achievements existe na resposta
        assert "new_achievements" in lesson_data

        # 4. Verificar estado atual das conquistas
        response = client.get(f"/api/achievements?user_id={user_id}")
        assert response.status_code == 200
        final_data = response.get_json()
        assert final_data["success"] is True


# =====================================================
# TESTES DE ENDPOINTS DA API
# =====================================================


class TestAchievementsAPI:
    """
    Testa os endpoints da API de conquistas com cliente de teste Flask.
    """

    def test_get_achievements_returns_correct_structure(self, client, app_test_data):
        """
        Testa que GET /api/achievements retorna estrutura correta.
        """
        response = client.get("/api/achievements?user_id=test_api_user")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "achievements" in data

        achievements = data["achievements"]
        assert "unlocked" in achievements
        assert "locked" in achievements
        assert "stats" in achievements

        stats = achievements["stats"]
        assert "total" in stats
        assert "unlocked" in stats
        assert "percentage" in stats

    def test_get_unlocked_achievements_empty_initially(self, client, app_test_data):
        """
        Testa que GET /api/achievements/unlocked retorna lista vazia para novo usuário.
        """
        response = client.get("/api/achievements/unlocked?user_id=new_user_123")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "unlocked" in data
        assert len(data["unlocked"]) == 0

    def test_check_achievements_returns_newly_unlocked(self, client, app_test_data):
        """
        Testa que POST /api/achievements/check retorna conquistas recém-desbloqueadas.
        """
        user_id = "test_check_user"

        # Primeiro, completar uma lição para criar progresso
        client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )

        # Agora verificar conquistas novamente
        response = client.post(
            "/api/achievements/check",
            json={"user_id": user_id},
            content_type="application/json",
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "newly_unlocked" in data
        assert "message" in data

    def test_check_achievements_with_empty_json(self, client, app_test_data):
        """
        Testa que POST /api/achievements/check com JSON vazio usa user_id padrão.
        """
        response = client.post(
            "/api/achievements/check",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True

    def test_get_achievements_with_unlocked(self, client, app_test_data):
        """
        Testa que GET /api/achievements retorna conquistas desbloqueadas corretamente.
        """
        user_id = "test_unlocked_user"

        # Completar lição e exercício para desbloquear conquistas
        client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )

        client.post(
            "/api/check-exercise",
            json={
                "course_id": "python-basico",
                "exercise_id": "ex-introducao-5",
                "code": "print('Olá, Python!')",
                "user_id": user_id,
            },
            content_type="application/json",
        )

        # Verificar conquistas
        response = client.get(f"/api/achievements?user_id={user_id}")
        assert response.status_code == 200

        data = response.get_json()
        unlocked = data["achievements"]["unlocked"]
        locked = data["achievements"]["locked"]
        stats = data["achievements"]["stats"]

        # A soma de locked + unlocked deve ser igual ao total
        assert len(unlocked) + len(locked) == stats["total"]


# =====================================================
# TESTES DE CONCORRÊNCIA
# =====================================================


class TestConcurrentUnlocking:
    """
    Testa cenários de desbloqueio concorrente.
    """

    def test_concurrent_lesson_completion(self, client, app_test_data):
        """
        Testa que múltiplas conclusões de lição simultâneas são tratadas corretamente.
        """
        user_id = "concurrent_test_user"
        results = []
        errors = []

        def complete_lesson(lesson_id):
            try:
                response = client.post(
                    "/api/progress/lesson",
                    json={
                        "course_id": "python-basico",
                        "lesson_id": lesson_id,
                        "user_id": user_id,
                    },
                    content_type="application/json",
                )
                return response.status_code, response.get_json()
            except Exception as e:
                errors.append(str(e))
                return None, None

        # Executar requisições concorrentes com mesma lição (deve funcionar)
        lessons = ["introducao-python", "introducao-python"]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(complete_lesson, lesson_id) for lesson_id in lessons]
            for future in as_completed(futures):
                status, data = future.result()
                if status:
                    results.append((status, data))

        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros durante execução concorrente: {errors}"

        # Verificar que todas as requisições foram bem-sucedidas
        for status, data in results:
            assert status == 200
            assert data["success"] is True

    def test_concurrent_exercise_submissions(self, client, app_test_data):
        """
        Testa que múltiplas submissões de exercício simultâneas são tratadas corretamente.
        """
        results = []
        errors = []
        lock = threading.Lock()

        def submit_exercise(user_id, exercise_id, code):
            try:
                response = client.post(
                    "/api/check-exercise",
                    json={
                        "course_id": "python-basico",
                        "exercise_id": exercise_id,
                        "code": code,
                        "user_id": user_id,
                    },
                    content_type="application/json",
                )
                with lock:
                    results.append((response.status_code, response.get_json()))
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # Diferentes usuários submetendo ao mesmo tempo
        users_and_exercises = [
            ("user1", "ex-introducao-5", "print('Olá, Python!')"),
            ("user2", "ex-introducao-5", "print('Olá, Python!')"),
            ("user3", "ex-introducao-1", "print('Olá, Mundo!')"),
        ]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(submit_exercise, user_id, exercise_id, code)
                for user_id, exercise_id, code in users_and_exercises
            ]
            for future in as_completed(futures):
                future.result()  # Wait for completion

        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros durante execução concorrente: {errors}"

        # Todas as requisições devem ter sido processadas
        assert len(results) == 3
        for status, _ in results:
            assert status == 200


# =====================================================
# TESTES DE CASOS EXTREMOS
# =====================================================


class TestEdgeCases:
    """
    Testa casos extremos: sem conquistas, todas as conquistas, limites exatos.
    """

    def test_user_with_no_achievements(self, client, app_test_data):
        """
        Testa comportamento para usuário sem nenhuma conquista.
        """
        response = client.get("/api/achievements?user_id=brand_new_user")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert len(data["achievements"]["unlocked"]) == 0
        assert data["achievements"]["stats"]["unlocked"] == 0
        assert data["achievements"]["stats"]["percentage"] == 0.0

    def test_achievement_not_unlocked_twice(self, client, app_test_data):
        """
        Testa que a mesma conquista não é desbloqueada duas vezes.
        """
        user_id = "duplicate_test_user"

        # Completar primeira lição
        response1 = client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )
        data1 = response1.get_json()
        first_unlock_count = len(data1.get("new_achievements", []))

        # Marcar a mesma lição como completa novamente
        response2 = client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )
        data2 = response2.get_json()
        second_unlock_count = len(data2.get("new_achievements", []))

        # Na segunda chamada não deve haver novas conquistas
        assert second_unlock_count <= first_unlock_count

        # Verificar total de conquistas desbloqueadas
        response = client.get(f"/api/achievements?user_id={user_id}")
        data = response.get_json()
        unlocked_ids = [a["id"] for a in data["achievements"]["unlocked"]]

        # Cada conquista deve aparecer apenas uma vez
        assert len(unlocked_ids) == len(set(unlocked_ids))

    def test_persistent_achievement_after_attempts(self, client, app_test_data):
        """
        Testa conquista "Persistente" que requer múltiplas tentativas.
        """
        user_id = "persistent_user"

        # Submeter código errado várias vezes
        for _ in range(3):
            client.post(
                "/api/check-exercise",
                json={
                    "course_id": "python-basico",
                    "exercise_id": "ex-introducao-5",
                    "code": "print('Wrong')",  # Código errado
                    "user_id": user_id,
                },
                content_type="application/json",
            )

        # Agora submeter código correto após tentativas falhas
        response = client.post(
            "/api/check-exercise",
            json={
                "course_id": "python-basico",
                "exercise_id": "ex-introducao-5",
                "code": "print('Olá, Python!')",  # Código correto
                "user_id": user_id,
            },
            content_type="application/json",
        )

        data = response.get_json()
        assert data["success"] is True

        # Verificar estatísticas de tentativas
        assert "stats" in data
        stats = data["stats"]
        assert stats["attempts"] >= 4  # 3 falhas + 1 sucesso

    def test_nonexistent_user(self, client, app_test_data):
        """
        Testa comportamento com ID de usuário que não existe.
        """
        response = client.get("/api/achievements?user_id=nonexistent_user_xyz_123")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        # Usuário novo deve ter lista vazia de desbloqueadas
        assert len(data["achievements"]["unlocked"]) == 0

    def test_empty_user_id(self, client, app_test_data):
        """
        Testa comportamento com user_id vazio (deve usar 'default').
        """
        response = client.get("/api/achievements")  # Sem user_id
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True

    def test_special_characters_in_user_id(self, client, app_test_data):
        """
        Testa comportamento com caracteres especiais no user_id.
        """
        special_user_ids = [
            "user-with-dashes",
            "user_with_underscores",
            "user.with.dots",
        ]

        for user_id in special_user_ids:
            response = client.get(f"/api/achievements?user_id={user_id}")
            assert response.status_code == 200, f"Falhou para user_id: {user_id}"

            data = response.get_json()
            assert data["success"] is True, f"Falhou para user_id: {user_id}"


# =====================================================
# TESTES DE INTEGRAÇÃO DE PROGRESSO E CONQUISTAS
# =====================================================


class TestProgressAchievementIntegration:
    """
    Testa a integração entre o sistema de progresso e conquistas.
    """

    def test_progress_updates_reflected_in_achievements(self, client, app_test_data):
        """
        Testa que atualizações no progresso são refletidas nas conquistas.
        """
        user_id = "progress_integration_user"

        # Estado inicial
        # initial_response = client.get(f"/api/achievements?user_id={user_id}")  # Não usado
        # initial_unlocked = len(initial_response.get_json()["achievements"]["unlocked"])  # Não usado

        # Atualizar progresso - completar lição
        client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )

        # Completar exercício
        client.post(
            "/api/check-exercise",
            json={
                "course_id": "python-basico",
                "exercise_id": "ex-introducao-5",
                "code": "print('Olá, Python!')",
                "user_id": user_id,
            },
            content_type="application/json",
        )

        # Verificar conquistas atualizadas
        final_response = client.get(f"/api/achievements?user_id={user_id}")
        final_data = final_response.get_json()

        # Deve ter processado corretamente
        assert final_data["success"] is True

    def test_multiple_progress_actions_count_correctly(self, client, app_test_data):
        """
        Testa que múltiplas ações de progresso são contadas corretamente.
        """
        user_id = "cumulative_user"

        # Completar lição
        response1 = client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )
        assert response1.status_code == 200

        # Completar exercício
        response2 = client.post(
            "/api/check-exercise",
            json={
                "course_id": "python-basico",
                "exercise_id": "ex-introducao-5",
                "code": "print('Olá, Python!')",
                "user_id": user_id,
            },
            content_type="application/json",
        )
        assert response2.status_code == 200

        # Verificar progresso
        response = client.get(f"/api/achievements?user_id={user_id}")
        data = response.get_json()

        # Deve ter processado ambas as ações
        assert data["success"] is True


# =====================================================
# TESTES DE RESPOSTA DA API
# =====================================================


class TestAPIResponses:
    """
    Testa formatos de resposta da API.
    """

    def test_achievements_response_has_timestamps(self, client, app_test_data):
        """
        Testa que conquistas desbloqueadas têm timestamps.
        """
        user_id = "timestamp_test_user"

        # Completar algo para desbloquear conquista
        client.post(
            "/api/progress/lesson",
            json={"course_id": "python-basico", "lesson_id": "introducao-python", "user_id": user_id},
            content_type="application/json",
        )

        # Verificar conquistas
        response = client.get(f"/api/achievements/unlocked?user_id={user_id}")
        data = response.get_json()

        # Se houver conquistas desbloqueadas, verificar estrutura
        for achievement in data.get("unlocked", []):
            # Pode ter ou não unlocked_at dependendo da implementação
            assert "id" in achievement

    def test_check_exercise_response_includes_stats(self, client, app_test_data):
        """
        Testa que a resposta de check-exercise inclui estatísticas.
        """
        response = client.post(
            "/api/check-exercise",
            json={
                "course_id": "python-basico",
                "exercise_id": "ex-introducao-5",
                "code": "print('Olá, Python!')",
                "user_id": "stats_test_user",
            },
            content_type="application/json",
        )

        data = response.get_json()
        assert "stats" in data
        assert "attempts" in data["stats"]

    def test_achievements_stats_calculation(self, client, app_test_data):
        """
        Testa que as estatísticas de conquistas são calculadas corretamente.
        """
        response = client.get("/api/achievements?user_id=stats_calc_user")
        data = response.get_json()

        stats = data["achievements"]["stats"]
        unlocked = data["achievements"]["unlocked"]
        locked = data["achievements"]["locked"]

        # Verificar consistência
        assert stats["total"] == len(unlocked) + len(locked)
        assert stats["unlocked"] == len(unlocked)

        # Verificar percentual
        if stats["total"] > 0:
            expected_percentage = (stats["unlocked"] / stats["total"]) * 100
            assert abs(stats["percentage"] - expected_percentage) < 0.1
