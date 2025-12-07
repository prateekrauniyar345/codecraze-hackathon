# ScholarSense Frontend

React + Vite frontend for ScholarSense - AI-powered application assistant.

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

The default configuration connects to `http://localhost:8000` for the backend API.

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at http://localhost:5173

### 4. Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Features

- **Authentication**: User registration and login with JWT
- **Resume Upload**: Upload PDF/DOCX resumes with automatic text extraction
- **Profile Management**: Automatic profile creation from uploaded resumes
- **Opportunity Analysis**: AI-powered fit analysis for jobs/internships/scholarships
- **Material Generation**: Auto-generate emails, subject lines, SOPs, and fit bullets
- **Dashboard**: Track all opportunities with status management
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework
- **React Icons** - Icon library
- **React Toastify** - Toast notifications

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # API client and endpoints
│   ├── components/
│   │   ├── Layout.jsx          # Main layout with sidebar
│   │   └── PrivateRoute.jsx    # Protected route wrapper
│   ├── context/
│   │   └── AuthContext.jsx     # Authentication context
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Upload.jsx
│   │   ├── AnalyzeOpportunity.jsx
│   │   ├── Opportunities.jsx
│   │   ├── OpportunityDetail.jsx
│   │   └── GenerateMaterials.jsx
│   ├── App.jsx                 # Main app component with routes
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Usage Flow

1. **Register/Login**: Create an account or sign in
2. **Upload Resume**: Upload your resume (PDF or DOCX)
3. **Analyze Opportunities**: Paste job postings to see fit scores
4. **Generate Materials**: Create tailored application materials
5. **Track Applications**: Manage status of all opportunities

## API Integration

The frontend communicates with the FastAPI backend through the axios client in `src/api/client.js`. All API calls include:

- Automatic JWT token attachment
- Error handling with automatic logout on 401
- Request/response interceptors
- Toast notifications for errors

## Styling

The app uses Tailwind CSS with custom utility classes defined in `index.css`:

- `.btn` - Base button styles
- `.btn-primary` - Primary button variant
- `.btn-secondary` - Secondary button variant
- `.input` - Form input styles
- `.card` - Card container styles

Dark mode is supported via Tailwind's dark mode classes.
