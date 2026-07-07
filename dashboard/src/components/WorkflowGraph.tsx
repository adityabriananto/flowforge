import React from "react";

interface WorkflowGraphProps {
  states: string[];
  currentState: string;
}

export const WorkflowGraph: React.FC<WorkflowGraphProps> = ({ states, currentState }) => {
  return (
    <div className="workflow-graph-card glass-panel">
      <h3 className="panel-title">State Machine Monitor</h3>
      <div className="nodes-container">
        {states.map((state, index) => {
          const isActive = state === currentState;
          const isCompleted = states.indexOf(currentState) > index;
          
          return (
            <React.Fragment key={state}>
              <div 
                className={`state-node ${isActive ? "active-node" : ""} ${isCompleted ? "completed-node" : ""}`}
              >
                <div className="node-glow"></div>
                <div className="node-content">
                  <span className="node-index">0{index + 1}</span>
                  <span className="node-name">{state}</span>
                  {isActive && <span className="active-badge">Active</span>}
                </div>
              </div>
              
              {index < states.length - 1 && (
                <div className={`connector-line ${isCompleted ? "completed-line" : ""}`}>
                  <div className="line-flow"></div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
