# WorkWave — Recruitment & Job Marketplace Platform

WorkWave is a full-stack recruitment and job marketplace application built with **Python 3.14** and **Django 6.1.2**. It connects job seekers with employers through a public job marketplace, candidate profiles, job applications, and an employer recruitment workspace.

The application uses Django's server-rendered templates rather than a frontend SPA framework. Its interface is built with HTML5, CSS3, Bootstrap 5.3.3, and Vanilla JavaScript.

> **Project handover note:** This README is based on the supplied project description. Confirm environment-specific values, installed package versions, deployment settings, and the current state of the source code before deploying to a live environment.

---

## Contents

- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Data Model and Integrity](#data-model-and-integrity)
- [Security](#security)
- [Requirements](#requirements)
- [Local Setup](#local-setup)
- [Environment Configuration](#environment-configuration)
- [Database and Media Files](#database-and-media-files)
- [Running Tests](#running-tests)
- [Production Deployment Checklist](#production-deployment-checklist)
- [Operational Recommendations](#operational-recommendations)
- [Client Handover Checklist](#client-handover-checklist)

---

## Key Features

### Job seeker portal
- Register and sign in as a job seeker.
- Maintain a candidate profile and skills.
- Manage a profile resume.
- Browse and search job listings.
- Submit applications.
- Track application progress.

### Employer workspace
- Register and manage an employer account.
- Maintain company information.
- Create, edit, and close job postings.
- View applicants for the employer's own job postings.
- Update application statuses.
- Access employer dashboard information.

### System administration
- Dedicated superuser-only application dashboard.
- User directory and platform metrics.
- Role-based administrative access.
- Django Admin access for authorized staff.

### Public marketplace
- Public landing page.
- Job search and filtering.
- Job detail pages.
- Login and registration pages.

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.14, Django 6.1.2 | Application logic, routing, ORM, templates, and security |
| Database | SQLite 3 | Relational data persistence in the supplied configuration |
| Authentication | Django Authentication | Login, sessions, password hashing, and permissions |
| Authorization | Custom Django decorators | Role and ownership checks |
| Cache / rate limiting | Django LocMemCache | Failed-login tracking and temporary lockouts |
| Image processing | Pillow 13.0.0 | Profile image processing |
| Frontend | HTML5, CSS3, Bootstrap 5.3.3 | Responsive interface |
| JavaScript | Vanilla JavaScript (ES6+) | Client-side interactions and CSRF-related handling |
| Typography | Inter, Plus Jakarta Sans | Interface typography |
| Icons | Bootstrap Icons | Interface icons |

The supplied description identifies SQLite as the configured database and notes that PostgreSQL is a recommended production alternative.

---

## User Roles

| Role | Main permissions |
|---|---|
| Job Seeker | Manage own profile, browse jobs, apply, and access own application information |
| Employer | Manage company profile, manage own job postings, and manage applicants for own jobs |
| Superuser | Access the custom administration dashboard and Django administrative functions |

Public registration does not grant staff or superuser privileges. Administrative privileges must be assigned through a trusted administrative process.

---

## Project Structure

The following is the structure described for the project. Some generated files, virtual-environment files, and deployment files may not be shown.

```text
workwave/
│
├── workwave/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── validators.py
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── decorators.py
│   ├── rate_limit.py
│   ├── urls.py
│   ├── tests.py
│   └── security_tests.py
│
├── seeker/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── employer/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── jobs/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── applications/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── components/
│   ├── accounts/
│   ├── seeker/
│   ├── employer/
│   ├── jobs/
│   └── applications/
│
├── static/
│   └── css/
│
├── media/
├── manage.py
└── db.sqlite3
```

### Application responsibilities

- **`accounts/`** — identity, registration, login, role dispatch, superuser dashboard, and login rate limiting.
- **`seeker/`** — candidate profile, skills, dashboard, and profile-resume access.
- **`employer/`** — company profile, employer dashboard, and applicant management.
- **`jobs/`** — public job marketplace, job search, job details, and job-posting management.
- **`applications/`** — application submission, application status, and protected resume downloads.
- **`workwave/`** — Django project configuration, top-level routing, and file validators.
- **`templates/` and `static/`** — server-rendered pages, reusable UI components, and frontend assets.
- **`media/`** — uploaded profile photos and resumes.

---

## Data Model and Integrity

The application retains Django's native authentication user model and uses related profile records for role-specific information.

The supplied project description identifies these integrity rules:

1. **One application per seeker per job**  
   A database unique constraint on `(seeker, job)` prevents duplicate applications.

2. **Allowed application statuses**  
   A database check constraint restricts application status to:
   - `pending`
   - `shortlisted`
   - `rejected`
   - `accepted`

3. **Salary range validation**  
   `JobForm.clean()` validates that the maximum salary is not lower than the minimum salary.

4. **Related-record deletion**  
   The described relationships use cascading deletion for related user profiles, job listings, and application submissions. Review the actual model `on_delete` settings before deleting production records.

5. **Skills relationship**  
   Seeker skills are represented through a many-to-many relationship.

---

## Security

The project description records the following implemented controls:

| Risk | Described mitigation |
|---|---|
| Username enumeration | Generic error messaging for invalid login attempts |
| Brute-force login attempts | Rate limiting based on IP address and username |
| Public signup privilege escalation | Signup explicitly sets `is_staff` and `is_superuser` to `False` |
| Unauthorized admin access | Superuser-only decorator checks `request.user.is_superuser` |
| Cross-employer job modification | Job ownership is checked before editing or closing a job |
| Cross-employer applicant access | Ownership is checked before displaying applicants or changing application status |
| Resume exposure | Resume downloads use authenticated Django streaming views rather than public template links |
| Unsafe file uploads | File extension, MIME type, size, and path-character validation |
| Session and browser security | Described cookie, MIME-sniffing, and clickjacking settings |

### Resume and upload restrictions

The supplied description specifies:
- Accepted resume extensions: `.pdf`, `.doc`, and `.docx`.
- Maximum upload size: **5 MB**.
- MIME type validation.
- Path traversal character validation.
- Protected resume streaming endpoints for authorized users.

Do not expose the `media/` directory publicly if it contains private resumes. Confirm that production web-server configuration does not bypass the application's authorization checks.

### Login rate limiting

The described implementation tracks failed login attempts using both IP address and username. It locks out after five failures for five minutes; the sixth failed attempt is expected to trigger an HTTP `429` response.

The current development/test cache is Django `LocMemCache`. This cache is local to a process and is not shared between multiple application workers. Use a shared cache such as Redis for multi-worker production deployments.

### Important security verification

Security controls are only effective when the deployed settings and code match the description. Before go-live, run Django's deployment checks, review production settings, and verify the protected routes and file-storage configuration.

---

## Requirements

The supplied description identifies the following runtime versions:

- Python 3.14
- Django 6.1.2
- Pillow 13.0.0
- SQLite 3
- Bootstrap 5.3.3 (frontend)

A complete dependency lockfile or `requirements.txt` was not included in the supplied description. Use the project's actual dependency file if one is present in the handover package. Do not assume the list above is the complete set of Python dependencies.

---

## Local Setup

The commands below are for a Windows environment using PowerShell. Adapt activation commands for macOS/Linux if required.

### 1. Obtain the project source

Copy or clone the WorkWave project into your development environment, then open a terminal in the directory containing `manage.py`.

### 2. Create and activate a virtual environment

```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an approved execution-policy configuration or activate the environment from Command Prompt:

```bat
venv\Scripts\activate.bat
```

### 3. Install dependencies

If the project includes `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If no dependency file is supplied, obtain the authoritative dependency list from the development team before installing packages manually.

### 4. Configure environment variables

Create a local `.env` file or configure environment variables in your shell/development environment. Do not commit secrets to source control.

Example values for local development:

```ini
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

The exact environment-variable parsing and defaults depend on `workwave/settings.py`.

### 5. Apply database migrations

```bash
python manage.py migrate
```

If the project includes pending model changes, create migrations only after reviewing them:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create an administrative account

```bash
python manage.py createsuperuser
```

Use a strong, unique password. Keep administrative credentials confidential and transfer them to the client through a secure channel—not in this README or a public repository.

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Django's built-in development server is for local development and testing. Do not use it as the production web server.

---

## Environment Configuration

The supplied deployment description lists these production environment variables:

| Variable | Example / purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Strong, private Django secret key |
| `DJANGO_DEBUG` | `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated production hostnames |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` when HTTPS is configured |
| `DJANGO_SESSION_COOKIE_SECURE` | `True` when served over HTTPS |
| `DJANGO_CSRF_COOKIE_SECURE` | `True` when served over HTTPS |
| `DJANGO_SECURE_HSTS_SECONDS` | `31536000` after HTTPS is verified |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` only when all subdomains support HTTPS |
| `DJANGO_SECURE_HSTS_PRELOAD` | `True` only when preload requirements are met |

Example production configuration:

```ini
DJANGO_SECRET_KEY=replace-with-a-cryptographically-strong-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=workwave.com,www.workwave.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
```

**Important:** These values are examples, not confirmation that the application already reads every variable. Check `workwave/settings.py` for the exact variable names and parsing logic. Enable HSTS and HTTPS-related settings only after the production domain and HTTPS configuration have been tested. Never use the example secret key as a real secret.

---

## Database and Media Files

### Database

The supplied configuration uses SQLite (`db.sqlite3`).

For a small deployment, SQLite may be adequate depending on traffic and write concurrency. For a production deployment with multiple workers or higher write activity, PostgreSQL is the recommended upgrade in the supplied project description.

Before changing databases:
1. Configure the PostgreSQL connection securely.
2. Install and configure the required database driver.
3. Apply migrations to the new database.
4. Transfer existing data using a tested migration/export process.
5. Verify users, profiles, jobs, applications, and relationships.
6. Take a backup before switching production traffic.

### Media files

Uploaded profile photos and resumes are stored under `media/` in the described configuration.

For production:
- Back up uploaded files independently of the database.
- Restrict access to private resumes.
- Consider private object storage such as AWS S3 or Google Cloud Storage.
- If using object storage, preserve authorization by streaming files through protected application views or using appropriately short-lived signed URLs.
- Test upload, download, deletion, and backup restoration.

Static assets and user-uploaded media are different: configure their production serving and storage separately.

---

## Running Tests

Run the complete automated test suite from the directory containing `manage.py`:

```bash
python manage.py test
```

The supplied project description reports this result:

```text
Ran 33 tests in 30.359s

OK

Found 33 test(s).
System check identified no issues (0 silenced).
```

This is a reported result from the supplied project description, not a new test run performed during this handover document's creation. Re-run the suite against the exact source code and environment being delivered.

### Reported test distribution

| Application / suite | Tests | Focus |
|---|---:|---|
| `accounts` — LogoutCsrfTests | 1 | CSRF token and session logout |
| `accounts` — AccountAuthAndDashboardTests | 6 | Registration and role routing |
| `accounts` — WorkWaveSecurityTests | 12 | Security scenarios |
| `employer` — EmployerDashboardTests | 3 | Dashboard and status updates |
| `seeker` — SeekerProfileTests | 2 | Profile editing and skills |
| `jobs` — JobTests | 7 | Search, filtering, apply, and post |
| `applications` — ApplicationModelTests | 2 | Unique and check constraints |
| **Total** | **33** | **Reported passing tests** |

### Reported security scenarios

The supplied description lists tests for:
1. Invalid superuser login rejection.
2. Valid job seeker login and role redirect.
3. Valid employer login and role redirect.
4. Job seeker blocked from superuser administration.
5. Employer blocked from superuser administration.
6. Job seeker blocked from editing another user's profile.
7. Employer blocked from editing another employer's job.
8. Employer blocked from viewing another employer's applicants.
9. Unauthenticated access to protected pages redirected to login.
10. Repeated failed login attempts triggering lockout.
11. Unauthorized resume downloads forbidden.
12. Public signup attempts to set staff/superuser flags neutralized.

---

## Production Deployment Checklist

Before publishing the application:

- [ ] Set `DJANGO_DEBUG=False`.
- [ ] Generate and configure a strong, private `DJANGO_SECRET_KEY`.
- [ ] Configure `DJANGO_ALLOWED_HOSTS` for the real domain.
- [ ] Configure HTTPS and verify SSL redirect and secure cookies.
- [ ] Review HSTS settings before enabling them.
- [ ] Run `python manage.py check --deploy`.
- [ ] Apply database migrations.
- [ ] Create and verify the production superuser securely.
- [ ] Configure a production WSGI server and reverse proxy/platform.
- [ ] Configure static-file collection and serving as required by the hosting environment.
- [ ] Configure persistent, private media storage.
- [ ] Ensure resume files cannot be accessed through public static URLs.
- [ ] Configure a shared cache such as Redis if running multiple workers.
- [ ] Configure database and media backups.
- [ ] Run the full test suite against the release candidate.
- [ ] Test registration, login, logout, job posting, job application, status updates, and resume downloads.
- [ ] Verify role boundaries using seeker, employer, and superuser accounts.
- [ ] Review application logs and configure monitoring/error reporting.
- [ ] Document the hosting provider, domain, deployment procedure, and rollback procedure.

---

## Operational Recommendations

The following items are recommendations in the supplied technical description; they should not be treated as already completed unless confirmed in the deployed environment.

### Shared production cache

For deployments with multiple Gunicorn/Uvicorn workers or multiple instances, configure Redis as Django's shared cache so rate-limit state is shared across workers.

The supplied description gives this example:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}
```

Install and configure the appropriate Redis client/package for the project's Django version and hosting environment.

### Optional login protection package

The supplied description mentions `django-axes` as an optional alternative for database-backed login-attempt tracking. It is not described as a required dependency or an already-installed component.

### Database and file backup

- Back up SQLite using a consistent database backup method while SQLite is in use.
- For PostgreSQL, establish scheduled backups and test restoration.
- Back up media files separately.
- Define retention periods and restrict backup access.

---

## Client Handover Checklist

The development team should provide the following separately and securely:

- [ ] Complete source code repository.
- [ ] Dependency file (`requirements.txt` or equivalent lockfile).
- [ ] Database migration files.
- [ ] Environment-variable reference (without secret values).
- [ ] Production hosting and domain details.
- [ ] Superuser credentials through a secure channel.
- [ ] Database and media backup procedure.
- [ ] Deployment and rollback instructions.
- [ ] Known issues and pending work, if any.
- [ ] Confirmation of the final test run on the delivered source code.

### Client responsibilities after handover

The client or designated system administrator should:
- Keep administrative credentials private and rotate them when required.
- Manage user accounts and platform content.
- Maintain domain, hosting, database, and storage subscriptions.
- Apply security updates and dependency updates.
- Monitor backups and periodically test restoration.
- Review access permissions and operational logs.

---

## Support and Maintenance

Project-specific support contacts, warranty terms, maintenance duration, hosting ownership, and service-level commitments were not included in the supplied technical description. Add the agreed details here before the README is issued as the final contractual handover document.

| Handover detail | Value |
|---|---|
| Project | WorkWave |
| Client / organization | To be completed |
| Delivery date | To be completed |
| Source repository | To be provided |
| Production URL | To be provided |
| Hosting provider | To be provided |
| Technical contact | To be provided |
| Support period | To be agreed |

---

## Project Summary

WorkWave brings together a public job marketplace, job seeker portal, employer workspace, and superuser administration area in a modular Django application. The supplied project description reports 33 passing automated tests and security controls covering authentication, authorization, job ownership, application access, and protected resume downloads.

Production readiness should be confirmed against the actual release environment. In particular, review database choice, shared caching, HTTPS settings, private media storage, backups, deployment checks, and the final test run before opening the platform to real users.
