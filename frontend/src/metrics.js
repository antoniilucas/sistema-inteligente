export function fmtPct(n) {
  return `${(n || 0).toFixed(1)}%`;
}

// Calcula os indicadores do dashboard a partir das salas e do resultado
// da última execução do motor (já vindo do back-end, incluindo status
// de intervenções manuais: aceita | rejeitada | alterada).
export function computeMetrics(rooms, run) {
  const results = run ? run.results : [];
  const alocadas = results.filter((r) => r.status !== 'rejeitada');
  const totalCap = rooms.filter((r) => r.disponivel).reduce((s, r) => s + r.capacidade, 0);
  const totalOcupado = alocadas.reduce((s, r) => s + r.tamanho, 0);
  const salasUsadas = new Set(alocadas.map((r) => r.sala_id)).size;
  const salasDisponiveis = rooms.filter((r) => r.disponivel).length;
  const naoAlocadas = run ? run.exceptions.length + results.filter((r) => r.status === 'rejeitada').length : 0;

  return {
    ocupacaoTotalPct: totalCap ? (totalOcupado / totalCap) * 100 : 0,
    salasOcupadas: salasUsadas,
    salasDisponiveis,
    salasLivres: salasDisponiveis - salasUsadas,
    funcionariosAlocados: totalOcupado,
    equipesAlocadas: alocadas.length,
    equipesNaoAlocadas: naoAlocadas,
    assentosOciosos: alocadas.reduce((s, r) => s + (r.capacidade - r.tamanho), 0),
    violacoes: run ? run.violacoes : 0,
  };
}
