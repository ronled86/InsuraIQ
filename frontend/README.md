# Frontend Development Guide

## 🏗️ Architecture

The frontend is built with:
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Supabase Client**: Authentication integration
- **CSS Modules**: Scoped styling

## 📁 Project Structure

```
frontend/
├── src/
│   ├── ui/
│   │   └── App.tsx              # Main application component
│   ├── styles/
│   │   └── app.css              # Global styles
│   └── main.tsx                 # Application entry point
├── index.html                   # HTML template
├── package.json                 # Dependencies and scripts
├── tsconfig.json                # TypeScript configuration
├── vite.config.ts               # Vite build configuration
├── Dockerfile                   # Docker build instructions
└── .env.example                 # Environment variables template
```

## 🚀 Setup and Installation

### Quick Start

```bash
cd frontend
npm install
npm run dev
```

### Detailed Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your settings
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

5. **Preview production build**:
   ```bash
   npm run preview
   ```

## 📦 Dependencies

### Core Dependencies

```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.45.5",  // Authentication client
    "react": "^18.3.1",                  // UI framework
    "react-dom": "^18.3.1"              // DOM rendering
  }
}
```

### Development Dependencies

```json
{
  "devDependencies": {
    "@types/react": "^18.3.4",          // React TypeScript types
    "@types/react-dom": "^18.3.0",      // React DOM TypeScript types
    "@vitejs/plugin-react": "^4.0.0",   // Vite React plugin
    "typescript": "^5.5.4",             // TypeScript compiler
    "vite": "^5.4.1"                    // Build tool and dev server
  }
}
```

## ⚙️ Configuration

### Vite Configuration (vite.config.ts)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Optional: Proxy API calls to backend
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

### TypeScript Configuration (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Environment Variables

Create `.env.local` for local development:

```bash
# Supabase Configuration (optional)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
```

## 🔗 API Integration

### Basic API Client

```typescript
// src/services/api.ts
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

export class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }
    
    return response.json()
  }

  async getPolicies(): Promise<Policy[]> {
    return this.request<Policy[]>('/policies/')
  }

  async createPolicy(policy: CreatePolicyRequest): Promise<Policy> {
    return this.request<Policy>('/policies/', {
      method: 'POST',
      body: JSON.stringify(policy),
    })
  }
}

export const apiClient = new ApiClient()
```

### Authentication Integration

```typescript
// src/services/auth.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)

export class AuthService {
  async getToken(): Promise<string | null> {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token || null
  }

  async signIn(email: string, password: string) {
    return supabase.auth.signInWithPassword({ email, password })
  }

  async signOut() {
    return supabase.auth.signOut()
  }
}

export const authService = new AuthService()
```

### Authenticated API Requests

```typescript
// Enhanced API client with authentication
export class AuthenticatedApiClient extends ApiClient {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await authService.getToken()
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  protected async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const authHeaders = await this.getAuthHeaders()
    
    return super.request<T>(endpoint, {
      ...options,
      headers: {
        ...authHeaders,
        ...options.headers,
      },
    })
  }
}
```

## 🎨 Styling

### CSS Modules

```css
/* src/components/PolicyCard.module.css */
.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin: 8px 0;
}

.title {
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 8px;
}

.premium {
  color: #2e7d32;
  font-weight: bold;
}
```

```typescript
// src/components/PolicyCard.tsx
import styles from './PolicyCard.module.css'

interface PolicyCardProps {
  policy: Policy
}

export function PolicyCard({ policy }: PolicyCardProps) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>{policy.insurer}</h3>
      <p className={styles.premium}>
        ${policy.premium_monthly}/month
      </p>
    </div>
  )
}
```

### Global Styles

```css
/* src/styles/app.css */
:root {
  --primary-color: #1976d2;
  --secondary-color: #dc004e;
  --success-color: #2e7d32;
  --warning-color: #f57c00;
  --error-color: #d32f2f;
  --text-primary: #212121;
  --text-secondary: #757575;
  --background-default: #fafafa;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
  background-color: var(--background-default);
  color: var(--text-primary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}
```

## 🧩 Component Architecture

### Type Definitions

```typescript
// src/types/policy.ts
export interface Policy {
  id: number
  user_id: string
  owner_name: string
  insurer: string
  product_type: string
  policy_number: string
  start_date: string
  end_date: string
  premium_monthly: number
  deductible: number
  coverage_limit: number
  notes: string
  active: boolean
  updated_at: string
}

export interface CreatePolicyRequest {
  owner_name: string
  insurer: string
  product_type: string
  policy_number: string
  start_date: string
  end_date: string
  premium_monthly: number
  deductible: number
  coverage_limit: number
  notes?: string
}
```

### React Hooks

```typescript
// src/hooks/usePolicies.ts
import { useState, useEffect } from 'react'
import { Policy } from '../types/policy'
import { apiClient } from '../services/api'

export function usePolicies() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPolicies() {
      try {
        const data = await apiClient.getPolicies()
        setPolicies(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchPolicies()
  }, [])

  const addPolicy = async (policy: CreatePolicyRequest) => {
    const newPolicy = await apiClient.createPolicy(policy)
    setPolicies(prev => [...prev, newPolicy])
  }

  return { policies, loading, error, addPolicy }
}
```

### Error Boundary

```typescript
// src/components/ErrorBoundary.tsx
import React, { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <details>
            {this.state.error?.message}
          </details>
        </div>
      )
    }

    return this.props.children
  }
}
```

## 🔄 State Management

### Context API (Simple State)

```typescript
// src/context/AppContext.tsx
import React, { createContext, useContext, useReducer } from 'react'

interface AppState {
  user: User | null
  policies: Policy[]
  loading: boolean
}

type AppAction = 
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_POLICIES'; payload: Policy[] }
  | { type: 'SET_LOADING'; payload: boolean }

const AppContext = createContext<{
  state: AppState
  dispatch: React.Dispatch<AppAction>
} | null>(null)

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload }
    case 'SET_POLICIES':
      return { ...state, policies: action.payload }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    default:
      return state
  }
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, {
    user: null,
    policies: [],
    loading: false,
  })

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

export function useAppContext() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider')
  }
  return context
}
```

## 🧪 Testing

### Vitest Setup (Recommended)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom'
```

### Component Testing

```typescript
// src/components/__tests__/PolicyCard.test.tsx
import { render, screen } from '@testing-library/react'
import { PolicyCard } from '../PolicyCard'
import { Policy } from '../../types/policy'

const mockPolicy: Policy = {
  id: 1,
  user_id: 'user-1',
  owner_name: 'John Doe',
  insurer: 'Test Insurance',
  product_type: 'auto',
  policy_number: 'POL-123',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  premium_monthly: 150,
  deductible: 500,
  coverage_limit: 50000,
  notes: 'Test policy',
  active: true,
  updated_at: '2024-01-01T00:00:00Z',
}

test('renders policy information', () => {
  render(<PolicyCard policy={mockPolicy} />)
  
  expect(screen.getByText('Test Insurance')).toBeInTheDocument()
  expect(screen.getByText('$150/month')).toBeInTheDocument()
})
```

## 🚀 Deployment

### Production Build

```bash
npm run build
```

### Docker Build

```dockerfile
# Multi-stage build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Static Deployment

The built files in `dist/` can be served by any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

## 🔧 Development Tools

### VS Code Extensions

Recommended extensions for `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

### ESLint Configuration

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off"
  }
}
```

### Prettier Configuration

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```
Could not resolve "@vitejs/plugin-react"
```
**Solution**: Ensure all dependencies are installed: `npm install`

#### TypeScript Errors
```
Cannot find module './types'
```
**Solution**: Check file paths and ensure TypeScript files have proper extensions

#### API Connection Issues
```
Network Error / CORS
```
**Solution**: 
- Check API base URL in environment variables
- Ensure backend is running
- Configure Vite proxy if needed

#### Development Server Issues
```
Port 5173 already in use
```
**Solution**: Kill existing process or change port in `vite.config.ts`

### Debug Mode

Enable detailed logging:
```typescript
// In development
if (import.meta.env.DEV) {
  console.log('Debug info:', data)
}
```

### Performance Optimization

1. **Code Splitting**: Use `React.lazy()` for route-based splitting
2. **Bundle Analysis**: Use `npm run build -- --analyze`
3. **Image Optimization**: Use WebP format and responsive images
4. **Caching**: Configure appropriate cache headers

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev/)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
- [Testing Library Documentation](https://testing-library.com/)
