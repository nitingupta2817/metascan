import { Routes, Route } from "react-router-dom"
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
}