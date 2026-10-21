import React, { useState } from "react";
import { Gift, Award } from "lucide-react";

export default function CreateListing({ onCreate }) {
  const [form, setForm] = useState({
    title: "",
    category: "Books & Stationery",
    description: "",
  });
  const [error, setError] = useState("");
  const [showScoreModal, setShowScoreModal] = useState(false);

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function submit(e) {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      setError("Please complete the item name and description.");
      return;
    }
    setError("");
    // Open modal first so the user sees their points award
    setShowScoreModal(true);
  }

  function handleModalClose() {
    setShowScoreModal(false);
    onCreate(form); // Trigger item creation and page navigation when dismissed
    setForm({ title: "", category: "Books & Stationery", description: "" });
  }

  return (
    <div className="page form-page">
      <div className="page-title">
        <div className="eyebrow">SHARE WITH YOUR NEIGHBOURS</div>
        <h1>Give an item a new home.</h1>
        <p>List an item in good usable condition. Giving and claiming items is free.</p>
      </div>

      {/* Score Pop-Up Modal */}
      {showScoreModal && (
        <div className="score-modal-overlay">
          <div className="score-modal-card">
            <div className="score-badge">
              <Award size={36} />
            </div>
            <h2>Item Published!</h2>
            <p>Thank you for contributing to your community.</p>
            <div className="score-points-display">Your item has been published! Green Points are awarded after a completed exchange.</div>
            <button
              className="button primary full"
              type="button"
              onClick={handleModalClose}
            >
              Awesome!
            </button>
          </div>
        </div>
      )}

      <form className="listing-form" onSubmit={submit}>
        <div className="form-icon">
          <Gift size={25} />
        </div>
        <h2>Item details</h2>

        <label>
          Item name
          <input
            name="title"
            value={form.title}
            onChange={update}
            placeholder="e.g. Intro to Biology textbook"
            maxLength={80}
            required
          />
        </label>

        <label>
          Category
          <select name="category" value={form.category} onChange={update}>
            <option>Books & Stationery</option>
            <option>Clothing</option>
            <option>Household Items</option>
            <option>Recyclables</option>
            <option>Other</option>
          </select>
        </label>

        <label>
          Description
          <textarea
            name="description"
            value={form.description}
            onChange={update}
            placeholder="Describe the condition and anything the new owner should know…"
            rows={4}
            maxLength={500}
            required
          />
        </label>

        <p className="form-hint">
          Demo mode uses an approximate distance. Real location matching will be connected to the backend.
        </p>

        {error && <p className="error">{error}</p>}

        <button className="button primary full" type="submit">
          Publish listing
        </button>
      </form>
    </div>
  );
}