# District Power Outage Management System (DPOMS)

**Improving Power Service Reliability Through Smart Outage Management**

A Python/Django web application for coordinating power outage reporting, electrician assignment, live location tracking, and citizen notifications between government administrators and citizens.

## Features

- **Dual Portal Authentication** — Separate registration and login for Government Admins and Citizens
- **Real-time Outage Reporting** — Citizens report outages with map-based location pinning
- **Admin Dashboard** — View all reported outages, assign electricians, update statuses
- **Electrician Management** — Admins add and manage field electricians; electricians can register/login and view assigned outages
- **Live Map Tracking** — Both admin and citizen can track assigned electrician location on an interactive map (Leaflet + OpenStreetMap)
- **Citizen Notifications** — Automatic alerts when status changes or electricians are assigned
- **Electrician Updates** — Electricians can send work status notifications back to admins
- **Estimated Restoration Time** — Admins set ETAs visible to citizens
- **Emergency Escalation** — Priority escalation for critical outages
- **Historical Analytics** — Outage statistics, status/priority breakdowns, resolution times

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Django |
| Frontend | HTML, CSS, JavaScript |
| Maps | Leaflet.js + OpenStreetMap (no API key required) |
| Database | SQLite |

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/districtpoms.git
cd districtpoms
```

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

### 6. Open the application

Visit **http://127.0.0.1:8000/** in your browser.

## Usage Guide

### Getting Started

1. **Register as Admin** — Go to Home → Government Admin Portal → Register
2. **Register as Citizen** — Go to Home → Citizen Portal → Register
3. **Register as Electrician** — Go to Home → Electrician Portal → Register
4. **Add Electricians** — Admin logs in → Electricians → Add Electrician
5. **Report Outage** — Citizen logs in → Report Outage (pin location on map)
6. **Assign & Track** — Admin opens the outage → Assign electrician → Set status to "En Route" → Open Live Tracking

### Workflow

```
Citizen reports outage
        ↓
Admin views dashboard → assigns electrician
        ↓
Citizen receives notification + electrician phone number
        ↓
Admin sets status to "En Route" → live tracking begins
        ↓
Electrician location updates on map (simulated movement toward outage)
        ↓
Admin updates status → Citizen gets notification
        ↓
Status set to "Power Restored" → Issue closed
```

### Live Tracking

- When an admin sets outage status to **"Electrician En Route"**, the tracking page automatically simulates the electrician moving toward the outage location.
- Both **admin** and **citizen** tracking pages poll location every 3 seconds.
- Maps use OpenStreetMap tiles — no Google Maps API key needed.

## Electrician role

- Electricians can register/login and will have a profile linked to a `User` account.
- Electricians can view outages assigned to them and see the citizen's address and phone.
- Electricians can send status updates which create notifications for all admins.
- Admins can still add detailed electrician records and assign outages from the admin portal.

## Deploying to Render

1. Ensure `DEBUG = False` in `districtpoms/settings.py` and set a secure `SECRET_KEY` as an environment variable on Render.
2. Add allowed hosts, e.g. `ALLOWED_HOSTS = ["your-app.onrender.com"]`.
3. Add `gunicorn` to `requirements.txt` if it is not already listed.
4. Add a `Procfile` in the project root with:

```text
web: gunicorn districtpoms.wsgi --log-file -
```

5. Commit your code to a GitHub repo and connect that repo to Render.
6. In the Render dashboard, create a new Web Service and choose your repo.
7. Set Build Command to:

```bash
pip install -r requirements.txt
```

8. Set the Start Command to:

```bash
gunicorn districtpoms.wsgi --log-file -
```

9. In Render environment variables, add:
- `SECRET_KEY` with a strong secret
- `DEBUG` set to `False`
- `DATABASE_URL` if using Postgres
- `ALLOWED_HOSTS` is handled in `settings.py` but Render will route correctly once the host is added there

10. If using Postgres, update `districtpoms/settings.py` to parse `DATABASE_URL` with `dj_database_url` or similar.
11. Run migrations in the Render shell:

```bash
python manage.py migrate
```

12. Create an admin user on Render:

```bash
python manage.py createsuperuser
```

Notes:
- For public access from phone or laptop, use the Render-generated URL shown on your service dashboard.
- SQLite works for development, but use Render Postgres for production reliability.
- Add `STATIC_ROOT` and optionally `whitenoise` to serve static files in production if needed.

## Project Structure

```
districtpoms/
├── districtpoms/          # Django project settings
│   ├── settings.py
│   └── urls.py
├── power/                 # Main application
│   ├── models.py          # User, Electrician, OutageReport, Notification
│   ├── views.py           # All view logic
│   ├── forms.py           # Registration & report forms
│   ├── urls.py            # URL routing
│   ├── templates/         # HTML templates
│   └── static/            # CSS & JavaScript
├── manage.py
├── requirements.txt
└── README.md
```

## URL Routes

| Route | Description |
|-------|-------------|
| `/` | Home page with portal selection |
| `/citizen/register/` | Citizen registration |
| `/citizen/login/` | Citizen login |
| `/citizen/dashboard/` | Citizen outage reports |
| `/citizen/report/` | Report new outage |
| `/citizen/track/<id>/` | Live electrician tracking |
| `/citizen/notifications/` | Citizen notifications |
| `/admin-portal/register/` | Admin registration |
| `/admin-portal/login/` | Admin login |
| `/admin-portal/dashboard/` | Admin dashboard |
| `/admin-portal/outage/<id>/` | Manage specific outage |
| `/admin-portal/electricians/` | Electrician list |
| `/admin-portal/electricians/add/` | Add electrician |
| `/admin-portal/track/<id>/` | Admin live tracking |
| `/admin-portal/analytics/` | Historical analytics |

## License

This project is open source and available for educational and demonstration purposes.
