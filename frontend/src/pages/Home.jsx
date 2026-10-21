import React from "react";
import { ArrowRight, BookOpen, MapPin, Recycle, Sparkles } from "lucide-react";

export default function Home({ items, challenge, onBrowse, onGive }) {
  const featured = challenge || { title: "Books & Stationery Week", category: "Books & Stationery", reward: 20, description: "Give old books, notebooks, and stationery a second life." };
  return <div className="page">
    <section className="hero">
      <div className="eyebrow"><Sparkles size={15}/> YOUR NEIGHBORHOOD, SHARING TOGETHER</div>
      <h1>Good things deserve<br/><span>another life.</span></h1>
      <p>Discover useful items nearby, pass on what you no longer need, and help your community waste less.</p>
      <div className="hero-actions"><button className="button primary" onClick={onBrowse}>Find items <ArrowRight size={17}/></button><button className="button secondary" onClick={onGive}>Give an item</button></div>
      <div className="hero-stats"><div><strong>{items.length}</strong><span>nearby listings</span></div><div><strong>2 km</strong><span>sharing radius</span></div><div><strong>Free</strong><span>to give and claim</span></div></div>
    </section>
    <section className="challenge-panel">
      <div className="challenge-icon"><BookOpen size={26}/></div><div className="challenge-copy"><div className="eyebrow">WEEKLY GREEN CHALLENGE · {featured.week || "THIS WEEK"}</div><h2>{featured.title || `${featured.category} Week`}</h2><p>{featured.description}</p></div>
      <div className="points"><strong>{featured.reward || 20}</strong><span>Green Points</span></div>
    </section>
    <section className="section-heading"><div><div className="eyebrow">PASS IT ON</div><h2>Nearby items</h2><p>Useful finds from people around you.</p></div><button className="text-button" onClick={onBrowse}>Browse all <ArrowRight size={16}/></button></section>
    {items.length ? <div className="item-grid">{items.slice(0,3).map(item => <article className="item-card" key={item.id}><div className="item-illustration"><Recycle size={30}/></div><div className="item-card-body"><span className="category-tag">{item.category}</span><h3>{item.title}</h3><p>{item.description}</p><div className="item-meta"><span><MapPin size={14}/>{item.distance} km away</span><span>Free</span></div></div></article>)}</div> : <div className="empty-state">No nearby listings yet. Be the first to share something!</div>}
    <section className="give-banner"><div><h2>Give an item a second life</h2><p>List something you no longer need and help a neighbour.</p></div><button className="button primary" onClick={onGive}>List an item <ArrowRight size={17}/></button></section>
  </div>;
}