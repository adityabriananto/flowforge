import React from "react";

interface DiffViewerProps {
  originalCode: string;
  modifiedCode: string;
  filename: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ originalCode, modifiedCode, filename }) => {
  const originalLines = originalCode.split("\n");
  const modifiedLines = modifiedCode.split("\n");

  return (
    <div className="diff-viewer-card glass-panel">
      <div className="diff-header">
        <span className="diff-filename">{filename}</span>
        <span className="diff-badge">Code Review (HITL)</span>
      </div>
      <div className="diff-split-container">
        {/* Original Code Panel */}
        <div className="diff-pane">
          <div className="pane-header">Original</div>
          <pre className="code-block original-block">
            <code>
              {originalLines.map((line, idx) => (
                <div key={idx} className="code-line deleted-line">
                  <span className="line-num">{idx + 1}</span>
                  <span className="line-sign">-</span>
                  <span className="line-text">{line}</span>
                </div>
              ))}
            </code>
          </pre>
        </div>

        {/* Modified Code Panel */}
        <div className="diff-pane">
          <div className="pane-header">Modified by AI</div>
          <pre className="code-block modified-block">
            <code>
              {modifiedLines.map((line, idx) => (
                <div key={idx} className="code-line added-line">
                  <span className="line-num">{idx + 1}</span>
                  <span className="line-sign">+</span>
                  <span className="line-text">{line}</span>
                </div>
              ))}
            </code>
          </pre>
        </div>
      </div>
    </div>
  );
};
