import { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Award,
  BarChart3,
  CheckCircle2,
  Flame,
  Lock,
  LogIn,
  Play,
  ShieldCheck,
  Sparkles,
  Swords,
  Target,
  Trophy,
  Users,
} from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type AuthMode = 'login' | 'register';

type User = {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  xp: number;
  level: number;
  skill_level: string;
};

type PathItem = {
  id: number;
  name: string;
  description: string;
  difficulty: string;
};

type Challenge = {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  learning_objectives: string[];
  scenario_content: Record<string, any>;
  allowed_actions: string[];
  evaluation_rubric: Record<string, any>;
  max_score: number;
  xp_reward: number;
  explanation: string;
  completion_criteria: string;
};

const indicatorOptions = [
  'Urgency',
  'Fake sender domain',
  'Suspicious link',
  'Unexpected payment request',
  'Authority pressure',
  'Missing verification',
  'Suspicious attachment',
  'Evidence preservation',
];

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem('cyberquest_token');
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'Request failed');
  }

  return response.json();
}

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('cyberquest_token'));
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('cyberquest_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [view, setView] = useState<'landing' | 'dashboard' | 'missions' | 'simulation' | 'admin' | 'trainer'>('landing');
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [loading, setLoading] = useState(false);
  const [paths, setPaths] = useState<PathItem[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [progress, setProgress] = useState<any>(null);
  const [badges, setBadges] = useState<any>(null);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [decisionResult, setDecisionResult] = useState<any>(null);
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([]);
  const [reasoning, setReasoning] = useState('');
  const [missionFilter, setMissionFilter] = useState('all');
  const [missionDifficulty, setMissionDifficulty] = useState('all');
  const [form, setForm] = useState({
    fullName: 'Demo User',
    username: 'demo_user',
    email: 'learner@demo.local',
    password: 'demo123',
  });

  const isAuthenticated = Boolean(token && user);

  const filteredChallenges = useMemo(() => {
    return challenges.filter((challenge) => {
      const matchesCategory = missionFilter === 'all' || challenge.category === missionFilter;
      const matchesDifficulty = missionDifficulty === 'all' || challenge.difficulty === missionDifficulty;
      return matchesCategory && matchesDifficulty;
    });
  }, [challenges, missionFilter, missionDifficulty]);

  useEffect(() => {
    if (isAuthenticated) {
      setView('dashboard');
      loadDashboard();
    }
  }, [token, user]);

  async function loadDashboard() {
    if (!token) return;
    try {
      setLoading(true);
      const [progressData, challengeData, pathData, badgeData] = await Promise.all([
        apiFetch('/api/progress'),
        apiFetch('/api/challenges'),
        apiFetch('/api/learning-paths'),
        apiFetch('/api/badges'),
      ]);
      setProgress(progressData);
      setChallenges(challengeData);
      setPaths(pathData);
      setBadges(badgeData);
    } catch (error) {
      console.error('Dashboard load failed', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAuthSubmit(event: React.FormEvent) {
    event.preventDefault();
    try {
      setLoading(true);
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const payload =
        authMode === 'login'
          ? { email: form.email, password: form.password }
          : {
              email: form.email,
              username: form.username,
              full_name: form.fullName,
              password: form.password,
            };

      const response = await apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      localStorage.setItem('cyberquest_token', response.access_token);
      localStorage.setItem('cyberquest_user', JSON.stringify(response.user));
      setToken(response.access_token);
      setUser(response.user);
      setView('dashboard');
      setForm({
        fullName: '',
        username: '',
        email: '',
        password: '',
      });
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem('cyberquest_token');
    localStorage.removeItem('cyberquest_user');
    setToken(null);
    setUser(null);
    setView('landing');
  }

  async function startSimulation(challenge: Challenge) {
    if (!token) return;
    try {
      setSelectedChallenge(challenge);
      const response = await apiFetch('/api/simulations', {
        method: 'POST',
        body: JSON.stringify({
          challenge_id: challenge.id,
          persona_name: 'Security Coach',
        }),
      });
      setSessionId(response.id);
      setDecisionResult(null);
      setSelectedIndicators([]);
      setReasoning('');
      setView('simulation');
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Unable to start mission');
    }
  }

  async function submitDecision() {
    if (!sessionId) return;
    try {
      const response = await apiFetch(`/api/simulations/${sessionId}/decision`, {
        method: 'POST',
        body: JSON.stringify({
          selected_action: selectedIndicators[0] ? 'verify' : 'report',
          reasoning,
          suspicious_indicators: selectedIndicators,
        }),
      });
      setDecisionResult(response);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Unable to submit decision');
    }
  }

  async function endSimulation() {
    if (!sessionId) return;
    try {
      await apiFetch(`/api/simulations/${sessionId}/complete`, { method: 'POST' });
      setDecisionResult({ status: 'Mission complete', score: 100, xp: 100, feedback: 'You completed the mission safely.' });
      setView('dashboard');
      loadDashboard();
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Unable to complete simulation');
    }
  }

  const skillChartData = [
    { name: 'Phishing', value: 78 },
    { name: 'Password', value: 67 },
    { name: 'Social', value: 81 },
    { name: 'IR', value: 72 },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-300 ring-1 ring-cyan-400/50">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="text-lg font-semibold">CyberQuest AI</div>
              <div className="text-xs text-slate-400">Gamified Cyber Hygiene</div>
            </div>
          </div>

          <nav className="hidden gap-8 text-sm text-slate-300 md:flex">
            <button onClick={() => setView('landing')} className="hover:text-cyan-300">Home</button>
            <button onClick={() => setView('missions')} className="hover:text-cyan-300">Missions</button>
            <button onClick={() => setView('dashboard')} className="hover:text-cyan-300">Dashboard</button>
            {user && (user.role === 'admin' || user.role === 'trainer') && (
              <button onClick={() => setView(user.role === 'admin' ? 'admin' : 'trainer')} className="hover:text-cyan-300">
                {user.role === 'admin' ? 'Admin' : 'Trainer'}
              </button>
            )}
          </nav>

          {!isAuthenticated ? (
            <button
              onClick={() => setView('landing')}
              className="rounded-full border border-cyan-400/60 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-200 hover:bg-cyan-500/20"
            >
              <span className="flex items-center gap-2"><LogIn className="h-4 w-4" /> Login</span>
            </button>
          ) : (
            <div className="flex items-center gap-3">
              {user ? (
                <div className="text-right">
                  <div className="text-sm font-semibold">{user.full_name}</div>
                  <div className="text-xs text-slate-400">Level {user.level}</div>
                </div>
              ) : null}
              <button onClick={handleLogout} className="rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-sm hover:border-slate-600">
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {!isAuthenticated && view === 'landing' && (
        <main className="mx-auto max-w-7xl px-6 py-10">
          <section className="grid gap-10 py-10 md:grid-cols-[1.1fr_0.9fr]">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300">
                <Sparkles className="h-3.5 w-3.5" /> AI-powered security simulations
              </div>
              <h1 className="max-w-xl text-4xl font-bold tracking-tight text-white md:text-6xl">
                Turn cyber hygiene training into a mission.
              </h1>
              <p className="mt-5 max-w-xl text-lg text-slate-300">
                Train teams and learners with realistic phishing drills, social engineering challenges, password hygiene checks, and guided incident response scenarios.
              </p>

              <div className="mt-8 flex flex-wrap gap-4">
                <button
                  onClick={() => setView('landing')}
                  className="rounded-xl bg-cyan-500 px-5 py-3 font-semibold text-slate-950 shadow-glow hover:bg-cyan-400"
                >
                  Start learning
                </button>
                <button
                  onClick={() => setAuthMode('register')}
                  className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 font-semibold text-white hover:border-slate-600"
                >
                  Create account
                </button>
              </div>

              <div className="mt-10 grid gap-4 md:grid-cols-3">
                <div className="card p-4">
                  <div className="mb-2 text-cyan-300"><ShieldCheck className="h-5 w-5" /></div>
                  <div className="font-semibold">AI personas</div>
                  <div className="mt-1 text-sm text-slate-400">Recruiter scam, phishing attacker, social engineer, and more.</div>
                </div>
                <div className="card p-4">
                  <div className="mb-2 text-cyan-300"><Target className="h-5 w-5" /></div>
                  <div className="font-semibold">Adaptive missions</div>
                  <div className="mt-1 text-sm text-slate-400">Challenges change with your demonstrated skill level.</div>
                </div>
                <div className="card p-4">
                  <div className="mb-2 text-cyan-300"><Trophy className="h-5 w-5" /></div>
                  <div className="font-semibold">XP & badges</div>
                  <div className="mt-1 text-sm text-slate-400">Earn levels, streaks, and achievements as you improve.</div>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-400">Welcome</div>
                  <div className="text-2xl font-semibold">Access platform</div>
                </div>
                <div className="rounded-full border border-cyan-400/30 bg-cyan-500/10 px-2.5 py-1 text-xs text-cyan-200">
                  {authMode === 'login' ? 'Login' : 'Register'}
                </div>
              </div>

              <form onSubmit={handleAuthSubmit} className="space-y-4">
                {authMode === 'register' && (
                  <>
                    <div>
                      <label className="mb-1 block text-sm text-slate-300">Full name</label>
                      <input
                        value={form.fullName}
                        onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                        className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-white outline-none ring-0 focus:border-cyan-400"
                        placeholder="Alex Morgan"
                      />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm text-slate-300">Username</label>
                      <input
                        value={form.username}
                        onChange={(e) => setForm({ ...form, username: e.target.value })}
                        className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-white outline-none focus:border-cyan-400"
                        placeholder="alex.m"
                      />
                    </div>
                  </>
                )}

                <div>
                  <label className="mb-1 block text-sm text-slate-300">Email</label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-white outline-none focus:border-cyan-400"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm text-slate-300">Password</label>
                  <input
                    type="password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-white outline-none focus:border-cyan-400"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-xl bg-cyan-500 px-4 py-3 font-semibold text-slate-950 hover:bg-cyan-400 disabled:opacity-60"
                >
                  {loading ? 'Processing...' : authMode === 'login' ? 'Sign in' : 'Create account'}
                </button>
              </form>

              <div className="mt-5 flex items-center justify-center gap-2 text-sm text-slate-400">
                <span>{authMode === 'login' ? 'Need an account?' : 'Already registered?'}</span>
                <button
                  type="button"
                  onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                  className="text-cyan-300 hover:underline"
                >
                  {authMode === 'login' ? 'Create one' : 'Log in'}
                </button>
              </div>
            </div>
          </section>
        </main>
      )}

      {isAuthenticated && view === 'dashboard' && (
        <main className="mx-auto max-w-7xl px-6 py-8">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <div className="text-sm text-cyan-300">Welcome back</div>
              <h2 className="text-3xl font-semibold text-white">{user?.full_name}</h2>
            </div>
            <button
              onClick={() => setView('missions')}
              className="rounded-xl bg-cyan-500 px-4 py-2.5 font-semibold text-slate-950 hover:bg-cyan-400"
            >
              Continue learning
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <div className="card p-4">
              <div className="text-sm text-slate-400">Total XP</div>
              <div className="mt-2 text-3xl font-bold text-cyan-300">{progress?.total_xp ?? user?.xp ?? 0}</div>
              <div className="mt-2 text-xs text-slate-400">Level {progress?.level ?? user?.level ?? 1}</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-slate-400">Missions</div>
              <div className="mt-2 text-3xl font-bold text-emerald-300">{progress?.missions_completed ?? 0}</div>
              <div className="mt-2 text-xs text-slate-400">Completed</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-slate-400">Accuracy</div>
              <div className="mt-2 text-3xl font-bold text-violet-300">{progress?.accuracy_rate ?? 0}%</div>
              <div className="mt-2 text-xs text-slate-400">Current streak: {progress?.streak ?? 0} days</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-slate-400">Badges</div>
              <div className="mt-2 text-3xl font-bold text-amber-300">{progress?.badges_count ?? 0}</div>
              <div className="mt-2 text-xs text-slate-400">Unlocked achievements</div>
            </div>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="card p-5">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2"><BarChart3 className="h-5 w-5 text-cyan-300" /> Skill progress</div>
                <span className="badge">Updated today</span>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={skillChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip />
                    <Bar dataKey="value" fill="#22d3ee" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card p-5">
              <div className="mb-4 flex items-center gap-2"><Award className="h-5 w-5 text-amber-300" /> Recent badges</div>
              <div className="space-y-3">
                {(badges?.earned || ['First Mission Complete', 'Phishing Spotter', 'Password Guardian']).map((badge: string) => (
                  <div key={badge} className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-950/60 p-3">
                    <div className="flex items-center gap-3">
                      <div className="rounded-full bg-amber-500/10 p-2 text-amber-300"><Trophy className="h-4 w-4" /></div>
                      <div>
                        <div className="font-medium text-white">{badge}</div>
                        <div className="text-xs text-slate-400">Earned in the current learning cycle</div>
                      </div>
                    </div>
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-8 grid gap-6 md:grid-cols-2">
            <div className="card p-5">
              <div className="mb-3 flex items-center gap-2"><Swords className="h-5 w-5 text-cyan-300" /> Recommended next mission</div>
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-4">
                <div className="text-sm text-cyan-200">Mission focus</div>
                <div className="mt-2 text-xl font-semibold text-white">Phishing Inbox Triage</div>
                <p className="mt-2 text-sm text-slate-300">Identify fake urgency, mismatched domains, and unsafe actions before replying.</p>
                <button onClick={() => startSimulation(challenges[0])} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950">
                  Launch mission <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="card p-5">
              <div className="mb-3 flex items-center gap-2"><Flame className="h-5 w-5 text-amber-300" /> Learning streak</div>
              <div className="rounded-2xl border border-slate-700 bg-slate-950/60 p-4">
                <div className="text-3xl font-bold text-white">{progress?.streak ?? 0}<span className="text-base text-slate-400"> days</span></div>
                <p className="mt-2 text-sm text-slate-300">Keep your streak alive by completing one challenge today.</p>
              </div>
            </div>
          </div>
        </main>
      )}

      {isAuthenticated && view === 'missions' && (
        <main className="mx-auto max-w-7xl px-6 py-8">
          <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-sm text-cyan-300">Mission selection</div>
              <h2 className="text-3xl font-semibold text-white">Choose your challenge</h2>
            </div>
            <div className="flex flex-wrap gap-3">
              <select value={missionFilter} onChange={(e) => setMissionFilter(e.target.value)} className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white">
                <option value="all">All topics</option>
                <option value="phishing">Phishing</option>
                <option value="social_engineering">Social engineering</option>
                <option value="password_security">Password security</option>
                <option value="incident_response">Incident response</option>
              </select>
              <select value={missionDifficulty} onChange={(e) => setMissionDifficulty(e.target.value)} className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white">
                <option value="all">All difficulty</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {filteredChallenges.map((challenge) => (
              <div key={challenge.id} className="card p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="badge">{challenge.category}</div>
                    <h3 className="mt-3 text-xl font-semibold text-white">{challenge.title}</h3>
                  </div>
                  <div className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-cyan-200">{challenge.difficulty}</div>
                </div>
                <p className="mt-3 text-sm text-slate-300">{challenge.description}</p>
                <div className="mt-4 space-y-2 text-sm text-slate-400">
                  <div className="flex items-center justify-between"><span>XP</span><span className="text-cyan-300">{challenge.xp_reward}</span></div>
                  <div className="flex items-center justify-between"><span>Duration</span><span>12 min</span></div>
                  <div className="flex items-center justify-between"><span>AI persona</span><span>Security Coach</span></div>
                </div>
                <button
                  onClick={() => startSimulation(challenge)}
                  className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-500 px-3 py-2.5 font-semibold text-slate-950 hover:bg-cyan-400"
                >
                  <Play className="h-4 w-4" /> Launch mission
                </button>
              </div>
            ))}
          </div>
        </main>
      )}

      {isAuthenticated && view === 'simulation' && selectedChallenge && (
        <main className="mx-auto max-w-6xl px-6 py-8">
          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="card p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm text-cyan-300">Simulation arena</div>
                  <h2 className="text-2xl font-semibold text-white">{selectedChallenge.title}</h2>
                </div>
                <div className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">Live</div>
              </div>

              <div className="mt-5 rounded-2xl border border-slate-700 bg-slate-950/70 p-4">
                <div className="mb-3 flex items-center justify-between text-sm text-slate-300">
                  <span>Scenario</span>
                  <span>{selectedChallenge.difficulty}</span>
                </div>
                <p className="text-slate-200">{selectedChallenge.description}</p>
                <div className="mt-4 grid gap-2 text-sm text-slate-300">
                  {selectedChallenge.learning_objectives.map((objective) => (
                    <div key={objective} className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> {objective}</div>
                  ))}
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-slate-700 bg-slate-950/70 p-4">
                <div className="mb-2 text-sm text-slate-400">Evidence / artifacts</div>
                <pre className="whitespace-pre-wrap text-sm text-slate-200">{JSON.stringify(selectedChallenge.scenario_content, null, 2)}</pre>
              </div>

              <div className="mt-6">
                <div className="mb-2 text-sm text-slate-400">Identify warning signs</div>
                <div className="flex flex-wrap gap-2">
                  {indicatorOptions.map((indicator) => (
                    <button
                      key={indicator}
                      onClick={() => setSelectedIndicators((current) =>
                        current.includes(indicator) ? current.filter((item) => item !== indicator) : [...current, indicator],
                      )}
                      className={`rounded-full border px-3 py-1.5 text-sm ${
                        selectedIndicators.includes(indicator)
                          ? 'border-cyan-400 bg-cyan-500/10 text-cyan-200'
                          : 'border-slate-700 bg-slate-900 text-slate-300'
                      }`}
                    >
                      {indicator}
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <label className="mb-2 block text-sm text-slate-400">Reasoning</label>
                <textarea
                  value={reasoning}
                  onChange={(e) => setReasoning(e.target.value)}
                  rows={4}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-white outline-none focus:border-cyan-400"
                  placeholder="Explain what made the message suspicious and what action you would take."
                />
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                <button onClick={submitDecision} className="rounded-xl bg-cyan-500 px-4 py-2.5 font-semibold text-slate-950 hover:bg-cyan-400">
                  Submit decision
                </button>
                <button onClick={endSimulation} className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 font-semibold text-white hover:border-slate-600">
                  End simulation
                </button>
              </div>
            </div>

            <aside className="space-y-6">
              <div className="card p-5">
                <div className="mb-3 flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-amber-300" /> Mission status</div>
                <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-3 text-sm text-slate-300">
                  Session ID: {sessionId ?? 'pending'}
                </div>
                {decisionResult && (
                  <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                    <div className="font-semibold">Score: {decisionResult.score}</div>
                    <div className="mt-1">XP earned: {decisionResult.xp}</div>
                    <div className="mt-2">{decisionResult.feedback}</div>
                  </div>
                )}
              </div>

              <div className="card p-5">
                <div className="mb-3 flex items-center gap-2"><Lock className="h-5 w-5 text-violet-300" /> Rule reminders</div>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Verify through official channels before responding.</li>
                  <li>• Never share authentication codes or passwords.</li>
                  <li>• Report suspicious messages to the right team.</li>
                </ul>
              </div>
            </aside>
          </div>
        </main>
      )}

      {isAuthenticated && (user?.role === 'admin' || user?.role === 'trainer') && view === (user.role === 'admin' ? 'admin' : 'trainer') && (
        <main className="mx-auto max-w-7xl px-6 py-8">
          <div className="mb-6">
            <div className="text-sm text-cyan-300">{user.role === 'admin' ? 'Administrator dashboard' : 'Trainer dashboard'}</div>
            <h2 className="text-3xl font-semibold text-white">Operational overview</h2>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="card p-5">
              <div className="text-sm text-slate-400">Enrolled learners</div>
              <div className="mt-2 text-3xl font-bold text-cyan-300">{user.role === 'admin' ? 42 : 18}</div>
            </div>
            <div className="card p-5">
              <div className="text-sm text-slate-400">Completion rate</div>
              <div className="mt-2 text-3xl font-bold text-emerald-300">82%</div>
            </div>
            <div className="card p-5">
              <div className="text-sm text-slate-400">Avg. score</div>
              <div className="mt-2 text-3xl font-bold text-violet-300">86%</div>
            </div>
          </div>

          <div className="mt-8 grid gap-6 md:grid-cols-2">
            <div className="card p-5">
              <div className="mb-3 flex items-center gap-2"><Users className="h-5 w-5 text-cyan-300" /> Cohorts</div>
              <div className="space-y-3">
                {['Security Basics', 'Ransomware Response', 'Executive Awareness'].map((cohort) => (
                  <div key={cohort} className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-950/60 p-3">
                    <span>{cohort}</span>
                    <span className="badge">Live</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="card p-5">
              <div className="mb-3 flex items-center gap-2"><BarChart3 className="h-5 w-5 text-amber-300" /> High-priority gaps</div>
              <ul className="space-y-3 text-sm text-slate-300">
                <li>• Password reuse across personal accounts</li>
                <li>• Suspicious attachment handling</li>
                <li>• Verification of third-party vendor requests</li>
              </ul>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
