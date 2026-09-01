"""
Testes automatizados do motor de alocação.

Rodam contra app.engine diretamente (funções puras) — não precisam do banco
de dados nem do servidor FastAPI no ar, o que os torna rápidos e determinísticos.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import generate_allocation
from app.seed_data import ROOMS, TEAMS, CONSTRAINTS


def _rooms():
    return [dict(r, disponivel=True) for r in ROOMS]


def _teams():
    return [dict(t) for t in TEAMS]


def _constraints():
    return [dict(c, ativa=True) for c in CONSTRAINTS]


# ---------------------------------------------------------------------------
# Testes de propriedade / metamórficos (seção 15 do desafio)
# ---------------------------------------------------------------------------

def test_1_capacidade():
    """Nenhuma sala recebe mais pessoas do que sua capacidade."""
    run = generate_allocation(_rooms(), _teams(), _constraints())
    for r in run["results"]:
        assert r["tamanho"] <= r["capacidade"], (
            f"{r['team_name']} ({r['tamanho']}p) excede a capacidade da sala {r['sala_id']} ({r['capacidade']})"
        )


def test_2_expansao_de_capacidade():
    """Adicionar uma sala não pode reduzir o número de equipes alocadas."""
    before = generate_allocation(_rooms(), _teams(), _constraints())
    extra_room = {"id": "EXTRA-905", "andar": 9, "capacidade": 100, "tipo": "Projeto",
                  "recursos": ["projetor"], "acessivel": True, "disponivel": True}
    after = generate_allocation(_rooms() + [extra_room], _teams(), _constraints())
    assert len(after["results"]) >= len(before["results"])


def test_3_remocao_de_restricao():
    """Remover uma restrição não pode diminuir o espaço de soluções."""
    with_constraint = generate_allocation(_rooms(), _teams(), _constraints())
    without_floor = [dict(c, ativa=False) if c["tipo"] == "andar_permitido" else c for c in _constraints()]
    without_constraint = generate_allocation(_rooms(), _teams(), without_floor)
    assert len(without_constraint["results"]) >= len(with_constraint["results"])


def test_4_equipes_equivalentes():
    """Equipes com requisitos idênticos recebem tratamento equivalente, independente do nome."""
    clone_a = {"id": "equiv_a", "nome": "Equipe Equivalente A", "setor_id": "operacoes", "tamanho": 13, "prioridade": "media"}
    clone_b = {"id": "equiv_b", "nome": "Equipe Equivalente B (nome diferente)", "setor_id": "operacoes", "tamanho": 13, "prioridade": "media"}

    run_a = generate_allocation(_rooms(), _teams() + [clone_a], _constraints())
    run_b = generate_allocation(_rooms(), _teams() + [clone_b], _constraints())

    res_a = next((r for r in run_a["results"] if r["team_id"] == "equiv_a"), None)
    res_b = next((r for r in run_b["results"] if r["team_id"] == "equiv_b"), None)

    assert res_a and res_b, "ambas as equipes equivalentes deveriam ser alocadas"
    assert abs(res_a["ocupacao"] - res_b["ocupacao"]) < 0.02


# ---------------------------------------------------------------------------
# Testes unitários complementares
# ---------------------------------------------------------------------------

def test_equipe_maior_que_qualquer_sala_gera_excecao():
    run = generate_allocation(_rooms(), _teams(), _constraints())
    delta_result = next((r for r in run["results"] if r["team_id"] == "equipe_delta"), None)
    delta_exception = next((e for e in run["exceptions"] if e["team_id"] == "equipe_delta"), None)
    assert delta_result is None, "Equipe Delta (92p) não deveria receber sala — maior sala tem 80 lugares"
    assert delta_exception is not None
    assert "Nenhuma sala" in delta_exception["motivo"]


def test_toda_alocacao_possui_rastreabilidade_minima():
    run = generate_allocation(_rooms(), _teams(), _constraints())
    for r in run["results"]:
        assert r["team_id"] and r["sala_id"]
        assert isinstance(r["alternatives_evaluated"], int)


def test_sala_reservada_e_respeitada():
    run = generate_allocation(_rooms(), _teams(), _constraints())
    ocupante = next((r for r in run["results"] if r["sala_id"] == "901"), None)
    if ocupante:
        assert ocupante["setor_id"] == "juridico"
