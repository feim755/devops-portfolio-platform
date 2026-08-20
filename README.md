# 🚀 Microservices DevOps Infrastructure Platform

A production-ready microservices architecture built with Flask, PostgreSQL, Nginx, and Prometheus, fully containerized using Docker Compose and automated via GitHub Actions CI/CD.

## 🏗️ Architecture Overview

- **Nginx Reverse Proxy / Gateway**: Listens on port `80` and routes traffic to internal microservices.
- **Auth Microservice (`app_auth`)**: Flask API providing authentication endpoints (Port `5000`).
- **Data Microservice (`app_data`)**: Flask API connected to PostgreSQL database (Port `5001`).
- **PostgreSQL Database**: Relational DB with persistent volume storage.
- **Prometheus Monitoring**: Collects system and service metrics (Port `9090`).

## 🛠️ Quick Start

```bash
# Clone the repository
git clone <your-github-repo-url>
cd devops-portfolio-platform

# Spin up the entire infrastructure
docker compose up -d --build
# Gateway Health Check
curl http://localhost/health

# Auth Service Endpoint
curl -X POST http://localhost/api/v1/auth/login

# Data Service Endpoint
curl http://localhost/api/v1/data/metrics
---

#### 2. Създаване на GitHub Actions CI/CD Workflow (`.github/workflows/ci-cd.yml`)

Сега ще добавим автоматичен CI/CD пайплайн, който GitHub ще изпълнява автоматично при всяка промяна!

Залепи следващия сив блок:

```bash
mkdir -p .github/workflows

cat << 'EOF' > .github/workflows/ci-cd.yml
name: CI/CD Infrastructure Pipeline

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - name: Check out repository
      uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Build and Test Docker Compose Stack
      run: |
        docker compose build
        docker compose up -d
        sleep 10
        docker compose ps
        curl -f http://localhost/health || exit 1
        curl -f http://localhost/api/v1/data/metrics || exit 1
        docker compose down
