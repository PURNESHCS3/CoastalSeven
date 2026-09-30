# ⚡ FastAPI Real-Time Media Hub (API-Only)

A high-performance, pure backend FastAPI service designed for testing directly via **Swagger UI** (`/docs`). Features secure file uploads, Pillow image processing & thumbnail generation, bi-directional WebSocket notifications, automated Pytest suite (**96%+ coverage**), and code-quality tooling (Black, isort, Flake8, mypy, pre-commit).

---

## 🎯 Direct Swagger UI Testing

Visiting the root URL `http://127.0.0.1:8000/` automatically redirects you to **Swagger UI** (`/docs`), where you can interactively test all API endpoints:

| Endpoint | Method | Tag | Description & Swagger Testing Instructions |
|---|---|---|---|
| `POST /api/upload` | `POST` | Uploads | Upload an image (`PNG`, `JPG`, `WEBP`, `GIF`, max 5MB). Generates thumbnail (150x150) and medium (600x600) variants via Pillow, and broadcasts `IMAGE_UPLOADED` to WebSocket clients. |
| `GET /api/upload` | `GET` | Uploads | List all uploaded images with direct static URLs to original, medium, and thumbnail files. |
| `GET /api/upload/{filename}` | `GET` | Uploads | Fetch metadata and URLs for a specific image filename. |
| `DELETE /api/upload/{filename}` | `DELETE` | Uploads | Remove an image and all its resized variants from disk. |
| `POST /api/ws/broadcast` | `POST` | WebSockets | **Trigger a WebSocket broadcast directly from Swagger UI!** Any connected WebSocket clients will receive the notification in real time. |
| `GET /api/ws/status` | `GET` | WebSockets | View the total active WebSocket connections and active client IDs. |
| `GET /health` | `GET` | General | Verify service status and API version. |
| `GET /static/...` | `GET` | Static | Direct file access to original, thumbnail, and medium image variants. |

---

## 📂 Project Structure

```
fastapi_realtime_media/
├── .flake8                     # Flake8 linter configuration
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hook definitions
├── pyproject.toml              # Configurations for black, isort, mypy, pytest, coverage
├── requirements.txt            # Pure API production dependencies
├── requirements-dev.txt        # Development, testing, and linting dependencies
├── README.md                   # Project documentation
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entrypoint, lifespan, CORS, static mounting
│   ├── config.py               # Settings (file size limits, MIME types, resizing dimensions)
│   ├── core/
│   │   ├── __init__.py
│   │   └── exceptions.py       # Custom HTTP exceptions (413, 415, 400, 404, 500)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── upload.py           # Pydantic schemas for upload responses & variant metadata
│   │   └── websocket.py        # Pydantic schemas for WebSocket messaging & Swagger broadcast
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py    # Pillow validation, header verify, aspect-ratio resizing
│   │   └── websocket_manager.py# ConnectionManager class (connect, disconnect, broadcast)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_upload.py    # POST /api/upload, GET /api/upload, GET/DELETE /{filename}
│   │   ├── routes_websocket.py # WS /ws/{client_id}, POST /api/ws/broadcast, GET /status
│   │   └── routes_views.py     # Root redirect to /docs and GET /health
│   └── static/
│       └── uploads/            # Static storage for original/, thumbnail/, and medium/
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures and mock image generators
    ├── test_image_service.py   # Unit tests for image validation & Pillow resizing
    ├── test_websocket_manager.py # Unit tests for ConnectionManager
    ├── test_api_upload.py      # Integration tests for upload endpoints & WS triggers
    ├── test_api_websocket.py   # Integration tests for WebSocket & HTTP broadcast
    └── test_main.py            # Integration tests for root redirect & health check
```

---

## 🏃 Quickstart & Running with Swagger UI

### 1. Install Dependencies
```powershell
pip install -r requirements-dev.txt
```

### 2. Start the FastAPI Development Server
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Open Swagger UI
Open your browser to:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** (or simply [http://127.0.0.1:8000/](http://127.0.0.1:8000/))

---

## 📡 Testing Real-Time WebSockets & Uploads

### Step 1: Open a WebSocket Connection in Browser Console or Client
In your browser developer console (F12 -> Console) or any WebSocket client (e.g. Postman, websocat, wscat):

```javascript
// Connect to WebSocket endpoint
const ws = new WebSocket("ws://127.0.0.1:8000/ws/client_test");

ws.onopen = () => console.log("Connected to Media Hub WebSocket!");
ws.onmessage = (event) => console.log("Real-Time Event Received:", JSON.parse(event.data));
```

### Step 2: Upload an Image in Swagger UI
1. Go to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.
2. Expand `POST /api/upload`.
3. Click **Try it out**.
4. Choose an image file and click **Execute**.
5. **Notice in your WebSocket console**: It immediately receives the real-time event:
   ```json
   {
     "event": "IMAGE_UPLOADED",
     "client_id": "system",
     "timestamp": "2026-09-26T...",
     "data": {
       "filename": "...",
       "original_filename": "avatar.png",
       "width": 800,
       "height": 600,
       "url": "/static/uploads/original/....png",
       "variants": {
         "thumbnail": { "url": "/static/uploads/thumbnail/....png", "width": 150, "height": 112 },
         "medium": { "url": "/static/uploads/medium/....png", "width": 600, "height": 450 }
       }
     }
   }
   ```

### Step 3: Test Broadcast from Swagger UI
1. In Swagger UI, expand `POST /api/ws/broadcast`.
2. Click **Try it out**, enter your message, and click **Execute**.
3. All connected WebSocket clients will instantly receive your broadcast!

---

## 🧪 Automated Testing with Pytest

Run the test suite with coverage report:

```powershell
python -m pytest
```

Results:
- **36 passed**
- **96.34% test coverage** (Target: 80%+)

---

## 🎨 Code Quality & Formatting

```powershell
# Format code
python -m black app tests
python -m isort app tests

# Lint with Flake8
python -m flake8 app tests

# Type-check with mypy
python -m mypy app
```
