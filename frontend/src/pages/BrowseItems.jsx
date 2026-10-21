import React, { useMemo, useState } from "react";
import { MapPin, Search, PackageOpen, Sparkles } from "lucide-react";

export default function BrowseItems({ items, onClaim }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [claimedItem, setClaimedItem] = useState(null);

  const categories = ["All", ...new Set(items.map(i => i.category).filter(Boolean))];

  const visible = useMemo(
    () =>
      items.filter(
        i =>
          Number(i.distance) <= 2 &&
          i.status === "available" &&
          (category === "All" || i.category === category) &&
          `${i.title} ${i.description} ${i.category}`
            .toLowerCase()
            .includes(query.toLowerCase())
      ),
    [items, query, category]
  );

  function handleClaim(item) {
    onClaim(item.id);
    setClaimedItem(item);
  }

  return (
    <div className="page">
      <div className="page-title">
        <div className="eyebrow">YOUR LOCAL COMMUNITY</div>
        <h1>Find something useful.</h1>
        <p>Every item is free. Every exchange keeps something useful in circulation.</p>
      </div>

      {/* Score Pop-Up Modal when receiving/claiming */}
      {claimedItem && (
        <div className="score-modal-overlay">
          <div className="score-modal-card">
            <div className="score-badge">
              <Sparkles size={36} />
            </div>
            <h2>Item Claimed!</h2>
            <p>You have reserved <strong>{claimedItem.title}</strong>.</p>
            <div className="score-points-display">+20 Green Points</div>
            <button
              className="button primary full"
              onClick={() => setClaimedItem(null)}
            >
              Got it!
            </button>
          </div>
        </div>
      )}

      <div className="filter-row">
        <label className="search-box">
          <Search size={17} />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search items…"
          />
        </label>
        <select
          value={category}
          onChange={e => setCategory(e.target.value)}
          aria-label="Filter category"
        >
          {categories.map(c => (
            <option key={c}>{c}</option>
          ))}
        </select>
      </div>

      {visible.length ? (
        <div className="item-grid">
          {visible.map((item, index) => (
            <article
              className="item-card item-card-animated"
              key={item.id}
              style={{ animationDelay: `${index * 0.12}s` }}
            >
              <div className="item-illustration">
                <PackageOpen size={30} />
              </div>
              <div className="item-card-body">
                <span className="category-tag">{item.category}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <div className="item-meta">
                  <span>
                    <MapPin size={14} />
                    {item.distance} km away
                  </span>
                  <span>Free</span>
                </div>
                <button
                  className="button primary full"
                  onClick={() => handleClaim(item)}
                >
                  Claim item
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          No matching items within 2 km. Try another search or category.
        </div>
      )}
    </div>
  );
}