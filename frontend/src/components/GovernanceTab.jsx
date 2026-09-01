import { fmtPct } from '../metrics.js';

export default function GovernanceTab({ governance }) {
  return (
    <div className="card">
      <h3 style={{ fontSize: 15 }}>Registro de auditoria</h3>
      <div className="muted" style={{ marginBottom: 10 }}>
        Cada execução do motor de alocação e cada intervenção manual geram um registro rastreável.
      </div>
      {governance && governance.length ? (
        governance.map((g) => (
          <div className="log-entry" style={{ borderLeftColor: 'var(--accent)' }} key={g.id}>
            <b>Execução #{g.id}</b> — {new Date(g.timestamp).toLocaleString('pt-BR')}
            <br />
            Usuário: {g.usuario} · Algoritmo: {g.algoritmo}
            <br />
            Equipes analisadas: {g.equipes_analisadas} · Salas analisadas: {g.salas_analisadas}
            <br />
            Equipes alocadas: {g.equipes_alocadas} · Não alocadas: {g.equipes_nao_alocadas}
            <br />
            Restrições violadas: {g.violacoes} · Ocupação prevista: {fmtPct(g.ocupacao_prevista)}
          </div>
        ))
      ) : (
        <div className="muted">Nenhum registro ainda — execute uma alocação.</div>
      )}
    </div>
  );
}
