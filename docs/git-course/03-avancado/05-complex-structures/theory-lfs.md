# Módulo 03/05: Git LFS (Large File Storage)

## Introdução
O Git não foi feito para arquivos binários grandes (vídeos, PSDs, modelos 3D). Como ele salva o histórico completo localmente, repositórios com binários ficam gigantescos rapidamente.

## 1. O Problema
Se você comita um arquivo de 100MB e depois o altera, o repositório cresce 200MB. Mesmo que você apague o arquivo no commit seguinte, ele continua no histórico (`.git/objects`), ocupando espaço para sempre.

## 2. A Solução: Git LFS
O Git LFS é uma extensão que substitui arquivos grandes por ponteiros de texto dentro do Git, enquanto armazena o conteúdo real em um servidor remoto especializado.

### Como Funciona
1.  Você diz ao Git LFS para rastrear `*.psd`.
2.  Quando você adiciona um PSD, o LFS intercepta.
3.  O Git normal vê apenas um arquivo de texto pequeno (o ponteiro).
4.  O servidor LFS armazena o blob grande.

## 3. Comandos Básicos

```bash
# 1. Instalar (uma vez por máquina)
git lfs install

# 2. Rastrear arquivos (uma vez por projeto)
git lfs track "*.psd"

# 3. Isso cria um .gitattributes, que deve ser comitado
git add .gitattributes
```

Depois disso, use `git add` e `git commit` normalmente. O LFS cuida do resto.
