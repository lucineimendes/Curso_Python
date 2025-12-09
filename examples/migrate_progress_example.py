"""
Exemplo de uso do módulo de migração de dados.

Este script demonstra como usar as funções de migração
programaticamente em seu próprio código.
"""

import json
import sys
from pathlib import Path

# Adicionar diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# ruff: noqa: E402
from projects.data_migration import migrate_file, migrate_user_progress


def example_1_migrate_data_in_memory():
    """Exemplo 1: Migrar dados em memória."""
    print("=== Exemplo 1: Migração em Memória ===\n")

    # Dados no formato antigo
    old_data = {
        "users": {
            "user123": {
                "courses": {},
                "total_lessons_completed": 5,
                "total_exercises_completed": 3,
                "created_at": "2025-12-01T10:00:00",
            }
        }
    }

    print("Dados antes da migração:")
    print(json.dumps(old_data, indent=2))

    # Migrar
    migrated_data = migrate_user_progress(old_data)

    print("\nDados após migração:")
    print(json.dumps(migrated_data, indent=2))
    print()


def example_2_migrate_file():
    """Exemplo 2: Migrar arquivo com backup."""
    print("=== Exemplo 2: Migração de Arquivo ===\n")

    # Criar arquivo temporário de exemplo
    temp_file = Path("temp_progress.json")

    example_data = {
        "users": {
            "alice": {
                "courses": {},
                "total_lessons_completed": 10,
                "total_exercises_completed": 8,
                "created_at": "2025-11-15T09:00:00",
            },
            "bob": {
                "courses": {},
                "total_lessons_completed": 3,
                "total_exercises_completed": 2,
                "created_at": "2025-12-01T14:30:00",
            },
        }
    }

    # Salvar arquivo
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(example_data, f, indent=4)

    print(f"Arquivo criado: {temp_file}")

    # Migrar arquivo
    success = migrate_file(str(temp_file))

    if success:
        print("✅ Migração bem-sucedida!")
        print(f"📁 Arquivo migrado: {temp_file}")
        print(f"💾 Backup criado: {temp_file}.backup")

        # Ler e mostrar resultado
        with open(temp_file, encoding="utf-8") as f:
            migrated = json.load(f)

        print("\nUsuários migrados:")
        for user_id, user_data in migrated["users"].items():
            print(f"  - {user_id}:")
            print(f"    achievements: {len(user_data.get('achievements', []))}")
            print(f"    achievement_stats: {user_data.get('achievement_stats', {})}")
    else:
        print("❌ Migração falhou")

    # Limpar arquivos temporários
    if temp_file.exists():
        temp_file.unlink()
    backup_file = Path(str(temp_file) + ".backup")
    if backup_file.exists():
        backup_file.unlink()

    print()


def example_3_check_if_migration_needed():
    """Exemplo 3: Verificar se migração é necessária."""
    print("=== Exemplo 3: Verificar Necessidade de Migração ===\n")

    def needs_migration(progress_data):
        """Verifica se dados precisam de migração."""
        if not isinstance(progress_data, dict):
            return True

        users = progress_data.get("users", {})
        if not isinstance(users, dict):
            return True

        for user_data in users.values():
            if not isinstance(user_data, dict):
                continue

            # Verificar se faltam campos
            if "achievements" not in user_data:
                return True
            if "achievement_stats" not in user_data:
                return True

        return False

    # Testar com dados antigos
    old_data = {"users": {"user1": {"courses": {}, "total_lessons_completed": 1, "total_exercises_completed": 0}}}

    print("Dados antigos precisam de migração?", needs_migration(old_data))

    # Testar com dados novos
    new_data = {
        "users": {
            "user1": {
                "courses": {},
                "total_lessons_completed": 1,
                "total_exercises_completed": 0,
                "achievements": [],
                "achievement_stats": {"perfect_exercises_count": 0, "lessons_in_day": 0, "last_activity_date": None},
            }
        }
    }

    print("Dados novos precisam de migração?", needs_migration(new_data))
    print()


def example_4_batch_migration():
    """Exemplo 4: Migração em lote de múltiplos arquivos."""
    print("=== Exemplo 4: Migração em Lote ===\n")

    # Simular múltiplos arquivos
    files = ["user_progress_prod.json", "user_progress_dev.json", "user_progress_test.json"]

    print("Migrando múltiplos arquivos:")
    for filename in files:
        # Em produção, você verificaria se o arquivo existe
        print(f"  - {filename}: ", end="")

        # Simular resultado
        # success = migrate_file(filename)
        # if success:
        #     print("✅")
        # else:
        #     print("❌")

        print("(simulado)")

    print("\nDica: Use um loop para migrar múltiplos ambientes")
    print()


def main():
    """Executa todos os exemplos."""
    print("=" * 60)
    print("Exemplos de Uso do Módulo de Migração")
    print("=" * 60)
    print()

    example_1_migrate_data_in_memory()
    example_2_migrate_file()
    example_3_check_if_migration_needed()
    example_4_batch_migration()

    print("=" * 60)
    print("Para mais informações, consulte:")
    print("  - docs/guides/MIGRATION_USER_PROGRESS.md")
    print("  - projects/data_migration.py")
    print("  - projects/testes/test_data_migration.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
