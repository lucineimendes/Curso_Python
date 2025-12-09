"""
Módulo para migração de dados de progresso do usuário.

Este módulo fornece funções para migrar arquivos user_progress.json antigos
para o novo formato que inclui campos achievements e achievement_stats.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def migrate_user_progress(progress_data: Dict) -> Dict:
    """
    Migra dados de progresso do usuário para incluir campos de conquistas.

    Adiciona campos 'achievements' e 'achievement_stats' a todos os usuários
    que não os possuem, preservando todos os dados existentes.

    Args:
        progress_data (Dict): Dados de progresso no formato antigo ou novo.

    Returns:
        Dict: Dados de progresso migrados com campos de conquistas.
    """
    if not isinstance(progress_data, dict):
        logger.error("progress_data não é um dicionário. Retornando dados vazios.")
        return {"users": {}}

    if "users" not in progress_data:
        logger.warning("Campo 'users' não encontrado. Adicionando estrutura vazia.")
        progress_data["users"] = {}

    if not isinstance(progress_data["users"], dict):
        logger.error("Campo 'users' não é um dicionário. Reinicializando.")
        progress_data["users"] = {}

    # Migrar cada usuário
    for user_id, user_data in progress_data["users"].items():
        if not isinstance(user_data, dict):
            logger.warning(f"Dados do usuário '{user_id}' não são um dicionário. Pulando.")
            continue

        # Adicionar campo achievements se não existir
        if "achievements" not in user_data:
            user_data["achievements"] = []
            logger.debug(f"Campo 'achievements' adicionado para usuário '{user_id}'")
        elif not isinstance(user_data["achievements"], list):
            logger.warning(f"Campo 'achievements' do usuário '{user_id}' não é uma lista. Reinicializando.")
            user_data["achievements"] = []

        # Adicionar campo achievement_stats se não existir
        if "achievement_stats" not in user_data:
            user_data["achievement_stats"] = {
                "perfect_exercises_count": 0,
                "lessons_in_day": 0,
                "last_activity_date": None,
            }
            logger.debug(f"Campo 'achievement_stats' adicionado para usuário '{user_id}'")
        elif not isinstance(user_data["achievement_stats"], dict):
            logger.warning(f"Campo 'achievement_stats' do usuário '{user_id}' não é um dicionário. Reinicializando.")
            user_data["achievement_stats"] = {
                "perfect_exercises_count": 0,
                "lessons_in_day": 0,
                "last_activity_date": None,
            }
        else:
            # Garantir que todos os subcampos existem
            stats = user_data["achievement_stats"]
            if "perfect_exercises_count" not in stats:
                stats["perfect_exercises_count"] = 0
            if "lessons_in_day" not in stats:
                stats["lessons_in_day"] = 0
            if "last_activity_date" not in stats:
                stats["last_activity_date"] = None

    logger.info(f"Migração concluída para {len(progress_data['users'])} usuários")
    return progress_data


def migrate_file(file_path: str, create_backup: bool = True) -> bool:
    """
    Migra um arquivo user_progress.json para o novo formato.

    Cria um backup do arquivo original antes de migrar.

    Args:
        file_path (str): Caminho para o arquivo user_progress.json.
        create_backup (bool): Se True, cria backup antes de migrar.

    Returns:
        bool: True se a migração foi bem-sucedida, False caso contrário.
    """
    file_path_obj = Path(file_path)

    # Verificar se arquivo existe
    if not file_path_obj.exists():
        logger.error(f"Arquivo '{file_path}' não encontrado.")
        return False

    try:
        # Ler dados originais
        with open(file_path_obj, encoding="utf-8") as f:
            original_data = json.load(f)

        # Criar backup se solicitado
        if create_backup:
            backup_path = file_path_obj.with_suffix(file_path_obj.suffix + ".backup")
            shutil.copy2(file_path_obj, backup_path)
            logger.info(f"Backup criado em: {backup_path}")

        # Migrar dados
        migrated_data = migrate_user_progress(original_data)

        # Salvar dados migrados
        with open(file_path_obj, "w", encoding="utf-8") as f:
            json.dump(migrated_data, f, indent=4, ensure_ascii=False)

        logger.info(f"Arquivo '{file_path}' migrado com sucesso.")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON de '{file_path}': {e}", exc_info=True)
        return False
    except OSError as e:
        logger.error(f"Erro de I/O ao processar '{file_path}': {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao migrar '{file_path}': {e}", exc_info=True)
        return False


def main():
    """
    Função principal para executar migração via linha de comando.

    Migra o arquivo user_progress.json padrão no diretório data/.
    """
    import sys

    # Configurar logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Determinar caminho do arquivo
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Usar caminho padrão
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / "data" / "user_progress.json"

    logger.info(f"Iniciando migração de: {file_path}")

    # Executar migração
    success = migrate_file(str(file_path))

    if success:
        logger.info("Migração concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("Migração falhou. Verifique os logs acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
