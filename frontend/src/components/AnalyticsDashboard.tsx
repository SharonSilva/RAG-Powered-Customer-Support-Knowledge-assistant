import { useEffect, useState } from "react";
import {
  getAnalyticsSummary,
  getKnowledgeGaps,
  getRecommendations,
  generateRecommendations,
  updateRecommendationStatus,
  type AnalyticsSummary,
  type GapCluster,
  type Recommendation,
} from "../api";
import "./AnalyticsDashboard.css";

export default function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [gaps, setGaps] = useState<GapCluster[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  async function loadAll() {
    setLoading(true);
    try {
      const [summaryData, gapsData, recsData] = await Promise.all([
        getAnalyticsSummary(),
        getKnowledgeGaps(),
        getRecommendations(),
      ]);
      setSummary(summaryData);
      setGaps(gapsData.gaps);
      setRecommendations(recsData.recommendations);
    } catch (err) {
      // leave previous state in place; the dashboard will just look stale
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      await generateRecommendations();
      await loadAll();
    } finally {
      setGenerating(false);
    }
  }

  async function handleStatusChange(id: number, status: "approved" | "rejected") {
    await updateRecommendationStatus(id, status);
    setRecommendations((prev) => prev.map((r) => (r.id === id ? { ...r, status } : r)));
  }

  if (loading) {
    return <div className="analytics-loading">Loading analytics…</div>;
  }

  return (
    <div className="analytics-dashboard">
      {summary && (
        <div className="health-score-card">
          <div className="health-score-number">{summary.health_score.knowledge_health_score}</div>
          <div className="health-score-label">Knowledge Health Score</div>
          <div className="health-score-breakdown">
            {Object.entries(summary.health_score.breakdown).map(([key, val]) => (
              <div key={key} className="breakdown-row">
                <span className="breakdown-label">{key.replace(/_/g, " ")}</span>
                <span className="breakdown-value">{val.value}</span>
              </div>
            ))}
          </div>
          <div className="summary-stats">
            <span>{summary.overall.total_queries} total questions</span>
            <span>{summary.overall.fallback_rate_percent}% fallback rate</span>
          </div>
        </div>
      )}

      <div className="dashboard-section">
        <h3>Knowledge gaps</h3>
        {gaps.length === 0 ? (
          <p className="empty-note">No recurring gaps detected yet.</p>
        ) : (
          gaps.map((gap, i) => (
            <div key={i} className="gap-row">
              <span className="gap-topic">{gap.topic}</span>
              <span className="gap-count">asked {gap.times_asked}×</span>
            </div>
          ))
        )}
      </div>

      <div className="dashboard-section">
        <div className="section-header-row">
          <h3>FAQ recommendations</h3>
          <button className="generate-button" onClick={handleGenerate} disabled={generating}>
            {generating ? "Generating…" : "Generate"}
          </button>
        </div>

        {recommendations.length === 0 ? (
          <p className="empty-note">No recommendations yet — click Generate to check for gaps.</p>
        ) : (
          recommendations.map((rec) => (
            <div key={rec.id} className="recommendation-card">
              <p className="rec-question">{rec.suggested_question}</p>
              <p className="rec-answer">{rec.suggested_answer}</p>
              <div className="rec-footer">
                <span className={`rec-status rec-status--${rec.status}`}>{rec.status}</span>
                {rec.status === "pending" && (
                  <div className="rec-actions">
                    <button onClick={() => handleStatusChange(rec.id, "approved")}>Approve</button>
                    <button onClick={() => handleStatusChange(rec.id, "rejected")}>Reject</button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}