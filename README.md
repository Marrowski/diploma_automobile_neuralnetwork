# Automobile Neural Network — ANPR System

A Django web application for automatic recognition of Ukrainian vehicle license plates using a YOLO detection model and EasyOCR.

## Features

- Upload an image or video and automatically detect license plates
- Recognizes Ukrainian plate formats and grants/denies access accordingly
- Handles common OCR errors (digit/letter confusion, angled photos, background noise)
- User registration, login, and profile management with avatar upload
- Scan history saved per user (plate texts, bounding boxes, image/video)
- Live war statistics on the main page (via russianwarship.rip API)
- Admin panel via Django Jazzmin
- Tailwind CSS UI with dark mode support

## Supported Ukrainian plate formats

| Format | Example |
|--------|---------|
| `AA####AA` | `AO0141YB` |
| `####AA` | `1234AB` |
| `AA#####` | `AB12345` |

Valid letters: `A B C E H I K M O P T X Y`

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0, Python |
| Database | PostgreSQL |
| Plate detection | YOLOv8 (Ultralytics) |
| OCR | EasyOCR (PyTorch) |
| Styling | Tailwind CSS, Django Tailwind |
| Admin | Jazzmin |

## Project structure

```
automobile_neuralnetwork/
├── automobile_application/
│   ├── anpr/
│   │   ├── detector.py          # YOLO + EasyOCR pipeline
│   │   └── license_plate_detector.pt
│   ├── main/
│   │   ├── models.py            # UserProfile, AutoNumbers, PlateScan, etc.
│   │   ├── views.py             # All views including anpr_upload
│   │   ├── forms.py
│   │   └── migrations/
│   ├── theme/
│   │   └── templates/           # HTML templates (Tailwind)
│   └── automobile_application/
│       ├── settings.py
│       └── urls.py
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Node.js + npm (for Tailwind CSS compilation)

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd automobile_neuralnetwork
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/macOS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install easyocr
```

### 3. Configure the database

Create a PostgreSQL database named `DiplomaProjectNN`, then update `settings.py` if your credentials differ:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'DiplomaProjectNN',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'PORT': '5432',
    }
}
```

### 4. Apply migrations

```bash
cd automobile_application
python manage.py migrate
```

### 5. Build Tailwind CSS

```bash
python manage.py tailwind install
python manage.py tailwind build
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Usage

| URL | Description |
|-----|-------------|
| `/` | Main page with war statistics |
| `/load/` | Upload image or video for plate recognition |
| `/profile/` | User profile (name, password, avatar) |
| `/register/` | Registration |
| `/login/` | Login |
| `/admin/` | Admin panel |

### How recognition works

1. YOLO model detects the license plate region in the uploaded file
2. The region is cropped, scaled, and passed to EasyOCR
3. OCR fragments are sorted left-to-right by position
4. Text is normalized: Cyrillic lookalikes → Latin, common digit/letter confusions corrected
5. A position-aware force-fit corrects remaining errors (e.g. `O→0` in digit slots, `G→4`, `Y` kept as valid UA letter)
6. If the result matches a Ukrainian plate pattern — access is granted

## Notes

- EasyOCR downloads its English model (~100 MB) on first run — this is cached automatically
- The YOLO model file (`license_plate_detector.pt`) must be present in `anpr/`
- For production deployment replace the `SECRET_KEY` in `settings.py` and set `DEBUG = False`
