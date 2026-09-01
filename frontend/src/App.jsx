import { useEffect, useState, useCallback } from 'react';
import api from './api.js';
import Header from './components/Header.jsx';
import Tabs from './components/Tabs.jsx';
import Dashboard from './components/Dashboard.jsx';
import RoomsTab from './components/RoomsTab.jsx';
import SectorsTab from './components/SectorsTab.jsx';
import ConstraintsTab from './components/ConstraintsTab.jsx';
import AllocationTab from './components/AllocationTab.jsx';
import TrustTab from './components/TrustTab.jsx';
import MonitoringTab from './components/MonitoringTab.jsx';
import GovernanceTab from './components/GovernanceTab.jsx';
import ExplainModal from './components/ExplainModal.jsx';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [rooms, setRooms] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [teams, setTeams] = useState([]);
  const [constraints, setConstraints] = useState([]);
  const [baseline, setBaseline] = useState(null);
  const [lastRun, setLastRun] = useState(null);
  const [governance, setGovernance] = useState([]);
  const [monitoring, setMonitoring] = useState(null);
  const [trustTests, setTrustTests] = useState([]);
  const [runCount, setRunCount] = useState(0);
  const [loadingRun, setLoadingRun] = useState(false);
  const [loadingTests, setLoadingTests] = useState(false);
  const [explainTeamId, setExplainTeamId] = useState(null);
  const [error, setError] = useState(null);

  const loadCore = useCallback(async () => {
    try {
      const [roomsData, sectorsData, teamsData, constraintsData, baselineData] = await Promise.all([
        api.getRooms(),
        api.getSectors(),
        api.getTeams(),
        api.getConstraints(),
        api.getBaseline(),
      ]);
      setRooms(roomsData);
      setSectors(sectorsData);
      setTeams(teamsData);
      setConstraints(constraintsData);
      setBaseline(baselineData);
    } catch (e) {
      setError(`Não foi possível conectar à API (${e.message}). Confirme que o back-end está rodando em VITE_API_URL.`);
    }
  }, []);

  const loadGovernance = useCallback(async () => {
    try {
      const [g, mon] = await Promise.all([api.getGovernance(), api.getMonitoring()]);
      setGovernance(g);
      setMonitoring(mon);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    loadCore();
    loadGovernance();
  }, [loadCore, loadGovernance]);

  async function handleToggleRoom(id, disponivel) {
    const updated = await api.updateRoom(id, { disponivel });
    setRooms((prev) => prev.map((r) => (r.id === id ? updated : r)));
    const baselineData = await api.getBaseline();
    setBaseline(baselineData);
  }

  async function handleUpdateTeamSize(id, tamanho) {
    const updated = await api.updateTeam(id, { tamanho });
    setTeams((prev) => prev.map((t) => (t.id === id ? updated : t)));
    const baselineData = await api.getBaseline();
    setBaseline(baselineData);
  }

  async function handleToggleConstraint(id, ativa) {
    const updated = await api.updateConstraint(id, { ativa });
    setConstraints((prev) => prev.map((c) => (c.id === id ? updated : c)));
  }

  async function handleRunAllocation() {
    setLoadingRun(true);
    setError(null);
    try {
      const run = await api.runAllocation();
      setLastRun(run);
      setRunCount((n) => n + 1);
      setActiveTab('dashboard');
      await loadGovernance();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingRun(false);
    }
  }

  async function handleReject(teamId) {
    if (!lastRun) return;
    try {
      const updatedRun = await api.intervene(lastRun.id, { team_id: teamId, acao: 'rejeitar' });
      setLastRun(updatedRun);
      await loadGovernance();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleRunTrustTests() {
    setLoadingTests(true);
    try {
      const results = await api.getTrustTests();
      setTrustTests(results);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingTests(false);
    }
  }

  const explainResult = lastRun ? lastRun.results.find((r) => r.team_id === explainTeamId) : null;
  const explainRoom = explainResult ? rooms.find((r) => r.id === explainResult.sala_id) : null;

  return (
    <div>
      <Header runCount={runCount} />
      <Tabs active={activeTab} onChange={setActiveTab} />

      {error && <div className="error-banner">{error}</div>}

      {activeTab === 'dashboard' && <Dashboard rooms={rooms} lastRun={lastRun} />}
      {activeTab === 'salas' && <RoomsTab rooms={rooms} onToggleRoom={handleToggleRoom} />}
      {activeTab === 'setores' && <SectorsTab sectors={sectors} teams={teams} onUpdateTeamSize={handleUpdateTeamSize} />}
      {activeTab === 'restricoes' && <ConstraintsTab constraints={constraints} onToggleConstraint={handleToggleConstraint} />}
      {activeTab === 'alocacao' && (
        <AllocationTab
          rooms={rooms}
          lastRun={lastRun}
          baseline={baseline}
          loading={loadingRun}
          onRun={handleRunAllocation}
          onExplain={setExplainTeamId}
          onReject={handleReject}
        />
      )}
      {activeTab === 'confianca' && <TrustTab tests={trustTests} loading={loadingTests} onRun={handleRunTrustTests} />}
      {activeTab === 'monitoramento' && <MonitoringTab monitoring={monitoring} governance={governance} />}
      {activeTab === 'governanca' && <GovernanceTab governance={governance} />}

      {explainResult && explainRoom && (
        <ExplainModal result={explainResult} room={explainRoom} onClose={() => setExplainTeamId(null)} />
      )}
    </div>
  );
}
