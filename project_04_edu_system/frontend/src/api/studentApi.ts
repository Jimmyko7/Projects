// API 调用封装 —— 所有与后端通信的逻辑集中在这里
import type { Student, StudentCreateRequest, StudentUpdateRequest } from '../types/student'

const BASE_URL = '/api/students'

/** 获取全部学生 */
export async function fetchAll(): Promise<Student[]> {
  const res = await fetch(BASE_URL)
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}

/** 按姓名查询 */
export async function fetchByName(name: string): Promise<Student> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`)
  if (!res.ok) {
    if (res.status === 404) throw new Error(`学生 "${name}" 不存在`)
    throw new Error(`请求失败: ${res.status}`)
  }
  return res.json()
}

/** 添加学生 */
export async function createStudent(data: StudentCreateRequest): Promise<Student> {
  const res = await fetch(BASE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || `添加失败: ${res.status}`)
  }
  return res.json()
}

/** 修改成绩 */
export async function updateStudent(name: string, data: StudentUpdateRequest): Promise<Student> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || `修改失败: ${res.status}`)
  }
  return res.json()
}

/** 删除学生 */
export async function deleteStudent(name: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || `删除失败: ${res.status}`)
  }
}
