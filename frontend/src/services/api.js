// Uses Flask when VITE_API_URL is configured and reachable.
// Until the backend is ready, demo data is stored in this browser session.
const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const STORAGE_KEY = "local-loop-demo-items";
const LEADERS = [
  { id: 1, name: "Green Starter", points: 120 },
  { id: 2, name: "Community Helper", points: 90 },
  { id: 3, name: "Reuse Champion", points: 70 }
];
const initialItems = [
  { id: 1, title: "Used textbooks", category: "Books & Stationery", description: "Well-kept textbooks ready for another student.", distance: 1.2, status: "available", owner: "A neighbour" },
  { id: 2, title: "Casual clothes bundle", category: "Clothing", description: "Clean clothes in good usable condition.", distance: 0.8, status: "available", owner: "A neighbour" },
  { id: 3, title: "Desk lamp", category: "Household Items", description: "Working desk lamp; bulb included.", distance: 1.7, status: "available", owner: "A neighbour" },
  { id: 4, title: "Notebooks and pens", category: "Books & Stationery", description: "Partly used notebooks and spare pens.", distance: 2.0, status: "available", owner: "A neighbour" },
  { id: 5, title: "Old bicycle", category: "Household Items", description: "Outside the default 2 km radius.", distance: 3.2, status: "available", owner: "A neighbour" }
];
function readItems() {
  try { const saved = localStorage.getItem(STORAGE_KEY); return saved ? JSON.parse(saved) : initialItems; }
  catch { return initialItems; }
}
function saveItems(items) { localStorage.setItem(STORAGE_KEY, JSON.stringify(items)); }
async function request(path, options = {}) {
  if (!API_BASE) throw new Error("No API URL configured");
  const response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  return response.status === 204 ? null : response.json();
}
export async function getItems() {
  if (API_BASE) { try { const data = await request("/items"); return Array.isArray(data) ? data : data.items || []; } catch (e) { console.warn("Using demo items:", e.message); } }
  return readItems().filter(i => i.status === "available" && Number(i.distance) <= 2);
}
export async function getLeaderboard() {
  if (API_BASE) { try { const data = await request("/leaderboard"); return Array.isArray(data) ? data : data.leaderboard || []; } catch (e) { console.warn("Using demo leaderboard:", e.message); } }
  return LEADERS;
}
export async function getChallenge() {
  if (API_BASE) { try { return await request("/challenge"); } catch (e) { console.warn("Using demo challenge:", e.message); } }
  return { category: "Books & Stationery", title: "Books & Stationery Week", reward: 20, description: "Give old books, notebooks, and stationery a second life.", week: "This week" };
}
export async function createListing(form) {
  if (API_BASE) { try { return await request("/items", { method: "POST", body: JSON.stringify(form) }); } catch (e) { console.warn("Using demo listing:", e.message); } }
  const items = readItems();
  const item = { ...form, id: Date.now(), distance: 0.5, status: "available", owner: "You" };
  saveItems([item, ...items]); return item;
}
export async function claimItem(id) {
  if (API_BASE) { try { return await request(`/items/${id}/claim`, { method: "POST", body: JSON.stringify({}) }); } catch (e) { console.warn("Using demo claim:", e.message); } }
  const items = readItems(); const item = items.find(i => String(i.id) === String(id));
  if (!item || item.status !== "available") throw new Error("This item is no longer available.");
  saveItems(items.map(i => String(i.id) === String(id) ? { ...i, status: "reserved" } : i)); return item;
}