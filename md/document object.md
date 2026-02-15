Great question! The `document` object is **not declared in your code** at all—it's provided automatically by the web browser!

### What is the `document` object?
The `document` object is a built-in object that represents the entire HTML page loaded in the browser. It's part of the **DOM (Document Object Model)**, which is the browser's way of letting JavaScript interact with the HTML content.

### Key Facts About `document`:
1. **Declared by the browser**: It's created automatically when your web page loads
2. **Global object**: Available everywhere in your JavaScript code (you don't need to import or declare it)
3. **Part of the browser environment**: Only exists in web browsers—not in Node.js or other JavaScript environments
4. **Represents your entire page**: It gives you access to every element on the page

### How It Works in Your Code:
```javascript
document.getElementById('score').textContent = score;
```

Breaking this down:
- `document` → The browser's built-in page object
- `.getElementById('score')` → Finds the HTML element with id="score" (your score display)
- `.textContent = score` → Changes the text content of that element to the current score value

### Think of It Like This:
The browser is like a host that provides you with tools (objects like `document`, `window`, etc.) to work with. You don't have to bring your own tools—they're already there waiting for you to use them!

### Summary:
You won't find `let document = ...` or `var document = ...` anywhere in your code. The `document` object is simply part of the web browser's JavaScript environment, ready for you to use to manipulate the HTML page.