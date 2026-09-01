const TABS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'salas', label: 'Salas' },
  { id: 'setores', label: 'Setores & Equipes' },
  { id: 'restricoes', label: 'Restrições' },
  { id: 'alocacao', label: 'Alocação' },
  { id: 'confianca', label: 'Painel de Confiança' },
  { id: 'monitoramento', label: 'Monitoramento' },
  { id: 'governanca', label: 'Governança' },
];

export default function Tabs({ active, onChange }) {
  return (
    <div className="tabs">
      {TABS.map((t) => (
        <div
          key={t.id}
          className={`tab ${active === t.id ? 'active' : ''}`}
          onClick={() => onChange(t.id)}
        >
          {t.label}
        </div>
      ))}
    </div>
  );
}
