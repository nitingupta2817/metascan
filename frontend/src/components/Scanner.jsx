import { useState } from "react"
import axios from "axios"
import { Search, AlertCircle, CheckCircle, XCircle, ChevronDown, ChevronUp, Download } from "lucide-react"

const API = "http://127.0.0.1:8000"

function getScore(r) {
  if (r.error) return 0
  return Math.max(0, 100
    - ((!r.title || r.title === "No title found") ? 25 : r.title_len > 60 ? 10 : 0)
    - ((!r.description || r.description === "No description found") ? 22 : r.desc_len > 160 ? 10 : 0)
    - (r.h1_texts?.length === 0 ? 20 : r.h1_texts?.length > 1 ? 10 : 0)
    - (r.imgs_no_alt > 0 ? 15 : 0)
    - (r.is_noindex ? 12 : 0)
    - (r.canonical_mismatch ? 8 : 0)
  )
}

function getIssues(r) {
  if (r.error) return ["fetch_error"]
  const issues = []
  if (!r.title || r.title === "No title found") issues.push("no_title")
  else if (r.title_len > 60) issues.push("title_long")
  if (!r.description || r.description === "No description found") issues.push("no_desc")
  else if (r.desc_len > 160) issues.push("desc_long")
  if (r.h1_texts?.length === 0) issues.push("no_h1")
  else if (r.h1_texts?.length > 1) issues.push("multi_h1")
  if (r.imgs_no_alt > 0) issues.push("img_no_alt")
  if (r.is_noindex) issues.push("noindex")
  if (r.canonical_mismatch) issues.push("canonical_mismatch")
  return issues
}

const ISSUE_LABELS = {
  fetch_error: { label: "Fetch Error", color: "text-red-400", bg: "bg-red-400/10 border-red-400/30" },
  no_title: { label: "No Title", color: "text-red-400", bg: "bg-red-400/10 border-red-400/30" },
  title_long: { label: "Title Too Long", color: "text-yellow-400", bg: "bg-yellow-400/10 border-yellow-400/30" },
  no_desc: { label: "No Description", color: "text-red-400", bg: "bg-red-400/10 border-red-400/30" },
  desc_long: { label: "Desc Too Long", color: "text-yellow-400", bg: "bg-yellow-400/10 border-yellow-400/30" },
  no_h1: { label: "No H1", color: "text-red-400", bg: "bg-red-400/10 border-red-400/30" },
  multi_h1: { label: "Multiple H1", color: "text-yellow-400", bg: "bg-yellow-400/10 border-yellow-400/30" },
  img_no_alt: { label: "Images Missing Alt", color: "text-orange-400", bg: "bg-orange-400/10 border-orange-400/30" },
  noindex: { label: "Noindex", color: "text-gray-400", bg: "bg-gray-400/10 border-gray-400/30" },
  canonical_mismatch: { label: "Canonical Mismatch", color: "text-yellow-400", bg: "bg-yellow-400/10 border-yellow-400/30" },
}

export default function Scanner() {
  const [urls, setUrls] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [activeFilter, setActiveFilter] = useState("all")

  const handleScan = async () => {
    const urlList = urls.split("\n").map(u => u.trim()).filter(Boolean)
    if (!urlList.length) return setError("Please enter at least one URL")
    setError("")
    setLoading(true)
    setResults([])
    setActiveFilter("all")
    try {
      const res = await axios.post(`${API}/scan`, { urls: urlList })
      setResults(res.data.results)
    } catch {
      setError("Failed to connect to backend. Make sure FastAPI is running on port 8000.")
    }
    setLoading(false)
  }

  const resultsWithMeta = results.map(r => ({
    ...r,
    _score: getScore(r),
    _issues: getIssues(r),
  }))

  const filters = [
    { key: "all", label: "All", count: resultsWithMeta.length },
    { key: "pass", label: "✓ Pass", count: resultsWithMeta.filter(r => r._issues.length === 0).length },
    { key: "warning", label: "⚠ Warning", count: resultsWithMeta.filter(r => r._issues.length > 0 && r._score >= 50).length },
    { key: "failed", label: "✗ Failed", count: resultsWithMeta.filter(r => r._score < 50 || r.error).length },
  ]

  const filtered = resultsWithMeta.filter(r => {
    if (activeFilter === "all") return true
    if (activeFilter === "pass") return r._issues.length === 0
    if (activeFilter === "warning") return r._issues.length > 0 && r._score >= 50
    if (activeFilter === "failed") return r._score < 50 || r.error
    return true
  })

  // Issue summary counts
  const issueSummary = Object.keys(ISSUE_LABELS).map(key => ({
    key,
    ...ISSUE_LABELS[key],
    count: resultsWithMeta.filter(r => r._issues.includes(key)).length,
  })).filter(i => i.count > 0)

  const exportCSV = () => {
    const rows = resultsWithMeta.map(r => ({
      URL: r.url,
      Score: r._score,
      Issues: r._issues.join(", "),
      Title: r.title,
      "Title Length": r.title_len,
      Description: r.description,
      "Desc Length": r.desc_len,
      H1: r.h1_texts?.join(" | "),
      H2: r.h2_texts?.join(" | "),
      Canonical: r.canonical,
      "OG Title": r.og_title,
      "Images Total": r.imgs_total,
      "Images No Alt": r.imgs_no_alt,
      Noindex: r.is_noindex ? "Yes" : "No",
      Error: r.error,
    }))
    const csv = [Object.keys(rows[0]).join(","), ...rows.map(r => Object.values(r).map(v => `"${v}"`).join(","))].join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = "metascan_results.csv"
    a.click()
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">URL Scanner</h1>
        <p className="text-gray-400">Analyse SEO metadata for one or more URLs</p>
      </div>

      {/* Input */}
      <div className="bg-bg2 border border-border1 rounded-xl p-6 mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 block">Target URLs</label>
        <textarea
          value={urls}
          onChange={e => setUrls(e.target.value)}
          placeholder={"https://example.com\nhttps://another-site.com"}
          rows={4}
          className="w-full bg-bg3 border border-border1 rounded-lg px-4 py-3 text-sm text-gray-200 font-mono placeholder-gray-600 focus:outline-none focus:border-accent resize-none"
        />
        <div className="flex items-center justify-between mt-4">
          <span className="text-xs text-gray-600">One URL per line</span>
          <button onClick={handleScan} disabled={loading}
            className="flex items-center gap-2 bg-accent hover:bg-accent2 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition-all">
            <Search size={15} />{loading ? "Scanning..." : "Scan URLs"}
          </button>
        </div>
        {error && <div className="mt-3 flex items-center gap-2 text-red-400 text-sm"><AlertCircle size={15} />{error}</div>}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm">Scanning URLs...</p>
          </div>
        </div>
      )}

      {resultsWithMeta.length > 0 && (
        <div>
          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total", value: results.length, color: "text-white" },
              { label: "Success", value: results.filter(r => !r.error).length, color: "text-green-400" },
              { label: "Errors", value: results.filter(r => r.error).length, color: "text-red-400" },
              { label: "Avg Score", value: Math.round(resultsWithMeta.reduce((a, r) => a + r._score, 0) / resultsWithMeta.length), color: "text-accent" },
            ].map(s => (
              <div key={s.label} className="bg-bg2 border border-border1 rounded-xl p-4">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{s.label}</div>
                <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
              </div>
            ))}
          </div>

          {/* Issue Summary Table */}
          {issueSummary.length > 0 && (
            <div className="bg-bg2 border border-border1 rounded-xl p-5 mb-6">
              <h3 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Issue Summary</h3>
              <div className="space-y-3">
                {issueSummary.map(({ key, label, color, count }) => (
                  <div key={key} className="flex items-center gap-4">
                    <span className={`text-xs font-semibold w-40 ${color}`}>{label}</span>
                    <div className="flex-1 bg-border1 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-accent transition-all"
                        style={{ width: `${(count / results.length) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-mono text-gray-300 w-16 text-right">{count} / {results.length}</span>
                    <button
                      onClick={() => setActiveFilter(key)}
                      className="text-xs text-accent hover:underline w-16 text-right"
                    >
                      Filter
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Scorecard + Filter */}
          <div className="bg-bg2 border border-border1 rounded-xl p-5 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">SEO Scorecard</h3>
              <button onClick={exportCSV}
                className="flex items-center gap-2 text-xs text-accent border border-accent/30 px-3 py-1.5 rounded-lg hover:bg-accent/10 transition-all">
                <Download size={13} /> Export CSV
              </button>
            </div>

            {/* Filter Pills */}
            <div className="flex items-center gap-2 mb-4 flex-wrap">
              {filters.map(f => (
                <button
                  key={f.key}
                  onClick={() => setActiveFilter(f.key)}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                    activeFilter === f.key
                      ? "bg-accent text-white border-accent"
                      : "bg-bg3 text-gray-400 border-border1 hover:border-accent/50"
                  }`}
                >
                  {f.label}
                  <span className={`px-1.5 py-0.5 rounded text-xs ${activeFilter === f.key ? "bg-white/20" : "bg-border1"}`}>
                    {f.count}
                  </span>
                </button>
              ))}
              {activeFilter !== "all" && (
                <button onClick={() => setActiveFilter("all")}
                  className="text-xs text-gray-500 hover:text-white transition-colors ml-2">
                  Clear filter ✕
                </button>
              )}
            </div>

            {/* Scorecard Rows */}
            <div className="space-y-2">
              {filtered.map((r, i) => (
                <ScorecardRow key={i} result={r} />
              ))}
              {filtered.length === 0 && (
                <div className="text-center py-8 text-gray-500 text-sm">No URLs match this filter</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ScorecardRow({ result: r }) {
  const [open, setOpen] = useState(false)
  const score = r._score
  const issues = r._issues
  const scoreColor = score >= 80 ? "text-green-400" : score >= 50 ? "text-yellow-400" : "text-red-400"
  const borderColor = score >= 80 ? "border-l-green-400" : score >= 50 ? "border-l-yellow-400" : "border-l-red-400"

  return (
    <div className={`bg-bg3 border border-border1 border-l-2 ${borderColor} rounded-lg overflow-hidden`}>
      {/* Row Header */}
      <div className="flex items-center gap-4 p-4 cursor-pointer hover:bg-bg2 transition-colors"
        onClick={() => setOpen(!open)}>
        {r.error ? <XCircle size={16} className="text-red-400 flex-shrink-0" />
          : score >= 80 ? <CheckCircle size={16} className="text-green-400 flex-shrink-0" />
          : <AlertCircle size={16} className="text-yellow-400 flex-shrink-0" />}

        <span className="text-sm font-mono text-gray-300 flex-1 truncate">{r.url}</span>

        {/* Issue chips */}
        <div className="hidden md:flex items-center gap-1 flex-shrink-0">
          {issues.slice(0, 3).map(issue => (
            <span key={issue} className={`text-xs px-2 py-0.5 rounded border ${ISSUE_LABELS[issue]?.bg || "bg-gray-400/10 border-gray-400/30"} ${ISSUE_LABELS[issue]?.color || "text-gray-400"}`}>
              {ISSUE_LABELS[issue]?.label || issue}
            </span>
          ))}
          {issues.length > 3 && (
            <span className="text-xs text-gray-500">+{issues.length - 3} more</span>
          )}
        </div>

        <div className="flex items-center gap-3 flex-shrink-0 ml-2">
          <div className="text-right">
            <div className={`text-xl font-bold ${scoreColor}`}>{score}</div>
            <div className="text-xs text-gray-600">score</div>
          </div>
          {open ? <ChevronUp size={15} className="text-gray-500" /> : <ChevronDown size={15} className="text-gray-500" />}
        </div>
      </div>

      {/* Expanded Detail */}
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
              <InfoRow label="Canonical" value={r.canonical || "Not set"} warn={r.canonical_mismatch} />
              <InfoRow label="Robots Meta" value={r.robots_content || "Not set"} />
              <InfoRow label="OG Title" value={r.og_title || "Not set"} />
              <InfoRow label="Noindex" value={r.is_noindex ? "Yes — blocked from Google" : "No — indexable"} warn={r.is_noindex} />

              {/* Images with alt text detail */}
              {r.imgs_total > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Images</span>
                    <span className={`text-xs ${r.imgs_no_alt > 0 ? "text-orange-400" : "text-green-400"}`}>
                      {r.imgs_total} total · {r.imgs_with_alt} with alt · {r.imgs_no_alt} missing alt
                    </span>
                  </div>
                  {r.img_data?.filter(img => !img.has_alt).slice(0, 5).map((img, i) => (
                    <div key={i} className="flex items-center gap-3 bg-bg2 rounded-lg px-3 py-2 mb-1">
                      <span className="text-orange-400 text-xs flex-shrink-0">⚠ No Alt</span>
                      <span className="text-xs font-mono text-gray-400 truncate">{img.src}</span>
                    </div>
                  ))}
                  {r.imgs_no_alt > 5 && (
                    <div className="text-xs text-gray-500 mt-1">+ {r.imgs_no_alt - 5} more images missing alt text</div>
                  )}
                </div>
              )}
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
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider w-32 flex-shrink-0 mt-0.5">{label}</span>
      <span className={`text-sm font-mono ${warn ? "text-yellow-400" : "text-gray-400"}`}>{value}</span>
    </div>
  )
}