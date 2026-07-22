from typing import Dict, List

# Topics considered "core" for interview prep
CORE_TOPICS = [
    "Array", "String", "Hash Table", "Dynamic Programming", "Binary Search",
    "Tree", "Depth-First Search", "Breadth-First Search", "Graph",
    "Two Pointers", "Sliding Window", "Backtracking", "Greedy",
    "Heap (Priority Queue)", "Union Find", "Trie", "Bit Manipulation"
]

CATEGORIES = {
    "Graph & Trees": ["Tree", "Depth-First Search", "Breadth-First Search", "Graph"],
    "Arrays & Strings": ["Array", "String", "Two Pointers", "Sliding Window"],
    "Advanced": ["Dynamic Programming", "Backtracking", "Greedy"]
}

def analyze_gaps(profile: dict) -> Dict:
    # 1. Unpack Tags from LeetCode's specific GraphQL structure
    tag_counts = {}
    tag_problem_counts = profile.get("tagProblemCounts", {})
    
    # Loop through the three nested levels LeetCode provides
    for level in ["advanced", "intermediate", "fundamental"]:
        for tag_data in tag_problem_counts.get(level, []):
            tag_name = tag_data.get("tagName", "")
            solved = tag_data.get("problemsSolved", 0)
            if tag_name:
                tag_counts[tag_name] = solved

    # 2. Unpack Difficulty Stats from submitStatsGlobal
    easy = medium = hard = total = 0
    stats = profile.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
    
    for stat in stats:
        diff = stat.get("difficulty")
        count = stat.get("count", 0)
        
        if diff == "All":
            total = count
        elif diff == "Easy":
            easy = count
        elif diff == "Medium":
            medium = count
        elif diff == "Hard":
            hard = count

    difficulty_breakdown = {
        "All": total,
        "Easy": easy,
        "Medium": medium,
        "Hard": hard
    }

    # 3. Dynamically calculate Strong and Weak topics
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    strong_topics = [{"topic": k, "count": v} for k, v in sorted_tags[:4]] if sorted_tags else []
    
    weak_topics = [{"topic": t, "count": tag_counts.get(t, 0)} for t in CORE_TOPICS if tag_counts.get(t, 0) <= 2][:5]

    # 4. Categorize problems for the Problem Bank
    user_categories = {}
    for cat_name, tags in CATEGORIES.items():
        user_categories[cat_name] = [
            tag for tag in tags if tag_counts.get(tag, 0) > 0
        ]
        
    return {
        "username": profile.get("username", "Unknown"),
        "totalSolved": total,
        "difficulty_breakdown": difficulty_breakdown,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "categorized_problems": user_categories 
    }