import React from 'react'

interface HeaderProps {
  title: string
  subtitle?: string
}

const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-title">
          <h1>{title}</h1>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <div className="header-actions">
          <button className="header-btn">🔍 搜索</button>
          <button className="header-btn">🔔 通知</button>
          <div className="user-info">
            <span className="user-avatar">👤</span>
            <span className="user-name">管理员</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header