import { useState } from "react";
import { askQuestion, type AskResponse } from "../api";

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: AskResponse["sources"];
  queryLogId?: number;
}

export default function ChatPanel(){
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleSend() {
        const question = input.trim()
        if(!question || loading) return;

        setMessages((prev) => [...prev, {role: "user", text: question}]);
        setInput("");
        setLoading(true);

        try{
            const result = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: result.answer,
          sources: result.sources,
          queryLogId: result.query_log_id,
        },
    ]);
    }catch(err){
        setMessages((prev) => [
            ...prev,
            { role: "assistant", text: "Something went wrong. Please try again."},
        ]);
    }finally{
        setLoading(false);
    }
}


return(
    <div>
        <div>
            {messages.map((msg, i) => (
                <div key={i}>
                    <strong>{msg.role === "user"? "you" : "Assistant"}:</strong>
                    {msg.text}
                </div>
            ))}
            {loading && <div>Thinking...</div>}
        </div>

        <div>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about billing, shipping, returns..."
            />
            <button onClick={handleSend} disabled={loading}>
                Send
            </button>
        </div>
    </div>
);
}