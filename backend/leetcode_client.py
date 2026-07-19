import httpx

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Query to get solved-problem stats by difficulty
STATS_QUERY = """
query userProblemsSolved($username: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    tagProblemCounts {
      advanced { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      fundamental { tagName problemsSolved }
    }
  }
}
"""

async def fetch_leetcode_profile(username: str) -> dict:
    payload = {
        "query": STATS_QUERY,
        "variables": {"username": username}
    }
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    if not data.get("data") or not data["data"].get("matchedUser"):
        raise ValueError(f"No LeetCode user found for '{username}'")

    return data["data"]["matchedUser"]