# YuiSync — Biblioteca de Conversação Natural para Petshops

Biblioteca independente de exemplos **adaptados de diálogos humanos simulados** para ensinar linguagem, fluxo de conversação e tomada de decisão no atendimento de petshops brasileiros.

**Estado:** conjunto inicial em revisão; **não está conectado ao YuiSync Next nem publicado na Cloudflare**.

## Objetivos

- Capturar a forma como clientes falam: informalidade, mudanças de ideia, dúvidas, mensagens incompletas e pedidos de confirmação.
- Separar exemplos de **estilo e estratégia** dos dados reais de preços, estoque, agenda, políticas e clientes de cada empresa.
- Preservar `source_conversation_id` e índices das falas do usuário para rastreabilidade.
- Validar antes de aprovar ou produzir embeddings.

## Fontes e direitos

A fonte inicial é [Taskmaster-2](https://github.com/google-research-datasets/Taskmaster/tree/master/TM-2-2020), © Google LLC / Bill Byrne e colaboradores, licenciada em [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Os diálogos do Taskmaster-2 são **encenações com falas de participantes humanos transcritas de áudio**, não históricos orgânicos de clientes reais. As adaptações para petshops são obras derivadas e não reproduzem os serviços ou as ofertas da fonte. Créditos e rastreabilidade estão em `metadata/sources.json`.

## Pastas

- `data/adapted/`: conversas em pt-BR, feitas para petshop, pendentes de revisão.
- `data/strategies/`: padrões de atendimento reutilizáveis (ainda não aprovados).
- `metadata/`: origem, licença, versionamento e rastreabilidade.
- `cloudflare/migrations/`: migração D1 **isolada**, para aplicar após revisar schema existente.
- `cloudflare/src/`: consultas seguras no D1 e Vectorize em Workers.
- `scripts/`: validação e exportação SQL parametrizada/escapada.
- `tests/`: checagens básicas sem serviços pagos.

## Arquitetura Cloudflare

`GitHub (versionamento) → revisão → R2 (snapshots) → D1 (conversas e estratégias aprovadas) → Vectorize (embeddings de estratégias aprovadas) → Worker/Agent`.

**Nunca** use as conversas para afirmar preço, horário ou estoque. O agente deve consultar ferramentas operacionais do YuiSync por empresa. Não faça upload de históricos reais com dados pessoais sem autorização e tratamento adequado.

## Primeiros comandos

```bash
python scripts/validate.py
python scripts/export_d1.py > /tmp/yuisync-library-seed.sql
python -m unittest discover -s tests -v
```

Leia `cloudflare/README.md` antes de integrar. O índice Vectorize deve ter a dimensão do **modelo de embeddings efetivamente escolhido**, não uma dimensão presumida.
