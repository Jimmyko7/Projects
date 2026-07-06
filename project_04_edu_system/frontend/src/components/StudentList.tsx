import React, { useState } from 'react'
import type { Student } from '../types/student'
import { deleteStudent } from '../api/studentApi'

// ── 组件 Props ─────────────────────────────────────
interface StudentListProps {
  students: Student[]
  loading: boolean
  error: string
  onRefresh: () => void
  onEdit: (student: Student) => void
}

// ── 组件 ───────────────────────────────────────────
const StudentList: React.FC<StudentListProps> = ({
  students,
  loading,
  error,
  onRefresh,
  onEdit,
}) => {
  const [deleting, setDeleting] = useState<string | null>(null)

  const handleDelete = async (name: string) => {
    if (!confirm(`确定要删除学生 "${name}" 吗？此操作不可撤销。`)) return

    setDeleting(name)
    try {
      await deleteStudent(name)
      onRefresh()
    } catch (err: any) {
      alert(err.message || '删除失败')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) return <p>加载中...</p>
  if (error) return <p className="error-msg">加载失败: {error}</p>

  if (students.length === 0) {
    return (
      <div className="empty-state">
        <p>暂无学生成绩记录</p>
        <button onClick={onRefresh}>刷新</button>
      </div>
    )
  }

  return (
    <div className="student-list">
      <div className="list-header">
        <span>共 {students.length} 名学生</span>
        <button onClick={onRefresh}>刷新</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>语文</th>
            <th>数学</th>
            <th>英语</th>
            <th>总分</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr key={s.name}>
              <td>{s.name}</td>
              <td>{s.chinese}</td>
              <td>{s.math}</td>
              <td>{s.english}</td>
              <td className="total">{s.total}</td>
              <td className="actions">
                <button onClick={() => onEdit(s)}>编辑</button>
                <button
                  className="danger"
                  onClick={() => handleDelete(s.name)}
                  disabled={deleting === s.name}
                >
                  {deleting === s.name ? '删除中...' : '删除'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default StudentList
