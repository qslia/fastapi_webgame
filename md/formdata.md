Great question! `FormData` is **not loaded from anywhere** - it's a **built-in browser API**, just like `document` that we discussed earlier.

## Where Does `FormData` Come From?

`FormData` is provided automatically by the web browser. You don't need to:
- Import it
- Declare it
- Load it from a library

It's simply **there**, ready to use!

## What is `FormData`?

`FormData` is a built-in JavaScript class that helps you create and manage form data to send to a server.

## How It's Used in Your Code:

```javascript
const formData = new FormData();           // Create an empty FormData object
formData.append('username', username);     // Add username field
formData.append('password', password);     // Add password field

const response = await fetch(endpoint, {
    method: 'POST',
    body: formData                         // Send the FormData to the server
});
```

## Why Use FormData?

| Without FormData | With FormData |
|------------------|---------------|
| Manually format data as JSON | Easy key-value pairs |
| Set headers manually | Browser handles encoding |
| More complex code | Simple, clean code |

## Simple Analogy:
Think of `FormData` like a **form-filling assistant** built into your browser:
1. You give it a blank form (`new FormData()`)
2. You fill in the fields (`.append('username', 'john')`)
3. It packages everything properly and hands it to the server

## Summary:
Just like `document`, `localStorage`, and `fetch`, `FormData` is part of the browser's built-in JavaScript environment. It's always available in any web page!