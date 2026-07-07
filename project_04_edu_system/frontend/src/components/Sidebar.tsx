import React, { useState } from 'react'

interface SidebarProps {
  activeMenu: string
  onMenuChange: (menu: string) => void
}

const menuItems = [
  { id: 'students', label: '学生管理', icon: '📚' },
  { id: 'courses', label: '课程管理', icon: '📖' },
  { id: 'scores', label: '成绩管理', icon: '📊' },
  { id: 'teachers', label: '教师管理', icon: '👨‍🏫' },
  { id: 'statistics', label: '数据统计', icon: '📈' },
  { id: 'settings', label: '系统设置', icon: '⚙️' },
]

const Sidebar: React.FC<SidebarProps> = ({ activeMenu, onMenuChange }) => {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!collapsed && (
          <div className="sidebar-logo">
            <span className="logo-icon">🎓</span>
            <span className="logo-text">教务管理系统</span>
          </div>
        )}
        {collapsed && (
          <div className="sidebar-logo-collapsed">
            <span className="logo-icon">🎓</span>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeMenu === item.id ? 'active' : ''}`}
            onClick={() => onMenuChange(item.id)}
            title={collapsed ? item.label : undefined}
          >
            <span className="nav-icon">{item.icon}</span>
            {!collapsed && <span className="nav-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? '▶' : '◀'}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar