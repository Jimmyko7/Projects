import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-left">
          <span>©教务管理系统</span>
        </div>
        <div className="footer-right">
          <span>版本 1.0.0</span>
          <span className="footer-divider">|</span>
          <span>技术支持</span>
        </div>
      </div>
    </footer>
  )
}

export default Footer