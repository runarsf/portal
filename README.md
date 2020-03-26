# portal

### Starting

```bash
docker-compose up -d
```

### Logging

```bash
docker-compose logs -f
```

### Changing container port

```bash
$ vim .env

===
PORT=8080
===
```

### Adding SSL cert

```bash
# Replace 'portal.example.com' with your desired domain.
# Alternatively put it directly in '/etc/nginx/sites-available/default'
$ sudo vim /etc/nginx/sites-available/portal.example.com

===
server {
  listen 80;
  listen [::]:80;
  # Replace 'portal.example.com' with your desired domain.
  server_name portal.example.com;

  location / {
    return 301 https://$host$request_uri;
  }
}
server {
  listen 443 ssl;
  listen [::]:443 ssl;
  # Replace 'portal.example.com' with your desired domain.
  server_name portal.example.com;

  location / {
    # Replace '127.0.0.1' with the IP of the container.
    # Replace '80' with the port of the container.
    proxy_pass       http://127.0.0.1:80;
    proxy_set_header Host      $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
===

# Test/validate nginx configuration
$ sudo nginx -t
# Aquire letsencrypt certificate, follow instructions (select no-redirect)
$ sudo certbot --nginx
# Test/validate nginx configuration
$ sudo nginx -t
# Reload nginx configuration
$ sudo nginx -s reload

```

### Adding your own links:

  * Copy `sample-links.json` to `links.json` and modify `links.json`.
    * `sample-links.json` will be loaded in case `links.json` failed to fetch.
