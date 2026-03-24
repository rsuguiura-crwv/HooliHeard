import { Routes, Route } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import DashboardPage from "./components/dashboard/DashboardPage";
import InsightsPage from "./components/insights/InsightsPage";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-slate-700">{title}</h2>
        <p className="mt-2 text-slate-500">Coming soon</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/lineage" element={<PlaceholderPage title="Lineage" />} />
        <Route path="/pipeline" element={<PlaceholderPage title="Pipeline" />} />
      </Routes>
    </AppShell>
  );
}
