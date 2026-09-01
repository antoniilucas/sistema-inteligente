export default function ExplainModal({ result, room, onClose }) {
  if (!result || !room) return null;
  const occPct = (result.tamanho / room.capacidade) * 100;

  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <span className="close-x" onClick={onClose}>&times;</span>
        <h3>Sala {room.id} recomendada para {result.team_name}</h3>
        <div className="row">
          <span className="muted">Capacidade da sala</span>
          <span className="mono">{room.capacidade} pessoas</span>
        </div>
        <div className="row">
          <span className="muted">Tamanho da equipe</span>
          <span className="mono">{result.tamanho} pessoas</span>
        </div>
        <div className="row">
          <span className="muted">Ocupação prevista</span>
          <span className="mono">{occPct.toFixed(1)}%</span>
        </div>
        <div className="row">
          <span className="muted">Recursos disponíveis na sala</span>
          <span className="mono">{room.recursos.length ? room.recursos.join(', ') : '—'}</span>
        </div>
        <div className="row">
          <span className="muted">Acessibilidade da sala</span>
          <span className="mono">{room.acessivel ? 'sim' : 'não'}</span>
        </div>
        <div className="row">
          <span className="muted">Alternativas avaliadas</span>
          <span className="mono">{result.alternatives_evaluated}</span>
        </div>
        <div className="verdict">
          Esta sala apresentou o melhor equilíbrio entre ocupação, localização e restrições dentre
          as alternativas disponíveis no momento da execução.
        </div>
      </div>
    </div>
  );
}
