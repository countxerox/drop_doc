# drop_doc

A lightweight self-hosted document drop page. Visitors can upload files via drag-and-drop or by browsing from their file system.

## Features

- Drag-and-drop file uploads
- Browse/select file uploads
- Multi-file upload support
- Basic file-type allowlist for common document formats
- Max request size limit (50MB)

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8000`.

## Deploy on Ubuntu VM (Proxmox)

1. Install system packages:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip nginx
   ```

2. Copy this repo to your VM, then inside the project folder:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create a systemd service at `/etc/systemd/system/drop_doc.service`:

   ```ini
   [Unit]
   Description=Drop Doc upload site
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/drop_doc
   Environment="PATH=/opt/drop_doc/.venv/bin"
   ExecStart=/opt/drop_doc/.venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. Install gunicorn into the venv:

   ```bash
   source /opt/drop_doc/.venv/bin/activate
   pip install gunicorn
   ```

5. Enable/start service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now drop_doc
   sudo systemctl status drop_doc
   ```

6. Configure nginx at `/etc/nginx/sites-available/drop_doc`:

   ```nginx
   server {
       listen 80;
       server_name _;

       client_max_body_size 50M;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

7. Enable the site:

   ```bash
   sudo ln -s /etc/nginx/sites-available/drop_doc /etc/nginx/sites-enabled/drop_doc
   sudo nginx -t
   sudo systemctl reload nginx
   ```

Your upload directory is `uploads/` in the project root.
