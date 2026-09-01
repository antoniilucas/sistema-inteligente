import { computeMetrics, fmtPct } from '../metrics.js';

function occOf(tamanho, capacidade) {
  return tamanho / capacidade;
}

export default function Dashboard({ rooms, lastRun }) {
  const m = computeMetrics(rooms, lastRun);

  const assignedByRoom = {};
  if (lastRun) {
    lastRun.results.forEach((r) => {
      if (r.status === 'rejeitada') return;
      assignedByRoom[r.sala_id] = r;
    });
  }

  const floors = [1, 2, 3, 4, 5, 6, 7, 8, 9].map((f) => {
    const floorRooms = rooms.filter((r) => r.andar === f);
    return { floor: f, rooms: floorRooms };
  });

  return (
    <div>
      <div className="grid kpis">
        <div className="kpi accent">
          <div className="val mono">{fmtPct(m.ocupacaoTotalPct)}</div>
          <div className="lbl">Ocupação total do prédio</div>
        </div>
        <div className="kpi">
          <div className="val mono">{m.funcionariosAlocados}</div>
          <div className="lbl">Funcionários alocados</div>
        </div>
        <div className={`kpi ${m.equipesNaoAlocadas > 0 ? 'warn' : ''}`}>
          <div className="val mono">{m.equipesNaoAlocadas}</div>
          <div className="lbl">Equipes não alocadas</div>
        </div>
        <div className="kpi">
          <div className="val mono">{m.salasOcupadas}/{m.salasDisponiveis}</div>
          <div className="lbl">Salas ocupadas / disponíveis</div>
        </div>
        <div className="kpi">
          <div className="val mono">{m.salasLivres}</div>
          <div className="lbl">Salas livres</div>
        </div>
        <div className={`kpi ${m.violacoes > 0 ? 'danger' : ''}`}>
          <div className="val mono">{m.violacoes}</div>
          <div className="lbl">Restrições violadas</div>
        </div>
      </div>

      <div className="card">
        <div className="flex between">
          <h3 style={{ fontSize: 14 }}>Corte transversal do prédio — ocupação por andar</h3>
          <span className="muted">passe o mouse sobre uma sala</span>
        </div>
        <div className="building">
          {floors.map(({ floor, rooms: floorRooms }) => (
            <div className="floor-row" key={floor}>
              <div className="floor-lbl">AND {floor}</div>
              <div className="floor-strip">
                {floorRooms.map((r) => {
                  const res = assignedByRoom[r.id];
                  const occ = res ? occOf(res.tamanho, r.capacidade) : 0;
                  const width = Math.max(22, r.capacidade * 1.5);
                  let bg = 'var(--surface3)';
                  if (res) {
                    if (occ > 0.95) bg = 'var(--accent)';
                    else if (occ > 0.6) bg = '#3FAE9F';
                    else bg = '#2C6B65';
                  }
                  const tip = res
                    ? `Sala ${r.id} · ${r.capacidade} lugares\n${res.team_name} (${res.tamanho}p) · ${fmtPct(occ * 100)}`
                    : `Sala ${r.id} · ${r.capacidade} lugares\nDisponível`;
                  return (
                    <div
                      key={r.id}
                      className={`room-block ${res ? '' : 'empty'}`}
                      style={{ width, height: 24, background: bg }}
                    >
                      {r.id}
                      <span className="tip">{tip}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {!lastRun && (
        <div className="card" style={{ marginTop: 14, borderColor: 'var(--accent-dim)' }}>
          <b>Nenhuma alocação executada ainda.</b>
          <div className="muted" style={{ marginTop: 4 }}>
            Vá até a aba <b>Alocação</b> e clique em "Gerar Alocação Otimizada" para ver o prédio ocupado.
          </div>
        </div>
      )}
    </div>
  );
}
