import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import UploadPanel from "./components/UploadPanel";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import "./App.css";

type Tab = "assistant" | "analytics";

function App() {
  const [tab, setTab] = useState<Tab>("assistant");

  return (
    <div className="app-container">
      <div className="app-header-row">
        <h1 className="app-header">Support Assistant</h1>
        <div className="tab-switcher">
          <button
            className={tab === "assistant" ? "tab-button tab-button--active" : "tab-button"}
            onClick={() => setTab("assistant")}
          >
            Assistant
          </button>
          <button
            className={tab === "analytics" ? "tab-button tab-button--active" : "tab-button"}
            onClick={() => setTab("analytics")}
          >
            Analytics
          </button>
        </div>
      </div>

      {tab === "assistant" ? (
        <div className="app-body">
          <UploadPanel />
          <div className="chat-column">
            <ChatPanel />
          </div>
        </div>
      ) : (
        <div className="app-body">
          <AnalyticsDashboard />
        </div>
      )}
    </div>
  );
}

export default App;