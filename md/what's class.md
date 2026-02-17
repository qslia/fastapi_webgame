The `class` attribute in HTML is used to assign one or more CSS class names to an element. Let me explain:

## What `class="secondary"` Does:

```html
<button class="secondary" onclick="toggleAuthMode()">Register Instead</button>
```

### 1. **Links to CSS Styling**
The `class="secondary"` connects this button to the CSS styles defined for `.secondary`:

```css
.auth-container button.secondary {
    background-color: #4CAF50;  /* Green color */
}
.auth-container button.secondary:hover {
    background-color: #45a049;  /* Darker green on hover */
}
```

### 2. **Visual Difference**
| Button | Class | Color |
|--------|-------|-------|
| Login button | (no extra class) | Blue (#008CBA) |
| Register Instead button | `secondary` | Green (#4CAF50) |

### 3. **Why Use Classes?**
- **Reuse styles**: Multiple elements can share the same class
- **Organize code**: Keep styling separate from HTML structure
- **Easy maintenance**: Change one CSS rule to update all elements with that class

### Simple Analogy:
Think of `class` like a **label or tag** you put on an element. All elements with the same label share the same "outfit" (styling). In this case, the "secondary" label gives the button a green outfit instead of the default blue one!