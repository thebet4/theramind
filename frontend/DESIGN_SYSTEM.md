# TheraMind Design System

## Color Tokens

All colors are defined as reusable CSS custom properties (CSS variables) in `src/index.css`. They automatically support both light and dark modes.

### Primary Colors - Calming Therapeutic Palette

```css
--primary: 200 95% 50%        /* Calming blue - main brand color */
--primary-foreground: 0 0% 100%  /* White text on primary */
```

### Secondary Colors - Trust & Professionalism

```css
--secondary: 220 15% 95%         /* Light gray for subtle backgrounds */
--secondary-foreground: 220 15% 20%  /* Dark text on secondary */
```

### Accent Colors - Warmth & Empathy

```css
--accent: 340 75% 60%            /* Warm pink/red for emphasis */
--accent-foreground: 0 0% 100%   /* White text on accent */
```

### Background & Surface Colors

```css
--background: 0 0% 100%          /* Main page background (white) */
--foreground: 220 15% 15%        /* Main text color (dark) */
--card: 0 0% 100%                /* Card background */
--card-foreground: 220 15% 15%   /* Card text color */
```

### Muted Colors - Subtle Elements

```css
--muted: 220 15% 96%             /* Muted background (very light gray) */
--muted-foreground: 220 15% 45%  /* Muted text color (medium gray) */
```

### Border & Input Colors

```css
--border: 220 15% 90%            /* Border color */
--input: 220 15% 90%             /* Input border color */
--ring: 200 95% 50%              /* Focus ring color (matches primary) */
```

### State Colors

```css
--success: 142 76% 36%           /* Success/positive actions (green) */
--warning: 38 92% 50%            /* Warning/caution (orange) */
--destructive: 0 84% 60%         /* Error/destructive actions (red) */
```

### Chart/Data Visualization Colors

```css
--chart-1: 200 95% 50%           /* Primary chart color */
--chart-2: 160 75% 45%           /* Secondary chart color (teal) */
--chart-3: 340 75% 60%           /* Tertiary chart color (pink) */
--chart-4: 280 65% 55%           /* Quaternary chart color (purple) */
--chart-5: 45 85% 55%            /* Quinary chart color (yellow) */
```

## Using Color Tokens

### In Tailwind CSS Classes

```tsx
<div className="bg-primary text-primary-foreground">
  Primary colored element
</div>

<div className="bg-accent hover:bg-accent/90">
  Accent colored button with hover state
</div>

<div className="border border-border text-muted-foreground">
  Subtle bordered element with muted text
</div>
```

### In Custom CSS

```css
.custom-element {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border: 1px solid hsl(var(--border));
}
```

## Typography

The design system uses **Inter** font family for a modern, professional look:

```css
font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto",
  ...;
```

## Components

All components are built with shadcn UI principles and are located in `src/components/ui/`:

- **Button** - `src/components/ui/button.tsx`

  - Variants: `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`
  - Sizes: `default`, `sm`, `lg`, `xl`, `icon`

- **Card** - `src/components/ui/card.tsx`

  - Exports: `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`

- **Badge** - `src/components/ui/badge.tsx`
  - Variants: `default`, `secondary`, `destructive`, `outline`

## Gradients

Special gradient effects for hero elements:

```tsx
<span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
  Gradient Text
</span>

<div className="bg-gradient-to-br from-primary/10 to-accent/10">
  Subtle gradient background
</div>
```

## Animations

Custom gradient animation for hero text:

```css
.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}
```

## Spacing & Layout

Uses standard Tailwind spacing scale with custom radius:

```css
--radius: 0.5rem; /* Default border radius for cards and buttons */
```

## Dark Mode

The design system automatically supports dark mode. All color tokens have dark mode variants defined in the `:root.dark` selector.

To toggle dark mode, add the `dark` class to the `<html>` element:

```html
<html class="dark"></html>
```

## Best Practices

1. **Always use color tokens** instead of hardcoded colors
2. **Use semantic color names** (primary, accent, muted) rather than specific color values
3. **Leverage Tailwind utilities** for consistency
4. **Test in both light and dark modes**
5. **Maintain accessibility** - ensure sufficient color contrast for text
