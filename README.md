# Start

## Usage

#### Custom link file
The link file URL option accepts a relative path (for [self-hosting](https://github.com/runarsf/start#self-hosting)) and URLs.
<br/>Default (relative): `/static/sample-links.json`
<br/>URL Example: `https://start.runarsf.dev/static/sample-links.json`

#### Scale
Scale modifies the size of the main container. `1 = width: 20%`, `2 = width: 40%`, etc.
A scale of `4.5` is recommended if you have a lot of links.
If you accidentally set the scale to something that messes up the UI, use any of these and then reload the page:
  * Auto-fix (search box): `fix-scale`
  * To manually set the scale setting (js console): `cookies.set('setting-scale', '1');`
  * To reset all settings to their defaults (js console): `cookies.clear();`
<br/>Default: `2`

#### Link search
Typing something in the search box will look for the entered text in all links and hide the links and boxes that don't match. Hitting <kbd>Enter</kbd> will search using the defined [search engine](https://github.com/runarsf/start#search-engines).

#### JavaScript evaluation
The search box evaluates JavaScript as you type, this means that you can type `1+1`, and it will return `2`.

#### Search engines
To use the search function, type something in the search box and click <kbd>Enter</kbd>.
This will append the user input to the "Search engine" option and open it (either redirect or new tab, based on the "Open links in new tab" option).
If the input starts with 'http' or contains a period and no space, it will treat the input as a URL and open it directly using https.
If the input starts with 'r/', it will treat the following text as a subreddit and open it.
<br/>Default: `https://google.com/#q=`

#### links.json format
To see a sample configuration, open [/public/static/sample-links.json](https://github.com/runarsf/start/blob/master/public/static/sample-links.json)

## Hosting

### Self-hosting
1. Set up the repo
    ```shell
    git clone https://github.com/runarsf/start.git
    cd start
    # using node
    npm start
    # using docker-compose
    docker-compose up -d
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
    sudo nginx -t # test the config file for errors
    sudo nginx -s reload # reload the nginx service
    # or
    sudo systemctl restart nginx
    ```
4. Add an SSL certificate managed by Certbot *[optional]*
    ```shell
    $ sudo certbot --nginx
    [??�]
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    1: start.runarsf.dev
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Select the appropriate numbers separated by commas and/or spaces, or leave input
    blank to select all options shown (Enter 'c' to cancel): 1 # select the index of the domain name
    [??�]
    Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 1 # select 1
    [??�]
    Congratulations! You have successfully enabled <https://start.runarsf.dev>
    You should test your configuration at:
    <https://www.ssllabs.com/ssltest/analyze.html?d=start.runarsf.dev>
    [??�]
    ```

### Adding CORS support to custom self-hosted JSON file with Nginx
Add this to your Nginx server block and reload nginx (see [Self-hosting](https://github.com/runarsf/start#Self-hosting))
  ```nginx
  location / {
      add_header Access-Control-Allow-Origin *;
  }
  ```

