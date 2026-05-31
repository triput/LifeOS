# LifeOS

A personal productivity OS built with Python, Reflex, and PostgreSQL (Neon). LifeOS combines work project management, learning/certification tracking, daily agenda, and time analytics into one unified dark-themed interface.

## Features

- **Work Track**: Epic → Project → Task → Subtask hierarchy with kanban and tree views
- **Academy Track**: Specialization → Course → Module → Learning Task hierarchy
- **Certifications**: PMP (PDUs) and CSM (SEUs) progress tracking
- **Agenda**: Day view with scheduled tasks and due-today list
- **Stats**: Time tracking analytics, status/priority distribution, completion rates
- **Settings**: Label customization, Notion/Skedpal/Google Calendar integration tokens
- **Dark Theme**: Dusty jewel tones with teal, sage, amber, and ruby accents

## Tech Stack

- [Python 3.11+](https://www.python.org/)
- [Reflex 0.6+](https://reflex.dev/) — full-stack Python web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) (via `rx.Model`) for ORM
- [Neon PostgreSQL](https://neon.tech/) for the database
- [Cabinet Grotesk + Satoshi](https://www.fontshare.com/) fonts

## Setup

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd lifeos-reflex
cp .env.example .env
# Edit .env and add your DATABASE_URL
```

### 2. Get your Neon DATABASE_URL

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string from the dashboard (it looks like `postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require`)
4. Paste it into your `.env` file as `DATABASE_URL`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize and migrate the database

```bash
reflex db init
reflex db makemigrations --message "initial schema"
reflex db migrate
```

### 5. Run the app

```bash
reflex run
```

The app will be available at `http://localhost:3000`.

## Deploying the App

### Railway

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) and create a new project from your repo
3. Add environment variable: `DATABASE_URL` (from Neon)
4. Railway auto-detects Python and deploys

### Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and create a new Web Service
3. Set build command: `pip install -r requirements.txt && reflex db migrate`
4. Set start command: `reflex run --env prod`
5. Add environment variable: `DATABASE_URL`

### Fly.io

```bash
fly launch
fly secrets set DATABASE_URL="your-neon-url"
fly deploy
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (Neon or other PostgreSQL provider) |

## Database Migrations

After making model changes:

```bash
reflex db makemigrations --message "description of change"
reflex db migrate
```
