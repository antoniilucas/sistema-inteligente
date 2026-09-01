export default function ConstraintsTab({ constraints, onToggleConstraint }) {
  return (
    <div className="card">
      <div className="flex between">
        <h3 style={{ fontSize: 14 }}>Restrições ativas</h3>
        <span className="muted">desmarque para testar o efeito da remoção (ver aba Confiança)</span>
      </div>
      <table style={{ marginTop: 10 }}>
        <thead>
          <tr>
            <th>Ativa</th>
            <th>Tipo</th>
            <th>Descrição</th>
          </tr>
        </thead>
        <tbody>
          {constraints.map((c) => (
            <tr key={c.id}>
              <td>
                <input
                  type="checkbox"
                  checked={c.ativa}
                  onChange={() => onToggleConstraint(c.id, !c.ativa)}
                />
              </td>
              <td className="mono">{c.tipo}</td>
              <td>{c.descricao}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
