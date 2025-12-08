# Módulo 03/01: Git Internals - Por Baixo do Capô

## Introdução
Muitos desenvolvedores usam o Git apenas decorando comandos. Para dominar a ferramenta e resolver problemas complexos, é fundamental entender como o Git armazena e processa dados. Diferente de outros VCS que armazenam diferenças (deltas), o Git é um **sistema de arquivos endereçável por conteúdo**.

## 1. O Diretório `.git`

Toda a mágica acontece dentro da pasta oculta `.git` na raiz do seu projeto.
Principais componentes:

-   `HEAD`: Um ponteiro para o branch atual.
-   `config`: Configurações locais do projeto.
-   `objects/`: O banco de dados de objetos (onde o conteúdo real vive).
-   `refs/`: Ponteiros para commits (heads/branches, tags, remotes).

## 2. Os Objetos do Git

O Git armazena dados em quatro tipos principais de objetos. Cada objeto é identificado por um hash SHA-1 de 40 caracteres, calculado com base no seu conteúdo.

### Blob (Binary Large Object)
Armazena o **conteúdo** de um arquivo. Não contém o nome do arquivo, apenas os dados.
*Se você tiver dois arquivos com o mesmo conteúdo em pastas diferentes, o Git armazenará apenas um blob.*

### Tree
Representa diretórios. Uma Tree mapeia nomes de arquivos para Blobs e nomes de subdiretórios para outras Trees. É o que dá estrutura ao projeto.

### Commit
O objeto principal que une tudo. Contém:
-   Ponteiro para a Tree raiz do projeto naquele momento.
-   Ponteiro para o(s) commit(s) pai(s).
-   Metadados (autor, data, mensagem).

### Tag
Um rótulo fixo para um commit específico (geralmente usado para releases). Pode conter uma mensagem e assinatura GPG (Annotated Tag).

## 3. Endereçamento por Conteúdo

No Git, o nome do arquivo no banco de dados `objects/` é o hash do seu conteúdo.
Isso significa que:
1.  A integridade é garantida criptograficamente.
2.  Desduplicação é automática.
