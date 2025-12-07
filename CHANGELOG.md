# Changelog

## [Não Lançado]

### Adicionado

#### Sistema de Roadmap e Progresso
- Roadmap visual interativo para acompanhamento de progresso
- Mapa com checkpoints e ramificações para cada lição
- Rastreamento automático de lições e exercícios completados
- Estatísticas detalhadas de progresso (lições, exercícios, percentuais)
- Persistência de progresso em JSON (backend) e localStorage (frontend)
- API RESTful para gerenciamento de progresso
- Visualização de exercícios por lição no roadmap
- Animações e transições suaves no roadmap
- Suporte a tema escuro no roadmap
- Botão de acesso ao roadmap na página de detalhes do curso

#### Tema Escuro
- Sistema de tema escuro/claro com alternância no navbar
- Botão de alternância de tema com ícones 🌙/☀️
- Persistência de preferência de tema em localStorage
- Detecção automática de preferência do sistema operacional
- Suporte a tema escuro no CodeMirror (tema monokai)
- Transições suaves entre temas (0.3s)
- Variáveis CSS para gerenciamento centralizado de cores
- Guia de documentação do sistema de temas (`theme-guide.md`)

### Formatadores e Linters
- Configuração do Ruff para formatação e linting Python
- Configuração do Prettier para JavaScript, CSS e HTML
- Arquivo `pyproject.toml` com configurações do Ruff
- Arquivo `.prettierrc` com configurações do Prettier
- Arquivo `.pre-commit-config.yaml` para hooks de pre-commit
- Makefile com comandos para formatação e linting
- Scripts npm para formatação automatizada

### Documentação
- Steering rules adicionadas (`.kiro/steering/`)
  - `product.md` - Visão geral do produto
  - `tech.md` - Stack tecnológico e comandos
  - `structure.md` - Estrutura e padrões do projeto
- `CONTRIBUTING.md` - Guia de contribuição completo
- `UV_GUIDE.md` - Guia de uso do uv
- Configurações do VS Code (`.vscode/settings.json`)
- Recomendações de extensões (`.vscode/extensions.json`)

### Gerenciamento de Pacotes
- Migração para `uv` como gerenciador de pacotes recomendado
- Script de setup automático (`setup.sh`)
- Atualização de todos os comandos para usar `uv`
- Documentação completa sobre uso do `uv`

### Modificado
- `requirements.txt` - Adicionadas ferramentas de desenvolvimento (ruff, black, pytest)
- `README.md` - Atualizado com instruções de instalação e desenvolvimento
- `Makefile` - Todos os comandos atualizados para usar `uv`
- `package.json` - Scripts atualizados para usar `uv`
- Todos os guias de documentação para usar `uv` em vez de `pip`

### Arquivos Criados

#### Sistema de Roadmap
- `projects/progress_manager.py` - Gerenciador de progresso do usuário
- `projects/static/js/roadmap.js` - Componente JavaScript do roadmap
- `projects/static/css/roadmap.css` - Estilos do roadmap
- `projects/templates/course_roadmap.html` - Template da página de roadmap
- `docs/architecture/ROADMAP_SYSTEM.md` - Documentação completa do sistema

#### Formatadores e Configuração
- `.prettierrc` - Configuração do Prettier
- `.prettierignore` - Arquivos ignorados pelo Prettier
- `pyproject.toml` - Configuração do projeto Python
- `package.json` - Configuração do projeto Node
- `Makefile` - Comandos automatizados
- `.pre-commit-config.yaml` - Hooks de pre-commit
- `setup.sh` - Script de configuração automática
- `CONTRIBUTING.md` - Guia de contribuição
- `CHANGELOG.md` - Este arquivo
- `docs/guides/UV_GUIDE.md` - Guia completo do uv
- `projects/static/css/theme-guide.md` - Guia do sistema de temas
- `.vscode/settings.json` - Configurações do VS Code
- `.vscode/extensions.json` - Extensões recomendadas

## Próximos Passos

- [ ] Adicionar mais temas (ex: tema de alto contraste)
- [ ] Implementar preferências de usuário no backend
- [ ] Adicionar testes para o sistema de temas
- [ ] Configurar CI/CD com GitHub Actions
- [ ] Adicionar badges ao README (build status, coverage, etc.)
