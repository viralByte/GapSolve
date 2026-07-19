from typing import Dict, List

# Topics considered "core" for interview prep — used as a baseline checklist
CORE_TOPICS = [
    "Array", "String", "Hash Table", "Dynamic Programming", "Binary Search",
    "Tree", "Depth-First Search", "Breadth-First Search", "Graph",
    "Two Pointers", "Sliding Window", "Backtracking", "Greedy",
    "Heap (Priority Queue)", "Union Find", "Trie", "Bit Manipulation"
]

def analyze_gaps(profile: dict) -> Dict:
    tag_counts = {}
    for bucket in ["fundamental", "intermediate", "advanced"]:
        for tag in profile.get("tagProblemCounts", {}).get(bucket, []):
            tag_counts[tag["tagName"]] = tag.get("problemsSolved", 0)

    weak_topics: List[Dict] = []
    strong_topics: List[Dict] = []

    for topic in CORE_TOPICS:
        solved = tag_counts.get(topic, 0)
        entry = {"topic": topic, "solved": solved}
        if solved <= 3:
            weak_topics.append(entry)
        else:
            strong_topics.append(entry)

    # Sort weakest-first for planning
    weak_topics.sort(key=lambda x: x["solved"])

    difficulty_breakdown = {
        item["difficulty"]: item["count"]
        for item in profile.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
    }

    return {
        "username": profile.get("username"),
        "difficulty_breakdown": difficulty_breakdown,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
    }