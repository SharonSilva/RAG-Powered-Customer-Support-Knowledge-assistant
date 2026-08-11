import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import UploadPanel from "./components/UploadPanel";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import Landing from "./pages/Landing";
import "./App.css";

type Tab = "assistant" | "analytics";
type View = "landing" | "app";

function App() {
  const [view, setView] = useState<View>("landing");
  const [tab, setTab] = useState<Tab>("assistant");

  if (view === "landing") {
    return <Landing onLaunch={() => setView("app")} />;
  }

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <button className="sidebar-brand" onClick={() => setView("landing")}>
          <span className="sidebar-brand-mark">1</span>
          Support Assistant
        </button>

        <nav className="sidebar-nav">
          <button
            className={
              tab === "assistant" ? "sidebar-nav-item sidebar-nav-item--active" : "sidebar-nav-item"
            }
            onClick={() => setTab("assistant")}
          >
            <span className="sidebar-nav-dot" />
            Chat
          </button>
          <button
            className={
              tab === "analytics" ? "sidebar-nav-item sidebar-nav-item--active" : "sidebar-nav-item"
            }
            onClick={() => setTab("analytics")}
          >
            <span className="sidebar-nav-dot" />
            Analytics
          </button>
        </nav>

        <div className="sidebar-divider" />

        <UploadPanel />
      </aside>

      <main className="app-main">
        <div className="app-main-inner">
          {tab === "assistant" ? <ChatPanel /> : <AnalyticsDashboard />}
        </div>
      </main>
    </div>
  );
}

export default App;
