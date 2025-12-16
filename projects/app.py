"""
Módulo principal da aplicação Flask para o Curso Interativo Python.

Este módulo define as rotas da interface do usuário (UI) e da API,
inicializa a aplicação Flask, configura o CORS e interage com os
módulos de gerenciamento de dados (CourseManager, LessonManager, ExerciseManager)
e o executor de código (code_executor).
"""
# ... imports ...
# ... inicialização do app Flask ...

import logging

from flask import Flask, abort, jsonify, render_template, request
from flask_cors import CORS

from . import code_executor
from .achievement_manager import AchievementManager
from .content_renderer import render_content

# Assume que estes módulos estão no mesmo diretório (projects/)
# Corrigido para import relativo consistente
from .course_manager import CourseManager
from .exercise_manager import ExerciseManager
from .lesson_manager import LessonManager
from .progress_manager import ProgressManager

# Configuração básica de logging
# Idealmente, esta configuração pode ser mais elaborada e centralizada
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas


# Configurar filtros Jinja2
def markdown_filter(text):
    """Filtro Jinja2 para converter Markdown em HTML usando arquitetura SOLID."""
    if not text or not isinstance(text, str):
        return text
    return render_content(text, format_type="markdown")


def plain_text_filter(text):
    """Filtro Jinja2 para renderizar texto simples com quebras de linha preservadas."""
    if not text or not isinstance(text, str):
        return text
    return render_content(text, format_type="plain")


# Registrar filtros no ambiente Jinja2
app.jinja_env.filters["markdown"] = markdown_filter
app.jinja_env.filters["plain_text"] = plain_text_filter

# Instancia os managers
# Os managers agora carregam dados sob demanda ou na inicialização, conforme suas implementações.
course_mgr = CourseManager()
lesson_mgr = LessonManager()
exercise_mgr = ExerciseManager()
progress_mgr = ProgressManager()
achievement_mgr = AchievementManager()

# --- Rotas de Apresentação (HTML) ---


@app.route("/")
def home():
    """Renderiza a página inicial da aplicação.

    Apresenta uma seção de "Cursos em Destaque" com os primeiros três cursos
    disponíveis, se houver.

    Returns:
        str: O conteúdo HTML da página inicial renderizada.
    """
    logger.info("Rota raiz '/' acessada.")
    all_courses = course_mgr.get_courses()
    # Passa todos os cursos para a seção "Cursos em Destaque"
    courses_for_index = all_courses if all_courses else []
    return render_template("index.html", courses=courses_for_index, title="Bem-vindo")


@app.route("/courses", methods=["GET"])
def list_courses_page():  # Renomeado para clareza (página vs API)
    """Renderiza a página de listagem de todos os cursos disponíveis.

    Returns:
        str: O conteúdo HTML da página de listagem de cursos renderizada.
    """
    logger.info("GET /courses - Solicitando página de listagem de cursos.")
    courses = course_mgr.get_courses()
    return render_template("course_list.html", courses=courses, title="Cursos Disponíveis")


@app.route("/courses/<string:course_id>", methods=["GET"])
def course_detail_page(course_id):  # Renomeado para clareza
    """Redireciona para a página de roadmap do curso.

    A visualização padrão ao acessar um curso agora é o roadmap.
    Se o curso não for encontrado, retorna um erro 404.

    Args:
        course_id (str): O ID do curso a ser exibido.

    Returns:
        Response: Redirecionamento para a página de roadmap do curso.
                  Ou uma resposta de erro 404 se o curso não for encontrado.
    """
    logger.info(f"GET /courses/{course_id} - Redirecionando para roadmap do curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"GET /courses/{course_id} - Curso não encontrado.")
        abort(404)  # Usa abort para tratamento de erro padrão do Flask

    # Carregar lições para o resumo do currículo
    lessons_file = course.get("lessons_file")
    lessons = lesson_mgr.load_lessons_from_file(lessons_file) if lessons_file else []

    return render_template(
        "course_detail.html", course=course, lessons=lessons, title=course.get("name", "Detalhes do Curso")
    )


@app.route("/courses/<string:course_id>/roadmap", methods=["GET"])
def course_roadmap_page(course_id):
    """Renderiza a página de roadmap visual de um curso específico.

    Exibe um mapa visual do progresso do usuário através das lições e exercícios.

    Args:
        course_id (str): O ID do curso.

    Returns:
        str: O conteúdo HTML da página de roadmap renderizada.
    """
    logger.info(f"GET /courses/{course_id}/roadmap - Solicitando roadmap do curso")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"Curso '{course_id}' não encontrado para roadmap.")
        abort(404)

    # Carregar lições e exercícios
    lessons_file = course.get("lessons_file")
    exercises_file = course.get("exercises_file")

    lessons = lesson_mgr.load_lessons_from_file(lessons_file) if lessons_file else []
    exercises = exercise_mgr.load_exercises_from_file(exercises_file) if exercises_file else []

    return render_template(
        "course_roadmap.html",
        course=course,
        lessons=lessons,
        exercises=exercises,
        title=f"Roadmap - {course.get('name', 'Curso')}",
    )


@app.route("/courses/<string:course_id>/lessons/<string:lesson_id_str>", methods=["GET"])
def lesson_detail_page(course_id, lesson_id_str):  # Renomeado para clareza
    """Renderiza a página de detalhes de uma lição específica dentro de um curso.

    Exibe o conteúdo da lição, uma lista de exercícios associados a ela
    (filtrados pelo nível do curso) e um link para a próxima lição, se houver.
    Retorna erro 404 se o curso ou a lição não forem encontrados, ou 500
    se houver problemas de configuração.

    Args:
        course_id (str): O ID do curso ao qual a lição pertence.
        lesson_id_str (str): O ID da lição a ser exibida.

    Returns:
        str: O conteúdo HTML da página de detalhes da lição renderizada.
    """
    logger.info(f"GET /courses/{course_id}/lessons/{lesson_id_str} - Solicitando página da lição.")
    current_course = course_mgr.get_course_by_id(course_id)
    if not current_course:
        logger.warning(f"Curso '{course_id}' não encontrado ao tentar obter lição '{lesson_id_str}'.")
        abort(404)

    lessons_file_relative_path = current_course.get("lessons_file")
    if not lessons_file_relative_path:
        logger.error(f"'lessons_file' não definido para o curso '{course_id}'.")
        abort(500, description="Configuração de lições ausente para este curso.")

    all_lessons_for_course = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)

    current_lesson = None
    current_lesson_index = -1
    for i, lesson_item_loop in enumerate(all_lessons_for_course):
        if isinstance(lesson_item_loop, dict) and str(lesson_item_loop.get("id")) == lesson_id_str:
            current_lesson = lesson_item_loop
            current_lesson_index = i
            break

    if not current_lesson:
        logger.warning(f"Lição com ID '{lesson_id_str}' não encontrada no curso '{course_id}'.")
        abort(404)

    course_level_from_course_json = current_course.get("level")
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    exercises_for_lesson = []
    exercises_file_relative_path = current_course.get("exercises_file")
    if exercises_file_relative_path:
        all_exercises_for_course = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
        lesson_actual_id = current_lesson.get("id")  # ID da lição atual
        if lesson_actual_id and all_exercises_for_course:
            for ex_item in all_exercises_for_course:
                # Log para depuração
                logger.debug(
                    f"Verificando exercício: ID='{ex_item.get('id')}', "
                    f"LessonID_Ex='{ex_item.get('lesson_id')}', LessonID_Atual='{lesson_actual_id}', "
                    f"Level_Ex='{ex_item.get('level', '').lower()}', Level_Esperado='{expected_exercise_level}'"
                )

                # Verifica se o exercício pertence à lição atual E ao nível esperado do curso
                if (
                    isinstance(ex_item, dict)
                    and str(ex_item.get("lesson_id")) == str(lesson_actual_id)
                    and (not expected_exercise_level or ex_item.get("level", "").lower() == expected_exercise_level)
                ):
                    exercises_for_lesson.append(ex_item)
        logger.debug(f"Encontrados {len(exercises_for_lesson)} exercícios para a lição '{lesson_actual_id}'.")
    else:
        logger.warning(f"Nenhum 'exercises_file' definido para o curso '{course_id}'.")

    next_lesson_obj = None
    if current_lesson_index != -1 and current_lesson_index < len(all_lessons_for_course) - 1:
        next_lesson_obj = all_lessons_for_course[current_lesson_index + 1]

    # Marcar lição como completa quando o usuário acessa
    try:
        user_id = "default"  # TODO: Implementar autenticação de usuários
        progress_mgr.mark_lesson_complete(user_id, course_id, lesson_id_str)
        logger.info(f"Lição '{lesson_id_str}' marcada como completa para usuário '{user_id}'")
    except Exception as prog_error:
        logger.error(f"Erro ao marcar progresso da lição: {prog_error}", exc_info=True)

    return render_template(
        "lesson_detail.html",  # Assumindo que o template se chama lesson_detail.html
        course=current_course,
        lesson=current_lesson,
        exercises=exercises_for_lesson,
        next_lesson=next_lesson_obj,
        title=current_lesson.get("title", "Lição"),
    )


@app.route("/courses/<string:course_id>/exercise/<string:exercise_id_str>/editor", methods=["GET"])
def exercise_code_editor_page(course_id, exercise_id_str):  # Renomeado para clareza
    """Renderiza a página do editor de código para um exercício específico.

    Apresenta o enunciado do exercício e uma área para o usuário inserir
    e testar seu código. O exercício é validado contra o nível do curso.
    Retorna erro 404 se o curso ou exercício não forem encontrados ou se o nível
    do exercício for incompatível, ou 500 se houver problemas de configuração.

    Args:
        course_id (str): O ID do curso ao qual o exercício pertence.
        exercise_id_str (str): O ID do exercício para o qual o editor será exibido.

    Returns:
        str: O conteúdo HTML da página do editor de código renderizada.
    """
    logger.info(f"GET /courses/{course_id}/exercise/{exercise_id_str}/editor - Acessando editor de código.")
    current_course = course_mgr.get_course_by_id(course_id)
    if not current_course:
        logger.warning(f"Editor: Curso '{course_id}' não encontrado.")
        abort(404)

    exercises_file_relative_path = current_course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"Editor: 'exercises_file' não definido para o curso '{course_id}'.")
        abort(500, description="Configuração de exercícios ausente para este curso.")

    course_level_from_course_json = current_course.get("level")
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    all_exercises_for_course = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    current_exercise = None
    for ex_item in all_exercises_for_course:
        if isinstance(ex_item, dict) and str(ex_item.get("id")) == exercise_id_str:
            if not expected_exercise_level or ex_item.get("level", "").lower() == expected_exercise_level:
                current_exercise = ex_item
                break
            else:
                logger.warning(
                    f"Editor: Exercício '{exercise_id_str}' encontrado, mas seu nível '{ex_item.get('level')}' não corresponde ao nível esperado do curso '{expected_exercise_level}'."
                )

    if not current_exercise:
        logger.warning(
            f"Editor: Exercício ID '{exercise_id_str}' não encontrado no curso '{course_id}' ou nível incompatível."
        )
        abort(404)

    # Encontrar a lição do exercício
    lesson_id = current_exercise.get("lesson_id")
    current_lesson = None
    if lesson_id:
        lessons_file = current_course.get("lessons_file")
        if lessons_file:
            all_lessons = lesson_mgr.load_lessons_from_file(lessons_file)
            for lesson in all_lessons:
                if str(lesson.get("id")) == str(lesson_id):
                    current_lesson = lesson
                    break

    # Encontrar próximo exercício ou próxima lição
    next_exercise = None
    next_lesson = None
    current_exercise_index = -1

    for i, ex in enumerate(all_exercises_for_course):
        if str(ex.get("id")) == exercise_id_str:
            current_exercise_index = i
            break

    # Próximo exercício da mesma lição
    if current_exercise_index != -1 and current_exercise_index < len(all_exercises_for_course) - 1:
        for i in range(current_exercise_index + 1, len(all_exercises_for_course)):
            next_ex = all_exercises_for_course[i]
            if str(next_ex.get("lesson_id")) == str(lesson_id):
                next_exercise = next_ex
                break

    # Se não há próximo exercício, buscar próxima lição
    if not next_exercise and current_lesson:
        lessons_file = current_course.get("lessons_file")
        if lessons_file:
            all_lessons = lesson_mgr.load_lessons_from_file(lessons_file)
            for i, lesson in enumerate(all_lessons):
                if str(lesson.get("id")) == str(lesson_id):
                    if i < len(all_lessons) - 1:
                        next_lesson = all_lessons[i + 1]
                    break

    return render_template(
        "exercise_editor.html",
        course=current_course,
        exercise=current_exercise,
        lesson=current_lesson,
        next_exercise=next_exercise,
        next_lesson=next_lesson,
        title=f"Editor: {current_exercise.get('title', 'Exercício')}",
    )


@app.route("/editor", methods=["GET"])
def generic_code_editor_page():
    """Renderiza uma página de editor de código genérico.

    Esta página fornece um editor de código sem estar associada a um curso
    ou exercício específico.
    Returns:
        str: O conteúdo HTML da página do editor de código genérico renderizada.
    """
    logger.info("GET /editor - Acessando editor de código genérico.")
    return render_template("code_editor.html", course=None, exercise=None, title="Editor de Código")


# --- Rotas de API (JSON) ---


@app.route("/api/courses", methods=["GET"])
def api_get_all_courses():
    """API endpoint para obter todos os cursos disponíveis.

    Returns:
        JSON: Lista de todos os cursos com suas informações básicas.
    """
    logger.info("GET /api/courses - Obtendo lista de todos os cursos.")
    try:
        all_courses = course_mgr.get_courses()
        logger.info(f"GET /api/courses - Sucesso: {len(all_courses)} cursos retornados.")
        return jsonify(all_courses)
    except Exception as e:
        logger.error(f"Erro ao obter lista de cursos: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor"}), 500


@app.route("/api/courses/<string:course_id>/lessons", methods=["GET"])
def api_get_lessons_for_course(course_id):
    """API endpoint para obter as lições de um curso específico.

    Args:
        course_id (str): O ID do curso.

    Returns:
        Response: Um objeto JSON contendo uma lista de lições.
            Em caso de sucesso (200 OK):
                `[{"id": "1", "title": "Lição 1", ...}, ...]`
            Em caso de curso não encontrado (404 Not Found):
                `{"error": "Curso não encontrado"}`
            Em caso de arquivo de lições não definido (500 Internal Server Error):
                `{"error": "Arquivo de lições não definido para este curso"}`

    """
    logger.info(f"API GET /courses/{course_id}/lessons - Solicitando lições para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"API GET /courses/{course_id}/lessons - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    lessons_file_relative_path = course.get("lessons_file")
    if not lessons_file_relative_path:
        logger.error(f"API GET /courses/{course_id}/lessons - 'lessons_file' não definido para este curso.")
        return jsonify({"error": "Arquivo de lições não definido para este curso"}), 500

    lessons = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)
    return jsonify(lessons)


@app.route("/api/courses/<string:course_id>/exercises", methods=["GET"])
def api_get_exercises_for_course(course_id):
    """API endpoint para obter os exercícios de um curso específico.

    Args:
        course_id (str): O ID do curso.

    Returns:
        Response: Um objeto JSON contendo uma lista de exercícios.
            Em caso de sucesso (200 OK):
                `[{"id": "ex1", "title": "Exercício 1", ...}, ...]`
            Em caso de curso não encontrado (404 Not Found):
                `{"error": "Curso não encontrado"}`
            Em caso de arquivo de exercícios não definido (500 Internal Server Error):
                `{"error": "Arquivo de exercícios não definido para este curso"}`

    """
    logger.info(f"API GET /courses/{course_id}/exercises - Solicitando exercícios para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"API GET /courses/{course_id}/exercises - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"API GET /courses/{course_id}/exercises - 'exercises_file' não definido para o curso.")
        return jsonify({"error": "Arquivo de exercícios não definido para este curso"}), 500

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    return jsonify(exercises)


@app.route("/api/execute-code", methods=["POST"])
def api_execute_code():
    """API endpoint para executar um trecho de código Python.

    Recebe um código Python via JSON e o executa, retornando
    sua saída padrão (stdout) e erros (stderr).

    JSON de Requisição:
        {
            "code": "str (código Python a ser executado)"
        }

    JSON de Resposta:
        Sucesso na execução (200 OK):
            `{"success": true, "output": "str (stdout)", "details": "str (stderr, pode ser vazio)"}`
        Falha na execução (200 OK, mas success: false):
            `{"success": false, "output": "str (stdout até o erro)", "details": "str (stderr com a mensagem de erro)"}`
        Payload inválido (400 Bad Request):
            `{"success": false, "output": "", "details": "Payload inválido ou campo 'code' ausente."}`
        Erro interno do servidor (500 Internal Server Error):
            `{"success": false, "output": "", "details": "Erro interno do servidor: <mensagem>"}`
    """
    logger.info("POST /api/execute-code - Recebida requisição para executar código.")
    data = request.get_json()
    if not data or "code" not in data:
        logger.warning("POST /api/execute-code - Payload inválido ou 'code' ausente.")
        return jsonify({"success": False, "output": "", "details": "Payload inválido ou campo 'code' ausente."}), 400

    user_code = data["code"]
    try:
        exec_result = code_executor.execute_code(user_code)
        success = exec_result["returncode"] == 0
        output = exec_result["stdout"]
        details = exec_result["stderr"]
        if not success and not details and exec_result.get("error_type") == "SyntaxError":
            details = "Erro de sintaxe no código."
        elif not success and not details:
            details = "Erro durante a execução do código."

        logger.info(f"POST /api/execute-code - Execução: success={success}")
        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /api/execute-code - Erro inesperado: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno do servidor: {str(e)}"}), 500


@app.route("/api/check-exercise", methods=["POST"])
def api_check_exercise():
    """API endpoint para verificar a solução de um exercício submetida pelo usuário.

    Recebe o código do usuário, o ID do curso e o ID do exercício.
    Executa o código do usuário e, se houver um `test_code` associado ao
    exercício, executa-o também. A saída do código do usuário é disponibilizada
    para o `test_code` através de uma variável global `output` no escopo do teste.

    JSON de Requisição:
        {
            "course_id": "str",
            "exercise_id": "str_ou_int",
            "code": "str (código do usuário)"
        }

    JSON de Resposta (200 OK, mesmo em caso de falha na lógica do exercício):
        Sucesso (código do usuário executou e testes passaram, ou não há testes):
            `{"success": true, "output": "str (saída combinada)", "details": "str (mensagens do teste, ex: 'SUCCESS')"}`
        Falha (código do usuário com erro, ou testes falharam):
            `{"success": false, "output": "str (saída até o erro)", "details": "str (mensagem de erro)"}`
        Payload inválido (400 Bad Request):
            `{"success": false, "output": "", "details": "Payload inválido..."}`
        Curso/Exercício não encontrado (404 Not Found):
            `{"success": false, "output": "", "details": "Curso/Exercício não encontrado..."}`
        Erro de configuração (500 Internal Server Error):
            `{"success": false, "output": "", "details": "Arquivo de exercícios não definido..."}`
        Erro interno do servidor (500 Internal Server Error):
            `{"success": false, "output": "", "details": "Erro interno do servidor ao verificar: <mensagem>"}`

    Returns:
        Response: Uma resposta JSON contendo o resultado da verificação.
    """
    logger.info("POST /api/check-exercise - Recebida requisição para verificar exercício.")
    data = request.get_json()
    if not data or not all(k in data for k in ["course_id", "exercise_id", "code"]):
        logger.warning("POST /api/check-exercise - Payload inválido ou campos ausentes.")
        return jsonify(
            {
                "success": False,
                "output": "",
                "details": "Payload inválido. 'course_id', 'exercise_id', e 'code' são obrigatórios.",
            }
        ), 400

    course_id = data["course_id"]
    exercise_id_str = str(data["exercise_id"])
    user_code = data["code"]

    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"POST /api/check-exercise - Curso '{course_id}' não encontrado.")
        return jsonify({"success": False, "output": "", "details": f"Curso '{course_id}' não encontrado."}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"POST /api/check-exercise - 'exercises_file' não definido para o curso '{course_id}'.")
        return jsonify(
            {"success": False, "output": "", "details": "Arquivo de exercícios não definido para este curso."}
        ), 500

    course_level_from_course_json = course.get("level")
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    exercise_details_to_check = None
    for ex_item in exercises:
        if isinstance(ex_item, dict) and str(ex_item.get("id")) == exercise_id_str:
            if not expected_exercise_level or ex_item.get("level", "").lower() == expected_exercise_level:
                exercise_details_to_check = ex_item
                break

    if not exercise_details_to_check:
        logger.warning(
            f"POST /api/check-exercise - Exercício '{exercise_id_str}' não encontrado no curso '{course_id}' ou nível incompatível."
        )  # No Linter: Adicionar espaço antes do #
        return jsonify(
            {
                "success": False,
                "output": "",
                "details": f"Exercício '{exercise_id_str}' não encontrado no curso '{course_id}'.",
            }
        ), 404

    test_code = exercise_details_to_check.get("test_code", "")
    # full_code_to_execute = user_code.rstrip() + "\n\n" + test_code # Lógica antiga

    try:
        # 1. Executar o código do usuário e capturar sua saída
        user_exec_result = code_executor.execute_code(user_code)
        user_stdout = user_exec_result["stdout"]
        user_stderr = user_exec_result["stderr"]
        user_success = user_exec_result["returncode"] == 0

        # Inicializa 'output' com a saída do código do usuário.
        # Será sobrescrito pela saída do test_code se este for executado.
        api_output_response = user_stdout
        details = user_stderr  # Detalhes podem vir do erro do usuário ou do teste
        success = False  # Assume que falha até que o test_code passe ou não haja test_code

        if not user_success:
            # Se o código do usuário já falhou (ex: SyntaxError), não precisamos rodar o test_code
            details = user_stderr if user_stderr else "Erro de sintaxe ou execução no seu código."
            logger.info(f"POST /api/check-exercise - Código do usuário falhou. Details: {details}")
        elif not test_code:
            # Se não há test_code, o sucesso depende apenas da execução do user_code
            success = user_success
            # 'api_output_response' já é user_stdout
            details = (
                "Código executado (sem testes automáticos)."
                if success
                else (details or "Erro na execução do código do usuário.")
            )
        else:
            # 2. Preparar e executar o test_code com a saída do user_code disponível
            test_globals = {"output": user_stdout}  # Disponibiliza a saída do user_code para o test_code
            test_exec_result = code_executor.execute_code(test_code, execution_globals=test_globals)
            success = test_exec_result["returncode"] == 0

            # O 'output' da API deve combinar o stdout do user_code e do test_code
            # Se o test_code produziu output (ex: "SUCCESS"), anexe-o.
            # Se o user_code produziu output, ele já está em api_output_response.
            if test_exec_result["stdout"]:
                api_output_response = (api_output_response or "") + test_exec_result["stdout"]

            # Os 'details' devem incluir o tipo de erro se houver
            details_from_test_code = test_exec_result["stderr"]
            error_type_from_test = test_exec_result.get("error_type")

            if error_type_from_test:
                details = f"{error_type_from_test}: {details_from_test_code}"
            else:
                details = (
                    details_from_test_code
                    if details_from_test_code
                    else ("Teste falhou sem stderr específico." if not success else "Teste passou.")
                )
            # Se o user_code teve stderr, mas o test_code passou, podemos querer limpar os detalhes ou priorizar os do teste.

        if not test_code and success:
            details = "Código executado com sucesso (nenhum teste automático para este exercício)."
        elif not test_code and not success:
            details = f"Erro ao executar o código: {details if details else 'Erro desconhecido'}"

        # Registrar tentativa do exercício (sucesso ou falha)
        try:
            user_id = data.get("user_id", "default")
            exercise_progress = progress_mgr.mark_exercise_attempt(user_id, course_id, exercise_id_str, success=success)

            # Adicionar estatísticas de tentativas na resposta
            exercise_stats = exercise_progress.get("exercises", {}).get(exercise_id_str, {})
            attempts_count = exercise_stats.get("attempts", 1)
            successful_attempts = exercise_stats.get("successful_attempts", 0)
            failed_attempts = exercise_stats.get("failed_attempts", 0)

            logger.info(
                f"Exercício '{exercise_id_str}' - Tentativa registrada. Total: {attempts_count}, Sucesso: {successful_attempts}, Falhas: {failed_attempts}"
            )
        except Exception as prog_error:
            logger.error(f"Erro ao registrar tentativa do exercício: {prog_error}", exc_info=True)
            attempts_count = 1
            successful_attempts = 1 if success else 0
            failed_attempts = 0 if success else 1

        logger.info(f"POST /api/check-exercise - Verificação: success={success}")

        # Verificar novas conquistas
        new_achievements = achievement_mgr.check_new_achievements(user_id, progress_mgr)

        # Preparar resposta com estatísticas
        response_data = {
            "success": success,
            "output": api_output_response,
            "details": details,
            "stats": {
                "attempts": attempts_count,
                "successful_attempts": successful_attempts,
                "failed_attempts": failed_attempts,
                "first_try": attempts_count == 1 and success,
            },
            "new_achievements": new_achievements,
        }

        return jsonify(response_data)
    except Exception as e:
        logger.error(f"POST /api/check-exercise - Erro inesperado: {e}", exc_info=True)
        return jsonify(
            {"success": False, "output": "", "details": f"Erro interno do servidor ao verificar: {str(e)}"}
        ), 500


# --- Rotas de API de Progresso ---


@app.route("/api/progress/lesson", methods=["POST"])
def api_mark_lesson_complete():
    """API endpoint para marcar uma lição como completa.

    JSON de Requisição:
        {
            "course_id": "str",
            "lesson_id": "str",
            "user_id": "str (opcional, padrão: 'default')"
        }

    Returns:
        Response: JSON com o progresso atualizado do curso.
    """
    logger.info("POST /api/progress/lesson - Marcando lição como completa")
    data = request.get_json()

    if not data or not all(k in data for k in ["course_id", "lesson_id"]):
        return jsonify({"success": False, "message": "Campos obrigatórios: course_id, lesson_id"}), 400

    user_id = data.get("user_id", "default")
    course_id = data["course_id"]
    lesson_id = data["lesson_id"]

    try:
        course_progress = progress_mgr.mark_lesson_complete(user_id, course_id, lesson_id)

        # Verificar novas conquistas
        new_achievements = achievement_mgr.check_new_achievements(user_id, progress_mgr)

        return jsonify(
            {
                "success": True,
                "message": "Lição marcada como completa",
                "progress": course_progress,
                "new_achievements": new_achievements,
            }
        )
    except Exception as e:
        logger.error(f"Erro ao marcar lição como completa: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


@app.route("/api/progress/exercise", methods=["POST"])
def api_mark_exercise_complete():
    """API endpoint para marcar um exercício como completo.

    JSON de Requisição:
        {
            "course_id": "str",
            "exercise_id": "str",
            "success": "bool (opcional, padrão: true)",
            "attempts": "int (opcional, padrão: 1)",
            "user_id": "str (opcional, padrão: 'default')"
        }

    Returns:
        Response: JSON com o progresso atualizado do curso.
    """
    logger.info("POST /api/progress/exercise - Marcando exercício como completo")
    data = request.get_json()

    if not data or not all(k in data for k in ["course_id", "exercise_id"]):
        return jsonify({"success": False, "message": "Campos obrigatórios: course_id, exercise_id"}), 400

    user_id = data.get("user_id", "default")
    course_id = data["course_id"]
    exercise_id = data["exercise_id"]
    success = data.get("success", True)
    attempts = data.get("attempts", 1)

    try:
        course_progress = progress_mgr.mark_exercise_complete(user_id, course_id, exercise_id, success, attempts)
        # Verificar novas conquistas
        new_achievements = achievement_mgr.check_new_achievements(user_id, progress_mgr)

        return jsonify(
            {
                "success": True,
                "message": "Exercício atualizado",
                "progress": course_progress,
                "new_achievements": new_achievements,
            }
        )
    except Exception as e:
        logger.error(f"Erro ao marcar exercício como completo: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


@app.route("/api/progress/course/<string:course_id>", methods=["GET"])
def api_get_course_progress(course_id):
    """API endpoint para obter o progresso de um curso.

    Args:
        course_id (str): ID do curso.

    Query Parameters:
        user_id (str): ID do usuário (opcional, padrão: 'default').

    Returns:
        Response: JSON com o progresso e estatísticas do curso.
    """
    logger.info(f"GET /api/progress/course/{course_id} - Obtendo progresso do curso")
    user_id = request.args.get("user_id", "default")

    try:
        # Obter informações do curso
        course = course_mgr.get_course_by_id(course_id)
        if not course:
            return jsonify({"success": False, "message": "Curso não encontrado"}), 404

        # Carregar lições e exercícios
        lessons_file = course.get("lessons_file")
        exercises_file = course.get("exercises_file")

        lessons = lesson_mgr.load_lessons_from_file(lessons_file) if lessons_file else []
        exercises = exercise_mgr.load_exercises_from_file(exercises_file) if exercises_file else []

        # Obter progresso
        course_progress = progress_mgr.get_course_progress(user_id, course_id)
        statistics = progress_mgr.get_course_statistics(user_id, course_id, len(lessons), len(exercises))

        return jsonify(
            {
                "success": True,
                "course": course,
                "progress": course_progress,
                "statistics": statistics,
                "lessons": lessons,
                "exercises": exercises,
            }
        )
    except Exception as e:
        logger.error(f"Erro ao obter progresso do curso: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


@app.route("/api/progress/user", methods=["GET"])
def api_get_user_progress():
    """API endpoint para obter o progresso geral do usuário.

    Query Parameters:
        user_id (str): ID do usuário (opcional, padrão: 'default').

    Returns:
        Response: JSON com estatísticas gerais do usuário.
    """
    logger.info("GET /api/progress/user - Obtendo progresso do usuário")
    user_id = request.args.get("user_id", "default")

    try:
        statistics = progress_mgr.get_all_statistics(user_id)
        return jsonify({"success": True, "statistics": statistics})
    except Exception as e:
        logger.error(f"Erro ao obter progresso do usuário: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


# --- Rotas de Conquistas ---


@app.route("/achievements")
def achievements_page():
    """Renderiza a página de conquistas."""
    logger.info("GET /achievements - Acessando página de conquistas.")
    return render_template("achievements.html", title="Minhas Conquistas")


@app.route("/api/achievements", methods=["GET"])
def api_get_achievements():
    """API endpoint para obter todas as conquistas com status de desbloqueio.

    Retorna todas as definições de conquistas com status de desbloqueio para o usuário atual.

    Query Parameters:
        user_id (str): ID do usuário (opcional, padrão: 'default')

    Returns:
        Response: JSON com todas as conquistas e seus status.
            Sucesso (200 OK):
                {
                    "success": true,
                    "achievements": {
                        "unlocked": [{"id": "...", "name": "...", "unlocked_at": "...", ...}],
                        "locked": [{"id": "...", "name": "...", "unlock_condition": {...}, ...}],
                        "stats": {"total": 10, "unlocked": 3, "percentage": 30.0}
                    }
                }
            Erro (500 Internal Server Error):
                {"success": false, "message": "Erro: <mensagem>"}
    """
    import time

    start_time = time.time()
    user_id = request.args.get("user_id", "default")
    logger.info(f"GET /api/achievements - Obtendo todas as conquistas com status para user_id='{user_id}'")

    try:
        # Obter todas as conquistas e conquistas desbloqueadas
        all_achievements = achievement_mgr.get_all_achievements()
        unlocked_achievements = progress_mgr.get_unlocked_achievements(user_id)
        unlocked_ids = {a["id"] for a in unlocked_achievements}

        # Separar conquistas desbloqueadas e bloqueadas
        unlocked_list = []
        locked_list = []

        for ach in all_achievements:
            if ach["id"] in unlocked_ids:
                # Encontrar timestamp de desbloqueio
                ach_data = ach.copy()
                for unlocked in unlocked_achievements:
                    if unlocked["id"] == ach["id"]:
                        ach_data["unlocked_at"] = unlocked.get("unlocked_at")
                        break
                unlocked_list.append(ach_data)
            else:
                locked_list.append(ach.copy())

        # Calcular estatísticas
        total = len(all_achievements)
        unlocked_count = len(unlocked_list)
        percentage = (unlocked_count / total * 100) if total > 0 else 0.0

        elapsed_time = time.time() - start_time
        logger.info(
            f"GET /api/achievements - Sucesso: user_id='{user_id}', "
            f"total={total}, unlocked={unlocked_count}, percentage={percentage:.2f}%, "
            f"elapsed_time={elapsed_time:.3f}s"
        )

        return jsonify(
            {
                "success": True,
                "achievements": {
                    "unlocked": unlocked_list,
                    "locked": locked_list,
                    "stats": {"total": total, "unlocked": unlocked_count, "percentage": round(percentage, 2)},
                },
            }
        )
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"GET /api/achievements - Erro: user_id='{user_id}', error='{str(e)}', elapsed_time={elapsed_time:.3f}s",
            exc_info=True,
        )
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


@app.route("/api/achievements/unlocked", methods=["GET"])
def api_get_unlocked_achievements():
    """API endpoint para obter apenas conquistas desbloqueadas.

    Retorna apenas as conquistas que o usuário já desbloqueou com timestamps.

    Query Parameters:
        user_id (str): ID do usuário (opcional, padrão: 'default')

    Returns:
        Response: JSON com conquistas desbloqueadas.
            Sucesso (200 OK):
                {
                    "success": true,
                    "unlocked": [{"id": "...", "name": "...", "unlocked_at": "...", ...}]
                }
            Erro (500 Internal Server Error):
                {"success": false, "message": "Erro: <mensagem>"}
    """
    import time

    start_time = time.time()
    user_id = request.args.get("user_id", "default")
    logger.info(f"GET /api/achievements/unlocked - Obtendo conquistas desbloqueadas para user_id='{user_id}'")

    try:
        # Obter conquistas desbloqueadas do progresso
        unlocked_achievements = progress_mgr.get_unlocked_achievements(user_id)
        unlocked_ids = {a["id"] for a in unlocked_achievements}

        # Obter definições completas das conquistas desbloqueadas
        all_achievements = achievement_mgr.get_all_achievements()
        unlocked_list = []

        for ach in all_achievements:
            if ach["id"] in unlocked_ids:
                ach_data = ach.copy()
                # Adicionar timestamp de desbloqueio
                for unlocked in unlocked_achievements:
                    if unlocked["id"] == ach["id"]:
                        ach_data["unlocked_at"] = unlocked.get("unlocked_at")
                        break
                unlocked_list.append(ach_data)

        elapsed_time = time.time() - start_time
        logger.info(
            f"GET /api/achievements/unlocked - Sucesso: user_id='{user_id}', "
            f"unlocked_count={len(unlocked_list)}, elapsed_time={elapsed_time:.3f}s"
        )

        return jsonify({"success": True, "unlocked": unlocked_list})
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"GET /api/achievements/unlocked - Erro: user_id='{user_id}', "
            f"error='{str(e)}', elapsed_time={elapsed_time:.3f}s",
            exc_info=True,
        )
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


@app.route("/api/achievements/check", methods=["POST"])
def api_check_achievements():
    """API endpoint para verificar e desbloquear novas conquistas.

    Avalia condições de desbloqueio baseadas no progresso atual do usuário
    e retorna conquistas recém-desbloqueadas.

    JSON de Requisição:
        {
            "user_id": "str (opcional, padrão: 'default')"
        }

    Returns:
        Response: JSON com conquistas recém-desbloqueadas.
            Sucesso (200 OK):
                {
                    "success": true,
                    "newly_unlocked": [{"id": "...", "name": "...", ...}],
                    "message": "X novas conquistas desbloqueadas"
                }
            Payload inválido (400 Bad Request):
                {"success": false, "message": "Payload inválido"}
            Erro (500 Internal Server Error):
                {"success": false, "message": "Erro: <mensagem>"}
    """
    import time

    start_time = time.time()
    logger.info("POST /api/achievements/check - Verificando novas conquistas")

    try:
        # Obter user_id do JSON ou usar padrão
        data = request.get_json() if request.is_json else {}
        if data is None:
            logger.warning("POST /api/achievements/check - Payload inválido (não é JSON)")
            return jsonify({"success": False, "message": "Payload inválido"}), 400

        user_id = data.get("user_id", "default")
        logger.debug(f"POST /api/achievements/check - Verificando para user_id='{user_id}'")

        # Verificar novas conquistas
        new_achievements = achievement_mgr.check_new_achievements(user_id, progress_mgr)

        # Preparar mensagem
        count = len(new_achievements)
        if count == 0:
            message = "Nenhuma nova conquista desbloqueada"
        elif count == 1:
            message = "1 nova conquista desbloqueada"
        else:
            message = f"{count} novas conquistas desbloqueadas"

        elapsed_time = time.time() - start_time
        logger.info(
            f"POST /api/achievements/check - Sucesso: user_id='{user_id}', "
            f"newly_unlocked={count}, elapsed_time={elapsed_time:.3f}s"
        )

        if count > 0:
            achievement_names = [a.get("name", a.get("id")) for a in new_achievements]
            logger.info(f"Novas conquistas desbloqueadas: {', '.join(achievement_names)}")

        return jsonify({"success": True, "newly_unlocked": new_achievements, "message": message})
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"POST /api/achievements/check - Erro: error='{str(e)}', elapsed_time={elapsed_time:.3f}s",
            exc_info=True,
        )
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500


# --- Rota Legada (Manter por compatibilidade ou remover se não for mais usada) ---
@app.route("/submit_exercise/<string:course_id>/<string:exercise_id_str>", methods=["POST"])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    """Rota legada para submissão de solução de exercício.

    Esta rota é mantida para compatibilidade, mas sua lógica foi
    majoritariamente duplicada da rota `/api/check-exercise`.
    Idealmente, esta rota deveria ser refatorada para chamar a lógica
    de `/api/check-exercise` ou ser removida se não for mais utilizada.

    Args:
        course_id (str): O ID do curso.
        exercise_id_str (str): O ID do exercício.

    Recebe:
        JSON ou Form-data com um campo 'code'.

    Returns:
        Response: JSON com o resultado da execução, similar a `/api/check-exercise`.
    """
    logger.info(f"POST /submit_exercise/{course_id}/{exercise_id_str} (legacy) - Submetendo solução.")
    # Esta rota agora redireciona sua lógica para a nova API /api/check-exercise
    # para evitar duplicação de código.

    data_from_request = request.get_json()
    user_code = None
    if data_from_request and "code" in data_from_request:
        user_code = data_from_request["code"]
    elif request.form and "code" in request.form:  # Tenta pegar de formulário se não for JSON
        user_code = request.form["code"]

    if user_code is None:
        logger.warning("POST /submit_exercise (legacy) - 'code' ausente no payload.")
        return jsonify({"success": False, "output": "", "details": "O campo 'code' é obrigatório."}), 400

    logger.warning(
        f"A rota LEGADA /submit_exercise/{course_id}/{exercise_id_str} foi chamada. "
        f"Redirecionando internamente para a lógica de /api/check-exercise."
    )

    # Chama a lógica da nova API internamente.
    # Isso requer que o contexto da aplicação Flask esteja disponível.
    # Uma forma mais limpa seria extrair a lógica de `api_check_exercise` para uma função helper.
    # Por simplicidade aqui, vamos assumir que podemos chamar a função diretamente se ela for refatorada.
    # Para este exemplo, vamos apenas logar e retornar um aviso,
    # pois chamar outra rota internamente pode ser complexo sem refatoração.

    # --- Início da lógica duplicada (idealmente refatorar para uma função helper) ---
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        return jsonify({"success": False, "output": "", "details": f"Curso '{course_id}' não encontrado."}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        return jsonify(
            {"success": False, "output": "", "details": "Arquivo de exercícios não definido para este curso."}
        ), 500

    course_level_from_course_json = course.get("level")
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    exercise_details_to_check = None
    for ex_item in exercises:
        if isinstance(ex_item, dict) and str(ex_item.get("id")) == exercise_id_str:
            if not expected_exercise_level or ex_item.get("level", "").lower() == expected_exercise_level:
                exercise_details_to_check = ex_item
                break

    if not exercise_details_to_check:
        return jsonify(
            {"success": False, "output": "", "details": f"Exercício '{exercise_id_str}' não encontrado."}
        ), 404

    test_code = exercise_details_to_check.get("test_code", "")
    full_code_to_execute = user_code.rstrip() + "\n\n" + test_code
    try:
        exec_result = code_executor.execute_code(full_code_to_execute)
        success = exec_result["returncode"] == 0
        output = exec_result["stdout"]
        details = exec_result["stderr"]
        if not success and not details and exec_result.get("error_type") == "SyntaxError":
            details = "Erro de sintaxe no código ou nos testes."
        elif not success and not details and exec_result.get("error_type") == "AssertionError":
            details = "Falha na asserção do teste."
        elif not success and not details:
            details = "Erro durante a execução do código de verificação."

        if not test_code and success:
            details = "Código executado com sucesso (nenhum teste automático)."
        elif not test_code and not success:
            details = f"Erro ao executar o código: {details if details else 'Erro desconhecido'}"

        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /submit_exercise (legacy) - Erro inesperado: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno: {str(e)}"}), 500
    # --- Fim da lógica duplicada ---


# --- Tratador de Erros Padrão ---
@app.errorhandler(404)
def page_not_found(e):
    """Tratador de erro para o código de status HTTP 404 (Não Encontrado).

    Renderiza uma página HTML 404 personalizada ou retorna uma resposta JSON
    dependendo do `Accept` header da requisição.

    Args:
        e (HTTPException): A exceção que causou o erro 404.

    Returns:
        tuple: (Conteúdo da resposta, código de status HTTP).
    """
    logger.warning(f"Erro 404 - Página não encontrada: {request.path} (Descrição: {e.description})")
    # Verifica se a requisição espera JSON ou HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error=str(e.description or "Recurso não encontrado")), 404
    return render_template("404.html", title="Página Não Encontrada", error_message=e.description), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Tratador de erro para o código de status HTTP 500 (Erro Interno do Servidor).

    Renderiza uma página HTML 500 personalizada ou retorna uma resposta JSON
    dependendo do `Accept` header da requisição.

    Args:
        e (HTTPException): A exceção que causou o erro 500.

    Returns:
        tuple: (Conteúdo da resposta, código de status HTTP).
    """
    logger.error(
        f"Erro 500 - Erro interno do servidor: {request.path} (Descrição: {e.description or str(e.original_exception or e)})",
        exc_info=True,
    )
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error=str(e.description or "Erro interno do servidor")), 500
    return render_template(
        "500.html", title="Erro Interno", error_message=e.description or "Ocorreu um erro inesperado."
    ), 500


if __name__ == "__main__":
    # Para desenvolvimento, debug=True é útil. Para produção, defina como False.
    # host='0.0.0.0' torna o servidor acessível externamente na rede.
    # A porta pode ser alterada se necessário.
    logger.info("Iniciando servidor Flask para desenvolvimento...")
    app.run(host="0.0.0.0", port=5000, debug=True)
