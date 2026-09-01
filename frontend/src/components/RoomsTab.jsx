export default function RoomsTab({ rooms, onToggleRoom }) {
  return (
    <div className="card">
      <div className="flex between">
        <h3 style={{ fontSize: 14 }}>Salas cadastradas ({rooms.length})</h3>
        <span className="muted">Coordenador Geral · gestão dos espaços físicos</span>
      </div>
      <table style={{ marginTop: 10 }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Andar</th>
            <th>Cap.</th>
            <th>Tipo</th>
            <th>Recursos</th>
            <th>Acessível</th>
            <th>Disponível</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((r) => (
            <tr key={r.id}>
              <td className="mono">{r.id}</td>
              <td>{r.andar}</td>
              <td className="mono">{r.capacidade}</td>
              <td>{r.tipo}</td>
              <td className="muted">{r.recursos.join(', ') || '—'}</td>
              <td>
                {r.acessivel ? (
                  <span className="pill pill-ok">sim</span>
                ) : (
                  <span className="pill pill-muted">não</span>
                )}
              </td>
              <td>
                <input
                  type="checkbox"
                  checked={r.disponivel}
                  onChange={() => onToggleRoom(r.id, !r.disponivel)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
