# description

The problem is with a username of `'i\n3?"Ru7/v\x0c\r\'M|I$H<HiMiEyd[I)'`,
represented here as a Python string. In JSON encoding, I believe this is
`"i\n3?\"Ru7/v\f\r'M|I$H<HiMiEyd[I)"`.

When submitting the data, the client encodes the JSON data as UTF-8, and the
api correctly guesses or checks that the encoding is UTF-8.

However, the api does not include `charset` in its Content-Type response
headers, and the `httpx` library incorrectly guesses Shift JIS 2004, which
results in the content being interpreted as
`{"id":2,"username":"i¥n3?¥"Ru7/v¥f¥r\'M|I$H<HiMiEyd[I)"}`, which is not valid
JSON.

It's trivial to set the encoding for the response content manually in the
client, but setting it at each place that makes a request would be annoying,
and it'd be nice to be able to set the response encoding and `charset` in the
api.

# analysis

It turns out that a Content-Type of `application/json` means the receiver
should check the content's initial byte sequence to determine its
encoding, as described succinctly in [the responses to a similar
suggestion.](https://github.com/request/request/issues/383)

There is an easy way to get `;charset=UTF-8` appended to `application/json` in
responses from the api:

```python
@app.middleware("http")
    async def add_charset_to_json(request, call_next):
        response = await call_next(request)
        if "Content-Type" not in response.headers:
            return response
        if response.headers["Content-Type"] != "application/json":
            return response
        response.headers["Content-Type"] = "application/json;charset=UTF-8"
        return response
```

But that's not necessary.

In light testing, `requests` has no problem with the same response that `httpx`
struggles with. `httpx` should be modified to prefer `utf-8` for
`application/json`.

`make_async_client()` can probably have another hook added to set the encoding
to `utf-8` on all responses with `Content-Type: application/json` in the
headers.

This makes a great case for testing the roundtrip creation with
[hypothesis,](https://pydantic-docs.helpmanual.io/hypothesis_plugin/) which
probably would have caught this error quite quickly, compared to how many tests
had to submit a random username to the api before this came up.
