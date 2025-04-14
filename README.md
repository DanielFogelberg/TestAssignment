# Messaging Service

Test assignment, a service for sending and retrieving messages

## Features

- Submit a message to a recipient
- Fetch unread messages
- Delete a single message
- Delete multiple messages
- Fetch messages with optional pagination

## Tech Stack

- Flask
- SQLite


## Setup Instructions

### 1. Clone the repository


### 2. Install dependencies and create a virtual environment
```bash
make install
```

This sets up a virtual environment and installs all packages from `requirements.txt`.

### 3. Run the server
```bash
make run
```

The API will be available at `http://127.0.0.1:5000`.

## API Usage with `make`

### Submit a message

```bash
make submit recipient="bob@mail.com" message="Hello!"
```

### Fetch all messages
```bash
make fetch
```

### Fetch messages based on optional start, stop and recipient. Sorted by time
```bash
make fetch start=0 stop=10 recipient="alice@mail.com"
```

### Fetch unread messages
```bash
make fetch-unread
```

### Delete a single message
```bash
make delete-single id=1
```

### Delete multiple messages
```bash
make delete-multiple ids='[1,2,3]'
```

### Clean up virtual environment and database
```bash
make clean
```

## Notes

- All endpoints are accessible with `curl` or similar tools
