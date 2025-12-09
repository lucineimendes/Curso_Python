#!/bin/bash

# Script para migrar dados de progresso do usuário
# Adiciona campos de conquistas ao user_progress.json

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Migração de Dados de Progresso do Usuário ===${NC}"
echo ""

# Verificar se arquivo existe
PROGRESS_FILE="${1:-projects/data/user_progress.json}"

if [ ! -f "$PROGRESS_FILE" ]; then
    echo -e "${RED}❌ Erro: Arquivo '$PROGRESS_FILE' não encontrado${NC}"
    echo "Uso: $0 [caminho/para/user_progress.json]"
    exit 1
fi

echo -e "${YELLOW}📁 Arquivo: $PROGRESS_FILE${NC}"
echo ""

# Perguntar confirmação
read -p "Deseja criar backup e migrar este arquivo? (s/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}⚠️  Migração cancelada${NC}"
    exit 0
fi

# Executar migração
echo -e "${GREEN}🚀 Executando migração...${NC}"
python projects/data_migration.py "$PROGRESS_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migração concluída com sucesso!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "1. Verifique o arquivo migrado: $PROGRESS_FILE"
    echo "2. Confirme que o backup foi criado: ${PROGRESS_FILE}.backup"
    echo "3. Execute os testes: python -m pytest projects/testes/test_data_migration.py"
    echo ""
    echo "Para reverter: cp ${PROGRESS_FILE}.backup $PROGRESS_FILE"
else
    echo ""
    echo -e "${RED}❌ Erro durante a migração${NC}"
    echo "Verifique os logs acima para mais detalhes"
    exit 1
fi
