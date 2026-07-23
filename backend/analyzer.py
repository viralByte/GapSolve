from typing import Dict, List
import json
from datetime import datetime, timezone

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

# Maps known problem title-slugs -> pattern, so we can cluster REAL recent solves.
# Maps known problem title-slugs -> pattern, so we can cluster REAL recent solves.
PATTERN_KEYWORDS = {
    "Sliding Window": ["window", "substring", "longest-substring", "minimum-window",
                       "max-consecutive", "fruit-into-baskets", "permutation-in-string", "alternating-sequence"],
    "2D Arrays / Matrix": ["matrix", "grid", "shift-2d", "spiral", "rotate-image", "search-a-2d", "island"],
    "Circular Queue / Deque": ["circular-queue", "deque", "circular-deque", "design-circular"],
    "Two Pointers": ["two-sum", "3sum", "container-with-most-water", "trapping-rain",
                     "sort-colors", "remove-duplicates", "valid-palindrome"],
    "Graphs & BFS/DFS": ["graph", "path-existence", "followers", "report-to-each-employee", "number-of-islands", 
                         "flood-fill", "rotting-oranges", "word-ladder", "clone-graph", "course-schedule", 
                         "surrounded-regions", "max-area-of-island", "pacific-atlantic", "walls-and-gates", "tree"],
    "Math & Number Theory": ["gcd", "divisor", "odd-and-even", "digits", "multiply", "pow", "average-time", "math"],
    "Dynamic Programming": ["climbing-stairs", "coin-change", "house-robber", "longest-increasing",
                            "edit-distance", "knapsack", "unique-paths", "word-break",
                            "maximum-subarray", "partition-equal", "decode-ways", "jump-game"],
    "Strings": ["string", "zigzag", "anagram", "palindrome", "valid-parentheses", "rearrange-string"],
    "Intervals": ["interval", "remove-covered-intervals", "merge-intervals", "insert-interval"],
    "SQL / Database": ["tweets", "names-in-a-table", "daily-leads", "employee"],
    "Binary Search": ["binary-search", "search-in-rotated", "find-minimum-in-rotated",
                      "koko", "median-of-two", "find-peak"],
    "Backtracking": ["subsets", "permutations", "combination-sum", "n-queens",
                     "generate-parentheses", "word-search", "palindrome-partitioning"],
    "Heap / Priority Queue": ["kth-largest", "top-k", "merge-k", "find-median", "task-scheduler"],
    "Linked List": ["linked-list", "reverse-linked", "merge-two-sorted", "cycle",
                    "reorder-list", "remove-nth"],
    "Stack": ["valid-parentheses", "min-stack", "daily-temperatures", "largest-rectangle",
              "evaluate-reverse-polish", "car-fleet"],
    "Arrays / Hashing": ["rank-transform", "array", "hash", "contains-duplicate", "majority-element"]
}


def _classify_problem(title_slug: str) -> str:
    slug = (title_slug or "").lower()
    for pattern, keywords in PATTERN_KEYWORDS.items():
        for kw in keywords:
            if kw in slug:
                return pattern
    return "Other / Uncategorized"


def _cluster_recent(recent: List[dict]) -> Dict[str, List[dict]]:
    clusters: Dict[str, List[dict]] = {}
    seen = set()
    for sub in recent:
        slug = sub.get("titleSlug", "")
        if not slug or slug in seen:
            continue
        seen.add(slug)
        pattern = _classify_problem(slug)
        clusters.setdefault(pattern, []).append({
            "title": sub.get("title", slug),
            "slug": slug,
            "url": f"https://leetcode.com/problems/{slug}/",
            "timestamp": sub.get("timestamp"),
        })
    return clusters


def _parse_calendar(calendar: dict) -> dict:
    """Returns streak info, daily heatmap data, and month-over-month progression."""
    raw = calendar.get("submissionCalendar", "{}")
    try:
        cal_map = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        cal_map = {}

    days = []
    for ts, count in cal_map.items():
        try:
            dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
            days.append({"date": dt.strftime("%Y-%m-%d"), "count": count, "ts": int(ts)})
        except Exception:
            continue
    days.sort(key=lambda d: d["date"])

    # Month-over-month progression (this month vs last month)
    now = datetime.now(tz=timezone.utc)
    this_month = f"{now.year:04d}-{now.month:02d}"
    prev_month_dt = datetime(now.year - (1 if now.month == 1 else 0),
                             12 if now.month == 1 else now.month - 1, 1, tzinfo=timezone.utc)
    last_month = f"{prev_month_dt.year:04d}-{prev_month_dt.month:02d}"

    this_month_total = sum(d["count"] for d in days if d["date"].startswith(this_month))
    last_month_total = sum(d["count"] for d in days if d["date"].startswith(last_month))

    return {
        "streak": calendar.get("streak", 0),
        "totalActiveDays": calendar.get("totalActiveDays", 0),
        "days": [{"date": d["date"], "count": d["count"]} for d in days],
        "progression": {
            "this_month": this_month_total,
            "last_month": last_month_total,
            "this_month_label": this_month,
            "last_month_label": last_month,
        },
    }


def analyze_gaps(profile: dict) -> Dict:
    tag_counts = {}
    tag_problem_counts = profile.get("tagProblemCounts", {})
    for level in ["advanced", "intermediate", "fundamental"]:
        for tag_data in tag_problem_counts.get(level, []):
            tag_name = tag_data.get("tagName", "")
            solved = tag_data.get("problemsSolved", 0)
            if tag_name:
                tag_counts[tag_name] = solved

    easy = medium = hard = total = 0
    stats = profile.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
    for stat in stats:
        diff = stat.get("difficulty")
        count = stat.get("count", 0)
        if diff == "All": total = count
        elif diff == "Easy": easy = count
        elif diff == "Medium": medium = count
        elif diff == "Hard": hard = count

    difficulty_breakdown = {"All": total, "Easy": easy, "Medium": medium, "Hard": hard}

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    strong_topics = [{"topic": k, "count": v} for k, v in sorted_tags[:4]] if sorted_tags else []
    weak_topics = [{"topic": t, "count": tag_counts.get(t, 0)}
                   for t in CORE_TOPICS if tag_counts.get(t, 0) <= 2][:5]

    user_categories = {}
    for cat_name, tags in CATEGORIES.items():
        user_categories[cat_name] = [tag for tag in tags if tag_counts.get(tag, 0) > 0]

    # Full topic list (only topics the user has touched) for bar chart + radar
    all_topic_counts = [
        {"topic": t, "count": tag_counts.get(t, 0)}
        for t in CORE_TOPICS if tag_counts.get(t, 0) > 0
    ]
    all_topic_counts.sort(key=lambda x: x["count"], reverse=True)

    return {
        "username": profile.get("username", "Unknown"),
        "totalSolved": total,
        "difficulty_breakdown": difficulty_breakdown,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "categorized_problems": user_categories,
        "all_topic_counts": all_topic_counts,
        "recent_clusters": _cluster_recent(profile.get("recentSubmissions", [])),
        "calendar": _parse_calendar(profile.get("calendar", {})),
    }