import ChatPanel from "./components/ChatPanel";
import UploadPanel from "./components/UploadPanel";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <h1 className="app-header">Support Assistant</h1>
      <div className="app-body">
        <UploadPanel />
        <div className="chat-column">
          <ChatPanel />
        </div>
      </div>
    </div>
  );
}

export default App;
