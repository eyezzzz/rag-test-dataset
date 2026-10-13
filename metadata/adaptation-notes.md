# Como foram adaptados os exemplos

Todos os **26** registros de conversa foram escritos especificamente em pt-BR a partir de **26 conversas distintas efetivamente verificadas** no Taskmaster-2, distribuídas em 12 pedidos de comida, 8 buscas de restaurantes e 6 buscas de hotéis. Não representam conversas autênticas coletadas em petshops brasileiros.

- O texto em `messages` é novo: transferência de domínio, não cópia nem tradução literal.
- A origem está nos campos `source.source_conversation_id` e `source.source_customer_turn_indices`; o SHA do arquivo original permite auditoria.
- O foco são comportamentos naturais de clientes: correções, mensagens fragmentadas, mudanças de ideia, restrições graduais, comparação, recusa de adicionais.
- As respostas do atendente foram reformuladas para evitar promessas não verificadas, sugestões inadequadas e erros presentes no corpus de origem.
- `pending_review` impede consumo em produção até uma auditoria humana; exemplos não são fatos comerciais, respostas canônicas nem material de fine-tuning obrigatório.
- Conjuntos naturais de **participantes humanos em simulações** são diferentes de logs reais de clientes.

**Atribuição:** adaptado de Taskmaster-2 (Google LLC, Byrne e colaboradores), CC BY 4.0, com modificações para pt-BR e petshops. Consulte `metadata/sources.json` e o [README original](https://github.com/google-research-datasets/Taskmaster/blob/master/TM-2-2020/README.md).
