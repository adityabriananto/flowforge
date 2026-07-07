import React from "react";

export interface TimelineStep {
  name: string;
  status: "idle" | "running" | "completed" | "failed";
  elapsed: string;
  tokens: string;
  cost: string;
  retry: number;
  worker: string;
}

interface WorkflowTimelineProps {
  steps: TimelineStep[];
}

export const WorkflowTimeline: React.FC<WorkflowTimelineProps> = ({ steps }) => {
  return (
    <div className="workflow-timeline-card glass-panel">
      <h3 className="panel-title">Workflow Execution Timeline</h3>
      <div className="timeline-steps-list">
        {steps.map((step, index) => {
          const isIdle = step.status === "idle";
          const isRunning = step.status === "running";
          const isCompleted = step.status === "completed";

          return (
            <div key={index} className={`timeline-step-item ${isRunning ? "step-running" : ""} ${isCompleted ? "step-completed" : ""}`}>
              <div className="step-indicator-wrapper">
                <div className={`step-dot-indicator ${step.status}`}>
                  {isCompleted && <span className="checkmark">✓</span>}
                  {isRunning && <span className="spinner"></span>}
                </div>
                {index < steps.length - 1 && <div className={`step-connector-line ${isCompleted ? "connector-completed" : ""}`}></div>}
              </div>

              <div className="step-detail-content">
                <div className="step-title-row">
                  <span className="step-name">{step.name}</span>
                  <span className={`step-status-badge ${step.status}`}>
                    {step.status.toUpperCase()}
                  </span>
                </div>
                
                {!isIdle && (
                  <div className="step-metrics-grid">
                    <div className="metric-box">
                      <span className="metric-label">Elapsed</span>
                      <span className="metric-val">{step.elapsed}</span>
                    </div>
                    <div className="metric-box">
                      <span className="metric-label">Tokens</span>
                      <span className="metric-val">{step.tokens}</span>
                    </div>
                    <div className="metric-box">
                      <span className="metric-label">Cost</span>
                      <span className="metric-val text-success">{step.cost}</span>
                    </div>
                    <div className="metric-box">
                      <span className="metric-label">Retry</span>
                      <span className="metric-val">{step.retry}</span>
                    </div>
                    <div className="metric-box full-width">
                      <span className="metric-label">Worker</span>
                      <span className="metric-val text-highlight">{step.worker}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
