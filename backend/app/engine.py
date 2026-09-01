"""
Motor de alocação — allocation-engine-v1

Função pura (sem I/O, sem banco de dados) para permitir os testes baseados em
propriedades (metamórficos) em tests/test_engine.py sem precisar subir a API
ou o banco. Recebe e devolve apenas dicionários simples.

Heurística gulosa com pontuação (não é Machine Learning — permitido pelo
enunciado):
  1. Ordena as equipes por prioridade e, em empate, por tamanho (maior primeiro).
  2. Filtra salas candidatas pelas restrições obrigatórias.
  3. Pontua as candidatas priorizando alta ocupação, baixa ociosidade e
     proximidade entre equipes do mesmo grupo.
  4. Se nenhuma sala atende, a equipe vira uma exceção com motivo explícito —
     nunca é forçada uma alocação inválida.
"""
import time
from typing import Any, Dict, List

PRIORITY_RANK = {"alta": 0, "media": 1, "baixa": 2}


def generate_allocation(
    rooms: List[Dict[str, Any]],
    teams: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]],
) -> Dict[str, Any]:
    start = time.perf_counter()
    active = [c for c in constraints if c.get("ativa")]
    cap_min = next((c for c in active if c["tipo"] == "capacidade_minima"), None)

    pool = [r for r in rooms if r["disponivel"] and (not cap_min or r["capacidade"] >= cap_min["valor"])]
    used = set()
    sorted_teams = sorted(
        teams, key=lambda t: (PRIORITY_RANK.get(t["prioridade"], 1), -t["tamanho"])
    )

    results: List[Dict[str, Any]] = []
    exceptions: List[Dict[str, Any]] = []
    floor_occupied: Dict[str, set] = {}
    violations = 0

    for team in sorted_teams:
        team_cs = [c for c in active if c.get("alvo") in (team["id"], team["setor_id"])]
        candidates = [r for r in pool if r["id"] not in used]
        alternatives_evaluated = len(candidates)

        candidates = [r for r in candidates if r["capacidade"] >= team["tamanho"]]

        access_c = next((c for c in team_cs if c["tipo"] == "acessibilidade_obrigatoria"), None)
        if access_c:
            candidates = [r for r in candidates if r["acessivel"]]

        equip_c = next((c for c in team_cs if c["tipo"] == "equipamento_obrigatorio"), None)
        equip_needed = equip_c["valor"] if equip_c else team.get("req_equip")
        if equip_needed:
            candidates = [r for r in candidates if all(e in r["recursos"] for e in equip_needed)]

        floor_c = next((c for c in team_cs if c["tipo"] == "andar_permitido"), None)
        if floor_c:
            candidates = [r for r in candidates if r["andar"] in floor_c["valor"]]

        reserved_c = next(
            (c for c in active if c["tipo"] == "sala_reservada" and c["alvo"] == team["setor_id"]), None
        )
        if reserved_c:
            candidates = [r for r in candidates if r["id"] == reserved_c["valor"]]

        all_reserved = [c["valor"] for c in active if c["tipo"] == "sala_reservada" and c["alvo"] != team["setor_id"]]
        candidates = [r for r in candidates if r["id"] not in all_reserved]

        if not candidates:
            any_cap_room = any(r["disponivel"] and r["capacidade"] >= team["tamanho"] for r in rooms)
            if not any_cap_room:
                maior = max((r["capacidade"] for r in rooms if r["disponivel"]), default=0)
                motivo = f"Nenhuma sala do prédio comporta {team['tamanho']} pessoas (maior sala disponível: {maior} lugares)."
            elif access_c:
                motivo = "Restrição de acessibilidade obrigatória não pôde ser atendida com capacidade suficiente."
            elif equip_needed:
                motivo = f"Restrição de equipamento obrigatório ({', '.join(equip_needed)}) não pôde ser atendida."
            elif floor_c:
                motivo = f"Nenhuma sala com capacidade suficiente disponível nos andares permitidos ({floor_c['valor']})."
            else:
                motivo = "Todas as salas compatíveis já foram alocadas para equipes de maior prioridade."
            exceptions.append(
                {
                    "team_id": team["id"],
                    "team_name": team["nome"],
                    "setor_id": team["setor_id"],
                    "tamanho": team["tamanho"],
                    "motivo": motivo,
                    "alternatives_evaluated": alternatives_evaluated,
                }
            )
            continue

        best, best_score = None, float("-inf")
        for r in candidates:
            occ = team["tamanho"] / r["capacidade"]
            score = occ * 100 - (r["capacidade"] - team["tamanho"]) * 0.6
            if team.get("grupo_proximidade"):
                allies = sum(
                    1
                    for res in results
                    if res.get("grupo_proximidade") == team["grupo_proximidade"] and res["andar"] == r["andar"]
                )
                score += allies * 25
            if score > best_score:
                best_score, best = score, r
        used.add(best["id"])

        no_share = next((c for c in active if c["tipo"] == "setores_nao_compartilham"), None)
        if no_share and team["setor_id"] in no_share["valor"]:
            other = next((s for s in no_share["valor"] if s != team["setor_id"]), None)
            if best["andar"] in floor_occupied.get(other, set()):
                violations += 1
            floor_occupied.setdefault(team["setor_id"], set()).add(best["andar"])

        results.append(
            {
                "team_id": team["id"],
                "team_name": team["nome"],
                "setor_id": team["setor_id"],
                "tamanho": team["tamanho"],
                "sala_id": best["id"],
                "andar": best["andar"],
                "capacidade": best["capacidade"],
                "ocupacao": team["tamanho"] / best["capacidade"],
                "grupo_proximidade": team.get("grupo_proximidade"),
                "alternatives_evaluated": alternatives_evaluated,
                "score": best_score,
            }
        )

    tempo_ms = (time.perf_counter() - start) * 1000
    return {"results": results, "exceptions": exceptions, "violations": violations, "tempo_ms": tempo_ms}


def naive_allocation(rooms: List[Dict[str, Any]], teams: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Alocação 'antes' — first-fit ingênuo, sem otimização, usada na comparação."""
    pool = [r for r in rooms if r["disponivel"]]
    used = set()
    results, exceptions = [], []
    for team in teams:
        room = next((r for r in pool if r["id"] not in used and r["capacidade"] >= team["tamanho"]), None)
        if not room:
            exceptions.append({"team_id": team["id"]})
            continue
        used.add(room["id"])
        results.append(
            {
                "team_id": team["id"],
                "tamanho": team["tamanho"],
                "sala_id": room["id"],
                "capacidade": room["capacidade"],
                "ocupacao": team["tamanho"] / room["capacidade"],
            }
        )
    return {"results": results, "exceptions": exceptions}
