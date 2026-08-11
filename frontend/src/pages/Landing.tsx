import "./Landing.css";

interface LandingProps {
  onLaunch: () => void;
}

export default function Landing({ onLaunch }: LandingProps) {
  return (
    <div className="landing">
      <nav className="landing-nav">
        <div className="landing-nav-brand">
          <span className="landing-nav-mark">1</span>
          Support Assistant
        </div>
        <div className="landing-nav-links">
          <a href="#trust">Why it's trustworthy</a>
          <a href="#how">How it works</a>
        </div>
        <button className="landing-nav-cta" onClick={onLaunch}>
          Try the demo
        </button>
      </nav>

      <header className="landing-hero">
        <div className="landing-hero-inner">
          <div>
            <div className="landing-eyebrow">RAG · pgvector · GPT-4o-mini</div>
            <h1>Support answers your customers can actually trust.</h1>
            <p className="landing-sub">
              Upload your documents. Get grounded answers with real citations —
              and see exactly what your knowledge base is still missing.
            </p>
            <div className="landing-hero-actions">
              <button className="landing-btn-primary" onClick={onLaunch}>
                Try the live demo
              </button>
              <a href="#how" className="landing-btn-secondary">
                See how it works
              </a>
            </div>
          </div>

          <div className="hero-card">
            <div className="hero-card-q">
              <span>What's your return policy?</span>
            </div>
            <div className="hero-card-a">
              Items can be returned within 14 days of delivery for a full
              refund. Items must be unused and in original packaging.{" "}
              <span className="hero-card-cite">1</span>
            </div>
            <div className="hero-card-sources">
              <div className="hero-card-source-tag">
                <span style={{ color: "var(--color-teal)" }}>1</span> Return Policy
              </div>
            </div>
          </div>
        </div>
      </header>

      <section className="landing-section" id="trust">
        <div className="landing-section-head">
          <h2>Built to earn trust, not just sound confident.</h2>
          <p>
            Most AI chatbots guess when they don't know. This one shows its
            work  and tells you what it's missing.
          </p>
        </div>

        <div className="trust-grid">
          <div className="trust-card">
            <div className="trust-card-tag">[1]</div>
            <h3>Grounded answers</h3>
            <p>
              Every answer traces back to your actual documents, with the
              exact section cited — so your team can verify it in one click.
            </p>
            <div className="trust-card-visual">
              <div className="hero-card-source-tag">
                <span style={{ color: "var(--color-teal)" }}>1</span> Warranty Information
              </div>
            </div>
          </div>

          <div className="trust-card">
            <div className="trust-card-tag">[2]</div>
            <h3>Honest when it doesn't know</h3>
            <p>
              If the answer isn't in your docs, it says so — instead of
              guessing and eroding customer trust.
            </p>
            <div className="trust-card-visual">
              <div className="trust-visual-fallback">
                I don't have information on that in the knowledge base.
              </div>
            </div>
          </div>

          <div className="trust-card">
            <div className="trust-card-tag">[3]</div>
            <h3>Knows what's missing</h3>
            <p>
              Every unanswered question becomes a tracked gap, with
              AI-drafted FAQs ready for your review.
            </p>
            <div className="trust-card-visual">
              <div className="trust-visual-score">72</div>
              <div className="trust-visual-score-label">Knowledge Health Score</div>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-section steps-section" id="how">
        <div className="landing-section-head">
          <h2>How it works</h2>
          <p>Three steps from raw documents to a self-improving knowledge base.</p>
        </div>

        <div className="steps-list">
          <div className="step-item">
            <div className="step-number">1</div>
            <div>
              <h4>Upload your documents</h4>
              <p>PDF, Word, Markdown, or a URL — organized by category.</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-number">2</div>
            <div>
              <h4>Customers ask questions</h4>
              <p>Answered directly from your content, with citations attached.</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-number">3</div>
            <div>
              <h4>Track what's missing</h4>
              <p>Review gaps, approve AI-drafted fixes, watch your score improve.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="footer-cta">
        <h2>See it answer your own questions.</h2>
        <p>No signup needed — try the live demo right now.</p>
        <button className="landing-btn-primary" onClick={onLaunch}>
          Try the live demo
        </button>
        <div className="landing-footer-badge">RAG · pgvector · GPT-4o-mini</div>
      </section>
    </div>
  );
}