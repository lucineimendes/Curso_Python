# Plano de Implementação

- [x] 1. Configurar estrutura de dados de conquistas e configuração
  - Criar `projects/data/achievements.json` com definições iniciais de conquistas
  - Definir todas as 10 conquistas: first_lesson, first_exercise, perfectionist, marathoner, conclusões de curso, python_master, persistent, speed_learner
  - Incluir todos os campos obrigatórios: id, name, description, icon, category, unlock_condition
  - _Requisitos: 5.1, 5.5_

- [x] 2. Implementar componente backend AchievementManager
  - Criar `projects/achievement_manager.py` com classe AchievementManager
  - Implementar `__init__` para carregar conquistas do JSON
  - Implementar `load_achievements()` para ler e parsear achievements.json
  - Implementar `get_all_achievements()` para retornar todas as definições de conquistas
  - _Requisitos: 5.1, 5.2_

- [x] 2.1 Implementar lógica de validação de conquistas
  - Adicionar método `_validate_achievement()` para verificar campos obrigatórios
  - Tratar conquistas inválidas graciosamente (registrar e pular)
  - Validar estrutura de unlock_condition
  - _Requisitos: 5.2, 5.3_

- [x] 2.2 Escrever teste de propriedade para validação de conquistas
  - **Propriedade 9: Validação de definição de conquista**
  - **Valida: Requisitos 5.2, 5.3**

- [x] 2.3 Escrever teste de propriedade para completude de dados de conquista
  - **Propriedade 4: Completude de dados de conquista**
  - **Valida: Requisitos 1.3, 6.5**

- [x] 3. Implementar sistema de avaliação de condições de desbloqueio
  - Adicionar método `_evaluate_condition()` ao AchievementManager
  - Implementar handlers de tipos de condição: lesson_count, exercise_count, perfect_exercises
  - Implementar handlers de tipos de condição: lessons_in_day, course_complete, all_courses_complete, exercise_after_attempts
  - _Requisitos: 2.4, 5.5_

- [x] 3.1 Escrever teste de propriedade para determinismo de avaliação de condição
  - **Propriedade 2: Determinismo de avaliação de condição de desbloqueio**
  - **Valida: Requisitos 2.4**

- [x] 3.2 Escrever teste de propriedade para suporte a todos os tipos de condição
  - **Propriedade 18: Todos os tipos de condição suportados**
  - **Valida: Requisitos 5.5**

- [x] 4. Estender ProgressManager para rastreamento de conquistas
  - Adicionar campo `achievements` à estrutura de dados de progresso do usuário
  - Adicionar campo `achievement_stats` para rastrear contadores (perfect_exercises_count, lessons_in_day, last_activity_date)
  - Implementar função de migração de dados para arquivos user_progress.json existentes
  - _Requisitos: 8.1, 8.3_
  - **Nota**: Considerar refatoração do ProgressManager seguindo princípios SOLID (ver docs/refactoring/PROGRESS_MANAGER.md)

- [x] 4.1 Implementar rastreamento de estatísticas de conquistas
  - Atualizar `mark_exercise_attempt()` para rastrear exercícios perfeitos (first_attempt_success)
  - Atualizar `mark_lesson_complete()` para rastrear contagem diária de lições
  - Adicionar métodos auxiliares para calcular estatísticas relacionadas a conquistas
  - _Requisitos: 4.4, 4.7_

- [x] 4.2 Escrever teste de propriedade para contador de exercícios perfeitos
  - **Propriedade 7: Incremento do contador de exercícios perfeitos**
  - **Valida: Requisitos 4.4**

- [x] 4.3 Escrever teste de propriedade para rastreamento de lições diárias
  - **Propriedade 8: Rastreamento de lições diárias**
  - **Valida: Requisitos 4.7**

- [x] 5. Implementar lógica de desbloqueio e persistência de conquistas
  - Adicionar método `get_user_achievements()` para retornar status de conquistas do usuário
  - Adicionar método `unlock_achievement()` para desbloquear e persistir conquistas
  - Adicionar método `check_unlocks()` para avaliar todas as condições e desbloquear conquistas elegíveis
  - Implementar registro de timestamp para conquistas desbloqueadas
  - _Requisitos: 2.1, 2.2, 2.3, 2.5_

- [x] 5.1 Escrever teste de propriedade para persistência de desbloqueio de conquista
  - **Propriedade 1: Persistência round-trip de desbloqueio de conquista**
  - **Valida: Requisitos 2.2, 8.1, 8.2**

- [x] 5.2 Escrever teste de propriedade para desbloqueio de múltiplas conquistas
  - **Propriedade 3: Completude de desbloqueio de múltiplas conquistas**
  - **Valida: Requisitos 2.1, 2.5**

- [x] 5.3 Escrever teste de propriedade para timestamps de desbloqueio
  - **Propriedade 5: Conquistas desbloqueadas têm timestamps**
  - **Valida: Requisitos 2.3, 8.3**

- [x] 6. Implementar detecção de conclusão de curso
  - Adicionar helper `_is_course_complete()` para verificar se todas as lições em um curso estão completas
  - Adicionar helper `_are_all_courses_complete()` para verificar se todos os três cursos estão completos
  - Adicionar helper `_has_exercise_after_attempts()` para verificar conquista persistente
  - _Requisitos: 4.3, 4.6_

- [x] 6.1 Escrever teste de propriedade para detecção de conclusão de curso
  - **Propriedade 6: Detecção de conclusão de curso**
  - **Valida: Requisitos 4.3**

- [ ] 7. Implementar rotas de API Flask para conquistas
  - Adicionar `@app.route('/api/achievements', methods=['GET'])` para retornar todas as conquistas com status
  - Adicionar `@app.route('/api/achievements/unlocked', methods=['GET'])` para retornar apenas desbloqueadas
  - Adicionar `@app.route('/api/achievements/check', methods=['POST'])` para verificar e desbloquear novas conquistas
  - Implementar tratamento de erros e códigos de status HTTP apropriados
  - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 7.1 Escrever teste de propriedade para filtragem de resposta da API
  - **Propriedade 10: Filtragem de resposta da API**
  - **Valida: Requisitos 6.2**

- [ ] 7.2 Escrever teste de propriedade para exclusão de recém-desbloqueadas
  - **Propriedade 11: Exclusão de conquistas recém-desbloqueadas**
  - **Valida: Requisitos 6.3**

- [ ] 7.3 Escrever teste de propriedade para códigos de status de erro da API
  - **Propriedade 12: Códigos de status de erro da API**
  - **Valida: Requisitos 6.4**

- [ ] 8. Checkpoint - Garantir que todos os testes backend passem
  - Garantir que todos os testes passem, perguntar ao usuário se surgirem questões.

- [ ] 9. Criar página frontend de galeria de conquistas
  - Criar template `projects/templates/achievements.html`
  - Exibir todas as conquistas em layout de grid
  - Mostrar conquistas desbloqueadas em cores completas, bloqueadas em escala de cinza
  - Exibir nome da conquista, descrição, ícone e data de desbloqueio (se desbloqueada)
  - Mostrar condições de desbloqueio para conquistas bloqueadas
  - Exibir estatísticas: total desbloqueadas, porcentagem de conclusão
  - _Requisitos: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 9.1 Escrever teste de propriedade para cálculo de estatísticas
  - **Propriedade 15: Precisão do cálculo de estatísticas**
  - **Valida: Requisitos 1.5**

- [ ] 10. Criar estilos CSS de conquistas
  - Criar `projects/static/css/achievements.css`
  - Estilizar cards de conquistas (estados bloqueado/desbloqueado)
  - Adicionar efeitos de hover e animações
  - Implementar layout de grid responsivo
  - Estilizar seção de estatísticas
  - _Requisitos: 1.2_

- [ ] 11. Implementar sistema de notificações de conquistas
  - Criar `projects/static/js/achievements.js`
  - Implementar classe `AchievementNotification`
  - Adicionar método `show()` para exibir notificação com animação
  - Adicionar método `checkNewAchievements()` para chamar API e mostrar notificações
  - Implementar fila de notificações para múltiplas conquistas
  - Adicionar auto-dismiss após 5 segundos
  - _Requisitos: 3.1, 3.2, 3.3, 3.4_

- [ ] 11.1 Escrever teste de propriedade para ordenação da fila de notificações
  - **Propriedade 13: Ordenação da fila de notificações**
  - **Valida: Requisitos 3.4**

- [ ] 11.2 Escrever teste de propriedade para estrutura de dados de notificação
  - **Propriedade 14: Estrutura de dados de notificação**
  - **Valida: Requisitos 3.2**

- [ ] 12. Implementar contador de badges na navegação
  - Criar `projects/static/js/badge_counter.js`
  - Implementar classe `BadgeCounter`
  - Adicionar método `updateCount()` para buscar e exibir contagem de desbloqueadas
  - Adicionar elemento de contador de badges à navegação no template base
  - Implementar tooltip mostrando conquistas recentes ao passar o mouse
  - Adicionar handler de clique para navegar à página de conquistas
  - _Requisitos: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 13. Integrar verificações de conquistas nos fluxos existentes
  - Atualizar fluxo de conclusão de lição para disparar verificação de conquistas
  - Atualizar fluxo de conclusão de exercício para disparar verificação de conquistas
  - Chamar `checkNewAchievements()` após atualizações de progresso
  - Atualizar contador de badges após novas conquistas
  - _Requisitos: 2.1, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ] 14. Adicionar link de navegação para página de conquistas
  - Atualizar navegação do template base para incluir link "Conquistas"
  - Adicionar indicador de ícone/badge na navegação
  - Garantir que link seja acessível de todas as páginas
  - _Requisitos: 7.3_

- [ ] 15. Implementar tratamento de erros e validação
  - Adicionar tratamento de erros para achievements.json corrompido
  - Adicionar tratamento de erros para dados de progresso do usuário corrompidos
  - Implementar degradação graciosa quando conquistas falham ao carregar
  - Adicionar validação para dados de conquista na leitura
  - _Requisitos: 5.3, 8.4, 8.5_

- [ ] 15.1 Escrever teste de propriedade para tratamento de dados corrompidos
  - **Propriedade 16: Tratamento gracioso de dados corrompidos**
  - **Valida: Requisitos 8.4**

- [ ] 15.2 Escrever teste de propriedade para validação de dados na leitura
  - **Propriedade 17: Validação de dados de conquista na leitura**
  - **Valida: Requisitos 8.5**

- [ ] 16. Implementar migração de dados para usuários existentes
  - Criar script de migração para adicionar campo achievements ao user_progress.json existente
  - Adicionar campo achievement_stats com valores padrão
  - Testar migração com dados de teste existentes
  - Documentar processo de migração
  - _Requisitos: 8.1_

- [ ] 16.1 Escrever testes unitários para migração de dados
  - Testar que migração adiciona campo achievements
  - Testar que migração preserva dados existentes
  - Testar que migração trata campos faltando
  - _Requisitos: 8.1_

- [ ] 17. Adicionar logging e monitoramento
  - Adicionar logging para desbloqueios de conquistas
  - Adicionar logging para erros de validação
  - Adicionar logging para erros de API
  - Registrar performance de verificação de conquistas
  - _Requisitos: 5.3, 6.4_

- [ ] 18. Checkpoint final - Garantir que todos os testes passem
  - Garantir que todos os testes passem, perguntar ao usuário se surgirem questões.

- [ ] 19. Escrever testes de integração
  - Testar fluxo completo: conclusão de lição → verificação de conquista → desbloqueio → notificação
  - Testar endpoints da API com cliente de teste Flask
  - Testar cenários de desbloqueio concorrente
  - Testar casos extremos: sem conquistas, todas as conquistas, limites exatos
  - _Requisitos: Todos_

- [ ] 20. Testes de performance e otimização
  - Testar performance de carregamento de conquistas
  - Testar tempos de resposta da API
  - Otimizar avaliação de condições se necessário
  - Testar com grande número de conquistas
  - _Requisitos: Todos_
