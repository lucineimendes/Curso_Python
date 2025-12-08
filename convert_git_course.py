#!/usr/bin/env python3
"""
Script para converter os arquivos Markdown do curso de Git para JSON
compatível com o sistema de lições da aplicação Flask.
"""

import json
from pathlib import Path

import markdown

# Configurações
DOCS_DIR = Path(__file__).parent / "docs" / "git-course"
OUTPUT_DIR = Path(__file__).parent / "projects" / "data" / "git-advanced"
COURSE_ID = "git-avancado"


def convert_md_to_html(md_content: str) -> str:
    """Converte Markdown para HTML."""
    return markdown.markdown(md_content, extensions=["fenced_code", "tables", "codehilite"])


def extract_title_from_md(md_content: str) -> str:
    """Extrai o título (primeiro # heading) do conteúdo Markdown."""
    for line in md_content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Sem Título"


def process_module(module_path: Path, order_start: int) -> list[dict]:
    """Processa um módulo (diretório) e retorna as lições."""
    lessons = []
    order = order_start

    # Ordenar arquivos: theory primeiro, depois labs
    md_files = sorted(module_path.glob("*.md"), key=lambda f: (0 if "theory" in f.name.lower() else 1, f.name))

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        title = extract_title_from_md(content)
        html_content = convert_md_to_html(content)

        lesson = {
            "id": f"{module_path.name}-{md_file.stem}",
            "course_id": COURSE_ID,
            "title": title,
            "order": order,
            "description": f"Lição do módulo {module_path.name}",
            "learning_objectives": [],
            "key_concepts": [],
            "content": html_content,
            "examples": [],
            "summary": "",
            "estimated_time_minutes": 30,
        }
        lessons.append(lesson)
        order += 1

    return lessons


def main():
    """Função principal para gerar o lessons.json."""
    all_lessons = []
    order_counter = 1

    # Processar cheat-sheet na raiz
    cheat_sheet_path = DOCS_DIR / "cheat-sheet.md"
    if cheat_sheet_path.exists():
        content = cheat_sheet_path.read_text(encoding="utf-8")
        title = extract_title_from_md(content)
        html_content = convert_md_to_html(content)
        all_lessons.append(
            {
                "id": "cheat-sheet",
                "course_id": COURSE_ID,
                "title": title,
                "order": 0,  # Primeiro item (referência rápida)
                "description": "Referência rápida de comandos Git",
                "learning_objectives": [],
                "key_concepts": [],
                "content": html_content,
                "examples": [],
                "summary": "",
                "estimated_time_minutes": 10,
            }
        )

    # Processar módulos na ordem: 01-basic, 02-intermediario, 03-avancado
    module_dirs = sorted([d for d in DOCS_DIR.iterdir() if d.is_dir()])

    for module_dir in module_dirs:
        if module_dir.name.startswith("0"):
            # É um módulo de nível (01-basic, 02-intermediario, 03-avancado)
            if module_dir.name == "03-avancado":
                # 03-avancado tem submódulos
                submodules = sorted([d for d in module_dir.iterdir() if d.is_dir()])
                for submodule in submodules:
                    lessons = process_module(submodule, order_counter)
                    all_lessons.extend(lessons)
                    order_counter += len(lessons)
            else:
                # Módulos simples (01-basic, 02-intermediario)
                lessons = process_module(module_dir, order_counter)
                all_lessons.extend(lessons)
                order_counter += len(lessons)

    # Salvar lessons.json
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lessons_file = OUTPUT_DIR / "lessons.json"
    with open(lessons_file, "w", encoding="utf-8") as f:
        json.dump(all_lessons, f, ensure_ascii=False, indent=4)

    print(f"Gerado: {lessons_file}")
    print(f"Total de lições: {len(all_lessons)}")

    # Criar exercises.json vazio
    exercises_file = OUTPUT_DIR / "exercises.json"
    with open(exercises_file, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

    print(f"Gerado: {exercises_file}")


if __name__ == "__main__":
    main()
