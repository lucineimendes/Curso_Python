# Visão Geral do Produto

Curso Interativo Python é uma plataforma de aprendizado interativo de Python construída com Flask. A aplicação fornece uma experiência de aprendizado estruturada com cursos, lições e exercícios práticos.

## Funcionalidades Principais

- Navegação por cursos organizados por nível de dificuldade (Básico, Intermediário, Avançado)
- **Roadmap Visual Interativo**: Mapa de progresso com checkpoints e estatísticas
- **Rastreamento de Progresso**: Acompanhamento automático de lições e exercícios completados
- Visualização de conteúdo de lições com formatação HTML
- Editor de código interativo para resolver exercícios
- Execução de código Python em tempo real no navegador
- Verificação automática de exercícios usando código de teste predefinido
- API RESTful para acesso programático e gerenciamento de progresso

## Fluxo do Usuário

Usuários navegam através de: cursos → **roadmap** → lições → exercícios.

### Roadmap do Curso
- Visualização do mapa de progresso com todos os checkpoints
- Estatísticas em tempo real (lições completadas, exercícios resolvidos, percentual geral)
- Navegação direta para lições e exercícios
- Indicadores visuais de progresso (nós verdes = completo, azuis = pendente)

### Cada Exercício Inclui
- Descrição do problema e instruções
- Editor de código com código inicial/starter
- Botão de execução para rodar código e ver saída
- Verificação automática contra casos de teste
- **Marcação automática de progresso ao completar**

## Modelo de Dados

Conteúdo armazenado em arquivos JSON organizados por nível do curso:
- `data/courses.json` - Metadados dos cursos
- `data/{level}/lessons.json` - Conteúdo das lições por curso
- `data/{level}/exercises.json` - Definições de exercícios com código de teste

Cada exercício inclui `solution_code` e `test_code` para verificação automatizada.

### Progresso do Usuário (`data/user_progress.json`)
- Rastreamento de lições completadas por curso
- Rastreamento de exercícios resolvidos com tentativas
- Timestamps de conclusão e último acesso
- Estatísticas agregadas por usuário
