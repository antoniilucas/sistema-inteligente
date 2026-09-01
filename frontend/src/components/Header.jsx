export default function Header({ runCount }) {
  return (
    <div className="hdr">
      <div>
        <div className="eyebrow">allocation-engine-v1 · protótipo</div>
        <h1>Sistema Inteligente de Gestão de Espaços Corporativos</h1>
      </div>
      <div className="user">
        Sessão ativa: <b>Coordenador Geral</b>
        <br />
        Execuções nesta sessão: <span className="mono">{runCount}</span>
      </div>
    </div>
  );
}
