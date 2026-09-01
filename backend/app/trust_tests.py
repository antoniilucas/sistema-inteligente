"""
Testes de propriedade (metamórficos) executáveis ao vivo — expostos via
GET /api/trust-tests para alimentar o "Painel de Confiança" no front-end,
e reutilizados em tests/test_engine.py como testes automatizados de verdade.

Para dezenas de salas/equipes/restrições não há uma resposta ótima conhecida
a priori (seção 15 do desafio), então verificamos relações que qualquer
alocação válida deve respeitar.
"""
from typing import Any, Dict, List

from .engine import generate_allocation


def run_trust_tests(
    rooms: List[Dict[str, Any]], teams: List[Dict[str, Any]], constraints: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    out = []

    # Teste 1 — Capacidade
    run1 = generate_allocation(rooms, teams, constraints)
    over_cap = [r for r in run1["results"] if r["tamanho"] > r["capacidade"]]
    out.append(
        {
            "titulo": "Teste 1 — Capacidade",
            "descricao": "Nenhuma sala pode receber mais pessoas do que sua capacidade.",
            "passou": len(over_cap) == 0,
            "detalhe": f"{'OK' if not over_cap else 'FALHA'} — {len(over_cap)} de {len(run1['results'])} alocações excedem a capacidade.",
        }
    )

    # Teste 2 — Expansão de capacidade
    extra_room = {"id": "EXTRA-905", "andar": 9, "capacidade": 100, "tipo": "Projeto", "recursos": ["projetor"], "acessivel": True, "disponivel": True}
    before = generate_allocation(rooms, teams, constraints)
    after = generate_allocation(rooms + [extra_room], teams, constraints)
    out.append(
        {
            "titulo": "Teste 2 — Expansão da capacidade",
            "descricao": "Adicionar uma sala não pode reduzir o número de equipes alocadas.",
            "passou": len(after["results"]) >= len(before["results"]),
            "detalhe": f"Antes: {len(before['results'])} equipes alocadas → Depois de adicionar sala: {len(after['results'])} equipes alocadas.",
        }
    )

    # Teste 3 — Remoção de restrição
    no_floor_constraint = [dict(c, ativa=False) if c["tipo"] == "andar_permitido" else c for c in constraints]
    with_c = generate_allocation(rooms, teams, constraints)
    without_c = generate_allocation(rooms, teams, no_floor_constraint)
    out.append(
        {
            "titulo": "Teste 3 — Remoção de restrição",
            "descricao": "Remover uma restrição não deve diminuir o espaço de soluções (nº de equipes alocáveis).",
            "passou": len(without_c["results"]) >= len(with_c["results"]),
            "detalhe": f"Com restrição de andar: {len(with_c['results'])} alocadas → Sem a restrição: {len(without_c['results'])} alocadas.",
        }
    )

    # Teste 4 — Equipes equivalentes
    clone_a = {"id": "equiv_a", "nome": "Equipe Equivalente A", "setor_id": "operacoes", "tamanho": 13, "prioridade": "media"}
    clone_b = {"id": "equiv_b", "nome": "Equipe Equivalente B (nome diferente)", "setor_id": "operacoes", "tamanho": 13, "prioridade": "media"}
    run_a = generate_allocation(rooms, teams + [clone_a], constraints)
    run_b = generate_allocation(rooms, teams + [clone_b], constraints)
    res_a = next((r for r in run_a["results"] if r["team_id"] == "equiv_a"), None)
    res_b = next((r for r in run_b["results"] if r["team_id"] == "equiv_b"), None)
    if res_a and res_b:
        diff = abs(res_a["ocupacao"] - res_b["ocupacao"])
        passou = diff < 0.02
        detalhe = f"Ocupação obtida: A={res_a['ocupacao']*100:.1f}% · B={res_b['ocupacao']*100:.1f}% (diferença {diff*100:.1f} p.p.)"
    else:
        passou = False
        detalhe = "Uma das equipes não pôde ser alocada — verifique disponibilidade de salas."
    out.append(
        {
            "titulo": "Teste 4 — Equipes equivalentes",
            "descricao": "Duas equipes com requisitos idênticos, diferindo apenas no nome, devem receber tratamento equivalente.",
            "passou": passou,
            "detalhe": detalhe,
        }
    )

    return out
