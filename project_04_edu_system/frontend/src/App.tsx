import React, { useState, useEffect, useCallback } from 'react'
import type { Student } from './types/student'
import { fetchAll, createStudent, updateStudent } from './api/studentApi'
import StudentList from './components/StudentList'
import StudentForm from './components/StudentForm'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Footer from './components/Footer'
import './App.css'

type PageMode = 'list' | 'add' | 'edit'

const App: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [mode, setMode] = useState<PageMode>('list')
  const [editingStudent, setEditingStudent] = useState<Student | undefined>()
  const [activeMenu, setActiveMenu] = useState('students')

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

  const handleAdd = async (data: any) => {
    await createStudent(data)
    setMode('list')
    await loadStudents()
  }

  const handleUpdate = async (data: any, name?: string) => {
    await updateStudent(name!, data)
    setMode('list')
    setEditingStudent(undefined)
    await loadStudents()
  }

  const handleEdit = (student: Student) => {
    setEditingStudent(student)
    setMode('edit')
  }

  const handleCancel = () => {
    setMode('list')
    setEditingStudent(undefined)
  }

  const handleMenuChange = (menu: string) => {
    setActiveMenu(menu)
    if (menu !== 'students') {
      setMode('list')
      setEditingStudent(undefined)
    }
  }

  return (
    <div className="app-container">
      <Sidebar activeMenu={activeMenu} onMenuChange={handleMenuChange} />
      
      <div className="main-content">
        <Header 
          title="学生管理" 
          subtitle="学生成绩管理 — FastAPI + React" 
        />
        
        <main className="app-main">
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

          {mode === 'add' && (
            <StudentForm onSubmit={handleAdd} onCancel={handleCancel} />
          )}

          {mode === 'edit' && editingStudent && (
            <StudentForm
              existing={editingStudent}
              onSubmit={handleUpdate}
              onCancel={handleCancel}
            />
          )}
        </main>
        
        <Footer />
      </div>
    </div>
  )
}

export default App