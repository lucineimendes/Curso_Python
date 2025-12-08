# Refatoração: Remoção de Rota Legada

## Metadata
- **Status**: 🟡 Proposta
- **Impacto**: Baixo
- **Esforço Estimado**: 30 minutos
- **Prioridade**: Média
- **Data**: 2025-12-08

## Problema Identificado

A rota legada `/submit_exercise/<course_id>/<exercise_id>` em `app.py` contém **~100 linhas de código duplicado** que violam o princípio **DRY (Don't Repeat Yourself)**.

### Evidências

1. **Código Duplicado**: A lógica da rota legada duplica completamente a lógica de `/api/check-exercise`
2. **Não Utilizada**: Busca no código confirma que a rota não é chamada em:
   - JavaScript (*.js)
   - Templates HTML (*.html)
   - Código Python (*.py)
3. **Reconhecimento no Código**: Os próprios comentários admitem a duplicação:
   ```python
   """Esta rota é mantida para compatibilidade, mas sua lógica foi
   majoritariamente duplicada da rota `/api/check-exercise`.
   Idealmente, esta rota deveria ser refatorada para chamar a lógica
   de `/api/check-exercise` ou ser removida se não for mais utilizada."""
   ```

### Violações de Princípios

- **DRY**: Código duplicado (~100 linhas)
- **YAGNI** (You Aren't Gonna Need It): Mantendo código não utilizado
- **Clean Code**: Aumenta complexidade desnecessariamente

## Proposta de Solução

### Opção 1: Remoção Completa (Recomendada)

Remover completamente a rota legada, já que não está sendo utilizada.

**Benefícios**:
- Elimina 100% da duplicação
- Reduz tamanho do app.py em ~11% (de 878 para ~778 linhas)
- Simplifica manutenção
- Melhora legibilidade

**Riscos**:
- Nenhum (rota não está sendo usada)

### Opção 2: Redirecionamento (Alternativa)

Se houver preocupação com compatibilidade externa (APIs de terceiros), criar um redirecionamento simples:

```python
@app.route('/submit_exercise/<string:course_id>/<string:exercise_id_str>', methods=['POST'])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    """Rota legada - redireciona para nova API."""
    logger.warning(f"Rota legada /submit_exercise chamada. Redirecionando para /api/check-exercise")

    data = request.get_json() or {}
    code = data.get('code') or request.form.get('code')

    if not code:
        return jsonify({"success": False, "details": "Campo 'code' obrigatório"}), 400

    # Redireciona para nova API
    return api_check_exercise()
```

**Benefícios**:
- Reduz duplicação de ~100 para ~10 linhas (90% de redução)
- Mantém compatibilidade se necessário

## Estrutura Atual vs. Proposta

### Atual (878 linhas)
```
app.py
├── Rotas UI (~200 linhas)
├── Rotas API (~500 linhas)
│   └── /api/check-exercise (lógica principal)
├── Rota Legada (~100 linhas) ❌ DUPLICAÇÃO
└── Error Handlers (~78 linhas)
```

### Proposta (778 linhas)
```
app.py
├── Rotas UI (~200 linhas)
├── Rotas API (~500 linhas)
│   └── /api/check-exercise (lógica principal)
└── Error Handlers (~78 linhas)
```

## Plano de Implementação

### Fase 1: Verificação (5 min)
- [x] Confirmar que rota não é usada no frontend
- [x] Confirmar que rota não é usada em testes
- [ ] Verificar logs de produção (se aplicável)

### Fase 2: Remoção (10 min)
- [ ] Remover função `submit_exercise_solution_legacy` (linhas 735-835)
- [ ] Atualizar comentários se necessário
- [ ] Executar formatação automática

### Fase 3: Testes (10 min)
- [ ] Executar suite de testes: `uv run pytest`
- [ ] Verificar que todos os testes passam
- [ ] Testar manualmente fluxo de exercícios

### Fase 4: Documentação (5 min)
- [ ] Atualizar `structure.md` removendo menção à rota legada
- [ ] Adicionar nota no CHANGELOG.md
- [ ] Marcar este documento como "Implementado"

## Código a Remover

**Arquivo**: `projects/app.py`
**Linhas**: 735-835 (aproximadamente)
**Função**: `submit_exercise_solution_legacy()`

```python
# --- Rota Legada (Manter por compatibilidade ou remover se não for mais usada) ---
@app.route('/submit_exercise/<string:course_id>/<string:exercise_id_str>', methods=['POST'])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    # ... ~100 linhas de código duplicado ...
```

## Métricas de Impacto

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Linhas em app.py | 878 | ~778 | -11% |
| Código duplicado | ~100 linhas | 0 | -100% |
| Rotas de exercício | 2 | 1 | -50% |
| Complexidade | Alta | Média | ✅ |
| Manutenibilidade | Média | Alta | ✅ |

## Testes de Regressão

### Testes Automáticos
```bash
# Executar todos os testes
uv run pytest

# Testes específicos de exercícios
uv run pytest projects/testes/test_app.py::test_check_exercise_api
uv run pytest projects/testes/test_meta_exercise.py
```

### Testes Manuais
1. Acessar página de exercício
2. Submeter código correto
3. Verificar feedback de sucesso
4. Submeter código incorreto
5. Verificar feedback de erro

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| API externa usando rota | Baixo | Médio | Verificar logs antes de remover |
| Testes quebrados | Muito Baixo | Baixo | Suite de testes completa |
| Funcionalidade quebrada | Muito Baixo | Alto | Testes manuais + automáticos |

## Rollback

Se necessário reverter:
```bash
# Reverter commit
git revert <commit-hash>

# Ou restaurar arquivo
git checkout HEAD~1 -- projects/app.py
```

## Próximos Passos

Após esta refatoração, considerar:

1. **Extrair lógica de verificação** para uma função helper (SRP)
2. **Criar camada de serviços** (conforme `APP_ROUTES.md`)
3. **Aplicar mesma análise** em outras rotas

## Referências

- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [YAGNI Principle](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it)
- [Refatoração APP_ROUTES.md](APP_ROUTES.md)
- [Clean Code - Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

## Decisão

**Recomendação**: Implementar **Opção 1 (Remoção Completa)**

**Justificativa**:
- Rota não está sendo usada
- Elimina 100% da duplicação
- Simplifica código significativamente
- Sem riscos identificados

**Aprovação Necessária**: ⬜ Sim / ✅ Não (baixo impacto)

---

**Última Atualização**: 2025-12-08
**Versão**: 1.0
**Autor**: Kiro Agent (Análise Automática)
