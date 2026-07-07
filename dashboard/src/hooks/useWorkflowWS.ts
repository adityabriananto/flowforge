import { useEffect, useState } from "react";

export interface WSMessage {
  event_type: string;
  instance_id: string;
  from_state: string;
  to_state: string;
  trigger_event: string;
  require_human: boolean;
}

export function useWorkflowWS(instanceId: string | null, onMessageReceived: (msg: WSMessage) => void) {
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("disconnected");

  useEffect(() => {
    if (!instanceId) return;

    setStatus("connecting");
    // Connect to backend WebSocket API
    const wsUrl = `ws://localhost:8000/ws/instances/${instanceId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatus("connected");
      console.log("WebSocket connected to FlowForge instance:", instanceId);
    };

    ws.onmessage = (event) => {
      try {
        const data: WSMessage = JSON.parse(event.data);
        console.log("WebSocket received event:", data);
        onMessageReceived(data);
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
      console.log("WebSocket disconnected");
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      setStatus("disconnected");
    };

    return () => {
      ws.close();
    };
  }, [instanceId, onMessageReceived]);

  return { status };
}
