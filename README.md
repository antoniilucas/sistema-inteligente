# Sistema Inteligente de Gestão e Otimização de Espaços Corporativos

Protótipo funcional (desafio de **uma semana** — ISTQB CT-AI) para alocar automaticamente
equipes de 8 setores de uma multinacional (~7.000 funcionários, prédio de 9 andares,
36 salas) às salas disponíveis, maximizando ocupação e atendimento de restrições, e
minimizando ociosidade e conflitos.

**Stack:** back-end em **FastAPI** com banco de dados (**SQLAlchemy + SQLite**, trocável por
Postgres via `DATABASE_URL`); front-end em **React** (Vite).

## Estrutura

```
backend/
  app/
    main.py            -> API FastAPI (rotas)
    database.py         -> engine/sessão SQLAlchemy
    models.py            -> modelos ORM (Room, Sector, Team, Constraint, AllocationRun, ...)
    schemas.py            -> schemas Pydantic (request/response)
    engine.py              -> motor de alocação (função pura, sem I/O)
    seed_data.py             -> dados de exemplo (puros, sem dependência de banco)
    seed.py                   -> popula o banco com seed_data na primeira execução
    trust_tests.py             -> testes metamórficos executáveis ao vivo via API
  tests/
    test_engine.py             -> pytest — inclui os 4 testes metamórficos exigidos
  requirements.txt
  conftest.py
frontend/
  src/
    App.jsx              -> estado da aplicação + orquestração das abas
    api.js                 -> cliente HTTP para a API FastAPI
    metrics.js               -> cálculo de indicadores no cliente
    components/                -> Dashboard, Salas, Setores, Restrições, Alocação,
                                   Painel de Confiança, Monitoramento, Governança, Modal
  package.json
  vite.config.js
.github/workflows/ci.yml   -> pipeline CI (pytest no back-end + build do front-end)
```

## Como executar

O sistema tem duas partes que rodam **ao mesmo tempo, em dois terminais separados**: a API
(FastAPI) e a interface (React). Suba a API primeiro.

### Pré-requisitos

- Python 3.10+ (`python3 --version`)
- Node.js 18+ (`node --version`)

### Passo 1 — Terminal 1: Back-end (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Deixe esse terminal aberto. Você deve ver algo como `Uvicorn running on http://127.0.0.1:8000`.
Na primeira execução, o SQLite (`alocacao.db`) é criado e populado automaticamente com os
dados de exemplo (36 salas, 8 setores, 23 equipes, 8 restrições — incluindo a "Equipe Delta"
com 92 pessoas, usada no enunciado como exemplo de exceção sem sala compatível).

Para confirmar que está no ar, abra `http://localhost:8000/docs` — deve aparecer a
documentação interativa (Swagger) da API.

### Passo 2 — Terminal 2: Front-end (React + Vite)

Abra um **novo terminal** (deixe o do back-end rodando) e execute:

```bash
cd frontend
cp .env.example .env   # ajuste VITE_API_URL se a API não estiver em localhost:8000
npm i
npm run dev
```

O terminal vai mostrar um endereço, geralmente `http://localhost:5173/` — abra-o no
navegador. Essa é a aplicação.

> A ordem importa: o front-end espera encontrar a API em `http://localhost:8000` (definido
> em `frontend/.env`). Se a API não estiver rodando, a aplicação abre normalmente, mas
> mostra uma faixa vermelha de erro no topo dizendo que não conseguiu conectar.

### Testes automatizados

```bash
cd backend
source .venv/bin/activate   # se ainda não estiver ativado
pytest -v
```

### Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| Faixa vermelha "Não foi possível conectar à API" no front-end | Back-end não está rodando, ou está em outra porta | Confira o Terminal 1; teste `http://localhost:8000/api/health` no navegador |
| `ModuleNotFoundError` ao rodar `uvicorn` | Ambiente virtual não ativado ou dependências não instaladas | Rode `source .venv/bin/activate` e depois `pip install -r requirements.txt` de novo |
| `command not found: uvicorn` | Ambiente virtual não ativado | Ative o `.venv` (veja acima) antes de rodar o comando |
| Porta 8000 ou 5173 já em uso | Outro processo já está usando a porta | Feche o processo anterior, ou rode com outra porta: `uvicorn app.main:app --reload --port 8001` (e ajuste `VITE_API_URL` no `.env`) |
| `npm i` falha com erro de versão do Node | Node muito antigo | Atualize para Node 18+ |
| Dados voltam ao estado inicial | O banco `backend/alocacao.db` foi apagado | Normal — ele é recriado e populado automaticamente na próxima vez que a API subir |

## Principais endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/rooms` | Lista salas |
| PATCH | `/api/rooms/{id}` | Atualiza disponibilidade/capacidade de uma sala |
| GET | `/api/sectors` | Lista setores |
| GET | `/api/teams` | Lista equipes |
| PATCH | `/api/teams/{id}` | Atualiza tamanho/prioridade de uma equipe |
| GET | `/api/constraints` | Lista restrições |
| PATCH | `/api/constraints/{id}` | Ativa/desativa uma restrição |
| POST | `/api/allocate` | Executa o motor e persiste a execução (governança) |
| GET | `/api/allocate/baseline` | Alocação "antes" (ingênua), para comparação |
| GET | `/api/governance` | Histórico de execuções |
| GET | `/api/governance/{id}` | Detalhe de uma execução (resultados + exceções) |
| POST | `/api/governance/{id}/intervene` | Registra intervenção humana (rejeitar/alterar) |
| GET | `/api/trust-tests` | Roda os 4 testes metamórficos ao vivo |
| GET | `/api/monitoring` | Métricas agregadas de observabilidade |

## Motor de alocação

Heurística gulosa com pontuação (não é Machine Learning — conforme permitido no enunciado):

1. Ordena as equipes por prioridade e, em empate, por tamanho.
2. Filtra salas candidatas pelas restrições obrigatórias (capacidade, acessibilidade,
   equipamento, andar permitido, sala reservada por setor).
3. Pontua as candidatas priorizando maior ocupação, menor ociosidade e proximidade entre
   equipes do mesmo grupo.
4. Se nenhuma sala atende, a equipe vira uma **exceção com motivo explícito** — nunca é
   forçada uma alocação inválida para "inflar" métricas de sucesso.

## Critérios de aceitação

1. Nenhuma sala pode receber mais pessoas do que sua capacidade.
2. Nenhuma restrição obrigatória pode ser ignorada numa recomendação aceita.
3. 100% das recomendações retornadas possuem justificativa rastreável
   (`alternatives_evaluated` + dados da sala).
4. Toda equipe não alocada possui motivo registrado (nunca fica de fora silenciosamente).
5. A alocação otimizada deve reduzir a ociosidade em relação à estratégia inicial ingênua
   (comparação "antes/depois" no dashboard, alimentada por `/api/allocate/baseline`).
6. Cada execução deve ser concluída em menos de 2 segundos para o volume de dados de
   exemplo (~40 salas × ~25 equipes) — validado pelo campo `tempo_ms`.

## Testes baseados em propriedades (metamórficos)

`backend/tests/test_engine.py` inclui os 4 testes exigidos pela seção 15 do desafio:

| Teste | Propriedade verificada |
|---|---|
| 1 — Capacidade | Nenhuma equipe alocada excede a capacidade da sala |
| 2 — Expansão de capacidade | Adicionar uma sala não pode diminuir o nº de equipes alocadas |
| 3 — Remoção de restrição | Remover uma restrição não pode diminuir o espaço de soluções |
| 4 — Equipes equivalentes | Duas equipes com requisitos idênticos recebem tratamento equivalente |

Esses mesmos testes rodam **ao vivo, contra os dados atuais do banco**, via
`GET /api/trust-tests` — usado na aba "Painel de Confiança" do front-end. A confiança no
sistema não depende de "confiar na IA": depende de poder reexecutar essas verificações a
qualquer momento, inclusive depois de editar salas, equipes e restrições pela interface.

## Explicabilidade, governança e observabilidade

- **Explicabilidade**: cada recomendação, ao ser selecionada na demo, mostra capacidade,
  tamanho da equipe, ocupação prevista, recursos da sala e nº de alternativas avaliadas.
- **Governança**: cada `POST /api/allocate` grava um `AllocationRun` no banco (usuário,
  algoritmo/versão, dados analisados, resultado) — consultável em `/api/governance` e na
  aba "Governança".
- **Observabilidade**: `/api/monitoring` agrega tempo médio de execução, taxa média de
  alocação, ocupação média e nº de intervenções manuais ao longo do tempo.
- **Intervenção humana**: `POST /api/governance/{id}/intervene` permite ao Coordenador
  Geral rejeitar ou substituir manualmente qualquer recomendação; toda intervenção é
  registrada como uma linha em `interventions` e conta no indicador de observabilidade.

## Por que confiar numa recomendação?

Não porque "usamos IA" — e sim porque cada recomendação é: testada (testes automatizados +
metamórficos, executáveis a qualquer momento via API), avaliada contra critérios de
aceitação objetivos, explicável (justificativa por decisão), auditável (registro de
governança persistido em banco) e sempre revisável por um humano.

## CI/CD

`.github/workflows/ci.yml` roda em dois jobs a cada push/PR:
- **backend**: instala dependências, valida a sintaxe dos módulos e executa `pytest`.
- **frontend**: instala dependências e executa `npm run build`.

Nenhuma mudança chega ao "cliente" sem passar por essas verificações.
