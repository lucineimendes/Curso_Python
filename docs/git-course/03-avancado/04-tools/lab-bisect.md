# Laboratório 04: Detetive Git com Bisect

**Objetivo**: Usar o `git bisect` para encontrar um commit que inseriu um bug no código.

## Passo 1: Preparando o Cenário

1.  Crie um repositório para o lab.
2.  Crie um script Python simples `app.py`:
    ```python
    def soma(a, b):
        return a + b

    print(f"2 + 2 = {soma(2, 2)}")
    ```
    Commit inicial: "feat: add soma function" (GOOD).

3.  Faça vários commits neutros (ex: atualizando docs, README).
4.  Faça o **commit do bug**:
    Altere `app.py` para:
    ```python
    def soma(a, b):
        return a * b  # BUG! Multiplicação em vez de soma
    ```
    Commit: "refactor: optimize math engine".

5.  Faça mais commits neutros depois disso.

## Passo 2: Iniciando a Caçada

Execute o script. Você verá `2 + 2 = 4` (ops, 2*2 também é 4, mau exemplo!).
Vamos mudar para: `soma(2, 3)`. O esperado é 5, mas o bug deve dar 6.

1.  Verifique o erro na HEAD:
    Execute e veja o resultado errado.

2.  Inicie o bisect:
    ```bash
    git bisect start
    git bisect bad  # A versão atual (HEAD) está ruim
    ```

3.  Vá para o commit inicial e verifique se estava bom:
    ```bash
    git checkout [HASH_INICIAL]
    python3 app.py # Verifica se 2+3=5
    git bisect good # A versão antiga estava boa
    ```

## Passo 3: O Processo de Bisect

O Git agora fará checkout um commit no meio do caminho.

1.  Teste a versão atual:
    ```bash
    python3 app.py
    ```
2.  Diga ao Git o resultado:
    - Se o resultado for 5 (correto): `git bisect good`
    - Se o resultado for 6 (errado): `git bisect bad`

3.  Repita até o Git dizer:
    `[HASH] is the first bad commit`

## Passo 4: Finalizando

1.  Saia do modo bisect:
    ```bash
    git bisect reset
    ```

2.  Agora você sabe quem quebrou o código!
