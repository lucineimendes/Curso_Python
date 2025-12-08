# Módulo 01: Fundamentos do Git

## Introdução
O Git é um sistema de controle de versão distribuído, essencial para qualquer desenvolvedor moderno. Ele permite rastrear mudanças no seu código, reverter para versões anteriores e colaborar com outros desenvolvedores.

## 1. Instalação e Configuração

Antes de começar, você precisa identificar-se para o Git. Isso garante que seus commits tenham sua autoria correta.

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

Para verificar suas configurações:
```bash
git config --list
```

## 2. O Ciclo de Vida Básico

O fluxo de trabalho básico no Git envolve três estados principais:
1.  **Working Directory**: Onde você edita seus arquivos.
2.  **Staging Area (Index)**: Onde você prepara as mudanças para serem salvas.
3.  **Repository**: Onde o Git armazena permanentemente o histórico.

### Comandos Essenciais

-   `git init`: Inicializa um novo repositório Git no diretório atual.
-   `git add <arquivo>`: Move mudanças do Working Directory para a Staging Area.
-   `git commit -m "mensagem"`: Grava as mudanças da Staging Area no Repositório.

## 3. Visualizando o Histórico

Para ver o que aconteceu no projeto até agora, usamos o comando `log`.

```bash
git log
```

Isso mostra o hash do commit, autor, data e mensagem. Para uma versão mais resumida:
```bash
git log --oneline
```

## 4. Ignorando Arquivos

Nem tudo deve ser versionado (arquivos temporários, builds, senhas). Para isso, criamos um arquivo chamado `.gitignore`.

Exemplo de `.gitignore`:
```
# Ignorar arquivos temporários do Python
__pycache__/
*.pyc

# Ignorar arquivos de ambiente
.env
```
