# Guia de Uso do uv

## O que é uv?

`uv` é um gerenciador de pacotes Python extremamente rápido, desenvolvido pela Astral (mesma equipe do Ruff). É uma alternativa moderna ao pip, sendo 10-100x mais rápido em muitas operações.

## Instalação

### Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Via pip

```bash
pip install uv
```

### Via pipx (isolado)

```bash
pipx install uv
```

### Verificar Instalação

```bash
uv --version
```

## Comandos Básicos

### Gerenciamento de Ambiente Virtual

```bash
# Criar ambiente virtual
uv venv

# Criar com nome específico
uv venv meu-venv

# Criar com versão específica do Python
uv venv --python 3.11
```

### Instalação de Pacotes

```bash
# Instalar pacote
uv pip install flask

# Instalar múltiplos pacotes
uv pip install flask pytest ruff

# Instalar de requirements.txt
uv pip install -r requirements.txt

# Instalar em modo desenvolvimento
uv pip install -e .
```

### Executar Comandos

```bash
# Executar comando sem ativar venv
uv run python script.py
uv run pytest
uv run ruff check .

# Executar com argumentos
uv run python projects/run.py
uv run pytest -v
```

### Outros Comandos

```bash
# Listar pacotes instalados
uv pip list

# Mostrar informações de um pacote
uv pip show flask

# Desinstalar pacote
uv pip uninstall flask

# Congelar dependências
uv pip freeze > requirements.txt
```

## Uso no Projeto

### Configuração Inicial

```bash
# 1. Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Criar ambiente virtual
uv venv

# 3. Instalar dependências
uv pip install -r requirements.txt
```

### Desenvolvimento Diário

```bash
# Executar servidor
uv run python projects/run.py

# Executar testes
uv run pytest

# Formatar código
uv run ruff format projects/

# Lint
uv run ruff check projects/

# Corrigir problemas
uv run ruff check --fix projects/
```

### Com Make

O Makefile já está configurado para usar uv:

```bash
make install    # Instala uv e dependências
make run        # Executa servidor com uv
make test       # Executa testes com uv
make format     # Formata código com uv
make lint       # Executa linters com uv
```

## Vantagens do uv

### Velocidade

- **10-100x mais rápido** que pip em muitas operações
- Resolução de dependências paralela
- Cache inteligente de pacotes

### Compatibilidade

- 100% compatível com pip
- Funciona com requirements.txt
- Suporta todos os pacotes do PyPI

### Recursos Modernos

- Resolução de dependências mais inteligente
- Melhor tratamento de conflitos
- Suporte a múltiplas versões do Python

## Comparação com pip

| Operação | pip | uv |
|----------|-----|-----|
| Instalar Flask | ~2s | ~0.2s |
| Instalar 50 pacotes | ~30s | ~3s |
| Resolver dependências | Sequencial | Paralelo |
| Cache | Básico | Avançado |

## Migração de pip para uv

### Comandos Equivalentes

```bash
# pip → uv
pip install package          → uv pip install package
pip install -r requirements  → uv pip install -r requirements
pip list                     → uv pip list
pip freeze                   → uv pip freeze
pip uninstall package        → uv pip uninstall package

# Novo no uv
python script.py             → uv run python script.py
```

### Sem Mudanças Necessárias

- `requirements.txt` funciona sem modificações
- `pyproject.toml` funciona sem modificações
- Todos os pacotes do PyPI são suportados

## Troubleshooting

### uv não encontrado após instalação

```bash
# Adicionar ao PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Adicionar ao ~/.bashrc ou ~/.zshrc
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Conflito com pip

uv e pip podem coexistir. Use uv para operações rápidas e pip quando necessário.

### Cache ocupando muito espaço

```bash
# Limpar cache do uv
uv cache clean
```

## Recursos

- [Documentação Oficial](https://docs.astral.sh/uv/)
- [GitHub](https://github.com/astral-sh/uv)
- [Anúncio do uv](https://astral.sh/blog/uv)

## Dicas

1. **Use `uv run`** para executar comandos sem ativar o venv
2. **Cache global** acelera instalações em múltiplos projetos
3. **Compatível com CI/CD** - funciona em GitHub Actions, GitLab CI, etc.
4. **Não substitui venv** - ainda precisa criar ambientes virtuais
5. **Atualização fácil** - `uv self update` para atualizar o próprio uv
