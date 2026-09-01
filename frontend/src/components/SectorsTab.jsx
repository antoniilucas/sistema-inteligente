const PRIORITY_CLASS = { alta: 'pill-accent', media: 'pill-warn', baixa: 'pill-muted' };

export default function SectorsTab({ sectors, teams, onUpdateTeamSize }) {
  return (
    <div>
      {sectors.map((s) => {
        const sectorTeams = teams.filter((t) => t.setor_id === s.id);
        const total = sectorTeams.reduce((sum, t) => sum + t.tamanho, 0);
        return (
          <div className="card" style={{ marginBottom: 12 }} key={s.id}>
            <div className="flex between">
              <h3 style={{ fontSize: 14 }}>{s.nome}</h3>
              <span className="muted">
                Coordenador: {s.coordenador} · {total} funcionários em {sectorTeams.length} equipes
              </span>
            </div>
            <table style={{ marginTop: 8 }}>
              <thead>
                <tr>
                  <th>Equipe</th>
                  <th>Tamanho</th>
                  <th>Prioridade</th>
                  <th>Requisitos</th>
                </tr>
              </thead>
              <tbody>
                {sectorTeams.map((t) => (
                  <tr key={t.id}>
                    <td>{t.nome}</td>
                    <td>
                      <input
                        type="number"
                        min="1"
                        value={t.tamanho}
                        onChange={(e) => onUpdateTeamSize(t.id, Math.max(1, parseInt(e.target.value, 10) || 1))}
                      />
                    </td>
                    <td>
                      <span className={`pill ${PRIORITY_CLASS[t.prioridade] || 'pill-muted'}`}>{t.prioridade}</span>
                    </td>
                    <td className="muted">
                      {t.req_equip ? `equip: ${t.req_equip.join(',')}` : t.grupo_proximidade ? `proximidade: ${t.grupo_proximidade}` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      })}
    </div>
  );
}
