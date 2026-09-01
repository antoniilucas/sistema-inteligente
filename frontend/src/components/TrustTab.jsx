export default function TrustTab({ tests, loading, onRun }) {
  return (
    <div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="flex between">
          <div>
            <h3 style={{ fontSize: 15 }}>Painel de Confiança</h3>
            <div className="muted">
              Testes de propriedade (metamórficos) — executados ao vivo contra o motor atual,
              sem depender de uma "resposta certa" conhecida.
            </div>
          </div>
          <button className="btn-primary" onClick={onRun} disabled={loading}>
            {loading ? 'Executando...' : 'Executar testes'}
          </button>
        </div>
      </div>
      <div>
        {tests.map((t) => (
          <div
            className="test-row"
            key={t.titulo}
            style={{ borderColor: t.passou ? 'rgba(111,207,151,.4)' : 'rgba(229,99,122,.5)' }}
          >
            <div className="flex between">
              <span className="t-title">{t.titulo}</span>
              {t.passou ? <span className="pill pill-ok">PASSOU</span> : <span className="pill pill-danger">FALHOU</span>}
            </div>
            <div className="t-desc">{t.descricao}</div>
            <div className="t-result mono">{t.detalhe}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
