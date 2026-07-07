import { useState, useCallback } from "react";
import { WorkflowGraph } from "./components/WorkflowGraph";
import { DiffViewer } from "./components/DiffViewer";
import { ApprovalPanel } from "./components/ApprovalPanel";
import { WorkflowTimeline } from "./components/WorkflowTimeline";
import type { TimelineStep } from "./components/WorkflowTimeline";
import { useWorkflowWS } from "./hooks/useWorkflowWS";
import type { WSMessage } from "./hooks/useWorkflowWS";
import { Activity, Shield, Terminal, ArrowRight, CheckCircle, AlertCircle } from "./components/Icons";

interface WorkflowInstance {
  id: string;
  workflow_id: string;
  current_state: string;
  variables: Record<string, any>;
}

interface AuditLog {
  id: string;
  event_type: string;
  payload: Record<string, any>;
  triggered_by: string;
  timestamp: string;
}

const API_BASE = "http://localhost:8000/api";

const originalCode = `def process_user_data(user):
    # Old logic
    print("Saving user data")
    return user.save()
`;

const modifiedCode = `def process_user_data(user):
    # Refactored for performance and thread safety
    if not user.is_active:
        raise ValueError("Cannot process inactive user")
    
    logger.info(f"Processing user: {user.id}")
    db.session.add(user)
    db.session.commit()
    return user
`;

function App() {
  const [instanceId, setInstanceId] = useState<string | null>(null);
  const [instance, setInstance] = useState<WorkflowInstance | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const getTimelineSteps = (state: string): TimelineStep[] => {
    return [
      {
        name: "Analysis",
        status: "completed",
        elapsed: "1.2s",
        tokens: "512",
        cost: "$0.007",
        retry: 0,
        worker: "Requirements Analyzer"
      },
      {
        name: "Architecture",
        status: "completed",
        elapsed: "3.5s",
        tokens: "2.4k",
        cost: "$0.048",
        retry: 0,
        worker: "Claude Arch Designer"
      },
      {
        name: "Coding",
        status: state === "CODING" ? "running" : (["TESTING", "AWAITING_APPROVAL", "COMPLETED", "FAILED"].includes(state) ? "completed" : "idle"),
        elapsed: state === "CODING" ? "4.1s" : (["TESTING", "AWAITING_APPROVAL", "COMPLETED", "FAILED"].includes(state) ? "5.8s" : "0s"),
        tokens: ["CODING", "TESTING", "AWAITING_APPROVAL", "COMPLETED", "FAILED"].includes(state) ? "4.1k" : "0",
        cost: ["CODING", "TESTING", "AWAITING_APPROVAL", "COMPLETED", "FAILED"].includes(state) ? "$0.082" : "$0.00",
        retry: 0,
        worker: "Codex Python Writer"
      },
      {
        name: "Testing",
        status: state === "TESTING" ? "running" : (["AWAITING_APPROVAL", "COMPLETED", "FAILED"].includes(state) ? "completed" : "idle"),
        elapsed: state === "TESTING" ? "2.1s" : (["AWAITING_APPROVAL", "COMPLETED", "FAILED"].includes(state) ? "2.3s" : "0s"),
        tokens: "N/A",
        cost: "$0.00",
        retry: 0,
        worker: "Pytest Automated Runner"
      },
      {
        name: "Review (HITL)",
        status: state === "AWAITING_APPROVAL" ? "running" : (state === "COMPLETED" ? "completed" : "idle"),
        elapsed: state === "COMPLETED" ? "12s" : "0s",
        tokens: "N/A",
        cost: "$0.00",
        retry: 0,
        worker: "Human Lead Approval"
      },
      {
        name: "Done",
        status: state === "COMPLETED" ? "completed" : "idle",
        elapsed: state === "COMPLETED" ? "0.2s" : "0s",
        tokens: "N/A",
        cost: "$0.00",
        retry: 0,
        worker: "Git Deployer"
      }
    ];
  };

  // Fetch instance details
  const fetchInstanceDetails = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/instances/${id}`);
      if (res.ok) {
        const data = await res.json();
        setInstance(data);
      }
    } catch (err) {
      console.error("Error fetching instance:", err);
    }
  };

  // Fetch audit logs
  const fetchAuditLogs = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/instances/${id}/events`);
      if (res.ok) {
        const data = await res.json();
        setAuditLogs(data);
      }
    } catch (err) {
      console.error("Error fetching audit logs:", err);
    }
  };

  // Handle incoming live sync updates via WebSocket
  const handleWSMessage = useCallback((msg: WSMessage) => {
    if (instance) {
      setInstance(prev => prev ? { ...prev, current_state: msg.to_state } : null);
      // Append transition to audit logs locally
      const mockLog: AuditLog = {
        id: crypto.randomUUID(),
        event_type: msg.event_type,
        payload: {
          from_state: msg.from_state,
          to_state: msg.to_state,
          trigger_event: msg.trigger_event,
          require_human: msg.require_human
        },
        triggered_by: "SYSTEM",
        timestamp: new Date().toISOString()
      };
      setAuditLogs(prev => [mockLog, ...prev]);
    }
  }, [instance]);

  const { status: wsStatus } = useWorkflowWS(instanceId, handleWSMessage);

  // Initialize demo workflow and instance
  const createDemoWorkflow = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Create Workflow Template
      const workflowRes = await fetch(`${API_BASE}/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "FlowForge Agentic Coder",
          version: "1.0.0",
          initial_state: "IDLE",
          states: {
            IDLE: { name: "IDLE", next_state: "CODING" },
            CODING: { name: "CODING", worker_type: "python_agent", script: "agents/coder.py", next_state: "TESTING", on_failure: "FAILED" },
            TESTING: { name: "TESTING", worker_type: "pytest_runner", script: "agents/tester.py", next_state: "AWAITING_APPROVAL", on_failure: "CODING" },
            AWAITING_APPROVAL: { name: "AWAITING_APPROVAL", require_human: true, on_approve: "COMPLETED", on_reject: "CODING" },
            COMPLETED: { name: "COMPLETED", is_final: true },
            FAILED: { name: "FAILED", is_final: true }
          }
        })
      });

      if (!workflowRes.ok) throw new Error("Failed to register demo workflow template");
      const workflow = await workflowRes.json();

      // 2. Create Instance
      const instanceRes = await fetch(`${API_BASE}/instances`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflow_id: workflow.id,
          variables: { "target_file": "utils/user.py" }
        })
      });

      if (!instanceRes.ok) throw new Error("Failed to instantiate demo workflow");
      const inst = await instanceRes.json();
      
      setInstanceId(inst.id);
      setInstance(inst);
      await fetchAuditLogs(inst.id);
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend server");
    } finally {
      setIsLoading(false);
    }
  };

  // Run initial transition from IDLE -> CODING -> TESTING -> AWAITING_APPROVAL for demo simulation
  const simulateWorkflowExecution = async () => {
    if (!instanceId) return;
    setIsLoading(true);
    try {
      // IDLE -> CODING
      await fetch(`${API_BASE}/instances/${instanceId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "START", triggered_by: "SYSTEM" })
      });
      // CODING -> TESTING
      await fetch(`${API_BASE}/instances/${instanceId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "SUCCESS", triggered_by: "SYSTEM" })
      });
      // TESTING -> AWAITING_APPROVAL
      await fetch(`${API_BASE}/instances/${instanceId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "SUCCESS", triggered_by: "SYSTEM" })
      });

      await fetchInstanceDetails(instanceId);
      await fetchAuditLogs(instanceId);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // HITL Action: Approve
  const handleApprove = async () => {
    if (!instanceId) return;
    setIsLoading(true);
    try {
      await fetch(`${API_BASE}/instances/${instanceId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "APPROVE", triggered_by: "HUMAN_LEAD" })
      });
      await fetchInstanceDetails(instanceId);
      await fetchAuditLogs(instanceId);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // HITL Action: Reject
  const handleReject = async (feedback: string) => {
    if (!instanceId) return;
    setIsLoading(true);
    try {
      console.log("Rejection feedback provided:", feedback);
      await fetch(`${API_BASE}/instances/${instanceId}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "REJECT", triggered_by: "HUMAN_LEAD" })
      });
      await fetchInstanceDetails(instanceId);
      await fetchAuditLogs(instanceId);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-app">
      {/* Top Header */}
      <header className="dashboard-header glass-header">
        <div className="header-brand">
          <Activity className="brand-icon" />
          <span className="brand-title">FlowForge</span>
          <span className="brand-tag">v0.1.0</span>
        </div>
        <div className="header-status">
          {instanceId && (
            <div className={`status-indicator ${wsStatus}`}>
              <span className="status-dot"></span>
              <span className="status-text">
                WS Sync: {wsStatus.toUpperCase()}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Main Grid Layout */}
      <main className="dashboard-main">
        {!instanceId ? (
          <div className="welcome-panel glass-panel">
            <Shield className="welcome-icon" />
            <h2>Welcome to FlowForge Orchestrator</h2>
            <p>
              Please launch the local server (`uv run fastapi dev src/flowforge/entrypoints/api/main.py`) first, then click below to bootstrap the demo environment.
            </p>
            {error && (
              <div className="alert-box error-alert">
                <AlertCircle className="alert-icon" />
                <span>{error}</span>
              </div>
            )}
            <button 
              className="btn btn-primary" 
              onClick={createDemoWorkflow}
              disabled={isLoading}
            >
              {isLoading ? "Starting Server Connection..." : "Bootstrap FlowForge Demo"}
            </button>
          </div>
        ) : (
          <div className="grid-layout">
            {/* Left Side: Monitor & Controls */}
            <div className="layout-left">
              <WorkflowGraph 
                states={["IDLE", "CODING", "TESTING", "AWAITING_APPROVAL", "COMPLETED", "FAILED"]}
                currentState={instance?.current_state || "IDLE"}
              />

              <WorkflowTimeline 
                steps={getTimelineSteps(instance?.current_state || "IDLE")} 
              />

              {instance?.current_state === "IDLE" && (
                <div className="control-panel glass-panel">
                  <h3 className="panel-title">Simulation Control</h3>
                  <p className="panel-desc">
                    Trigger the initial steps asynchronously. The AI agent will auto-write code, run pytest suite, and loop back if failing, or await your approval when test passes.
                  </p>
                  <button className="btn btn-primary" onClick={simulateWorkflowExecution} disabled={isLoading}>
                    Simulate Agentic Run
                  </button>
                </div>
              )}

              {instance?.current_state === "AWAITING_APPROVAL" && (
                <ApprovalPanel 
                  onApprove={handleApprove}
                  onReject={handleReject}
                  isLoading={isLoading}
                />
              )}

              {instance?.current_state === "COMPLETED" && (
                <div className="success-panel glass-panel">
                  <CheckCircle className="success-icon" />
                  <h3>Workflow Completed Successfully!</h3>
                  <p>All coding changes approved and changes compiled to target file.</p>
                  <button className="btn btn-cancel" onClick={createDemoWorkflow}>Reset Demo</button>
                </div>
              )}
            </div>

            {/* Right Side: Diff Code Review & Audit Log */}
            <div className="layout-right">
              {instance?.current_state === "AWAITING_APPROVAL" ? (
                <DiffViewer 
                  originalCode={originalCode}
                  modifiedCode={modifiedCode}
                  filename={instance.variables["target_file"] || "utils/user.py"}
                />
              ) : (
                <div className="terminal-pane glass-panel">
                  <div className="terminal-header">
                    <Terminal className="terminal-icon" />
                    <span>Worker Run Logs</span>
                  </div>
                  <div className="terminal-content">
                    {instance?.current_state === "CODING" && (
                      <p className="log-line anim-typing">[INFO] AI Worker starting code generation on utils/user.py...</p>
                    )}
                    {instance?.current_state === "TESTING" && (
                      <>
                        <p className="log-line">[INFO] Running test suite using pytest...</p>
                        <p className="log-line text-success">tests/test_user.py::test_user_data PASSED [100%]</p>
                      </>
                    )}
                    {instance?.current_state === "IDLE" && (
                      <p className="log-line text-muted">[System] Ready. Click 'Simulate Agentic Run' to start.</p>
                    )}
                  </div>
                </div>
              )}

              {/* Event Logs / Audit Trail */}
              <div className="audit-trail-card glass-panel">
                <h3 className="panel-title">Audit Trail</h3>
                <div className="audit-list">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="audit-item">
                      <div className="audit-meta">
                        <span className="audit-type">{log.event_type}</span>
                        <span className="audit-time">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="audit-payload">
                        {log.payload.from_state ? (
                          <>
                            State: <span className="text-highlight">{log.payload.from_state}</span> 
                            <ArrowRight className="inline-arrow" /> 
                            <span className="text-highlight">{log.payload.to_state}</span> (Trigger: {log.payload.trigger_event})
                          </>
                        ) : (
                          JSON.stringify(log.payload)
                        )}
                      </p>
                      <span className="audit-actor">Actor: {log.triggered_by}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
