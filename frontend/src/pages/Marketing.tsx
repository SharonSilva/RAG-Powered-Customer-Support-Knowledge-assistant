import { useEffect, useRef, useState } from "react";
import "./Marketing.css";

interface MarketingProps {
  onContinue: () => void;
}

export default function Marketing({ onContinue }: MarketingProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const els = rootRef.current?.querySelectorAll(".mkt-reveal");
    if (!els) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("mkt-reveal--visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );

    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="mkt" ref={rootRef}>
      <nav className={scrolled ? "mkt-nav mkt-nav--scrolled" : "mkt-nav"}>
        <div className="mkt-nav-brand">
          <span className="mkt-nav-mark">1</span>
          Support Assistant
        </div>
        <button className="mkt-nav-cta" onClick={onContinue}>
          Explore the platform
        </button>
      </nav>

      <section className="mkt-hero">
        <div className="mkt-orb mkt-orb--1" />
        <div className="mkt-orb mkt-orb--2" />
        <div className="mkt-orb mkt-orb--3" />

        <div className="mkt-eyebrow">For support &amp; operations teams</div>
        <h1>
          Turn your documents into a support team that <em>never sleeps.</em>
        </h1>
        <p className="mkt-hero-sub">
          An AI knowledge assistant that answers customers directly from your
          own content  cites every source, tells the truth when it doesn't
          know, and shows you exactly what to fix next.
        </p>
        <div className="mkt-hero-actions">
          <button className="mkt-btn-primary" onClick={onContinue}>
            Explore the platform
          </button>
          <button className="mkt-btn-secondary" onClick={onContinue}>
            See how it works
          </button>
        </div>
      </section>

      <div className="mkt-marquee-wrap">
        <div className="mkt-marquee">
          <span>GROUNDED IN YOUR DOCS</span>
          <span>·</span>
          <span>EVERY ANSWER CITED</span>
          <span>·</span>
          <span>HONEST WHEN IT DOESN'T KNOW</span>
          <span>·</span>
          <span>TRACKS EVERY GAP</span>
          <span>·</span>
          <span>GROUNDED IN YOUR DOCS</span>
          <span>·</span>
          <span>EVERY ANSWER CITED</span>
          <span>·</span>
          <span>HONEST WHEN IT DOESN'T KNOW</span>
          <span>·</span>
          <span>TRACKS EVERY GAP</span>
          <span>·</span>
        </div>
      </div>

      <section className="mkt-value">
        <div className="mkt-value-inner">
          <div className="mkt-value-head mkt-reveal">
            <div className="mkt-eyebrow">Why it matters</div>
            <h2>Built for teams who can't afford to guess.</h2>
            <p>
              Every wrong answer costs trust. This system is designed around
              one rule: never say something it can't back up.
            </p>
          </div>

          <div className="mkt-value-grid">
            <div className="mkt-value-card mkt-reveal">
              <div className="mkt-value-num">01</div>
              <h3>Fewer repetitive tickets</h3>
              <p>
                Customers get instant, accurate answers from your own docs 
                without waiting in a support queue.
              </p>
            </div>
            <div className="mkt-value-card mkt-reveal">
              <div className="mkt-value-num">02</div>
              <h3>Nothing invented</h3>
              <p>
                Every response is grounded in your real documentation, with
                the exact source cited for your team to verify.
              </p>
            </div>
            <div className="mkt-value-card mkt-reveal">
              <div className="mkt-value-num">03</div>
              <h3>A knowledge base that improves itself</h3>
              <p>
                Every unanswered question becomes a tracked, actionable gap 
                with AI-drafted fixes ready for review.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mkt-final">
        <div className="mkt-orb mkt-orb--1" style={{ opacity: 0.2 }} />
        <h2 className="mkt-reveal">Ready to see it work?</h2>
        <p className="mkt-reveal">No signup required  explore the live platform now.</p>
        <button className="mkt-btn-primary mkt-reveal" onClick={onContinue}>
          Explore the platform
        </button>
      </section>
    </div>
  );
}
