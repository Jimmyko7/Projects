import { useState } from 'react'
import type { Student } from '../types/student'
import { deleteStudent } from '../api/studentApi'

interface StudentListProps {
  students: Student[]
  loading: boolean
  error: string
  onRefresh: () => void
  onEdit: (student: Student) => void
  onAiAnalyze: (student: Student) => void
  page: number
  totalPages: number
  total: number
  onPageChange: (page: number) => void
  sortBy: string
  order: string
  onSort: (field: string) => void
}

const SORT_FIELDS = [
  { key: 'name', label: '姓名' },
  { key: 'chinese', label: '语文' },
  { key: 'math', label: '数学' },
  { key: 'english', label: '英语' },
  { key: 'total', label: '总分' },
]

const StudentList = ({
  students, loading, error, onRefresh, onEdit, onAiAnalyze,
  page, totalPages, total, onPageChange, sortBy, order, onSort,
}: StudentListProps) => {
  const [deleting, setDeleting] = useState<string | null>(null)

  const handleDelete = async (name: string) => {
    if (!confirm(`确定删除 "${name}" 吗？`)) return
    setDeleting(name)
    try { await deleteStudent(name); onRefresh() }
    catch (err: unknown) { alert(err instanceof Error ? err.message : '删除失败') }
    finally { setDeleting(null) }
  }

  // 排序箭头指示
  const sortArrow = (field: string) => {
    if (sortBy !== field) return ' ↕'
    return order === 'asc' ? ' ↑' : ' ↓'
  }

  // 页码按钮范围
  const pageButtons = () => {
    const buttons: number[] = []
    const start = Math.max(1, page - 2)
    const end = Math.min(totalPages, page + 2)
    for (let i = start; i <= end; i++) buttons.push(i)
    return buttons
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
        <span>共 {total} 名学生（第 {page}/{totalPages} 页）</span>
        <button onClick={onRefresh}>刷新</button>
      </div>

      <table>
        <thead>
          <tr>
            {SORT_FIELDS.map(f => (
              <th key={f.key} onClick={() => onSort(f.key)} className="sortable">
                {f.label}{sortArrow(f.key)}
              </th>
            ))}
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {students.map(s => (
            <tr key={s.name}>
              <td>{s.name}</td>
              <td>{s.chinese}</td>
              <td>{s.math}</td>
              <td>{s.english}</td>
              <td className="total">{s.total}</td>
              <td className="actions">
                <button onClick={() => onEdit(s)}>编辑</button>
                <button className="danger" onClick={() => handleDelete(s.name)}
                  disabled={deleting === s.name}>
                  {deleting === s.name ? '删除中...' : '删除'}
                </button>
                <button className="ai-btn" onClick={() => onAiAnalyze(s)}
                  title="AI 成绩分析">🤖</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* 分页控件 */}
      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
            ← 上一页
          </button>
          {pageButtons().map(p => (
            <button key={p} className={p === page ? 'active' : ''}
              onClick={() => onPageChange(p)}>{p}</button>
          ))}
          <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}>
            下一页 →
          </button>
        </div>
      )}
    </div>
  )
}

export default StudentList
