import React, { useState } from 'react'
import type { Student, StudentCreateRequest, StudentUpdateRequest } from '../types/student'

// ── 组件 Props ─────────────────────────────────────
interface StudentFormProps {
  /** 编辑模式：传入现有学生数据；新增模式：undefined */
  existing?: Student
  /** 提交回调：接收请求体，父组件负责调用 API */
  onSubmit: (data: StudentCreateRequest | StudentUpdateRequest, name?: string) => Promise<void>
  /** 取消回调 */
  onCancel: () => void
}

// ── 组件 ───────────────────────────────────────────
const StudentForm: React.FC<StudentFormProps> = ({ existing, onSubmit, onCancel }) => {
  const isEdit = !!existing

  const [name, setName] = useState(existing?.name ?? '')
  const [chinese, setChinese] = useState(existing?.chinese.toString() ?? '')
  const [math, setMath] = useState(existing?.math.toString() ?? '')
  const [english, setEnglish] = useState(existing?.english.toString() ?? '')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const c = parseInt(chinese), m = parseInt(math), en = parseInt(english)

    if (isNaN(c) || isNaN(m) || isNaN(en)) {
      setError('成绩必须为数字')
      return
    }
    if (c < 0 || c > 100 || m < 0 || m > 100 || en < 0 || en > 100) {
      setError('成绩必须在 0~100 之间')
      return
    }
    if (!isEdit && !name.trim()) {
      setError('姓名不能为空')
      return
    }

    setLoading(true)
    try {
      if (isEdit) {
        // 修改模式：只传成绩，不传姓名
        await onSubmit({ chinese: c, math: m, english: en }, existing!.name)
      } else {
        // 新增模式：传全部字段
        await onSubmit({ name: name.trim(), chinese: c, math: m, english: en })
      }
    } catch (err: any) {
      setError(err.message || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="student-form">
      <h3>{isEdit ? `修改成绩 — ${existing!.name}` : '添加学生'}</h3>

      {!isEdit && (
        <div className="form-field">
          <label>姓名</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="请输入姓名" />
        </div>
      )}

      <div className="form-row">
        <div className="form-field">
          <label>语文</label>
          <input type="number" min={0} max={100} value={chinese}
            onChange={(e) => setChinese(e.target.value)} placeholder="0~100" />
        </div>
        <div className="form-field">
          <label>数学</label>
          <input type="number" min={0} max={100} value={math}
            onChange={(e) => setMath(e.target.value)} placeholder="0~100" />
        </div>
        <div className="form-field">
          <label>英语</label>
          <input type="number" min={0} max={100} value={english}
            onChange={(e) => setEnglish(e.target.value)} placeholder="0~100" />
        </div>
      </div>

      {error && <p className="error-msg">{error}</p>}

      <div className="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? '提交中...' : isEdit ? '保存修改' : '添加'}
        </button>
        <button type="button" onClick={onCancel}>取消</button>
      </div>
    </form>
  )
}

export default StudentForm
