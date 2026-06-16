import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/industrial-theme.css'  // Industrial AI Theme
import AppWithRouter from './AppWithRouter.tsx'  // NEW: Router wrapper

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppWithRouter />
  </StrictMode>,
)
