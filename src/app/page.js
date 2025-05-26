import Link from 'next/link';

export default function Dashboard() {
  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">Good morning! How are you feeling today?</h1>
          <p className="page-subtitle">Your AI agents have been analyzing your patterns</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Energy Trend</div>
            <div className="stat-value positive">↗ +15%</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Active Agents</div>
            <div className="stat-value primary">3</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Patterns Found</div>
            <div className="stat-value accent">7</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Streak</div>
            <div className="stat-value warning">12 days</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card">
            <h2 className="card-header flex items-center">
              <span className="w-3 h-3 bg-blue-500 rounded-full mr-3"></span>
              Recent Insights
            </h2>
            <div className="space-y-4">
              <div className="insight-card pattern">
                <p className="text-muted text-sm">Pattern Agent</p>
                <p className="text-primary font-medium">Your energy peaks on days when you exercise before 10 AM</p>
              </div>
              <div className="insight-card insight">
                <p className="text-muted text-sm">Insight Agent</p>
                <p className="text-primary font-medium">Consider scheduling important tasks between 9-11 AM</p>
              </div>
              <div className="insight-card spawned">
                <p className="text-muted text-sm">Weekend Energy Agent</p>
                <p className="text-primary font-medium">New specialized agent created to optimize your weekends!</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="card-header">Today's Recommendations</h2>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-primary font-medium">Try a morning walk</p>
                  <p className="text-secondary text-sm">Based on your energy patterns</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-primary font-medium">Schedule creative work for 2 PM</p>
                  <p className="text-secondary text-sm">Your peak creative hours</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Link href="/daily_entry" className="btn btn-primary">
            Log Today's Entry
          </Link>
        </div>
      </div>
    </div>
  );
}