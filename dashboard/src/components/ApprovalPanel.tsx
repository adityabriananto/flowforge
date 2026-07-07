import React, { useState } from "react";

interface ApprovalPanelProps {
  onApprove: () => Promise<void>;
  onReject: (feedback: string) => Promise<void>;
  isLoading: boolean;
}

export const ApprovalPanel: React.FC<ApprovalPanelProps> = ({ onApprove, onReject, isLoading }) => {
  const [feedback, setFeedback] = useState("");
  const [showRejectForm, setShowRejectForm] = useState(false);

  const handleRejectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedback.trim()) return;
    await onReject(feedback);
    setFeedback("");
    setShowRejectForm(false);
  };

  return (
    <div className="approval-panel glass-panel">
      <div className="panel-info">
        <h3 className="panel-title">Human Approval Required</h3>
        <p className="panel-desc">
          AI Worker has completed the code changes and test execution. Please review the changes and approve to deploy, or reject with feedback.
        </p>
      </div>

      {!showRejectForm ? (
        <div className="action-buttons">
          <button 
            className="btn btn-approve" 
            onClick={onApprove} 
            disabled={isLoading}
          >
            {isLoading ? "Processing..." : "Approve Changes"}
          </button>
          <button 
            className="btn btn-reject" 
            onClick={() => setShowRejectForm(true)} 
            disabled={isLoading}
          >
            Reject / Revise
          </button>
        </div>
      ) : (
        <form onSubmit={handleRejectSubmit} className="reject-form-container">
          <textarea
            className="feedback-textarea"
            placeholder="Provide constructive feedback for AI revision..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            required
            disabled={isLoading}
          />
          <div className="form-buttons">
            <button 
              type="submit" 
              className="btn btn-reject-submit" 
              disabled={isLoading || !feedback.trim()}
            >
              {isLoading ? "Sending..." : "Submit Rejection"}
            </button>
            <button 
              type="button" 
              className="btn btn-cancel" 
              onClick={() => setShowRejectForm(false)}
              disabled={isLoading}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
