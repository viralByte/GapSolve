# GapSolve — AI-Powered LeetCode Study Planner

> **GapSolve** is an intelligent, full-stack application designed to analyze a user's LeetCode performance, spot their weakest computer science fundamentals, and generate a personalized, streamed day-by-day DSA study plan.

---
Live App Link- main.d5tuh7eyc0351.amplifyapp.com

## 🚀 Features

* **Automated Profile Analysis:** Parses public LeetCode profiles via GraphQL to calculate difficulty breakdowns and topic mastery metrics.
* **Smart Topic Clustering:** Groups recently solved problems into recognizable patterns (e.g., Sliding Window, Dynamic Programming, Graphs)[cite: 4].
* **Real-Time LLM Streaming:** Integrates with the Google Gemini API to stream a tailored 8–10 day study plan chunk-by-chunk using Server-Sent Events (SSE)[cite: 5].
* **Interactive Dashboard:** Features Chart.js visualizations (doughnut, radar, and horizontal bar charts), consistency streak heatmaps, and month-over-month progression trackers[cite: 1].
* **Custom Focus Selector:** Allows users to pick specific weak modules via an interactive multi-select dropdown for targeted revision[cite: 1].
* **Friend Comparison Mode:** Stacks two user profiles head-to-head on a unified coverage radar chart[cite: 1].
* **Secure Authentication:** JWT-based session management with robust password hashing (bcrypt) and restricted `@gmail.com` access rules[cite: 2].

---

## 🛠️ Technology Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Chart.js[cite: 1]
* **Hosting (Frontend):** AWS Amplify[cite: 1]
* **Backend:** Python, FastAPI, Mangum[cite: 6, 7]
* **Compute (Backend):** AWS Lambda (Serverless Container)[cite: 3]
* **AI & Parsing:** Google Gemini API (`gemini-2.5-flash`), HTTPX (GraphQL Client)[cite: 4, 5]
* **Storage:** Ephemeral writable execution storage (`/tmp/users_db.json`)[cite: 3]

---

## 📂 Project Structure

```text
GapSolve/
├── main.py              # FastAPI application entry point & Mangum handler[cite: 6]
├── auth.py              # User authentication, password hashing & JWT logic[cite: 2]
├── leetcode_client.py   # Asynchronous LeetCode GraphQL profile fetcher[cite: 4]
├── analyzer.py          # Gap analysis, pattern clustering & calendar parser[cite: 1]
├── llm_service.py       # LLM provider integration & streaming service[cite: 5]
├── Dockerfile           # AWS Lambda container configuration[cite: 3]
├── requirements.txt     # Python dependency manifest[cite: 8]
└── index.html           # Full frontend dashboard UI & client logic[cite: 1]
```

## ⚙️ Local Development & Setup
### 1. Clone the repository:
git clone [https://github.com/your-username/gapsolve.git](https://github.com/your-username/gapsolve.git)
cd gapsolve

### 2. Install dependencies:
pip install -r requirements.txt

### 3. Configure Environment Variables:
Create a .env file in the root directory:
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

### 4. Run the FastAPI development server:
uvicorn main:app --reload


## ☁️ Cloud Architecture & Deployment
GapSolve utilizes a decoupled serverless architecture:
* **Frontend:** Deployed and distributed globally via AWS Amplify.
* **Backend:** Containerized using Docker (Dockerfile), pushed to Amazon ECR, and executed serverless-style through AWS Lambda via a Function URL and the Mangum ASGI adapter.  
