
# AiGov Tokens (User + Admin) — Light & Dark

## Files
- tokens.light.json — light semantic tokens
- tokens.dark.json  — dark semantic tokens
- config.light.json — Style Dictionary build for :root (light)
- config.dark.json  — Style Dictionary build for [data-theme="dark"] (dark)

## Build
```bash
cd design-tokens
# copy these files into this folder first
npx style-dictionary build --config config.light.json
npx style-dictionary build --config config.dark.json
```
This generates:
- build/tokens-light.css   (attached to :root)
- build/tokens-dark.css    (attached to [data-theme="dark"])

## Use
In your app shell:
```html
<html data-theme="light"> <!-- or 'dark' -->
  ...
</html>
```

Merge both CSS files in your app:
```ts
import "design-tokens/build/tokens-light.css";
import "design-tokens/build/tokens-dark.css";
```

Toggle theme at runtime (React example):
```tsx
document.documentElement.setAttribute('data-theme', 'dark'); // or 'light'
```

No Tailwind changes required if you reference CSS variables, e.g.:
```js
// tailwind.config.js
theme: {
  colors: {
    primary: "var(--color-brand-primary)",
    body:    "var(--color-text-body)",
    card:    "var(--color-bg-card)"
  }
}
```
