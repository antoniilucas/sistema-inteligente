import { computeMetrics, fmtPct } from '../metrics.js';

function baselineMetrics(rooms, baseline) {
  if (!baseline) return { ocupacaoPct: 0, ociosos: 0, naoAlocadas: 0 };
  const totalCap = rooms.filter((r) => r.disponivel).reduce((s, r) => s + r.capacidade, 0);
  const ocupado = baseline.results.reduce((s, r) => s + r.tamanho, 0);
  return {
    ocupacaoPct: totalCap ? (ocupado / totalCap) * 100 : 0,
    ociosos: baseline.results.reduce((s, r) => s + (r.capacidade - r.tamanho), 0),
    naoAlocadas: baseline.exceptions.length,
  };
}

export default function AllocationTab({ rooms, lastRun, baseline, loading, onRun, onExplain, onReject }) {
  const m = lastRun ? computeMetrics(rooms, lastRun) : null;
  const bm = baselineMetrics(rooms, baseline);

  return (
    <div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="flex between">
          <div>
            <h3 style={{ fontSize: 15 }}>Motor de alocação</h3>
            <div className="muted">Analisa salas, equipes e restrições e sugere a melhor distribuição possível.</div>
          </div>
          <button className="btn-primary" onClick={onRun} disabled={loading}>
            {loading ? 'Gerando...' : 'Gerar Alocação Otimizada'}
          </button>
        </div>
      </div>

      <div className="section-title">Recomendações</div>
      <div className="card">
        {!lastRun ? (
          <div className="muted">Nenhuma execução ainda.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Equipe</th>
                <th>Pessoas</th>
                <th>Sala</th>
                <th>Cap.</th>
                <th>Andar</th>
                <th>Ocup.</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {lastRun.results.map((r) => {
                const pill =
                  r.status === 'rejeitada' ? (
                    <span className="pill pill-danger">rejeitada</span>
                  ) : r.status === 'alterada' ? (
                    <span className="pill pill-warn">alterada</span>
                  ) : (
                    <span className="pill pill-ok">aceita</span>
                  );
                return (
                  <tr key={r.team_id}>
                    <td>{r.team_name}</td>
                    <td className="mono">{r.tamanho}</td>
                    <td className="mono">{r.sala_id}</td>
                    <td className="mono">{r.capacidade}</td>
                    <td className="mono">AND {r.andar}</td>
                    <td className="mono">{fmtPct((r.tamanho / r.capacidade) * 100)}</td>
                    <td>{pill}</td>
                    <td>
                      <button className="btn-ghost btn-sm" onClick={() => onExplain(r.team_id)}>Justificativa</button>{' '}
                      <button className="btn-ghost btn-sm" onClick={() => onReject(r.team_id)} disabled={r.status === 'rejeitada'}>Rejeitar</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {lastRun && lastRun.exceptions.length > 0 && (
        <>
          <div className="section-title">Equipes não alocadas — exceções</div>
          {lastRun.exceptions.map((e) => (
            <div className="card" style={{ borderColor: 'rgba(240,168,87,.4)', marginBottom: 8 }} key={e.team_id}>
              <div className="flex between">
                <b>{e.team_name}</b>
                <span className="pill pill-warn">ALERTA</span>
              </div>
              <div className="muted" style={{ marginTop: 4 }}>
                Tamanho da equipe: {e.tamanho} pessoas · Alternativas avaliadas: {e.alternatives_evaluated}
              </div>
              <div style={{ marginTop: 6, fontSize: 13 }}>{e.motivo}</div>
              <div className="muted" style={{ marginTop: 4 }}>
                Encaminhamento sugerido: revisar manualmente com o Coordenador Geral ou reavaliar restrições/capacidade disponível.
              </div>
            </div>
          ))}
        </>
      )}

      {lastRun && (
        <>
          <div className="section-title">Comparação — antes vs. depois</div>
          <div className="card">
            <table>
              <thead>
                <tr>
                  <th>Indicador</th>
                  <th>Antes (alocação simples)</th>
                  <th>Depois (otimizado)</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Ocupação média</td><td className="mono">{fmtPct(bm.ocupacaoPct)}</td><td className="mono">{fmtPct(m.ocupacaoTotalPct)}</td></tr>
                <tr><td>Assentos ociosos</td><td className="mono">{bm.ociosos}</td><td className="mono">{m.assentosOciosos}</td></tr>
                <tr><td>Equipes sem sala</td><td className="mono">{bm.naoAlocadas}</td><td className="mono">{m.equipesNaoAlocadas}</td></tr>
                <tr><td>Violações</td><td className="mono">—</td><td className="mono">{m.violacoes}</td></tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
