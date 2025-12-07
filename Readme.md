# 🌟 ScholarSense

**AI-Powered Application Assistant for Students**

*Built for CodeCraze 2025 Hackathon*

---

## 🚀 Overview

**ScholarSense** is an AI-powered application assistant that helps students find and apply to opportunities (jobs, internships, scholarships, hackathons, research positions) by analyzing their profile fit and auto-generating tailored application materials.

### The Problem
Students face overwhelming challenges when applying to opportunities:
- **Repetitive writing** of similar emails, SOPs, and cover letters
- **No centralized tracking** of applications across multiple platforms
- **Unclear fit assessment** - "Should I even apply?"
- **Time-consuming customization** for each opportunity

### The Solution
ScholarSense streamlines the entire application workflow:
1. **Upload resume once** → Profile automatically created
2. **Paste any opportunity** → Get instant AI fit score (0-100)
3. **Generate materials** → Tailored emails, SOPs, bullets in seconds
4. **Track everything** → Unified dashboard for all applications

---

## 🎯 Key Features

### 1. Resume Intake & Profile Builder

Upload your resume (PDF/DOCX) and let ScholarSense automatically extract:

* Skills
* Projects
* Experience
* Education
* Achievements

Your profile becomes a personalized foundation for opportunity matching.

---

### **2. AI-Powered Opportunity Analyzer**

Paste any opportunity text — internship posting, scholarship, hackathon, research ad.

ScholarSense instantly extracts:

* Title & organization
* Requirements
* Preferred skills
* Eligibility
* Deadline
* Opportunity type
* Workload estimate
* Location

Output is returned as **strict JSON**, ensuring reliability and integration with the backend.

---

### **3. Fit Score Engine (0–100)**

ScholarSense evaluates how well the student matches each opportunity using:

* Skill overlap
* Eligibility match
* Experience relevance
* Academic alignment

It also explains *why* the student fits or doesn’t fit — no guessing.

---

### **4. Auto-Generated Application Materials**

Save hours of writing.

ScholarSense generates:

* **Cold email outreach**
* **Bullet-point justification for applications**
* **SOP/Cover Letter paragraph**
* **Professional subject lines**

Each output is **personalized**, concise, and grounded in the student's actual profile — no hallucinated experiences.

---

### **5. Organized Application Dashboard**

Track all your opportunities in one place.

Each entry includes:

* Fit score badge
* Status: *To Apply*, *Applied*, *Interview*, *Offer*
* AI-generated materials
* Requirements summary

A clean, student-friendly workflow designed for clarity and speed.

---

## 🎯 **Why ScholarSense Matters**

### **Real-world Impact**

Students worldwide struggle with:

* Overwhelming application writing
* Scattered postings across platforms
* Unclear requirements
* Limited time

ScholarSense brings clarity, confidence, and speed by acting as a **24/7 application co-pilot**.

A tool like this genuinely empowers:

* First-generation students
* International students
* Students with limited access to advisors
* Busy learners with heavy workloads

This is not just productivity — it is **accessibility and opportunity democratization**.

---

## 🛠️ **Tech Stack**

### **Backend**

* **FastAPI** – High-performance async API framework
* **SQLAlchemy + PostgreSQL** – Data management & persistence
* **Pydantic v2** – Strict schema validation
* **OpenRouter/LLM Integration** – GPT/Llama models
* **ChromaDB (Optional)** – RAG-based resume/context retrieval
* **Python 3.11+**

### **Frontend**

* **React + Vite** – Lightning-fast SPA
* **TailwindCSS** – Clean, modern UI
* **Axios** – API communication
* **React Router** – Navigation & state management

### **Infrastructure**

* `.env` based config
* CORS-enabled backend
* Modular service-oriented architecture
* Clear separation of:

  * Routes
  * Services
  * Models
  * Schemas
  * Prompts
  * LLM client

---

## 🧩 **System Architecture (High-Level)**

1. **Client (React)**

   * Resume upload
   * Opportunity submission
   * Dashboard display
   * Materials viewer

2. **API Layer (FastAPI)**

   * `/profile` — Upload + extract resume
   * `/opportunity/analyze` — LLM-based extraction
   * `/materials/generate` — Email + SOP + bullets
   * `/dashboard` — CRUD for stored opportunities

3. **LLM Orchestration**

   * Strict JSON outputs
   * Structured prompts
   * Error handling + retries
   * Deterministic schema enforcement

4. **Database**

   * Users
   * Profiles
   * Opportunities
   * Generated outputs
   * Status updates

---

## 🧪 **LLM Prompt Engineering Strategy**

The model is guided through:

* A global system prompt defining ScholarSense’s personality and constraints
* A strict JSON schema for opportunity analysis
* A separate schema for generating materials
* Zero hallucination rules
* Validation + auto-repair logic

This ensures consistent results, clean parsing, and robust backend integration.

---

## 📈 **What Makes ScholarSense Stand Out (Judging Alignment)**

### ✔ **Uniqueness**

There is no centralized AI platform that:

* Parses opportunities
* Scores fit
* Generates application materials
* Tracks applications
* Tailors outputs to students

All in a single cohesive tool.

### ✔ **Real World Impact**

Removes barriers for students worldwide.
Saves hours per application.
Improves confidence and clarity.

### ✔ **Technical Execution**

* LLM prompt engineering
* Modern full-stack architecture
* Strict schema-controlled AI
* Robust backend engineering
* Clean UI/UX

### ✔ **Presentation Quality**

Demo video will show:

* The overwhelming real problem
* How ScholarSense solves it in seconds
* Clear workflow
* Clean engineering
* Real impact

---

## 🗺️ **Roadmap**

### **Future Enhancements**

* Browser extension for instant scraping
* Chrome sidebar assistant
* Multi-language support
* Export to PDF/Docs
* Multi-student collaborative advisor mode
* University integration APIs
* LLM fine-tuning for academic language

---

## 🧑‍💻 **Team**

Designed & developed by **Pratik Rauniyar** for CodeCraze Hackathon 2025.

---

## 📽️ **Demo Video Script (Short Outline)**

1. **Hook:**
   “Students waste hours writing repetitive emails and parsing confusing opportunity postings…”

2. **Problem:**
   Show a messy set of random job postings and SOP drafts.

3. **Solution:**
   Introduce ScholarSense — your AI co-pilot.

4. **Live Demo:**

   * Upload resume
   * Paste opportunity
   * View JSON extraction
   * See fit score
   * See cold email + SOP paragraph
   * Update dashboard status

5. **Tech Stack Overview:**
   FastAPI, React, PostgreSQL, LLM, RAG.

6. **Impact:**
   “This tool democratizes access to opportunities for students everywhere.”

7. **Closing:**
   ScholarSense — built to help students apply better, faster, and smarter.

---

## 🏁 **Conclusion**

ScholarSense transforms a frustrating, time-consuming workflow into a guided, AI-enhanced experience. It’s practical, impactful, technically strong, and designed for real students facing real challenges — exactly the kind of innovation CodeCraze was made to showcase.

