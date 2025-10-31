# Configuration Guide

This project uses a **centralized configuration system** with a single source of truth: `config.json`. This file contains all configurable parameters for both backend and frontend.

## Benefits

✅ **Single Source of Truth** - Edit one file to change configuration for both backend and frontend
✅ **Environment Variable Override** - Any config value can be overridden via environment variables
✅ **Type Safety** - Configuration is validated and type-checked
✅ **Easy Maintenance** - No need to modify code when changing settings

## Configuration File

The main configuration file is located at the project root:

```
config.json
```

## Configuration Structure

### App-level Configuration

```json
{
  "app": {
    "name": "Image Reconstruction API",
    "version": "1.0.0",
    "description": "Image reconstruction service using PyTorch models"
  }
}
```

### Backend Configuration

```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "model": {
      "path": "backend/data/models/model.pth",
      "device": "auto",
      "device_options": ["auto", "cpu", "cuda"]
    },
    "upload": {
      "max_size_mb": 10,
      "allowed_mime_types": [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp"
      ],
      "allowed_extensions": [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
      ]
    },
    "cors": {
      "allowed_origins": ["*"],
      "allow_credentials": true,
      "allow_methods": ["*"],
      "allow_headers": ["*"]
    },
    "directories": {
      "data_dir": "backend/data",
      "uploads_dir": "backend/data/uploads",
      "outputs_dir": "backend/data/outputs",
      "models_dir": "backend/data/models"
    }
  }
}
```

### Frontend Configuration

```json
{
  "frontend": {
    "port": 5173,
    "backend_url": "http://localhost:8000",
    "polling": {
      "interval_ms": 800,
      "retry_attempts": 3
    },
    "ui": {
      "preview_enabled": true,
      "download_enabled": true,
      "show_progress_bar": true
    }
  }
}
```

## Environment Variable Overrides

Any configuration value can be overridden using environment variables. The naming convention is:

```
<SECTION>_<SUBSECTION>_<KEY> = value
```

All uppercase, with dots (`.`) replaced by underscores (`_`).

### Examples

#### Override Backend Port

**config.json:**
```json
{
  "backend": {
    "port": 8000
  }
}
```

**Environment Variable:**
```bash
# Linux/macOS
export BACKEND_PORT=9000

# Windows PowerShell
$env:BACKEND_PORT = "9000"
```

#### Override Model Path

**config.json:**
```json
{
  "backend": {
    "model": {
      "path": "backend/data/models/model.pth"
    }
  }
}
```

**Environment Variable:**
```bash
# Linux/macOS
export BACKEND_MODEL_PATH="custom/path/to/model.pth"

# Windows PowerShell
$env:BACKEND_MODEL_PATH = "custom\path\to\model.pth"
```

#### Override Max Upload Size

**config.json:**
```json
{
  "backend": {
    "upload": {
      "max_size_mb": 10
    }
  }
}
```

**Environment Variable:**
```bash
# Linux/macOS
export BACKEND_UPLOAD_MAX_SIZE_MB=20

# Windows PowerShell
$env:BACKEND_UPLOAD_MAX_SIZE_MB = "20"
```

#### Override CORS Origins (JSON Array)

**config.json:**
```json
{
  "backend": {
    "cors": {
      "allowed_origins": ["*"]
    }
  }
}
```

**Environment Variable:**
```bash
# Linux/macOS
export BACKEND_CORS_ALLOWED_ORIGINS='["http://localhost:3000", "http://localhost:5173"]'

# Windows PowerShell
$env:BACKEND_CORS_ALLOWED_ORIGINS = '["http://localhost:3000", "http://localhost:5173"]'
```

#### Override Frontend Polling Interval

**config.json:**
```json
{
  "frontend": {
    "polling": {
      "interval_ms": 800
    }
  }
}
```

**Environment Variable:**
```bash
# Linux/macOS
export FRONTEND_POLLING_INTERVAL_MS=1000

# Windows PowerShell
$env:FRONTEND_POLLING_INTERVAL_MS = "1000"
```

## Configuration Priority

The configuration system follows this priority order (highest to lowest):

1. **Environment Variables** (highest priority)
2. **config.json values**
3. **Code defaults** (lowest priority)

This means:
- Environment variables override config.json
- config.json overrides code defaults
- If nothing is set, code defaults are used

## How It Works

### Backend

1. **config_loader.py** reads `config.json` from project root
2. **config.py** uses `ConfigLoader` to build `Config` dataclass
3. Environment variables can override any config value
4. Configuration is passed to all backend services

### Frontend

1. Frontend fetches configuration from backend via `GET /api/config`
2. Backend serves frontend-specific config from `config.json`
3. Frontend applies configuration to UI behavior (polling interval, upload limits, etc.)

## Configuration Parameters Reference

### Backend Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend.host` | string | "0.0.0.0" | Backend server host |
| `backend.port` | integer | 8000 | Backend server port |
| `backend.model.path` | string | "backend/data/models/model.pth" | Path to PyTorch model file |
| `backend.model.device` | string | "auto" | Device for model inference (auto/cpu/cuda) |
| `backend.upload.max_size_mb` | float | 10 | Maximum upload size in megabytes |
| `backend.upload.allowed_mime_types` | array | ["image/png", ...] | Allowed MIME types for uploads |
| `backend.upload.allowed_extensions` | array | [".png", ...] | Allowed file extensions |
| `backend.cors.allowed_origins` | array | ["*"] | CORS allowed origins |
| `backend.directories.data_dir` | string | "backend/data" | Root data directory |
| `backend.directories.uploads_dir` | string | "backend/data/uploads" | Upload directory |
| `backend.directories.outputs_dir` | string | "backend/data/outputs" | Output directory |
| `backend.directories.models_dir` | string | "backend/data/models" | Models directory |

### Frontend Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frontend.port` | integer | 5173 | Frontend server port |
| `frontend.backend_url` | string | "http://localhost:8000" | Backend API base URL |
| `frontend.polling.interval_ms` | integer | 800 | Job status polling interval in milliseconds |
| `frontend.polling.retry_attempts` | integer | 3 | Number of retry attempts on error |
| `frontend.ui.preview_enabled` | boolean | true | Show image preview after completion |
| `frontend.ui.download_enabled` | boolean | true | Show download button |
| `frontend.ui.show_progress_bar` | boolean | true | Show progress bar during processing |

## Common Configuration Scenarios

### Development Setup

```json
{
  "backend": {
    "port": 8000,
    "cors": {
      "allowed_origins": ["http://localhost:5173"]
    },
    "model": {
      "device": "cpu"
    }
  },
  "frontend": {
    "polling": {
      "interval_ms": 500
    }
  }
}
```

### Production Setup

```json
{
  "backend": {
    "port": 8000,
    "cors": {
      "allowed_origins": ["https://yourdomain.com"]
    },
    "model": {
      "device": "cuda"
    },
    "upload": {
      "max_size_mb": 50
    }
  },
  "frontend": {
    "polling": {
      "interval_ms": 1000
    }
  }
}
```

### High-Performance Setup (GPU)

```json
{
  "backend": {
    "model": {
      "device": "cuda"
    },
    "upload": {
      "max_size_mb": 100
    }
  },
  "frontend": {
    "polling": {
      "interval_ms": 500
    }
  }
}
```

## API Endpoint

Frontend can fetch configuration from backend:

```
GET /api/config
```

Response:
```json
{
  "polling": {
    "interval_ms": 800,
    "retry_attempts": 3
  },
  "ui": {
    "preview_enabled": true,
    "download_enabled": true,
    "show_progress_bar": true
  },
  "upload": {
    "max_size_mb": 10,
    "allowed_extensions": [".png", ".jpg", ".jpeg", ".webp"],
    "allowed_mime_types": ["image/png", "image/jpeg", "image/jpg", "image/webp"]
  }
}
```

## Best Practices

1. **Don't commit secrets** - Use environment variables for sensitive data
2. **Use config.json for defaults** - Set sensible defaults in config.json
3. **Override in production** - Use environment variables for production-specific settings
4. **Document changes** - Update this file when adding new configuration options
5. **Validate values** - Backend validates configuration on startup

## Troubleshooting

### Config file not found

**Error:** `FileNotFoundError: Config file not found: config.json`

**Solution:** Ensure `config.json` exists in the project root directory.

### Invalid JSON syntax

**Error:** `json.JSONDecodeError: ...`

**Solution:** Validate your JSON syntax using a JSON validator or linter.

### Environment variable not working

**Issue:** Environment variable changes not reflected

**Solution:**
- Check variable name follows the uppercase + underscore convention
- Restart the backend server after setting environment variables
- For arrays/objects, ensure you're passing valid JSON strings

### Configuration not applied to frontend

**Issue:** Frontend still using old configuration

**Solution:**
- Clear browser cache and reload
- Check browser console for config fetch errors
- Ensure backend is running and accessible
- Verify CORS settings allow frontend to access `/api/config`

## Migration from Old Config

If you're migrating from the old environment-variable-only configuration:

1. All your existing environment variables will still work
2. You can gradually move settings to `config.json`
3. Environment variables always take precedence
4. No code changes needed - backward compatible

## See Also

- `backend/config_loader.py` - Configuration loader implementation
- `backend/config.py` - Backend configuration module
- `frontend/script.js` - Frontend configuration usage
