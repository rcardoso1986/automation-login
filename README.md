# H&W Simultaneous Login Test System (Dockerized, Python 3.11, Flask, Selenium WebDriver with Chrome)

## Overview

This application allows you to test and monitor multiple parallel login attempts to verify system performance and authentication reliability. It provides real-time feedback on each login attempt, including execution time, success/failure status, and session tokens.

## Features

- **Parallel Execution**: Execute multiple login attempts simultaneously
- **Real-time Monitoring**: Live updates as each login completes
- **Statistics Dashboard**: View success rate, failure count, and total execution time
- **Detailed Results**: Individual login status, tokens, and execution time
- **Clean Interface**: Simple Bootstrap-based UI
- **Docker Support**: Easy deployment with Docker and Docker Compose

---

## Requirements

- Docker and Docker Compose installed
- Ports 5000 available

## Getting Started

1. **Build and start all services:**

```bash
# Build the image
docker build -t login-automation .

# Run the container
docker compose up

# Access the application
# Open your browser at http://localhost:5000
```

## How to Use

1. **Access the Web Interface**: Open `http://localhost:5000` in your browser
2. **Set Login Quantity**: Enter the number of simultaneous logins (1-50)
3. **Execute**: Click the "Executar" button
4. **Monitor Results**: Watch real-time updates as each login completes
5. **View Statistics**: Check the summary cards for success/failure rates and total time

## Results

Each login attempt returns:

- **Login ID**: Sequential identifier
- **Status**: SUCCESS or FAILURE
- **Token**: Session token (truncated for display)
- **Time**: Execution time in seconds
- **Message**: Success/error message

## Performance

- **Parallel Execution**: Uses Python's `ThreadPoolExecutor` for efficient parallel processing
- **Headless Chrome**: Runs without GUI for better performance
- **Resource Optimization**: Properly manages WebDriver instances

## Troubleshooting

### Chrome/ChromeDriver Version Mismatch

The application uses Selenium Manager to automatically download compatible ChromeDriver versions. If you see warnings, they can usually be ignored.

### Slow Execution

- Reduce the number of simultaneous logins
- Check network connectivity
- Verify target website availability

## License

MIT