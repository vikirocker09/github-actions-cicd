# GitHub Actions CI/CD Pipeline for Flask Application

A complete CI/CD pipeline using GitHub Actions to automate testing, building, and deployment of a Python Flask web application to AWS EC2.

---
### screenshots
<img width="940" height="448" alt="image" src="https://github.com/user-attachments/assets/abc0449a-76e4-459a-bb3e-74d2b8b14fcf" />
<img width="940" height="479" alt="image" src="https://github.com/user-attachments/assets/94b147dc-6a47-483d-bae1-51018050a2ab" />

## Repository Structure

```
github-actions-cicd/
├── .github/
│   └── workflows/
│       └── cicd.yml        # GitHub Actions workflow definition
├── app.py                  # Flask web application
├── tests/
│   └── test_app.py         # pytest unit tests
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code — deploys on release tag |
| `staging` | Staging environment — deploys on every push |

---

## Workflow Overview

The pipeline runs 4 automated jobs on every push:

```
Install & Test ──► Build ──► Deploy to Staging  (staging branch only)
                         └──► Deploy to Production (release tag only)
```

### Job 1 — Install & Test
- Triggered on every push to `main` or `staging`
- Sets up Python 3.10 environment
- Installs all dependencies from `requirements.txt`
- Runs full pytest suite with coverage reporting
- Uploads coverage XML as a downloadable artifact

### Job 2 — Build
- Only runs after tests pass
- Creates a versioned `.tar.gz` deployment package
- Tags package with the Git commit SHA
- Uploads package as a build artifact

### Job 3 — Deploy to Staging
- Only runs when code is pushed to the `staging` branch
- SSHes into staging EC2 server using stored secrets
- Pulls latest code from the staging branch
- Installs/updates dependencies
- Restarts the Flask application via systemd

### Job 4 — Deploy to Production
- Only runs when a GitHub Release tag is published
- SSHes into production EC2 server
- Pulls latest code from the main branch
- Installs/updates dependencies
- Restarts the Flask application via systemd

---

## API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/health` | Health check | `{"status": "healthy"}` |
| GET | `/api/items` | Get all items | JSON list of items |
| POST | `/api/items` | Add new item | Created item JSON |

---

## Prerequisites

- AWS Account with EC2 access
- GitHub Account
- Python 3.10 or higher
- Two Ubuntu 22.04 EC2 instances (staging + production)

---

## Setup Instructions

### Step 1 — Fork the Repository

Click the **Fork** button on the top right of this page to create your own copy.

### Step 2 — Create the Staging Branch

```bash
git checkout -b staging
git push origin staging
```

### Step 3 — Launch EC2 Instances on AWS

Launch two Ubuntu 22.04 LTS instances:

| Instance | Type | Purpose |
|----------|------|---------|
| Staging-Server | t3.micro | Staging deployments |
| Production-Server | t3.micro | Production deployments |

On each server, run:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

Security group inbound rules required:
| Port | Protocol | Source |
|------|----------|--------|
| 22 | TCP | 0.0.0.0/0 (SSH) |
| 8080 | TCP | 0.0.0.0/0 (Flask) |

### Step 4 — Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**

Add all 6 secrets:

| Secret Name | Value |
|-------------|-------|
| `STAGING_HOST` | Public IPv4 of staging EC2 |
| `STAGING_USER` | `ubuntu` |
| `STAGING_SSH_KEY` | Full contents of your `.pem` key file |
| `PROD_HOST` | Public IPv4 of production EC2 |
| `PROD_USER` | `ubuntu` |
| `PROD_SSH_KEY` | Full contents of your `.pem` key file |

To get your PEM key contents:
```bash
cat ~/Downloads/your-key.pem
```
Copy everything including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`

### Step 5 — Set Up systemd Service on Each EC2 Server

Run this on both staging and production servers:
```bash
sudo tee /etc/systemd/system/flaskapp.service << 'EOF'
[Unit]
Description=Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/app
ExecStart=/home/ubuntu/app/venv/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable flaskapp
```

---

## Triggering the Pipeline

### Trigger Staging Deploy
Push any change to the staging branch:
```bash
git checkout staging
git merge main
git push origin staging
```

### Trigger Production Deploy
1. Go to GitHub → **Releases**
2. Click **Create a new release**
3. Set tag to `v1.0.0`
4. Set target branch to `main`
5. Click **Publish release**

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/<your-username>/github-actions-cicd.git
cd github-actions-cicd

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov=.

# Start the app
python3 app.py
# App runs at http://localhost:8080
```

### Verify it works
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/items
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_VERSION` | `1.0.0` | Application version shown in /health |
| `ENVIRONMENT` | `dev` | Current environment (dev/staging/production) |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 3.0.0 | Web framework |
| pytest | 7.4.0 | Test runner |
| pytest-cov | 4.1.0 | Coverage reporting |
| requests | 2.31.0 | HTTP client |
| Werkzeug | 3.0.1 | WSGI utility |

---

## Submission

- GitHub Repository: `https://github.com/<your-username>/github-actions-cicd`
- Workflow file: `.github/workflows/cicd.yml`
- All pipeline stages visible in the **Actions** tab
