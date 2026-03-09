import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ReadPage from './pages/ReadPage'
import ShopPage from './pages/ShopPage'
import LessonsPage from './pages/LessonsPage'
import ProgressPage from './pages/ProgressPage'
import RewardsPage from './pages/RewardsPage'
import AdminPage from './pages/AdminPage'
import LessonEnginePage from './pages/LessonEnginePage'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/read" element={<ReadPage />} />
        <Route path="/shop" element={<ShopPage />} />
        <Route path="/lessons" element={<LessonsPage />} />
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="/rewards" element={<RewardsPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/lesson-engine" element={<LessonEnginePage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
