import { Link } from "react-router-dom";
import AppNavbar from "../components/AppNavbar";

function LandingPage() {
  return (
    <div className="landing-page min-vh-100">
      <AppNavbar />

      <section className="hero-section position-relative overflow-hidden">
        <div className="hero-glow hero-glow-1"></div>
        <div className="hero-glow hero-glow-2"></div>

        <div className="container py-5">
          <div className="row align-items-center g-5 hero-main-row">
            <div className="col-12 col-lg-6">
              <div className="hero-badge fade-in-up">
                Your personal nutrition companion
              </div>

              <h1 className="hero-title fade-in-up-delay-1">
                Track your nutrition with structure, clarity, and smarter goals
              </h1>

              <p className="hero-subtitle fade-in-up-delay-2">
                Build your own food library, log meals throughout the day,
                import external foods, and measure your progress against daily
                calorie and macro goals.
              </p>

              <div className="hero-actions fade-in-up-delay-3">
                <Link to="/register" className="btn btn-dark btn-lg px-4 me-3">
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-outline-dark btn-lg px-4">
                  Sign In
                </Link>
              </div>
            </div>

            <div className="col-12 col-lg-6">
              <div className="hero-preview-wrapper fade-in-up-delay-2">
                <div className="hero-preview-card shadow-lg">
                  <div className="hero-preview-top">
                    <div>
                      <div className="preview-kicker">Today’s Progress</div>
                      <div className="preview-date">16-03-2026</div>
                    </div>
                    <div className="preview-pill">Goals active</div>
                  </div>

                  <div className="preview-rings">
                    <div className="mini-progress-card">
                      <div className="mini-ring mini-ring-1">
                        <span>62%</span>
                      </div>
                      <div className="mini-label">Calories</div>
                    </div>

                    <div className="mini-progress-card">
                      <div className="mini-ring mini-ring-2">
                        <span>75%</span>
                      </div>
                      <div className="mini-label">Protein</div>
                    </div>

                    <div className="mini-progress-card">
                      <div className="mini-ring mini-ring-3">
                        <span>43%</span>
                      </div>
                      <div className="mini-label">Carbs</div>
                    </div>
                  </div>

                  <div className="preview-meals">
                    <div className="preview-meal-card">
                      <div className="preview-meal-title">🍳 Breakfast</div>
                      <div className="preview-meal-item">Greek yogurt — 200g</div>
                      <div className="preview-meal-item">Banana — 120g</div>
                    </div>

                    <div className="preview-meal-card">
                      <div className="preview-meal-title">🥗 Lunch</div>
                      <div className="preview-meal-item">Chicken breast — 180g</div>
                      <div className="preview-meal-item">Rice — 150g</div>
                    </div>
                  </div>

                  <div className="preview-bottom">
                    <div className="preview-library-pill">Food library ready</div>
                    <div className="preview-library-pill preview-library-pill-dark">
                      External search connected
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="row g-4 mt-5">
            <div className="col-12 col-md-4">
              <div className="card border-0 shadow-sm feature-card fade-in-up">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">🎯</div>
                  <h3 className="h5 fw-bold">Goal Tracking</h3>
                  <p className="text-muted mb-0">
                    Set daily calorie and macro goals, then monitor progress visually.
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12 col-md-4">
              <div className="card border-0 shadow-sm feature-card fade-in-up-delay-1">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">🍽️</div>
                  <h3 className="h5 fw-bold">Meal Logging</h3>
                  <p className="text-muted mb-0">
                    Organise foods into breakfast, lunch, dinner, and snack sections.
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12 col-md-4">
              <div className="card border-0 shadow-sm feature-card fade-in-up-delay-2">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">📚</div>
                  <h3 className="h5 fw-bold">Food Library</h3>
                  <p className="text-muted mb-0">
                    Create your own foods or import external items into your personal library.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;