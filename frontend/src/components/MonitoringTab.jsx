import { fmtPct } from '../metrics.js';

export default function MonitoringTab({ monitoring, governance }) {
  const last = governance && governance.length ? governance[0] : null;

  return (
    <div>
      <div className="grid kpis">
        <div className="kpi">
          <div className="val mono">{last ? `${last.tempo_ms.toFixed(0)} ms` : '—'}</div>
          <div className="lbl">Tempo da última otimização</div>
        </div>
        <div className="kpi">
          <div className="val mono">{monitoring ? monitoring.execucoes : 0}</div>
          <div className="lbl">Número de execuções</div>
        </div>
        <div className="kpi accent">
          <div className="val mono">{fmtPct(monitoring ? monitoring.taxa_alocacao_media : 0)}</div>
          <div className="lbl">Taxa média de alocação</div>
        </div>
        <div className="kpi">
          <div className="val mono">{fmtPct(monitoring ? monitoring.ocupacao_media : 0)}</div>
          <div className="lbl">Ocupação média</div>
        </div>
        <div className={`kpi ${monitoring && monitoring.intervencoes > 0 ? 'warn' : ''}`}>
          <div className="val mono">{monitoring ? monitoring.intervencoes : 0}</div>
          <div className="lbl">Intervenções manuais</div>
        </div>
        <div className="kpi">
          <div className="val mono">{monitoring ? monitoring.erros : 0}</div>
          <div className="lbl">Erros ocorridos</div>
        </div>
      </div>

      <div className="section-title">Histórico de execuções</div>
      <div className="card">
        {governance && governance.length ? (
          governance.map((g) => (
            <div className="log-entry" key={g.id}>
              <b>Execução #{g.id}</b> · {new Date(g.timestamp).toLocaleString('pt-BR')} · tempo {g.tempo_ms.toFixed(0)}ms ·
              {' '}alocadas {g.equipes_alocadas} · não alocadas {g.equipes_nao_alocadas} ·
              {' '}ocupação {fmtPct(g.ocupacao_prevista)} · violações {g.violacoes}
            </div>
          ))
        ) : (
          <div className="muted">Nenhuma execução registrada ainda.</div>
        )}
      </div>
    </div>
  );
}
