
const API_BASE = (import.meta.env.VITE_API_URL || "https://local-loop-api.onrender.com").replace(/\/$/, "");

// Demo location for the hackathon. Both demo users are placed at the same
// coordinates so they can exchange items within the 2 km radius.
const DEMO_LOCATION = {
  latitude: 3.1390,
  longitude: 101.6869
};

const GIVER_NAME = "Local Loop Demo Giver";
const RECEIVER_NAME = "Local Loop Demo Receiver";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `API error ${response.status}: ${message || response.statusText}`
    );
  }

  if (response.status === 204) return null;
  return response.json();
}

function asArray(data, key) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.[key])) return data[key];
  return [];
}

function mapListing(item) {
  return {
    ...item,
    id: item.id,
    title: item.title,
    category: item.category,
    description: item.description || "",
    status: item.status || "available",
    owner: item.owner_name || item.owner || "A neighbour",
    distance: Number(item.distance_km ?? item.distance ?? 0),
    featured: Boolean(item.featured)
  };
}

// Find existing demo users first to avoid creating duplicates.
async function ensureDemoUsers() {
  const data = await request("/api/users");
  const users = asArray(data, "users");

  let giver = users.find(user => user.name === GIVER_NAME);
  let receiver = users.find(user => user.name === RECEIVER_NAME);

  if (!giver) {
    const created = await request("/api/users", {
      method: "POST",
      body: JSON.stringify({
        name: GIVER_NAME,
        ...DEMO_LOCATION
      })
    });
    giver = created.user || created;
  }

  if (!receiver) {
    const created = await request("/api/users", {
      method: "POST",
      body: JSON.stringify({
        name: RECEIVER_NAME,
        ...DEMO_LOCATION
      })
    });
    receiver = created.user || created;
  }

  if (giver.id == null || receiver.id == null) {
    throw new Error("Could not obtain demo user IDs from the backend.");
  }

  return { giver, receiver };
}

export async function getItems() {
  const { receiver } = await ensureDemoUsers();

  const params = new URLSearchParams({
    lat: String(DEMO_LOCATION.latitude),
    lon: String(DEMO_LOCATION.longitude),
    exclude_user_id: String(receiver.id)
  });

  const data = await request(`/api/listings?${params.toString()}`);
  return asArray(data, "listings").map(mapListing);
}

export async function getLeaderboard() {
  const data = await request("/api/leaderboard");

  return asArray(data, "leaderboard").map(person => ({
    ...person,
    points: Number(
      person.total_points ?? person.points ?? person.green_points ?? 0
    )
  }));
}

export async function getChallenge() {
  const data = await request("/api/challenge");
  const challenge = data.challenge || data;

  return {
    ...challenge,
    title: challenge.title || "Weekly Green Challenge",
    category: challenge.category || "Community Sharing",
    description:
      challenge.description ||
      "Share useful items with people in your neighbourhood.",
    reward: Number(data.featured_points ?? challenge.reward ?? 20),
    week: challenge.week || "This week"
  };
}

export async function createListing(form) {
  const { giver } = await ensureDemoUsers();

  const data = await request("/api/listings", {
    method: "POST",
    body: JSON.stringify({
      owner_id: giver.id,
      title: form.title,
      category: form.category,
      description: form.description || ""
    })
  });

  return mapListing(data.listing || data);
}

export async function claimItem(id) {
  const { receiver } = await ensureDemoUsers();

  const data = await request("/api/exchanges/claim", {
    method: "POST",
    body: JSON.stringify({
      listing_id: Number(id),
      receiver_id: receiver.id
    })
  });

  return data.exchange || data;
}
