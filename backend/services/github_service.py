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
    if token and not token.startswith("<") and not "token" in token.lower():
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

                html_url = repo.get("html_url") or f"https://github.com/{username}/{repo.get('name')}"
                stargazers = repo.get("stargazers_count", 0)
                forks_count = repo.get("forks_count", 0)
                projects.append({
                    "name": repo.get("name", "Untitled"),
                    "description": repo.get("description") or "No description provided.",
                    "stars": stargazers,
                    "stargazers_count": stargazers,
                    "forks": forks_count,
                    "forks_count": forks_count,
                    "link": html_url,
                    "html_url": html_url,
                    "language": repo.get("language") or "Python",
                    "topics": repo.get("topics") or []
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
            "stargazers_count": 5,
            "forks": 1,
            "forks_count": 1,
            "link": f"https://github.com/{username}/DevHamid",
            "html_url": f"https://github.com/{username}/DevHamid",
            "language": "Python",
            "topics": ["portfolio", "flask", "supabase", "render"]
        },
        {
            "name": "face-attendance-system",
            "description": "Real-time face recognition attendance system using OpenCV, dlib and Supabase.",
            "stars": 12,
            "stargazers_count": 12,
            "forks": 3,
            "forks_count": 3,
            "link": f"https://github.com/{username}/face-attendance-system",
            "html_url": f"https://github.com/{username}/face-attendance-system",
            "language": "Python",
            "topics": ["face-recognition", "opencv", "computer-vision"]
        },
        {
            "name": "voice-biometrics-attendance",
            "description": "Voice recognition and anti-spoofing attendance system with PyDub & SpeechRecognition.",
            "stars": 8,
            "stargazers_count": 8,
            "forks": 2,
            "forks_count": 2,
            "link": f"https://github.com/{username}/voice-biometrics-attendance",
            "html_url": f"https://github.com/{username}/voice-biometrics-attendance",
            "language": "Python",
            "topics": ["voice-recognition", "biometrics", "audio-processing"]
        }
    ]
