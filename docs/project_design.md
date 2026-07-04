# Project Design

First-stage design: GitHub API is attempted first, then local sample fallback is used only when collection returns no usable rows. Pipeline modules write durable CSV, JSON, HTML, and model artifacts for Streamlit to read.

Second-stage design adds PCA/KMeans clustering after scoring, model comparison artifacts, richer static and interactive charts, stronger Agent prompts, and a styled HTML report. Streamlit remains a read-only presentation layer over generated artifacts.
