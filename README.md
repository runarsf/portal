# Start

### Custom self-hosted JSON file with Nginx and CORS
Add this to your Nginx server block and reload nginx (see [Self-hosting](https://github.com/runarsf/start#Self-hosting))
  ```nginx
  location / {
      add_header Access-Control-Allow-Origin *;
  }
  ```

### Self-hosting
1. Set up the repo
    ```shell
    $ git clone https://github.com/runarsf/start.git
    $ cd start
    $ npm start
    ```
2. Modify your Nginx config (`/etc/nginx/sites-available/default`)
This is an example for the domain `https://start.runarsf.dev`
    ```nginx
    server {
            listen 80;
            server_name start.runarsf.dev;

            location / {
                proxy_pass       http://localhost:4180;
                proxy_set_header Host      $host;
                proxy_set_header X-Real-IP $remote_addr;
                      
    }
    ```
3. Check config and restart Nginx
    ```shell
    $ sudo nginx -t # test the config file for errors
    $ sudo nginx -s reload # reload the nginx service
    # or
    $ sudo systemctl restart nginx
    ```
4. Add an SSL certificate managed by Certbot *[optional]*
    ```shell
    $ sudo certbot --nginx
    […]
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    1: start.runarsf.dev
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Select the appropriate numbers separated by commas and/or spaces, or leave input
    blank to select all options shown (Enter 'c' to cancel): 1 # select the index of the domain name
    […]
    Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 1 # select 1
    […]
    Congratulations! You have successfully enabled <https://start.runarsf.dev>
    You should test your configuration at:
    <https://www.ssllabs.com/ssltest/analyze.html?d=start.runarsf.dev>
    […]
    ```