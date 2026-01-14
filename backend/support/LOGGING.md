# Logging Configuration

## Overview

The application uses Python's built-in logging module with a rotating file handler to manage logs efficiently.

## Log Files

Located in `backend/logs/`:
- `app.log` - All application logs (INFO, DEBUG, WARNING, ERROR)
- `error.log` - Only ERROR level logs

## Log Rotation

- Maximum file size: 10 MB
- Backup count: 5 files
- Old logs are automatically rotated when size limit is reached

## Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational events (user actions, system events)
- **WARNING**: Non-critical issues (failed login attempts, limit warnings)
- **ERROR**: Critical failures requiring attention

## Logged Events

### Authentication
- User login attempts (success/failure)
- Token generation
- Invalid credentials
- Inactive account access attempts

### User Management
- User registration
- Profile updates
- Account deletion/deactivation
- Admin actions

### Image Processing
- Image upload and processing
- Operation type and parameters
- Processing success/failure
- Image deletion

### Subscriptions
- Plan upgrades/downgrades
- Operation limit checks
- Operation count increments

### Authorization
- Token validation failures
- Admin access attempts
- Permission denied events

## Log Format

```
YYYY-MM-DD HH:MM:SS - module_name - LEVEL - message
```

Example:
```
2026-01-15 00:09:04 - app.auth_service - INFO - User authenticated successfully: john_doe (ID: 123)
```
