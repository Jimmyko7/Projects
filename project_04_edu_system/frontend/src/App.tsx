import React, { useState, useEffect, useCallback } from 'react'
import type { Student } from './types/student'
import { fetchAll, createStudent, updateStudent } from './api/studentApi'
import StudentList from './components/StudentList'
import StudentForm from './components/StudentForm'
import './App.css'

// ── 页面状态机 ─────────────────────────────────────
type PageMode = 'list' | 'add' | 'edit'

const App: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [mode, setMode] = useState<PageMode>('list')
  const [editingStudent, setEditingStudent] = useState<Student | undefined>()

  // 获取学生列表
  const loadStudents = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await fetchAll()
      setStudents(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadStudents()
  }, [loadStudents])

  // 添加学生
  const handleAdd = async (data: any) => {
    await createStudent(data)
    setMode('list')
    await loadStudents()
  }

  // 修改成绩
  const handleUpdate = async (data: any, name?: string) => {
    await updateStudent(name!, data)
    setMode('list')
    setEditingStudent(undefined)
    await loadStudents()
  }

  // 进入编辑模式
  const handleEdit = (student: Student) => {
    setEditingStudent(student)
    setMode('edit')
  }

  // 取消操作
  const handleCancel = () => {
    setMode('list')
    setEditingStudent(undefined)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>教务管理系统</h1>
        <p>学生成绩管理 — FastAPI + React 全栈演示</p>
      </header>

      <main className="app-main">
        {/* 列表模式 */}
        {mode === 'list' && (
          <>
            <div className="toolbar">
              <button className="btn-primary" onClick={() => setMode('add')}>
                + 添加学生
              </button>
            </div>
            <StudentList
              students={students}
              loading={loading}
              error={error}
              onRefresh={loadStudents}
              onEdit={handleEdit}
            />
          </>
        )}

        {/* 添加模式 */}
        {mode === 'add' && (
          <StudentForm onSubmit={handleAdd} onCancel={handleCancel} />
        )}

        {/* 编辑模式 */}
        {mode === 'edit' && editingStudent && (
          <StudentForm
            existing={editingStudent}
            onSubmit={handleUpdate}
            onCancel={handleCancel}
          />
        )}
      </main>
    </div>
  )
}

export default App
