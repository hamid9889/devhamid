"""
GitHub Service
Fetches public repositories for Hamid (@hamid9889) via the GitHub REST API.
Transforms each repository into a clean dictionary with:
  - name: Project name
  - description: Repository description
  - stars: Stargazers count
  - forks: Forks count
  - link: URL to repository (html_url)
Includes an in-memory 15-minute cache to avoid rate limits.
"""

import os
import time
import requests
from typing import List, Dict, Any

# In-memory repository cache
_cache: Dict[str, Any] = {
    "projects": None,
    "timestamp": 0
}
CACHE_TTL = 900  # 15 minutes in seconds

def get_github_projects(username: str = "hamid9889") -> List[Dict[str, Any]]:
    """
    Fetch repositories for given username and return structured project data.
    """
    now = time.time()
    
    # Return cached data if still fresh
    if _cache["projects"] is not None and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["projects"]

    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=30"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DevHamid-Portfolio-Flask"
    }

    # Optional GitHub Personal Access Token to raise rate limit from 60 to 5,000 req/hr
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            raw_repos = response.json()
            projects = []
            
            for repo in raw_repos:
                # Omit user's special profile config repo if desired
                if repo.get("name") == username and not repo.get("description"):
                    continue

                projects.append({
                    "name": repo.get("name", "Untitled"),
                    "description": repo.get("description") or "No description provided.",
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "link": repo.get("html_url", f"https://github.com/{username}/{repo.get('name')}")
                })

            _cache["projects"] = projects
            _cache["timestamp"] = now
            return projects

        # If rate-limited or error, return cached data if available
        if _cache["projects"] is not None:
            return _cache["projects"]

        print(f"[WARN] GitHub API returned status {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"[ERROR] GitHub API fetch error: {e}")
        if _cache["projects"] is not None:
            return _cache["projects"]

    # Fallback default projects if GitHub is completely unreachable
    return [
        {
            "name": "DevHamid",
            "description": "Professional Full-Stack Developer Portfolio & AI Research Showcase.",
            "stars": 5,
            "forks": 1,
            "link": f"https://github.com/{username}/DevHamid"
        },
        {
            "name": "face-attendance-system",
            "description": "Real-time face recognition attendance system using OpenCV, dlib and Supabase.",
            "stars": 12,
            "forks": 3,
            "link": f"https://github.com/{username}/face-attendance-system"
        },
        {
            "name": "voice-biometrics-attendance",
            "description": "Voice recognition and anti-spoofing attendance system with PyDub & SpeechRecognition.",
            "stars": 8,
            "forks": 2,
            "link": f"https://github.com/{username}/voice-biometrics-attendance"
        }
    ]
