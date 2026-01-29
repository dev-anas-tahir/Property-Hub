# PropertyHub Template Architecture

This document outlines the new scalable and maintainable template structure for PropertyHub, featuring an Airbnb-inspired design with a purplish-blue color scheme.

## 🏗️ Directory Structure

```
templates/
├── _layouts/                 # Base layout templates
│   ├── base.html            # Main base template
│   ├── auth.html            # Authentication layout
│   └── dashboard.html       # Dashboard layout with sidebar
├── _components/             # Reusable UI components
│   ├── navigation/
│   │   ├── navbar.html      # Main navigation bar
│   │   └── footer.html      # Site footer
│   ├── ui/
│   │   ├── messages.html    # Flash messages
│   │   ├── loading.html     # Loading spinners
│   │   ├── pagination.html  # Pagination component
│   │   └── empty_state.html # Empty state component
│   ├── properties/
│   │   ├── property_card.html    # Property card component
│   │   ├── property_grid.html    # Property grid layout
│   │   └── favorite_button.html  # Favorite toggle button
│   └── forms/
│       ├── input.html       # Form input component
│       ├── textarea.html    # Textarea component
│       └── select.html      # Select dropdown component
├── properties/              # Property-specific pages
│   ├── list.html           # Property listing page
│   ├── detail.html         # Property detail page
│   ├── create.html         # Property creation form
│   ├── edit.html           # Property edit form
│   ├── favorites.html      # User favorites page
│   └── myprops.html        # User's properties page
├── users/                  # User-specific pages
│   ├── login.html          # Login page
│   ├── signup.html         # Registration page
│   ├── profile.html        # User profile page
│   └── password_change.html # Password change form
└── README.md               # This file
```

## 🎨 Design System

### Color Palette
- **Primary**: Purplish-blue gradient (#6366f1 to #4f46e5)
- **Secondary**: Purple accent (#d946ef to #c026d3)
- **Accent**: Orange highlights (#f97316)
- **Neutral**: Gray tones for text and backgrounds

### Typography
- **Display Font**: Poppins (headings, logos)
- **Body Font**: Inter (body text, UI elements)

### Components
- **Cards**: Rounded corners (2xl), soft shadows, hover effects
- **Buttons**: Gradient backgrounds, smooth transitions
- **Forms**: Clean inputs with focus states
- **Navigation**: Sticky header with dropdown menus

## 📱 Responsive Design

The template system uses a mobile-first approach with Tailwind CSS breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🧩 Component Usage

### Layouts

#### Base Layout
```django
{% extends '_layouts/base.html' %}
{% block content %}
  <!-- Your content here -->
{% endblock %}
```

#### Auth Layout
```django
{% extends '_layouts/auth.html' %}
{% block auth_content %}
  <!-- Auth form content -->
{% endblock %}
```

#### Dashboard Layout
```django
{% extends '_layouts/dashboard.html' %}
{% block dashboard_content %}
  <!-- Dashboard content -->
{% endblock %}
```

### Components

#### Form Input
```django
{% include '_components/forms/input.html' with field=form.email label="Email" placeholder="Enter your email" required=True %}
```

#### Property Card
```django
{% include '_components/properties/property_card.html' with property=property %}
```

#### Messages
```django
{% include '_components/ui/messages.html' %}
```

#### Pagination
```django
{% include '_components/ui/pagination.html' with page_obj=page_obj %}
```

## 🎯 Best Practices

### Template Organization
1. **Layouts**: Use for page structure and common elements
2. **Components**: Create reusable UI elements
3. **Pages**: Keep page-specific templates minimal
4. **Naming**: Use descriptive names with underscores

### Performance
1. **CSS**: Use Tailwind's utility classes for consistency
2. **Images**: Optimize and use appropriate formats
3. **JavaScript**: Minimize and use Alpine.js for interactions
4. **Caching**: Leverage Django's template caching

### Accessibility
1. **Semantic HTML**: Use proper HTML5 elements
2. **ARIA Labels**: Add labels for screen readers
3. **Keyboard Navigation**: Ensure all interactive elements are accessible
4. **Color Contrast**: Maintain WCAG AA compliance

## 🔧 Development Workflow

### Adding New Components
1. Create component in appropriate `_components/` subdirectory
2. Use consistent naming convention
3. Include proper documentation
4. Test across different screen sizes

### Modifying Layouts
1. Update base layouts carefully as they affect all pages
2. Test changes across all page types
3. Maintain backward compatibility when possible

### CSS Changes
1. Update `static/src/input.css` for custom styles
2. Run `npm run build-css-prod` to compile
3. Use Tailwind utilities when possible
4. Document custom CSS classes

## 🚀 Features

### Interactive Elements
- **Alpine.js**: For dynamic interactions
- **HTMX**: For partial page updates
- **Smooth Animations**: CSS transitions and keyframes

### Form Handling
- **Validation**: Client-side and server-side
- **Error States**: Clear error messaging
- **Loading States**: Visual feedback during submission

### Property Features
- **Image Galleries**: Responsive image displays
- **Favorite System**: Toggle favorites with AJAX
- **Search & Filters**: Advanced property filtering
- **Responsive Cards**: Optimized for all devices

## 📚 Dependencies

### CSS Framework
- **Tailwind CSS**: Utility-first CSS framework
- **DaisyUI**: Component library for Tailwind

### JavaScript Libraries
- **Alpine.js**: Lightweight reactive framework
- **HTMX**: HTML-driven interactions

### Fonts
- **Google Fonts**: Inter and Poppins font families

## 🔄 Migration Guide

If migrating from the old template structure:

1. **Backup**: Create backup of existing templates
2. **Update Views**: Change template paths in Django views
3. **Test**: Verify all pages render correctly
4. **Cleanup**: Remove old template files
5. **CSS**: Rebuild CSS with new configuration

## 🐛 Troubleshooting

### Common Issues
1. **CSS not loading**: Check static file configuration
2. **Components not rendering**: Verify template paths
3. **JavaScript errors**: Check Alpine.js and HTMX setup
4. **Responsive issues**: Test on actual devices

### Debug Tips
1. Use Django's template debug mode
2. Check browser developer tools
3. Validate HTML markup
4. Test with different browsers

## 📞 Support

For questions or issues with the template system:
1. Check this documentation first
2. Review component examples
3. Test in isolation
4. Consult Django template documentation