# Project Page Design System

This document outlines the design system used for project pages on the 12Stone Designs website.

## Colors

### Primary Colors
- Background: `#0A0A0F` (Page background)
- Card Background: `#1A1A1F` (Component background)
- Neon Blue: `#00F3FF` (Description text, links)
- Neon Green: `#39FF14` (Titles, headings)
- Gray Text: `text-[#00F3FF]/90` (Regular text with 90% opacity)

### Borders & Opacity
- Border Color: `border-[#00F3FF]/30` (30% opacity neon blue)
- Card Background: `bg-[#1A1A1F]` (Solid)
- Hover States: `hover:bg-[#00F3FF]/10` (10% opacity neon blue)

## Card Styles

### Key Feature Cards
```jsx
<div className="bg-[#1A1A1F] p-6 rounded-xl border border-[#00F3FF]/30">
  <div className="text-4xl mb-4">{icon}</div>
  <h3 className="text-xl font-bold text-[#39FF14] mb-2">{title}</h3>
  <p className="text-[#00F3FF]/90">{description}</p>
</div>
```

### Tech Stack Cards
```jsx
<div className="bg-[#1A1A1F] p-6 rounded-xl border border-[#00F3FF]/30">
  <h3 className="text-xl font-bold text-[#39FF14] mb-4">{category}</h3>
  <ul className="space-y-2">
    {items.map(item => (
      <li className="text-[#00F3FF]/90">{item}</li>
    ))}
  </ul>
</div>
```

### Feature Cards
```jsx
<div className="bg-[#1A1A1F] p-4 rounded-lg border border-[#00F3FF]/30 text-[#00F3FF]/90">
  {feature}
</div>
```

### Technology Tags
```jsx
<span className="bg-[#1A1A1F] px-4 py-2 rounded-full border border-[#00F3FF]/30 text-[#00F3FF]/90">
  {techName}
</span>
```

### Installation Code Block
```jsx
<div className="bg-[#1A1A1F] p-6 rounded-xl border border-[#00F3FF]/30">
  <div className="font-mono mb-2 text-[#00F3FF]/90">$ {command}</div>
</div>
```

### Additional Content Cards
```jsx
<section className="bg-[#1A1A1F] rounded-xl p-6 border border-[#00F3FF]/30">
  <h3 className="text-xl font-bold text-[#39FF14] mb-4">{title}</h3>
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div>
      <h4 className="text-lg font-semibold text-[#39FF14] mb-2">{subtitle}</h4>
      <ul className="space-y-2 text-[#00F3FF]/90">
        <li>• {item}</li>
      </ul>
    </div>
  </div>
</section>
```

## Typography

### Headers
- Page Title: `text-4xl font-bold text-[#39FF14]`
- Section Headers: `text-2xl font-bold text-[#39FF14]`
- Card Titles: `text-xl font-bold text-[#39FF14]`
- Category Headers: `text-xl font-bold text-[#39FF14]`
- Subtitles: `text-lg font-semibold text-[#39FF14]`

### Body Text
- Description: `text-xl text-[#00F3FF]/90`
- Regular Text: `text-[#00F3FF]/90`
- List Items: `text-[#00F3FF]/90`

## Layout

### Grid Systems
- Key Features: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`
- Tech Stack: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`
- Features: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`

### Spacing
- Section Spacing: `mb-12`
- Card Padding (Large): `p-6`
- Card Padding (Small): `p-4`
- List Spacing: `space-y-2`
- Grid Gap: `gap-6`

### Borders & Rounded Corners
- Large Cards: `rounded-xl`
- Small Cards: `rounded-lg`
- Tags: `rounded-full`

## Interactive Elements

### Navigation Links
```jsx
<Link 
  to="/projects" 
  className="inline-flex items-center text-[#00F3FF] hover:text-[#39FF14] transition-colors mb-8"
>
  <span className="mr-2">←</span> Back to Projects
</Link>
```

### Links
```jsx
<Link className="text-[#00F3FF] hover:text-[#39FF14] transition-colors">
  {content}
</Link>
```

### Buttons
```jsx
<a className="bg-[#1A1A1F] px-6 py-3 rounded-lg border border-[#00F3FF]/30 hover:bg-[#00F3FF]/10 transition-colors text-[#00F3FF]">
  {content}
</a>
```

## Best Practices

1. Maintain consistent spacing between sections (mb-12)
2. Use appropriate rounded corners based on element size
3. Include hover states for interactive elements
4. Follow the color hierarchy:
   - Neon Green (#39FF14) for all titles and headings
   - Neon Blue (#00F3FF) for descriptions and interactive elements
   - Use 90% opacity for regular text
5. Use grid layouts that adapt to different screen sizes
6. Include proper padding and spacing within cards
7. Maintain consistent border opacity (30%)
8. Use semantic HTML structure for better accessibility
