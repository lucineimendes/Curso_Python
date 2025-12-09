# Guia de Migração de Dados de Progresso do Usuário

## Visão Geral

Este guia documenta o processo de migração de arquivos `user_progress.json` do formato antigo (sem campos de conquistas) para o novo formato que inclui suporte ao sistema de conquistas e badges.

## O Que a Migração Faz

A migração adiciona dois novos campos aos dados de cada usuário:

1. **`achievements`**: Lista de conquistas desbloqueadas pelo usuário
   - Formato: `[{"id": "achievement_id", "unlocked_at": "timestamp"}, ...]`
   - Valor padrão: `[]` (lista vazia)

2. **`achievement_stats`**: Estatísticas para rastreamento de conquistas
   - Formato: `{"perfect_exercises_count": 0, "lessons_in_day": 0, "last_activity_date": null}`
   - Valores padrão: todos os contadores em 0, data nula

## Quando Executar a Migração

A migração deve ser executada:

- **Antes de implantar** o sistema de conquistas em produção
- **Após fazer backup** dos dados existentes
- **Uma única vez** por ambiente (a migração é idempotente)

## Como Executar a Migração

### Opção 1: Migração Automática via Script

Execute o script de migração diretamente:

```bash
# Migrar o arquivo padrão (projects/data/user_progress.json)
python projects/data_migration.py

# Migrar um arquivo específico
python projects/data_migration.py /caminho/para/user_progress.json
```

O script irá:
1. Criar um backup automático (`user_progress.json.backup`)
2. Migrar os dados
3. Salvar o arquivo atualizado

### Opção 2: Migração Programática

Use as funções do módulo em seu código:

```python
from projects.data_migration import migrate_file, migrate_user_progress

# Migrar arquivo com backup
success = migrate_file("projects/data/user_progress.json")

# Ou migrar dados em memória
import json

with open("user_progress.json") as f:
    data = json.load(f)

migrated_data = migrate_user_progress(data)

with open("user_progress.json", "w") as f:
    json.dump(migrated_data, f, indent=4)
```

## Estrutura de Dados

### Antes da Migração

```json
{
  "users": {
    "default": {
      "courses": {...},
      "total_lessons_completed": 5,
      "total_exercises_completed": 3,
      "created_at": "2025-12-03T17:48:26.625209"
    }
  }
}
```

### Depois da Migração

```json
{
  "users": {
    "default": {
      "courses": {...},
      "total_lessons_completed": 5,
      "total_exercises_completed": 3,
      "created_at": "2025-12-03T17:48:26.625209",
      "achievements": [],
      "achievement_stats": {
        "perfect_exercises_count": 0,
        "lessons_in_day": 0,
        "last_activity_date": null
      }
    }
  }
}
```

## Garantias da Migração

A migração garante:

✅ **Preservação de dados**: Todos os dados existentes são mantidos intactos
✅ **Idempotência**: Pode ser executada múltiplas vezes sem problemas
✅ **Backup automático**: Cria backup antes de modificar o arquivo
✅ **Tratamento de erros**: Lida graciosamente com dados corrompidos ou faltando
✅ **Validação**: Verifica e corrige estruturas de dados inválidas

## Casos Especiais

### Usuários com Conquistas Existentes

Se um usuário já possui os campos `achievements` ou `achievement_stats`, a migração:
- **Preserva** os dados existentes
- **Não sobrescreve** conquistas já desbloqueadas
- **Adiciona** apenas campos faltando

### Dados Corrompidos

Se os dados estiverem corrompidos:
- Campos inválidos são reinicializados com valores padrão
- Logs de erro são gerados para auditoria
- A migração continua para outros usuários válidos

### Arquivo Inexistente

Se o arquivo não existir:
- A migração retorna `False`
- Um erro é registrado no log
- Nenhuma exceção é lançada

## Verificação Pós-Migração

Após executar a migração, verifique:

1. **Backup criado**: Confirme que `user_progress.json.backup` existe
2. **Campos adicionados**: Verifique que todos os usuários têm `achievements` e `achievement_stats`
3. **Dados preservados**: Confirme que cursos, lições e exercícios não foram alterados
4. **Formato válido**: Valide que o JSON está bem formatado

```bash
# Verificar estrutura do arquivo migrado
python -c "
import json
with open('projects/data/user_progress.json') as f:
    data = json.load(f)
    for user_id, user_data in data['users'].items():
        assert 'achievements' in user_data, f'achievements faltando para {user_id}'
        assert 'achievement_stats' in user_data, f'achievement_stats faltando para {user_id}'
print('✅ Migração verificada com sucesso!')
"
```

## Rollback

Se precisar reverter a migração:

```bash
# Restaurar do backup
cp projects/data/user_progress.json.backup projects/data/user_progress.json
```

## Testes

Execute os testes de migração para validar o processo:

```bash
# Executar todos os testes de migração
python -m pytest projects/testes/test_data_migration.py -v

# Executar teste específico
python -m pytest projects/testes/test_data_migration.py::test_migrate_preserves_existing_data -v
```

## Logs

A migração gera logs detalhados:

- **INFO**: Operações bem-sucedidas
- **WARNING**: Dados inválidos que foram corrigidos
- **ERROR**: Falhas que impediram a migração

Configure o nível de log conforme necessário:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Para logs detalhados
```

## Suporte

Em caso de problemas:

1. Verifique os logs de erro
2. Confirme que o backup foi criado
3. Execute os testes de migração
4. Consulte a documentação do sistema de conquistas

## Referências

- **Módulo de migração**: `projects/data_migration.py`
- **Testes**: `projects/testes/test_data_migration.py`
- **Design de conquistas**: `.kiro/specs/achievements-badges/design.md`
- **Requisitos**: `.kiro/specs/achievements-badges/requirements.md`
