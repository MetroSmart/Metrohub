import React from 'react'
import { useNavigate } from 'react-router-dom'
import './Landing.css'

function Landing() {
  const navigate = useNavigate()

  return (
    <div className="page">
      <nav className="navbar">
        <div className="logo" onClick={() => navigate('/')} style={{cursor: 'pointer'}}>
          Metro<span>Smart</span>
        </div>
        <div className="nav-links">
          <a href="#servicios">Servicios</a>
          <a href="#como-funciona">¿Cómo funciona?</a>
          <a href="#contacto">Contacto</a>
        </div>
        <div className="nav-right">
          <button className="btn-login" onClick={() => navigate('/login')}>Iniciar sesión</button>
          <button className="btn-signup" onClick={() => navigate('/register')}>Registrarse</button>
        </div>
      </nav>

      <section className="hero">
        <h1>Viaja con <span className="highlight">inteligencia</span></h1>
        <p>La plataforma más inteligente para explorar el Metropolitano de Lima en tiempo real</p>
        <div className="hero-buttons">
          <button className="btn-primary" onClick={() => navigate('/map')}>Explorar ahora</button>
          <button className="btn-secondary" onClick={() => alert('Demo próximamente')}>Ver demo</button>
        </div>
        <div className="hero-image"></div>
      </section>

      <section className="services" id="servicios">
        <div className="services-header">
          <h2>Nuestros Servicios</h2>
          <p>Todo lo que necesitas para viajar de forma inteligente</p>
        </div>
        <div className="services-grid">
          <div className="service-card">
            <div className="service-icon">🗺️</div>
            <h3>Mapa en Tiempo Real</h3>
            <p>Visualiza la aglomeración de todas las estaciones del Metropolitano actualizada cada 5 minutos</p>
          </div>
          <div className="service-card">
            <div className="service-icon">🚌</div>
            <h3>Rutas Inteligentes</h3>
            <p>Descubre las rutas disponibles más cercanas a ti según tu hora y ubicación actual</p>
          </div>
          <div className="service-card">
            <div className="service-icon">⏱️</div>
            <h3>Predicción con IA</h3>
            <p>Predice tu tiempo de viaje con precisión usando aprendizaje automático</p>
          </div>
          <div className="service-card">
            <div className="service-icon">📊</div>
            <h3>Dashboard Admin</h3>
            <p>Gestiona rutas, horarios y visualiza indicadores clave</p>
          </div>
        </div>
      </section>

      <section className="cta">
        <h2>¿Listo para comenzar?</h2>
        <p>Únete a miles de usuarios que viajan inteligentemente</p>
        <button className="btn-primary" onClick={() => navigate('/login')}>Comenzar ahora</button>
      </section>

      <footer className="footer">
        <p>MetroSmart © 2026 · Universidad Nacional de Ingeniería</p>
      </footer>
    </div>
  )
}

export default Landing