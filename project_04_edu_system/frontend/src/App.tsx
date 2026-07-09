import { useState, useEffect, useCallback } from 'react'
import type { Student, PaginatedResponse, StudentCreateRequest, StudentUpdateRequest } from './types/student'
import { fetchPaginated, createStudent, updateStudent } from './api/studentApi'
import StudentList from './components/StudentList'
import StudentForm from './components/StudentForm'
import AiAnalysisModal from './components/AiAnalysisModal'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Footer from './components/Footer'
import './App.css'

type PageMode = 'list' | 'add' | 'edit'

const App = () => {
  // ── 数据状态 ──
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // ── 分页 + 搜索 + 排序状态 ──
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [order, setOrder] = useState('asc')
  const pageSize = 10

  // ── UI 状态 ──
  const [mode, setMode] = useState<PageMode>('list')
  const [editingStudent, setEditingStudent] = useState<Student | undefined>()
  const [activeMenu, setActiveMenu] = useState('students')
  const [aiTarget, setAiTarget] = useState<Student | null>(null)

  // ── 加载分页数据 ──
  const loadStudents = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const data: PaginatedResponse = await fetchPaginated({
        page, page_size: pageSize, search: search || undefined,
        sort_by: sortBy, order,
      })
      setStudents(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally { setLoading(false) }
  }, [page, search, sortBy, order])

  useEffect(() => { loadStudents() }, [loadStudents])

  // ── 排序：同一字段切换升降序 ──
  const handleSort = (field: string) => {
    if (sortBy === field) {
      setOrder(o => o === 'asc' ? 'desc' : 'asc')
    } else { setSortBy(field); setOrder('asc') }
    setPage(1)
  }

  const handleSearch = (keyword: string) => { setSearch(keyword); setPage(1) }

  // ── CRUD ──
  const handleSubmit = async (data: StudentCreateRequest | StudentUpdateRequest, name?: string) => {
    if ('name' in data) await createStudent(data as StudentCreateRequest)
    else await updateStudent(name!, data)
    setMode('list'); setEditingStudent(undefined); setPage(1)
  }
  const handleEdit = (s: Student) => { setEditingStudent(s); setMode('edit') }
  const handleCancel = () => { setMode('list'); setEditingStudent(undefined) }

  return (
    <div className="app-container">
      <Sidebar activeMenu={activeMenu} onMenuChange={setActiveMenu} />
      <div className="main-content">
        <Header title="学生管理" subtitle="v2.1 — 分页搜索 + AI 分析" />
        <main className="app-main">
          {mode === 'list' && (
            <>
              <div className="toolbar">
                <button className="btn-primary" onClick={() => setMode('add')}>+ 添加学生</button>
                <input className="search-input" type="text" placeholder="搜索姓名..."
                  value={search} onChange={e => handleSearch(e.target.value)} />
              </div>
              <StudentList
                students={students} loading={loading} error={error}
                onRefresh={loadStudents} onEdit={handleEdit} onAiAnalyze={setAiTarget}
                page={page} totalPages={totalPages} total={total}
                onPageChange={p => { if (p >= 1 && p <= totalPages) setPage(p) }}
                sortBy={sortBy} order={order} onSort={handleSort}
              />
            </>
          )}
          {mode === 'add' && <StudentForm onSubmit={handleSubmit} onCancel={handleCancel} />}
          {mode === 'edit' && editingStudent && (
            <StudentForm existing={editingStudent} onSubmit={handleSubmit} onCancel={handleCancel} />
          )}
        </main>
        <Footer />
      </div>
      {aiTarget && <AiAnalysisModal studentName={aiTarget.name} onClose={() => setAiTarget(null)} />}
    </div>
  )
}

export default App
