# Módulo 03/05: Estruturas Complexas (Submódulos)

## Introdução
À medida que os projetos crescem, surge a necessidade de compartilhar código entre repositórios. O Git oferece **Submodules** (e Subtrees) para resolver isso.

## 1. O que são Submodules?
Um submódulo permite manter um repositório Git dentro de outro repositório Git. O projeto principal (superprojeto) mantém apenas um link para um commit específico do submódulo.

### Conceitos Chave
-   O submódulo é um repositório completo e independente.
-   O superprojeto não rastreia o *conteúdo* do submódulo, apenas aponta para um HASH.
-   Quando você clona o superprojeto, os submódulos vêm vazios por padrão.

## 2. Comandos Essenciais

### Adicionar um Submódulo
```bash
git submodule add https://github.com/exemplo/lib.gitlibs/lib
```

### Clonar com Submódulos
```bash
git clone --recursive <url-do-superprojeto>
```
Ou, se já clonou:
```bash
git submodule update --init --recursive
```

### Atualizar Submódulos
Se o repositório remoto do submódulo mudou:
```bash
git submodule update --remote
```

## 3. Cuidados
-   **Esquecer de atualizar**: Se você mudar o commit do submódulo mas não comitar no superprojeto, outros não verão a mudança.
-   **Complexidade**: Git Submodules são famosos por serem difíceis de gerenciar. Use apenas se necessário (monorepos ou libs compartilhadas privadas).
