# Git Cheat Sheet - Referência Rápida

## Configuração
```bash
git config --global user.name "Nome"
git config --global user.email "email@exemplo.com"
git config --list                  # Ver config
```

## Básico
```bash
git init                           # Iniciar repositório
git clone <url>                    # Clonar repositório
git status                         # Ver estado dos arquivos
git add <arquivo>                  # Adicionar ao stage
git add .                          # Adicionar tudo
git commit -m "Mensagem"           # Comitar
git log --oneline                  # Histórico resumido
```

## Branches
```bash
git branch                         # Listar branches
git branch <nome>                  # Criar branch
git checkout <nome>                # Mudar de branch
git checkout -b <nome>             # Criar e mudar
git merge <nome>                   # Mesclar branch no atual
git branch -d <nome>               # Deletar branch
```

## Remoto
```bash
git remote add origin <url>        # Adicionar remoto
git push -u origin <branch>        # Enviar (primeira vez)
git push                           # Enviar alterações
git pull                           # Trazer alterações
git fetch                          # Trazer sem mesclar
```

## Avançado
```bash
git commit --amend                 # Corrigir último commit
git rebase -i <commit>             # Rebase interativo
git reset --hard HEAD~1            # Voltar 1 commit (destrutivo)
git reflog                         # Histórico de ações (salva vidas)
git cherry-pick <hash>             # Copiar commit específico
git stash                          # Guardar mudanças temporariamente
git stash pop                      # Recuperar mudanças
git bisect start                   # Iniciar busca de bug
```
