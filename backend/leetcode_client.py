import httpx

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Existing: solved-problem stats by difficulty + tag counts
STATS_QUERY = """
query userProblemsSolved($username: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum { difficulty count }
    }
    tagProblemCounts {
      advanced { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      fundamental { tagName problemsSolved }
    }
  }
}
"""

# NEW: last ~20 accepted submissions (real problem titles for clustering)
RECENT_AC_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
  }
}
"""

# NEW: submission calendar for streak heatmap + progression trend
CALENDAR_QUERY = """
query userCalendar($username: String!) {
  matchedUser(username: $username) {
    userCalendar {
      streak
      totalActiveDays
      submissionCalendar
    }
  }
}
"""


async def _post(client: httpx.AsyncClient, query: str, variables: dict, username: str) -> dict:
    payload = {"query": query, "variables": variables}
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
    }
    resp = await client.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


async def fetch_leetcode_profile(username: str) -> dict:
    """Backwards-compatible: returns stats + tag counts only."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        data = await _post(client, STATS_QUERY, {"username": username}, username)

    if not data.get("data") or not data["data"].get("matchedUser"):
        raise ValueError(f"No LeetCode user found for '{username}'")

    return data["data"]["matchedUser"]


async def fetch_full_profile(username: str) -> dict:
    """Fetches stats + recent submissions + calendar. Extras fail gracefully."""
    async with httpx.AsyncClient(timeout=12.0) as client:
        stats_data = await _post(client, STATS_QUERY, {"username": username}, username)

        if not stats_data.get("data") or not stats_data["data"].get("matchedUser"):
            raise ValueError(f"No LeetCode user found for '{username}'")

        try:
            recent_data = await _post(
                client, RECENT_AC_QUERY, {"username": username, "limit": 20}, username
            )
            recent = recent_data.get("data", {}).get("recentAcSubmissionList", []) or []
        except Exception:
            recent = []

        try:
            cal_data = await _post(client, CALENDAR_QUERY, {"username": username}, username)
            calendar = (
                cal_data.get("data", {}).get("matchedUser", {}).get("userCalendar", {}) or {}
            )
        except Exception:
            calendar = {}

    profile = stats_data["data"]["matchedUser"]
    profile["recentSubmissions"] = recent
    profile["calendar"] = calendar
    return profile