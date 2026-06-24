import { Link, useLocation } from "react-router-dom"
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
}