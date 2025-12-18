# 445 · Engineering Project Site  
**Interactive 3D Visualization, Scheduling, and Decision Support Prototype**

---

## Overview

This repository contains a full-stack engineering project site developed to support civil and construction engineering workflows under realistic technical and operational constraints.

The platform intentionally prioritizes engineering-grade determinism, transparency, and scalability limits over consumer-style abstraction. It integrates:

- Client-side 3D visualization for very large CAD models
- Deterministic Critical Path Method (CPM) scheduling analysis
- Structured planning and decision-support tools (WDM, budgeting, documentation)

Rather than simulating ideal conditions, the system is designed to reflect real engineering realities: large files, auditable logic, minimal backend state, and reproducible results.

---

## Core Capabilities

### 1. 3D Model Viewer (STL)

- Browser-based STL viewer built with Three.js
- Designed explicitly for very large CAD models
- No server-side STL storage or streaming
- Models are:
  - Hosted externally (e.g., Google Drive)
  - Downloaded and opened locally by the user
  - Parsed and rendered entirely client-side
- Interaction features:
  - Explicit Orbit / Pan / Zoom modes
  - Grid toggle
  - Auto-centering and normalization
  - Reset view
- Optimized for mouse, trackpad, and touch input

This architecture avoids GitHub limits, CDN bottlenecks, server memory constraints, and opaque file handling while remaining transparent and reproducible.

---

### 2. CPM Scheduling Engine

- Python-based Critical Path Method (CPM) implementation
- Deterministic, dependency-driven scheduling logic
- Automatically computes:
  - Early Start (ES) / Early Finish (EF)
  - Late Start (LS) / Late Finish (LF)
  - Total Float (TF)
  - Critical Path activities
- Exposed through a JSON API endpoint for reuse and testing

This mirrors professional engineering practice: auditable, deterministic, and repeatable scheduling logic.

---

### 3. Planning & Decision Support

- Weighted Decision Matrix (WDM)
- Budget and planning views
- Survey and documentation pages
- Static and dynamic data integration

These tools support structured engineering decision-making rather than black-box optimization.

---

## System Architecture

### Backend

Flask (Python)
- Routing and page rendering
- CPM scheduling API
- Lightweight, deterministic backend
- No persistent storage of heavy assets

app.py
- Application entry point
- CPM computation logic
- API endpoints

---

### Frontend

Jinja2 Templates
- viewer.html — 3D STL viewer
- schedule.html — CPM scheduling interface
- wdm.html — weighted decision matrix
- base.html — shared layout and styling

Static Assets
- Local ES module build of Three.js
- Stylesheets and UI assets
- JSON data for scheduling examples

---

### Design Principles

- Heavy assets handled entirely client-side
- Deterministic calculations handled server-side
- Clear separation of concerns
- No background processing or hidden state
- Engineering-grade transparency over convenience

---

## Technology Stack

![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)
![Three.js](https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=three.js&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)

---

## Getting Started

Clone the repository:

    git clone https://github.com/ZanderDent/445.git
    cd 445

Create and activate a virtual environment:

    python -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install flask requests

Run the application:

    python app.py

Open in your browser:

    http://127.0.0.1:8080

---

## Usage Notes

- Large STL files are not hosted or streamed by the server
- Models are downloaded externally and opened locally by the user
- This avoids GitHub file limits, browser memory crashes, and server bandwidth constraints
- CPM calculations are deterministic and reproducible via API

These decisions are intentional and reflect real-world engineering constraints.

---

## Project Context

This project was developed as an engineering systems prototype, not a consumer web application.

It prioritizes:
- Determinism over abstraction
- Transparency over convenience
- Real constraints over simulated ones

Suitable for engineering coursework, technical demonstrations, and early-stage engineering software prototyping.

---

## License

MIT License

---

## Author

Zander Dent  
Civil Engineering · Software Systems
