import os

files = {}

files["frontend/index.html"] = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MetaScan</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''

files["frontend/tailwind.config.js"] = '''/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg1: '#0a0b0e',
        bg2: '#0d0f16',
        bg3: '#0f1117',
        border1: '#1e2130',
        border2: '#2a3050',
        accent: '#3b82f6',
        accent2: '#2563eb',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}'''

files["frontend/src/index.css"] = '''@tailwind base;
@tailwind components;
@tailwind utilities;

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background-color: #0a0b0e;
  color: #c9cdd6;
  font-family: Inter, sans-serif;
  min-height: 100vh;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0f16; }
::-webkit-scrollbar-thumb { background: #1e2130; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3b82f6; }'''

files["frontend/src/main.jsx"] = '''import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"
import "./index.css"
import App from "./App.jsx"

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
)'''

files["frontend/src/App.jsx"] = '''import { Routes, Route } from "react-router-dom"
import Navbar from "./components/Navbar"
import Scanner from "./components/Scanner"
import Crawler from "./components/Crawler"

export default function App() {
  return (
    <div className="min-h-screen bg-bg1">
      <Navbar />
      <main className="max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Scanner />} />
          <Route path="/crawler" element={<Crawler />} />
        </Routes>
      </main>
    </div>
  )
}'''

files["frontend/src/components/Navbar.jsx"] = '''import { Link, useLocation } from "react-router-dom"
import { Search, Globe } from "lucide-react"

export default function Navbar() {
  const location = useLocation()
  return (
    <nav className="border-b border-border1 bg-bg2 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
            <Search size={18} className="text-white" />
          </div>
          <div>
            <div className="text-white font-bold text-lg leading-none">MetaScan</div>
            <div className="text-xs text-gray-500 leading-none mt-0.5">SEO Inspector</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/" className={"flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all " + (location.pathname === "/" ? "bg-accent text-white" : "text-gray-400 hover:text-white hover:bg-border1")}>
            <Search size={15} />URL Scanner
          </Link>
          <Link to="/crawler" className={"flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all " + (location.pathname === "/crawler" ? "bg-accent text-white" : "text-gray-400 hover:text-white hover:bg-border1")}>
            <Globe size={15} />Site Crawler
          </Link>
        </div>
      </div>
    </nav>
  )
}'''

files["frontend/src/components/Scanner.jsx"] = '''import { useState } from "react"
import axios from "axios"
import { Search, AlertCircle, CheckCircle, XCircle, ChevronDown, ChevronUp } from "lucide-react"

const API = "http://127.0.0.1:8000"

export default function Scanner() {
  const [urls, setUrls] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleScan = async () => {
    const urlList = urls.split("\\n").map(u => u.trim()).filter(Boolean)
    if (!urlList.length) return setError("Please enter at least one URL")
    setError("")
    setLoading(true)
    setResults([])
    try {
      const res = await axios.post(`${API}/scan`, { urls: urlList })
      setResults(res.data.results)
    } catch {
      setError("Failed to connect to backend. Make sure FastAPI is running on port 8000.")
    }
    setLoading(false)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">URL Scanner</h1>
        <p className="text-gray-400">Analyse SEO metadata for one or more URLs</p>
      </div>

      <div className="bg-bg2 border border-border1 rounded-xl p-6 mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 block">Target URLs</label>
        <textarea
          value={urls}
          onChange={e => setUrls(e.target.value)}
          placeholder={"https://example.com\\nhttps://another-site.com"}
          rows={4}
          className="w-full bg-bg3 border border-border1 rounded-lg px-4 py-3 text-sm text-gray-200 font-mono placeholder-gray-600 focus:outline-none focus:border-accent resize-none"
        />
        <div className="flex items-center justify-between mt-4">
          <span className="text-xs text-gray-600">One URL per line</span>
          <button onClick={handleScan} disabled={loading} className="flex items-center gap-2 bg-accent hover:bg-accent2 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition-all">
            <Search size={15} />{loading ? "Scanning..." : "Scan URLs"}
          </button>
        </div>
        {error && <div className="mt-3 flex items-center gap-2 text-red-400 text-sm"><AlertCircle size={15} />{error}</div>}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm">Scanning URLs...</p>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total", value: results.length, color: "text-white" },
              { label: "Success", value: results.filter(r => !r.error).length, color: "text-green-400" },
              { label: "Errors", value: results.filter(r => r.error).length, color: "text-red-400" },
              { label: "Perfect", value: results.filter(r => !r.error && r.title_len <= 60 && r.desc_len <= 160).length, color: "text-accent" },
            ].map(s => (
              <div key={s.label} className="bg-bg2 border border-border1 rounded-xl p-4">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{s.label}</div>
                <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
              </div>
            ))}
          </div>
          {results.map((r, i) => <ResultCard key={i} result={r} />)}
        </div>
      )}
    </div>
  )
}

function ResultCard({ result: r }) {
  const [open, setOpen] = useState(false)
  const score = r.error ? 0 : Math.max(0, 100
    - ((!r.title || r.title === "No title found") ? 25 : r.title_len > 60 ? 10 : 0)
    - ((!r.description || r.description === "No description found") ? 22 : r.desc_len > 160 ? 10 : 0)
    - (r.h1_texts?.length === 0 ? 20 : r.h1_texts?.length > 1 ? 10 : 0)
    - (r.imgs_no_alt > 0 ? 15 : 0))
  const scoreColor = score >= 80 ? "text-green-400" : score >= 50 ? "text-yellow-400" : "text-red-400"
  const borderColor = score >= 80 ? "border-green-400/30" : score >= 50 ? "border-yellow-400/30" : "border-red-400/30"

  return (
    <div className={`bg-bg2 border ${borderColor} rounded-xl mb-4 overflow-hidden`}>
      <div className="flex items-center justify-between p-5 cursor-pointer hover:bg-bg3 transition-colors" onClick={() => setOpen(!open)}>
        <div className="flex items-center gap-4 min-w-0">
          {r.error ? <XCircle size={18} className="text-red-400 flex-shrink-0" />
            : score >= 80 ? <CheckCircle size={18} className="text-green-400 flex-shrink-0" />
            : <AlertCircle size={18} className="text-yellow-400 flex-shrink-0" />}
          <span className="text-sm text-gray-300 truncate font-mono">{r.url}</span>
        </div>
        <div className="flex items-center gap-4 flex-shrink-0">
          <div className="text-right">
            <div className={`text-2xl font-bold ${scoreColor}`}>{score}</div>
            <div className="text-xs text-gray-600">score</div>
          </div>
          {open ? <ChevronUp size={16} className="text-gray-500" /> : <ChevronDown size={16} className="text-gray-500" />}
        </div>
      </div>
      {open && (
        <div className="border-t border-border1 p-5 space-y-4">
          {r.error ? (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 text-red-300 text-sm">{r.error}</div>
          ) : (
            <>
              <Field label="Meta Title" value={r.title} length={r.title_len} limit={60} />
              <Field label="Meta Description" value={r.description} length={r.desc_len} limit={160} />
              <HeadingField label="H1 Tags" items={r.h1_texts} ideal={1} />
              <HeadingField label="H2 Tags" items={r.h2_texts} />
              <InfoRow label="Canonical" value={r.canonical || "Not set"} />
              <InfoRow label="Robots Meta" value={r.robots_content || "Not set"} />
              <InfoRow label="OG Title" value={r.og_title || "Not set"} />
              <InfoRow label="Images" value={`${r.imgs_total} total · ${r.imgs_with_alt} with alt · ${r.imgs_no_alt} missing alt`} warn={r.imgs_no_alt > 0} />
            </>
          )}
        </div>
      )}
    </div>
  )
}

function Field({ label, value, length, limit }) {
  const missing = !value || value === "No title found" || value === "No description found"
  const tooLong = !missing && length > limit
  const color = missing ? "text-red-400" : tooLong ? "text-yellow-400" : "text-green-400"
  const status = missing ? "Missing" : tooLong ? `Too long (${length}/${limit})` : `Good (${length}/${limit})`
  return (
    <div>
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</span>
        <span className={`text-xs ${color}`}>{status}</span>
      </div>
      <div className="text-sm text-gray-300 bg-bg3 rounded-lg px-3 py-2 font-mono">
        {missing ? <span className="text-red-400 italic">Not found</span> : value}
      </div>
    </div>
  )
}

function HeadingField({ label, items, ideal }) {
  const count = items?.length || 0
  const color = count === 0 ? "text-red-400" : ideal && count > ideal ? "text-yellow-400" : "text-green-400"
  const status = count === 0 ? "Missing" : ideal && count > ideal ? `${count} found (should be ${ideal})` : `${count} found`
  return (
    <div>
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</span>
        <span className={`text-xs ${color}`}>{status}</span>
      </div>
      {items?.length > 0 && (
        <div className="space-y-1">
          {items.slice(0, 3).map((h, i) => (
            <div key={i} className="text-sm text-gray-300 bg-bg3 rounded-lg px-3 py-2 font-mono truncate">{h}</div>
          ))}
        </div>
      )}
    </div>
  )
}

function InfoRow({ label, value, warn }) {
  return (
    <div className="flex items-start gap-4">
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider w-28 flex-shrink-0 mt-0.5">{label}</span>
      <span className={`text-sm font-mono ${warn ? "text-yellow-400" : "text-gray-400"}`}>{value}</span>
    </div>
  )
}'''

files["frontend/src/components/Crawler.jsx"] = '''import { useState } from "react"
import axios from "axios"
import { Globe, AlertCircle, CheckCircle, XCircle } from "lucide-react"

const API = "http://127.0.0.1:8000"

export default function Crawler() {
  const [rootUrl, setRootUrl] = useState("")
  const [maxPages, setMaxPages] = useState(50)
  const [maxDepth, setMaxDepth] = useState(3)
  const [delayMs, setDelayMs] = useState(200)
  const [sameDomain, setSameDomain] = useState(true)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleCrawl = async () => {
    if (!rootUrl.trim()) return setError("Please enter a URL")
    setError("")
    setLoading(true)
    setResults([])
    try {
      const res = await axios.post(`${API}/crawl`, {
        root_url: rootUrl,
        max_pages: maxPages,
        max_depth: maxDepth,
        delay_ms: delayMs,
        same_domain_only: sameDomain,
      })
      setResults(res.data.results)
    } catch {
      setError("Failed to connect to backend.")
    }
    setLoading(false)
  }

  const issues = {
    no_title: results.filter(r => r.issues?.includes("no_title")).length,
    no_desc: results.filter(r => r.issues?.includes("no_desc")).length,
    no_h1: results.filter(r => r.issues?.includes("no_h1")).length,
    noindex: results.filter(r => r.issues?.includes("noindex")).length,
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Site Crawler</h1>
        <p className="text-gray-400">Crawl an entire website and audit every page</p>
      </div>

      <div className="bg-bg2 border border-border1 rounded-xl p-6 mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 block">Root URL</label>
        <input
          value={rootUrl}
          onChange={e => setRootUrl(e.target.value)}
          placeholder="https://example.com"
          className="w-full bg-bg3 border border-border1 rounded-lg px-4 py-3 text-sm text-gray-200 font-mono placeholder-gray-600 focus:outline-none focus:border-accent mb-4"
        />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {[
            { label: "Max Pages", value: maxPages, set: setMaxPages, min: 5, max: 500 },
            { label: "Max Depth", value: maxDepth, set: setMaxDepth, min: 1, max: 10 },
            { label: "Delay ms", value: delayMs, set: setDelayMs, min: 0, max: 2000 },
          ].map(({ label, value, set, min, max }) => (
            <div key={label}>
              <label className="text-xs text-gray-500 mb-1 block">{label}</label>
              <input type="number" value={value} onChange={e => set(Number(e.target.value))} min={min} max={max}
                className="w-full bg-bg3 border border-border1 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-accent" />
            </div>
          ))}
          <div className="flex flex-col justify-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={sameDomain} onChange={e => setSameDomain(e.target.checked)} className="w-4 h-4 accent-accent" />
              <span className="text-sm text-gray-400">Same domain only</span>
            </label>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-600">Be respectful with delay settings</span>
          <button onClick={handleCrawl} disabled={loading} className="flex items-center gap-2 bg-accent hover:bg-accent2 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition-all">
            <Globe size={15} />{loading ? "Crawling..." : "Start Crawl"}
          </button>
        </div>
        {error && <div className="mt-3 flex items-center gap-2 text-red-400 text-sm"><AlertCircle size={15} />{error}</div>}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm">Crawling website — this may take a while...</p>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              { label: "Pages Crawled", value: results.length, color: "text-white" },
              { label: "Avg Score", value: Math.round(results.reduce((a, r) => a + r.score, 0) / results.length), color: "text-accent" },
              { label: "With Issues", value: results.filter(r => r.issues?.length > 0).length, color: "text-yellow-400" },
              { label: "Errors", value: results.filter(r => r.error).length, color: "text-red-400" },
            ].map(s => (
              <div key={s.label} className="bg-bg2 border border-border1 rounded-xl p-4">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{s.label}</div>
                <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
              </div>
            ))}
          </div>

          {Object.values(issues).some(v => v > 0) && (
            <div className="bg-bg2 border border-border1 rounded-xl p-5 mb-6">
              <h3 className="text-sm font-semibold text-white mb-4">Issue Breakdown</h3>
              <div className="space-y-3">
                {[
                  { label: "Missing Meta Title", count: issues.no_title, color: "bg-red-400" },
                  { label: "Missing Meta Description", count: issues.no_desc, color: "bg-orange-400" },
                  { label: "Missing H1 Tag", count: issues.no_h1, color: "bg-yellow-400" },
                  { label: "Noindex Pages", count: issues.noindex, color: "bg-gray-400" },
                ].filter(i => i.count > 0).map(({ label, count, color }) => (
                  <div key={label} className="flex items-center gap-3">
                    <span className="text-sm text-gray-400 w-48">{label}</span>
                    <div className="flex-1 bg-border1 rounded-full h-2">
                      <div className={`${color} h-2 rounded-full`} style={{ width: `${(count / results.length) * 100}%` }} />
                    </div>
                    <span className="text-sm font-mono text-gray-300 w-12 text-right">{count}/{results.length}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-2">
            {results.map((r, i) => (
              <div key={i} className="bg-bg2 border border-border1 rounded-lg p-4 flex items-center gap-4">
                {r.error ? <XCircle size={16} className="text-red-400 flex-shrink-0" />
                  : r.score >= 80 ? <CheckCircle size={16} className="text-green-400 flex-shrink-0" />
                  : <AlertCircle size={16} className="text-yellow-400 flex-shrink-0" />}
                <span className="text-sm font-mono text-gray-300 flex-1 truncate">{r.url}</span>
                <div className="flex items-center gap-3 flex-shrink-0">
                  {r.issues?.slice(0, 3).map(issue => (
                    <span key={issue} className="text-xs bg-border1 text-gray-400 px-2 py-0.5 rounded">{issue.replace("_", " ")}</span>
                  ))}
                  <span className={`text-sm font-bold w-8 text-right ${r.score >= 80 ? "text-green-400" : r.score >= 50 ? "text-yellow-400" : "text-red-400"}`}>{r.score}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}'''

# ── Write all files ────────────────────────────────────────────────────────────
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Created: {path}")

print("\n🎉 All files created successfully!")
print("Now run: cd frontend && npm run dev")