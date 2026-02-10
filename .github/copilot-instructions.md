# Copilot Instructions

## Project Overview
This is a **Point Cloud Dataset Project Page** for ICRA 2026 - a static research website showcasing a large-scale indoor SLAM/3D reconstruction dataset. The project contains trajectory and point cloud preview data for 24+ indoor environments (libraries, offices, parking areas, etc.).

## Architecture

### Core Structure
- **`project_page.html`**: Single-page HTML application with embedded CSS and JavaScript. Uses gradient backgrounds, responsive grid layouts, and interactive elements for dataset showcase.
- **`data/preview/`**: Contains trajectory JSON files (24 sequences) and `sequences.json` metadata file that defines available datasets
- **`resources/thumbnails/`**: Directory for dataset preview images (currently empty - to be populated)

### Data Format
- **Trajectories**: Stored as JSON arrays of `[x, y, z]` coordinate triples representing camera pose history
- **Metadata**: `sequences.json` maps human-readable names to file paths with two properties per sequence:
  - `ply_path`: Path to full point cloud (.ply format)
  - `trajectory_path`: Path to corresponding trajectory JSON file

## Key Development Patterns

### Naming Conventions
- Sequences use **snake_case** with descriptive prefixes: `Basement_Ascent_Path`, `LargeHall_E1_Loop`, `Library_3F_Loop`
- Human display names may have spaces: `"LargeHall Night Half Path"` (in sequences.json)
- Always align display names with file paths to prevent 404s

### Interactive Elements
- Buttons use icon + text pattern: `.btn-icon` + text label
- Gallery items use CSS hover transforms (`transform: translateY(-2px)`)
- Videos embedded with rounded corners and shadow styling: `border-radius: 16px; box-shadow: 0 10px 40px`

### Styling System
- **Color Scheme**: Purple gradient (`#667eea` to `#764ba2`) for headers and accents
- **Responsive Design**: Uses `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))` for gallery layouts
- **Section Headers**: Underline decoration via `h2::after` pseudo-element with 60px width

## Critical Integration Points

### Adding New Sequences
1. Add trajectory JSON file to `data/preview/{name}_trajectory.json`
2. Add entry to `sequences.json` with matching `name`, `ply_path`, and `trajectory_path`
3. (Optional) Add thumbnail image to `resources/thumbnails/` and reference in HTML
4. Update HTML gallery section if adding visual previews

### Common Tasks
- **Update Metadata**: Edit `sequences.json` array - each object requires `name`, `ply_path`, `trajectory_path`
- **Style Changes**: Modify CSS in `<style>` block (lines ~8-400). Use existing gradient variables for consistency
- **Add Features**: JavaScript in `<script>` block at page end handles interactivity (3D viewers, filters, downloads)

## Dependencies & Environment
- **Build System**: None - static HTML/CSS/JS, directly openable in browsers
- **No External Dependencies**: All styling and functionality self-contained within single HTML file
- **Viewport**: Responsive design targets mobile (320px) to desktop (1200px+)

## Performance Considerations
- Point cloud preview data (trajectories) are small JSON arrays, suitable for client-side processing
- Large `.ply` files referenced but stored separately - ensure proper CDN/server configuration
- Gallery responsive grid prevents layout shifts on dynamic content loads

## Testing & Validation
- **Visual Regression**: Compare gradient colors and layout across Firefox, Chrome, Safari
- **Data Integrity**: Verify `sequences.json` entries point to valid trajectory files
- **Responsive**: Test viewport sizes: 320px (mobile), 768px (tablet), 1200px+ (desktop)
