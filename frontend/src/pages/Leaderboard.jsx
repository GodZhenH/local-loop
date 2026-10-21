import React from "react";
import { Trophy, Leaf } from "lucide-react";

export default function Leaderboard({ leaders }) {
  const ranked = [...leaders].sort((a,b)=>(b.points||0)-(a.points||0));
  return <div className="page"><div className="page-title"><div className="eyebrow">SMALL ACTIONS, SHARED IMPACT</div><h1>Community leaderboard.</h1><p>Green Points are awarded after an eligible exchange is completed and verified.</p></div>
    <div className="leaderboard">{ranked.map((person, i)=><div className="leader-row" key={person.id ?? person.name}><span className={`rank rank-${i+1}`}>{i+1}</span><span className="leader-avatar"><Leaf size={18}/></span><div className="leader-name"><strong>{person.name || person.username || "Community member"}</strong><small>Community contributor</small></div><strong className="leader-points">{person.points ?? person.green_points ?? 0} pts</strong></div>)}
    {!ranked.length && <p className="empty-state">The leaderboard will appear after residents earn Green Points.</p>}</div>
    <p className="form-hint">Sample leaderboard data is shown until the Flask API is connected.</p>
  </div>;
}