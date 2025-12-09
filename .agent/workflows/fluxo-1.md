---
description: Fluxo de trabalho principal para desenvolvimento do Curso Python Interativo
---

# Fluxo de Trabalho - Curso Python Interativo

Este documento descreve o fluxo completo para desenvolver, testar e validar funcionalidades no projeto usando **uv** como gerenciador de pacotes.

---

## 1. Configuração do Ambiente

### Primeira vez (instalação completa)
```bash
# Instalar uv (se necessário)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar todas as dependências
make install
```

### Ativação do ambiente (dia a dia)
O `uv run` gerencia automaticamente o ambiente virtual, não precisa ativar manualmente.

---

## 2. Iniciar Servidor de Desenvolvimento

// turbo
```bash
uv run python -m projects.app
```

**Alternativa com Make:**
```bash
make run
```

O servidor estará disponível em: `http://localhost:5000`

---

## 3. Executar Testes

### Todos os testes
// turbo
```bash
uv run pytest
```

**Alternativa com Make:**
```bash
make test
```

### Testes específicos
```bash
# Testar apenas um arquivo
uv run pytest projects/testes/test_course_manager.py -v

# Testar uma função específica
uv run pytest projects/testes/test_course_manager.py::test_get_courses -v
```

---

## 4. Verificar Qualidade do Código

### Lint (verificar problemas)
// turbo
```bash
uv run ruff check projects/
```

**Alternativa com Make:**
```bash
make lint
```

### Lint com correções automáticas
```bash
uv run ruff check --fix projects/
```

### Formatação
```bash
# Verificar formatação
uv run ruff format --check projects/

# Aplicar formatação
uv run ruff format projects/
```

**Alternativa com Make:**
```bash
make format-check  # verificar
make format        # aplicar
```

---

## 5. Testar Navegação no Browser

### Teste automatizado (via agente)
Solicitar: "teste a navegação da aplicação web"

### Teste manual
```bash
# Abrir no Brave
brave-browser http://localhost:5000

# Ou no Chrome
google-chrome http://localhost:5000
```

---

## 6. Estrutura de Arquivos Principais

```
projeto/
├── projects/
│   ├── app.py              # Aplicação Flask principal
│   ├── templates/          # Templates HTML (Jinja2)
│   ├── static/             # CSS, JS, imagens
│   ├── data/               # JSON de cursos, lições, exercícios
│   ├── *_manager.py        # Managers de domínio
│   ├── testes/             # Testes unitários
│   └── run.py              # Script de execução
├── docs/                   # Documentação e conteúdo dos cursos
├── Makefile                # Comandos automatizados
├── pyproject.toml          # Configuração do projeto Python
└── requirements.txt        # Dependências Python
```

---

## 7. Adicionar Novo Conteúdo (Cursos/Lições/Exercícios)

### 7.1 Adicionar novo curso
1. Editar `projects/data/courses.json`
2. Criar arquivo de lições: `projects/data/lessons_<curso>.json`
3. Criar arquivo de exercícios: `projects/data/exercises_<curso>.json`
4. Criar documentação em `docs/<curso>/`

### 7.2 Adicionar lição
1. Editar o arquivo `projects/data/lessons_<curso>.json`
2. Adicionar objeto com: `id`, `title`, `description`, `content`

### 7.3 Adicionar exercício
1. Editar o arquivo `projects/data/exercises_<curso>.json`
2. Adicionar objeto com: `id`, `lesson_id`, `title`, `description`, `test_code`

---

## 8. Gerenciamento de Dependências com uv

### Adicionar nova dependência
```bash
uv pip install <pacote>
uv pip freeze > requirements.txt
```

### Sincronizar dependências
```bash
uv pip sync requirements.txt
```

### Ver dependências instaladas
```bash
uv pip list
```

---

## 9. Commit e Versionamento

### Antes de commitar
```bash
# 1. Formatar código
make format

# 2. Verificar lint
make lint

# 3. Rodar testes
make test
```

### Fazer commit
```bash
git add .
git commit -m "feat: descrição do que foi feito"
git push
```

---

## 10. Limpeza

### Limpar arquivos temporários
// turbo
```bash
make clean
```

---

## 11. Troubleshooting

### Porta 5000 em uso
```bash
# Encontrar processo na porta 5000
lsof -i :5000

# Matar processo
kill -9 <PID>
```

### uv não encontrado
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # ou ~/.zshrc
```

### Ambiente virtual corrompido
```bash
rm -rf .venv
uv venv
uv pip sync requirements.txt
```

### Imports relativos não funcionam
Use `uv run python -m projects.app` em vez de `python projects/app.py`

---

// turbo-all
