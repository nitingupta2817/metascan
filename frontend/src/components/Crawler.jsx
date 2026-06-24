import { useState } from "react"
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
}