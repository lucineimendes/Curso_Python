"""
Testes de Performance e Otimização para o Sistema de Conquistas.

TASK-20: Testes de performance e otimização
- Testar performance de carregamento de conquistas
- Testar tempos de resposta da API
- Otimizar avaliação de condições se necessário
- Testar com grande número de conquistas
"""

import json
import logging
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

logger = logging.getLogger(__name__)


# =====================================================
# CONSTANTES DE PERFORMANCE
# =====================================================

# Limites de tempo aceitáveis (em segundos)
MAX_API_RESPONSE_TIME = 0.5  # 500ms para resposta da API
MAX_ACHIEVEMENT_CHECK_TIME = 0.1  # 100ms para verificação de conquistas
MAX_LOAD_ACHIEVEMENTS_TIME = 0.05  # 50ms para carregar conquistas
MAX_CONCURRENT_REQUESTS_TIME = 2.0  # 2s para 10 requisições concorrentes


# =====================================================
# FIXTURES DE PERFORMANCE
# =====================================================


@pytest.fixture
def performance_timer():
    """
    Fixture para medir tempo de execução.
    """

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None

        def start(self):
            self.start_time = time.perf_counter()
            return self

        def stop(self):
            self.end_time = time.perf_counter()
            self.elapsed = self.end_time - self.start_time
            return self.elapsed

        def __enter__(self):
            self.start()
            return self

        def __exit__(self, *args):
            self.stop()

    return Timer


@pytest.fixture
def large_achievements_data(tmp_path):
    """
    Gera um grande número de conquistas para testes de performance.
    """
    achievements = {"achievements": []}

    # Gerar 100 conquistas de teste
    for i in range(100):
        achievements["achievements"].append(
            {
                "id": f"perf_test_{i}",
                "name": f"Conquista de Teste {i}",
                "description": f"Descrição da conquista de teste número {i}",
                "icon": "🏆",
                "category": "performance_test",
                "unlock_condition": {"type": "exercise_count", "value": i + 1},
            }
        )

    achievements_file = tmp_path / "large_achievements.json"
    with open(achievements_file, "w", encoding="utf-8") as f:
        json.dump(achievements, f, indent=2)

    return {"file": achievements_file, "data": achievements, "count": 100}


# =====================================================
# TESTES DE CARREGAMENTO DE CONQUISTAS
# =====================================================


class TestAchievementLoadingPerformance:
    """
    Testa performance de carregamento de conquistas.
    """

    def test_load_achievements_time(self, client, app_test_data, performance_timer):
        """
        Testa que o carregamento inicial de conquistas é rápido.
        """
        times = []

        # Executar múltiplas vezes para obter média
        for _ in range(10):
            timer = performance_timer()
            timer.start()

            response = client.get("/api/achievements?user_id=perf_test_user")

            elapsed = timer.stop()
            times.append(elapsed)

            assert response.status_code == 200

        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)

        logger.info(
            f"Tempo de carregamento de conquistas - "
            f"Média: {avg_time * 1000:.2f}ms, "
            f"Min: {min_time * 1000:.2f}ms, "
            f"Max: {max_time * 1000:.2f}ms"
        )

        # O tempo médio deve estar dentro do limite
        assert avg_time < MAX_API_RESPONSE_TIME, (
            f"Tempo médio de carregamento ({avg_time * 1000:.2f}ms) "
            f"excede o limite de {MAX_API_RESPONSE_TIME * 1000:.2f}ms"
        )

    def test_load_unlocked_achievements_time(self, client, app_test_data, performance_timer):
        """
        Testa que carregar conquistas desbloqueadas é rápido.
        """
        times = []

        for _ in range(10):
            timer = performance_timer()
            timer.start()

            response = client.get("/api/achievements/unlocked?user_id=perf_test_user_2")

            elapsed = timer.stop()
            times.append(elapsed)

            assert response.status_code == 200

        avg_time = statistics.mean(times)

        logger.info(f"Tempo médio de carregamento de conquistas desbloqueadas: {avg_time * 1000:.2f}ms")

        assert avg_time < MAX_API_RESPONSE_TIME


# =====================================================
# TESTES DE TEMPO DE RESPOSTA DA API
# =====================================================


class TestAPIResponseTime:
    """
    Testa tempos de resposta da API.
    """

    def test_get_achievements_response_time(self, client, app_test_data, performance_timer):
        """
        Testa tempo de resposta do endpoint GET /api/achievements.
        """
        timer = performance_timer()

        with timer:
            response = client.get("/api/achievements?user_id=api_perf_user")

        assert response.status_code == 200
        assert (
            timer.elapsed < MAX_API_RESPONSE_TIME
        ), f"GET /api/achievements levou {timer.elapsed * 1000:.2f}ms, limite: {MAX_API_RESPONSE_TIME * 1000:.2f}ms"

        logger.info(f"GET /api/achievements: {timer.elapsed * 1000:.2f}ms")

    def test_post_check_achievements_response_time(self, client, app_test_data, performance_timer):
        """
        Testa tempo de resposta do endpoint POST /api/achievements/check.
        """
        timer = performance_timer()

        with timer:
            response = client.post(
                "/api/achievements/check",
                json={"user_id": "api_perf_user"},
                content_type="application/json",
            )

        assert response.status_code == 200
        assert timer.elapsed < MAX_API_RESPONSE_TIME, (
            f"POST /api/achievements/check levou {timer.elapsed * 1000:.2f}ms, "
            f"limite: {MAX_API_RESPONSE_TIME * 1000:.2f}ms"
        )

        logger.info(f"POST /api/achievements/check: {timer.elapsed * 1000:.2f}ms")

    def test_check_exercise_response_time(self, client, app_test_data, performance_timer):
        """
        Testa tempo de resposta do endpoint POST /api/check-exercise (inclui verificação de conquistas).
        """
        timer = performance_timer()

        with timer:
            response = client.post(
                "/api/check-exercise",
                json={
                    "course_id": "python-basico",
                    "exercise_id": "ex-introducao-5",
                    "code": "print('Olá, Python!')",
                    "user_id": "api_perf_check_exercise",
                },
                content_type="application/json",
            )

        assert response.status_code == 200

        # Este endpoint pode ser mais lento pois executa código
        # Usamos um limite maior (1 segundo)
        assert timer.elapsed < 1.0, f"POST /api/check-exercise levou {timer.elapsed * 1000:.2f}ms, limite: 1000ms"

        logger.info(f"POST /api/check-exercise: {timer.elapsed * 1000:.2f}ms")

    def test_progress_lesson_response_time(self, client, app_test_data, performance_timer):
        """
        Testa tempo de resposta do endpoint POST /api/progress/lesson.
        """
        timer = performance_timer()

        with timer:
            response = client.post(
                "/api/progress/lesson",
                json={
                    "course_id": "python-basico",
                    "lesson_id": "introducao-python",
                    "user_id": "api_perf_progress",
                },
                content_type="application/json",
            )

        assert response.status_code == 200
        assert timer.elapsed < MAX_API_RESPONSE_TIME, (
            f"POST /api/progress/lesson levou {timer.elapsed * 1000:.2f}ms, "
            f"limite: {MAX_API_RESPONSE_TIME * 1000:.2f}ms"
        )

        logger.info(f"POST /api/progress/lesson: {timer.elapsed * 1000:.2f}ms")


# =====================================================
# TESTES DE AVALIAÇÃO DE CONDIÇÕES
# =====================================================


class TestConditionEvaluationPerformance:
    """
    Testa performance da avaliação de condições de conquistas.
    """

    def test_condition_evaluation_time(self, client, app_test_data, performance_timer):
        """
        Testa que a avaliação de condições é rápida.
        """
        # Primeiro, criar progresso para ter dados para avaliar
        client.post(
            "/api/progress/lesson",
            json={
                "course_id": "python-basico",
                "lesson_id": "introducao-python",
                "user_id": "condition_perf_user",
            },
            content_type="application/json",
        )

        # Agora medir tempo de verificação
        times = []

        for _ in range(10):
            timer = performance_timer()
            timer.start()

            response = client.post(
                "/api/achievements/check",
                json={"user_id": "condition_perf_user"},
                content_type="application/json",
            )

            elapsed = timer.stop()
            times.append(elapsed)
            assert response.status_code == 200

        avg_time = statistics.mean(times)

        logger.info(f"Tempo médio de avaliação de condições: {avg_time * 1000:.2f}ms")

        assert avg_time < MAX_ACHIEVEMENT_CHECK_TIME, (
            f"Tempo médio de avaliação ({avg_time * 1000:.2f}ms) "
            f"excede o limite de {MAX_ACHIEVEMENT_CHECK_TIME * 1000:.2f}ms"
        )

    def test_multiple_conditions_evaluation(self, client, app_test_data, performance_timer):
        """
        Testa que avaliar múltiplas condições não degrada performance significativamente.
        """
        user_id = "multi_condition_user"

        # Criar múltiplas ações de progresso
        for _ in range(5):
            client.post(
                "/api/progress/lesson",
                json={
                    "course_id": "python-basico",
                    "lesson_id": "introducao-python",
                    "user_id": user_id,
                },
                content_type="application/json",
            )

        # Medir tempo de verificação
        timer = performance_timer()

        with timer:
            response = client.post(
                "/api/achievements/check",
                json={"user_id": user_id},
                content_type="application/json",
            )

        assert response.status_code == 200
        assert timer.elapsed < MAX_ACHIEVEMENT_CHECK_TIME * 2  # Permitir 2x o tempo normal

        logger.info(f"Avaliação de múltiplas condições: {timer.elapsed * 1000:.2f}ms")


# =====================================================
# TESTES DE CONCORRÊNCIA E CARGA
# =====================================================


class TestConcurrencyPerformance:
    """
    Testa performance sob carga concorrente.
    """

    def test_concurrent_api_requests(self, client, app_test_data, performance_timer):
        """
        Testa performance com múltiplas requisições concorrentes.
        """
        num_requests = 10
        results = []
        errors = []

        def make_request(request_id):
            try:
                start = time.perf_counter()
                response = client.get(f"/api/achievements?user_id=concurrent_user_{request_id}")
                elapsed = time.perf_counter() - start
                return response.status_code, elapsed
            except Exception as e:
                errors.append(str(e))
                return None, None

        timer = performance_timer()
        timer.start()

        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in as_completed(futures):
                status, elapsed = future.result()
                if status:
                    results.append((status, elapsed))

        total_time = timer.stop()

        assert len(errors) == 0, f"Erros durante requisições concorrentes: {errors}"
        assert len(results) == num_requests

        # Todas as requisições devem ter sucesso
        for status, _ in results:
            assert status == 200

        # Tempo total não deve exceder o limite
        assert total_time < MAX_CONCURRENT_REQUESTS_TIME, (
            f"Tempo total para {num_requests} requisições concorrentes ({total_time * 1000:.2f}ms) "
            f"excede o limite de {MAX_CONCURRENT_REQUESTS_TIME * 1000:.2f}ms"
        )

        # Calcular estatísticas
        response_times = [r[1] for r in results]
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        logger.info(
            f"Requisições concorrentes ({num_requests}x) - "
            f"Total: {total_time * 1000:.2f}ms, "
            f"Média por requisição: {avg_time * 1000:.2f}ms, "
            f"Max: {max_time * 1000:.2f}ms"
        )

    def test_rapid_sequential_requests(self, client, app_test_data, performance_timer):
        """
        Testa performance com requisições sequenciais rápidas.
        """
        num_requests = 20
        times = []

        timer = performance_timer()
        timer.start()

        for i in range(num_requests):
            request_start = time.perf_counter()
            response = client.get(f"/api/achievements?user_id=rapid_user_{i}")
            request_time = time.perf_counter() - request_start
            times.append(request_time)
            assert response.status_code == 200

        total_time = timer.stop()

        avg_time = statistics.mean(times)

        logger.info(
            f"Requisições sequenciais rápidas ({num_requests}x) - "
            f"Total: {total_time * 1000:.2f}ms, "
            f"Média: {avg_time * 1000:.2f}ms"
        )

        # Média deve ser razoável
        assert avg_time < MAX_API_RESPONSE_TIME


# =====================================================
# TESTES COM GRANDE NÚMERO DE CONQUISTAS
# =====================================================


class TestLargeScalePerformance:
    """
    Testa performance com grande número de conquistas.
    """

    def test_response_time_consistency(self, client, app_test_data, performance_timer):
        """
        Testa que o tempo de resposta é consistente entre requisições.
        """
        times = []

        for i in range(20):
            timer = performance_timer()
            timer.start()

            response = client.get(f"/api/achievements?user_id=consistency_user_{i}")

            elapsed = timer.stop()
            times.append(elapsed)
            assert response.status_code == 200

        avg = statistics.mean(times)
        std_dev = statistics.stdev(times)
        coefficient_of_variation = std_dev / avg if avg > 0 else 0

        logger.info(
            f"Consistência de tempo de resposta - "
            f"Média: {avg * 1000:.2f}ms, "
            f"Desvio Padrão: {std_dev * 1000:.2f}ms, "
            f"CV: {coefficient_of_variation:.2%}"
        )

        # Coeficiente de variação deve ser baixo (menos de 50%)
        assert (
            coefficient_of_variation < 0.5
        ), f"Tempo de resposta muito inconsistente (CV={coefficient_of_variation:.2%})"

    def test_achievements_with_many_unlocked(self, client, app_test_data, performance_timer):
        """
        Testa performance quando usuário tem muitas conquistas desbloqueadas.
        """
        user_id = "many_unlocked_user"

        # Completar várias lições e exercícios para desbloquear conquistas
        for _ in range(5):
            client.post(
                "/api/progress/lesson",
                json={
                    "course_id": "python-basico",
                    "lesson_id": "introducao-python",
                    "user_id": user_id,
                },
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

        # Medir tempo de resposta com muitas conquistas
        timer = performance_timer()

        with timer:
            response = client.get(f"/api/achievements?user_id={user_id}")

        assert response.status_code == 200
        data = response.get_json()

        unlocked_count = len(data["achievements"]["unlocked"])
        logger.info(f"Carregamento com {unlocked_count} conquistas desbloqueadas: {timer.elapsed * 1000:.2f}ms")

        # Mesmo com muitas conquistas, deve ser rápido
        assert timer.elapsed < MAX_API_RESPONSE_TIME


# =====================================================
# TESTES DE MÉTRICAS E MONITORAMENTO
# =====================================================


class TestPerformanceMetrics:
    """
    Coleta métricas de performance para monitoramento.
    """

    def test_api_performance_summary(self, client, app_test_data, performance_timer):
        """
        Gera um resumo de performance de todos os endpoints.
        """
        endpoints = [
            ("GET", "/api/achievements", {"user_id": "metrics_user"}),
            ("GET", "/api/achievements/unlocked", {"user_id": "metrics_user"}),
        ]

        metrics = {}

        for method, endpoint, params in endpoints:
            times = []

            for _ in range(5):
                timer = performance_timer()
                timer.start()

                if method == "GET":
                    query_string = "&".join(f"{k}={v}" for k, v in params.items())
                    response = client.get(f"{endpoint}?{query_string}")
                else:
                    response = client.post(endpoint, json=params, content_type="application/json")

                elapsed = timer.stop()
                times.append(elapsed)
                assert response.status_code == 200

            metrics[f"{method} {endpoint}"] = {
                "avg_ms": statistics.mean(times) * 1000,
                "min_ms": min(times) * 1000,
                "max_ms": max(times) * 1000,
                "std_dev_ms": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
            }

        # Logar métricas
        logger.info("=== RESUMO DE PERFORMANCE DA API ===")
        for endpoint, stats in metrics.items():
            logger.info(
                f"{endpoint}: "
                f"Avg={stats['avg_ms']:.2f}ms, "
                f"Min={stats['min_ms']:.2f}ms, "
                f"Max={stats['max_ms']:.2f}ms, "
                f"StdDev={stats['std_dev_ms']:.2f}ms"
            )

        # Verificar que todos os endpoints estão dentro do limite
        for endpoint, stats in metrics.items():
            assert (
                stats["avg_ms"] < MAX_API_RESPONSE_TIME * 1000
            ), f"{endpoint} excede o limite de tempo ({stats['avg_ms']:.2f}ms)"

    def test_exercise_check_performance_breakdown(self, client, app_test_data, performance_timer):
        """
        Analisa performance do fluxo completo de verificação de exercício.
        """
        user_id = "breakdown_user"
        stages = []

        # Estágio 1: Submissão do exercício
        timer = performance_timer()
        with timer:
            response = client.post(
                "/api/check-exercise",
                json={
                    "course_id": "python-basico",
                    "exercise_id": "ex-introducao-5",
                    "code": "print('Olá, Python!')",
                    "user_id": user_id,
                },
                content_type="application/json",
            )
        stages.append(("check-exercise", timer.elapsed))
        assert response.status_code == 200

        # Estágio 2: Verificação de conquistas
        timer = performance_timer()
        with timer:
            response = client.post(
                "/api/achievements/check",
                json={"user_id": user_id},
                content_type="application/json",
            )
        stages.append(("achievements-check", timer.elapsed))
        assert response.status_code == 200

        # Estágio 3: Carregamento de conquistas
        timer = performance_timer()
        with timer:
            response = client.get(f"/api/achievements?user_id={user_id}")
        stages.append(("achievements-get", timer.elapsed))
        assert response.status_code == 200

        logger.info("=== BREAKDOWN DE PERFORMANCE ===")
        for stage_name, elapsed in stages:
            logger.info(f"{stage_name}: {elapsed * 1000:.2f}ms")

        total_time = sum(t for _, t in stages)
        logger.info(f"Total: {total_time * 1000:.2f}ms")
