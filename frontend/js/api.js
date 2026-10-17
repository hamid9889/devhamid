// Base API URL (Render backend)
export const API_URL = "https://devhamid.onrender.com";

// Health check
export async function checkHealth() {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

// Fetch projects from Supabase via backend
export async function fetchProjects() {
  const res = await fetch(`${API_URL}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

// Increment visits counter
export async function incrementVisits() {
  const res = await fetch(`${API_URL}/visits`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to increment visits");
  return res.json();
}

// Example usage in frontend component
export default async function runPortfolio() {
  console.log("Checking backend health...");
  const health = await checkHealth();
  console.log("Health:", health);

  console.log("Fetching projects...");
  const projects = await fetchProjects();
  console.log("Projects:", projects);

  console.log("Incrementing visits...");
  await incrementVisits();
  console.log("Visits incremented successfully!");
}
