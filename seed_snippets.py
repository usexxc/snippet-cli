"""Seed snippets into database."""
import sqlite3, json
from pathlib import Path

db_path = Path.home() / '.snippet-cli' / 'snippets.db'
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(str(db_path))
conn.executescript('''
    CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        language TEXT DEFAULT 'text',
        code TEXT NOT NULL,
        tags TEXT DEFAULT '',
        is_favorite INTEGER DEFAULT 0,
        use_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    );
''')

snippets = [
    ("flask_post_route", "Flask route with POST + JSON", "python",
     """from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def handle_data():
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')
    return jsonify({'status': 'ok', 'name': name, 'value': value}), 200""",
     "flask,api,post,json"),

    ("python_read_file", "Read & write file Python", "python",
     """# Read file
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = f.readlines()

# Write file
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write('Hello World\\n')

# Append file
with open('log.txt', 'a', encoding='utf-8') as f:
    f.write('log entry\\n')""",
     "python,file,io"),

    ("python_requests", "HTTP request with requests", "python",
     """import requests

# GET
resp = requests.get('https://api.github.com/users/defunkt',
    headers={'User-Agent': 'MyApp'}, timeout=10)
data = resp.json()
print(data['login'])

# POST
resp = requests.post('https://httpbin.org/post',
    json={'name': 'John', 'age': 30})
print(resp.status_code)

# Download
resp = requests.get('https://example.com/file.pdf', stream=True)
with open('file.pdf', 'wb') as f:
    for chunk in resp.iter_content(8192):
        f.write(chunk)""",
     "python,api,http,requests"),

    ("python_decorator", "Custom Python decorators", "python",
     """import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f'{func.__name__} took {elapsed:.2f}s')
        return result
    return wrapper

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator""",
     "python,decorator,timer"),

    ("python_sqlite", "SQLite CRUD operations", "python",
     """import sqlite3

conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row
conn.execute('PRAGMA journal_mode=WAL')

conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, email TEXT UNIQUE, age INTEGER)''')

conn.execute('INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
    ('Budi', 'budi@email.com', 20))
conn.commit()

rows = conn.execute('SELECT * FROM users WHERE age > ?', (18,)).fetchall()
for row in rows:
    print(f'{row[\"id\"]}: {row[\"name\"]}')

conn.execute('UPDATE users SET age = ? WHERE name = ?', (21, 'Budi'))
conn.commit()
conn.close()""",
     "python,sqlite,database,crud"),

    ("python_datetime", "Date/time formatting Python", "python",
     """from datetime import datetime, timedelta, date

now = datetime.now()
today = date.today()

# Format
print(now.strftime('%Y-%m-%d %H:%M:%S'))       # 2026-06-11 15:30:00
print(now.strftime('%A, %d %B %Y'))             # Thursday, 11 June 2026

# Parse
dt = datetime.strptime('2026-06-11', '%Y-%m-%d')

# Arithmetic
yesterday = now - timedelta(days=1)
next_week = now + timedelta(weeks=1)

# ISO
iso = now.isoformat()""",
     "python,datetime,time"),

    ("python_list_comp", "List/dict comprehension", "python",
     """# List comprehension
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]

# Dict comprehension
sq_dict = {x: x**2 for x in range(10)}
keys = ['a', 'b']; vals = [1, 2]
mapped = {k: v for k, v in zip(keys, vals)}

# Flatten
nested = [[1,2], [3,4]]
flat = [x for sub in nested for x in sub]

# Filter None
items = [1, None, 3]
clean = [x for x in items if x is not None]""",
     "python,list,dict,comprehension"),

    ("js_fetch_api", "Fetch API with async/await", "javascript",
     """// GET
async function getUsers() {
    const resp = await fetch('https://api.example.com/users');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

// POST
async function createUser(user) {
    const resp = await fetch('https://api.example.com/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user),
    });
    return resp.json();
}""",
     "javascript,fetch,api,async"),

    ("js_dom", "DOM manipulation", "javascript",
     """// Select
const el = document.querySelector('.class');
const all = document.querySelectorAll('li');
const byId = document.getElementById('id');

// Create
const div = document.createElement('div');
div.textContent = 'Hello';
div.className = 'card';
parent.appendChild(div);

// Events
el.addEventListener('click', (e) => console.log(e.target));

// Class
el.classList.add('active');
el.classList.remove('hidden');
el.classList.toggle('visible');""",
     "javascript,dom,frontend"),

    ("go_gin_api", "REST API with Gin", "go",
     """package main

import (
    \"net/http\"
    \"github.com/gin-gonic/gin\"
)

type User struct {
    ID   int    `json:\"id\"`
    Name string `json:\"name\"`
}

var users = []User{{1, \"Alice\"}, {2, \"Bob\"}}

func main() {
    r := gin.Default()
    r.GET(\"/users\", getUsers)
    r.POST(\"/users\", createUser)
    r.Run(\":8080\")
}

func getUsers(c *gin.Context) {
    c.JSON(http.StatusOK, users)
}

func createUser(c *gin.Context) {
    var u User
    if err := c.ShouldBindJSON(&u); err != nil {
        c.JSON(400, gin.H{\"error\": err.Error()})
        return
    }
    users = append(users, u)
    c.JSON(201, u)
}""",
     "go,gin,api,rest"),

    ("go_goroutine", "Goroutine & channel patterns", "go",
     """package main

import (
    \"fmt\"
    \"sync\"
    \"time\"
)

func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func main() {
    var wg sync.WaitGroup
    for i := 1; i <= 5; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            fmt.Println(\"Done\", n)
        }(i)
    }
    wg.Wait()
}""",
     "go,goroutine,channel,concurrency"),

    ("docker_compose", "Docker Compose web + db", "docker",
     """version: \"3.8\"

services:
  web:
    build: .
    ports:
      - \"5000:5000\"
    environment:
      - FLASK_ENV=production
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:""",
     "docker,compose,postgres"),

    ("docker_multistage", "Multi-stage Dockerfile", "docker",
     """# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server .

# Run stage
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD [\"./server\"]""",
     "docker,multistage,golang"),

    ("git_undo", "Git undo & fix mistakes", "text",
     """# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Unstage file
git restore --staged file.txt

# Amend commit message
git commit --amend -m "New message"

# Revert pushed commit
git revert HEAD

# Discard all local changes
git checkout .
git clean -fd""",
     "git,undo,fix"),

    ("git_branch", "Git branch commands", "text",
     """# Create & switch
git checkout -b feature-xyz

# List
git branch -a
git branch --merged

# Delete
git branch -d feature-xyz           # local
git push origin --delete feature    # remote

# Merge
git checkout main
git merge feature-xyz

# Push new branch
git push -u origin feature-xyz""",
     "git,branch,merge"),

    ("sql_joins", "SQL JOIN cheat sheet", "sql",
     """-- INNER JOIN
SELECT u.name, o.order_date
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN
SELECT u.name, COUNT(o.id) as orders
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- Self JOIN
SELECT e.name as emp, m.name as mgr
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Multiple JOINs
SELECT u.name, p.name as product
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;""",
     "sql,join,database"),

    ("css_flexbox", "CSS Flexbox patterns", "css",
     """.container {
    display: flex;
    flex-direction: row;         /* row | column */
    flex-wrap: wrap;             /* nowrap | wrap */
    justify-content: center;     /* flex-start | center | space-between */
    align-items: center;
    gap: 16px;
}

.item {
    flex: 1;                     /* grow equally */
    flex: 0 0 300px;             /* fixed width */
}

/* Centering */
.center {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}""",
     "css,flexbox,layout"),

    ("linux_cmds", "Useful Linux commands", "text",
     """# Find
find . -name "*.py" -type f
find . -size +100M
find . -mtime -7

# Disk
du -sh *
df -h

# Network
ss -tuln            # listening ports
curl -v localhost:5000
nc -zv localhost 3306

# Process
ps aux | grep python
kill -9 PID

# Tar
tar -czf archive.tar.gz folder/
tar -xzf archive.tar.gz

# System
systemctl status nginx
journalctl -u nginx -f
free -h
uname -a""",
     "linux,command,terminal"),

    ("regex_patterns", "Common regex patterns", "text",
     """# Email
^[\\\\w.-]+@[\\\\w.-]+\\\\.\\\\w{2,}$

# Phone Indonesia
^(\\\\+62|0)8[1-9][0-9]{7,11}$

# Date YYYY-MM-DD
^\\\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\\\d|3[01])$

# IP Address
^\\\\d{1,3}\\\\.\\\\d{1,3}\\\\.\\\\d{1,3}\\\\.\\\\d{1,3}$

# Strong password
^(?=.*[A-Z])(?=.*[a-z])(?=.*\\\\d)(?=.*[!@#$%^&*])[A-Za-z\\\\d!@#$%^&*]{8,}$""",
     "regex,pattern,validation"),

    ("sql_create_table", "SQL create table with constraints", "sql",
     """CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age >= 0 AND age < 150),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- With foreign key
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
     "sql,create,table,schema"),

    ("html_template", "HTML5 basic template", "html",
     """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    <main>
        <h1>Welcome</h1>
        <p>Content here</p>
    </main>
    <script src="app.js"></script>
</body>
</html>""",
     "html,template,frontend"),
]

count = 0
for name, desc, lang, code, tags in snippets:
    try:
        conn.execute('''INSERT INTO snippets (name, description, language, code, tags)
            VALUES (?, ?, ?, ?, ?)''', (name, desc, lang, code, tags))
        count += 1
    except sqlite3.IntegrityError:
        pass

conn.commit()
total = conn.execute('SELECT COUNT(*) as c FROM snippets').fetchone()[0]
conn.close()

print(f'✅ {count} snippet baru ditambahkan!')
print(f'📦 Total: {total} snippet di database')
