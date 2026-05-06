# Chronicles of Documents - Frontend

Modern Next.js frontend for the Chronicles of Documents system.

## Features

- 🎨 Clean Material-UI design (white & gray theme)
- 📱 Responsive layout with collapsible sidebar
- 📄 Case management interface
- 📤 Drag & drop file upload
- 📊 Real-time scan progress tracking
- 🔍 Document status monitoring

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Material-UI 6** - Component library
- **Axios** - API client
- **React Dropzone** - File upload

## Setup

### Option 1: Docker (Recommended)

```bash
# Start all services (backend + frontend)
docker-compose -f docker-compose.simple.yml up --build

# Access frontend at http://localhost:3000
```

### Option 2: Local Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

## Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── cases/             # Case management pages
│   │   ├── [id]/         # Case details page
│   │   ├── new/          # Create case page
│   │   └── page.tsx      # Cases list page
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page (redirects)
│   └── globals.css       # Global styles
├── components/            # React components
│   ├── Layout.tsx        # Main layout with sidebar
│   ├── Sidebar.tsx       # Collapsible sidebar
│   ├── Footer.tsx        # App footer
│   ├── FileUploadDialog.tsx  # File upload modal
│   └── ThemeProvider.tsx # MUI theme config
├── lib/                   # Utilities
│   └── api.ts            # API client & types
└── package.json          # Dependencies
```

## Pages

### Cases List (`/cases`)
- View all cases in grid layout
- Stats overview (total cases, documents, active)
- Create new case button

### Case Details (`/cases/[id]`)
- View case information
- Upload documents (drag & drop)
- Start document scan
- Monitor scan progress
- View document status table

### New Case (`/cases/new`)
- Create new case form
- Case number, title, description
- Form validation

## Components

### Layout
Main application layout with:
- Fixed header with app title
- Collapsible sidebar (280px expanded, 70px collapsed)
- Main content area
- Footer

### Sidebar
- List of all cases
- Expand/collapse animation
- Active case highlighting
- New case and refresh buttons
- Document count badges

### FileUploadDialog
- Drag & drop file upload
- File type validation (PDF, DOCX, DOC, PNG, JPG, JPEG)
- File size validation (max 50MB)
- Upload progress indicator
- File list with remove option

## API Integration

All API calls are in `lib/api.ts`:

```typescript
import { createCase, uploadDocuments, startScan, getScanStatus } from '@/lib/api';

// Create case
const newCase = await createCase({
  case_number: 'CASE-2024-001',
  title: 'My Case',
  description: 'Optional description'
});

// Upload documents
const result = await uploadDocuments(caseId, files);

// Start scan
await startScan(caseId);

// Get status
const status = await getScanStatus(caseId);
```

## Theme Customization

Edit `components/ThemeProvider.tsx`:

```typescript
const theme = createTheme({
  palette: {
    primary: {
      main: '#2c3e50',  // Dark blue-gray
    },
    secondary: {
      main: '#3498db',  // Light blue
    },
    background: {
      default: '#f5f5f5',  // Light gray
      paper: '#ffffff',     // White
    },
  },
});
```

## Security

- Latest Next.js 15 (no vulnerabilities)
- Latest Material-UI 6
- Updated dependencies
- No known security issues

## Build for Production

```bash
# Build
npm run build

# Start production server
npm start
```

## Docker Production Build

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting

### Port 3000 already in use
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
PORT=3001 npm run dev
```

### API connection failed
- Check backend is running at http://localhost:8000
- Verify NEXT_PUBLIC_API_URL in .env.local
- Check CORS settings in backend

### Module not found errors
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

## Contributing

1. Follow TypeScript best practices
2. Use Material-UI components
3. Keep components small and focused
4. Add proper error handling
5. Test API integrations

## License

MIT
