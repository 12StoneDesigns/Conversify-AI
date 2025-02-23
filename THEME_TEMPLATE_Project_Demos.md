# Neon Cyberpunk Theme Template

This template describes the visual styling and components used in the project.

## Color Palette

```css
/* Primary Colors */
--background-dark: #0A0A0F;     /* Main background */
--card-background: #1A1A1F;     /* Header, footer, card background */
--neon-blue: #00F3FF;          /* Links, interactive elements */
--neon-green: #39FF14;         /* Headings, brand text */
```

## Component Styles

### Header
```css
/* Header Container */
.header {
  background-color: #1A1A1F;
  border-bottom: 1px solid rgba(0, 243, 255, 0.3);
  padding: 1rem;
}

/* Navigation Links */
.nav-link {
  color: rgba(0, 243, 255, 0.9);
  transition: color 0.2s;
}
.nav-link:hover {
  color: #00F3FF;
}

/* Brand Text */
.brand-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #39FF14;
}
```

### Footer
```css
/* Footer Container */
.footer {
  background-color: #1A1A1F;
  border-top: 1px solid rgba(0, 243, 255, 0.3);
  padding: 1rem;
  text-align: center;
}

/* Footer Links */
.footer-link {
  color: rgba(0, 243, 255, 0.9);
  margin: 0 0.5rem;
}
.footer-link:hover {
  color: #39FF14;
}
```

### Cards
```css
/* Basic Card */
.card {
  background-color: #1A1A1F;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Neon Card */
.neon-card {
  border: 1px solid rgba(0, 243, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
}
```

### Back to Projects Link
```css
.back-link {
  color: #00F3FF;
  transition: color 0.2s;
}
.back-link:hover {
  color: #39FF14;
}
```

## Animations

```css
/* Neon Pulse Animation */
@keyframes neonPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-neon {
  animation: neonPulse 2s ease-in-out infinite;
}
```

## Typography

```css
/* Headings */
.heading-primary {
  font-size: 2.25rem; /* 36px */
  font-weight: 800;
  color: #39FF14;
  letter-spacing: -0.025em;
}

.heading-secondary {
  font-size: 1.875rem; /* 30px */
  color: #00F3FF;
}

/* Body Text */
body {
  background-color: #0A0A0F;
  color: white;
  font-family: system-ui, -apple-system, sans-serif;
}
```

## Layout Components

### Header Implementation
```jsx
<header className="bg-[#1A1A1F] border-b border-[#00F3FF]/30">
  <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
    <div className="flex items-center">
      <Link to="/" className="flex items-center">
        <h1 className="text-2xl font-bold text-[#39FF14]">Brand</h1>
      </Link>
    </div>
    <nav className="flex space-x-6">
      <Link to="/" className="text-[#00F3FF]/90 hover:text-[#00F3FF] transition-colors">
        Home
      </Link>
      <Link to="/about" className="text-[#00F3FF]/90 hover:text-[#00F3FF] transition-colors">
        About
      </Link>
    </nav>
  </div>
</header>
```

### Footer Implementation
```jsx
<footer className="bg-[#1A1A1F] border-t border-[#00F3FF]/30">
  <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 text-center">
    <p className="text-[#00F3FF]/90">
      &copy; {new Date().getFullYear()} Your Brand. All rights reserved.
    </p>
    <div className="mt-2">
      <Link to="/privacy" className="text-[#00F3FF]/90 hover:text-[#39FF14] mx-2">
        Privacy Policy
      </Link>
      <Link to="/terms" className="text-[#00F3FF]/90 hover:text-[#39FF14] mx-2">
        Terms of Service
      </Link>
    </div>
  </div>
</footer>
```

### Back to Projects Link Implementation
```jsx
<a 
  href="https://your-projects-url.com"
  className="absolute left-8 top-4 text-[#00F3FF] hover:text-[#39FF14] transition-colors duration-200"
  target="_blank"
  rel="noopener noreferrer"
>
  ← Back to Projects
</a>
```

### Card Implementation
```jsx
<div className="bg-[#1A1A1F] rounded-lg p-6 shadow-lg">
  <div 
    className="animate-neon"
    style={{
      boxShadow: '0 0 20px rgba(0, 243, 255, 0.3)',
      border: '1px solid rgba(0, 243, 255, 0.2)'
    }}
  >
    {/* Card content */}
  </div>
</div>
```

## Usage Notes

1. The theme uses a dark background (#0A0A0F) with neon accents in blue (#00F3FF) and green (#39FF14).
2. Interactive elements (links, buttons) use the neon blue color with a hover state that either brightens or changes to neon green.
3. Cards and containers use a slightly lighter background (#1A1A1F) with neon borders and shadows for depth.
4. The neon effect is achieved through a combination of:
   - Semi-transparent borders (opacity: 0.3)
   - Box shadows with blue glow
   - Pulse animations for dynamic elements
5. Typography uses system fonts with bold weights for headings and regular weight for body text.
