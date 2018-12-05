<h1 id="ibmiotf.APIException">APIException</h1>

```python
APIException(self, httpCode, message, response)
```

Exception raised when any API call fails

__Attributes__

- `httpCode (int)`: The HTTP status code returned
- `message (string)`: The exception message
- `response (string)`: The reponse body that triggered the exception

