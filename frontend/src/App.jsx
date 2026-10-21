import React, { useEffect, useState } from "react";
import { Home as HomeIcon, Search, PlusCircle, Trophy, Leaf } from "lucide-react";
import Home from "./pages/Home.jsx";
import BrowseItems from "./pages/BrowseItems.jsx";
import CreateListing from "./pages/CreateListing.jsx";
import Leaderboard from "./pages/Leaderboard.jsx";
import { getItems, getLeaderboard, getChallenge, createListing, claimItem } from "./services/api.js";

export default function App() {
  const [page, setPage] = useState("home");
  const [items, setItems] = useState([]);
  const [leaders, setLeaders] = useState([]);
  const [challenge, setChallenge] = useState(null);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    try {
      const [itemData, leaderData, challengeData] = await Promise.all([getItems(), getLeaderboard(), getChallenge()]);
      setItems(itemData); setLeaders(leaderData); setChallenge(challengeData);
    } catch (e) { setNotice("Could not load data: " + e.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { refresh(); }, []);

  async function handleCreate(form) {
    try { await createListing(form); setNotice("Your item listing was added."); await refresh(); setPage("browse"); }
    catch (e) { setNotice("Could not create listing: " + e.message); }
  }
  async function handleClaim(id) {
    try { await claimItem(id); setNotice("Item reserved! Contact the owner to arrange handover."); await refresh(); }
    catch (e) { setNotice("Could not claim item: " + e.message); }
  }

  const nav = [
    ["home", "Home", HomeIcon], ["browse", "Browse items", Search],
    ["create", "Give an item", PlusCircle], ["leaderboard", "Leaderboard", Trophy]
  ];
  return <div className="app-shell">
    <header className="topbar">
      <button className="brand" onClick={() => setPage("home")}><span className="brand-mark"><Leaf size={21}/></span><span>Local Loop<small>Share locally. Live sustainably.</small></span></button>
      <nav>{nav.map(([id, label, Icon]) => <button key={id} className={page === id ? "nav-link active" : "nav-link"} onClick={() => setPage(id)}><Icon size={17}/>{label}</button>)}</nav>
    </header>
    <main className="main-content">
      {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice("")} aria-label="Dismiss">×</button></div>}
      {loading && <p className="muted">Loading Local Loop…</p>}
      {page === "home" && <Home items={items} challenge={challenge} onBrowse={() => setPage("browse")} onGive={() => setPage("create")} />}
      {page === "browse" && <BrowseItems items={items} onClaim={handleClaim} />}
      {page === "create" && <CreateListing onCreate={handleCreate} />}
      {page === "leaderboard" && <Leaderboard leaders={leaders} />}
      <footer>Local Loop · A little sharing makes a greener community.</footer>
    </main>
  </div>;
}