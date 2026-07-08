// API 调用封装 — v2.1：升级到 /api/v1/ + 分页支持
import type { Student, PaginatedResponse, StudentCreateRequest, StudentUpdateRequest } from '../types/student'

const BASE_URL = '/api/v1/students'

/** 获取全部学生（兼容旧调用） */
export async function fetchAll(): Promise<Student[]> {
  const res = await fetch(BASE_URL + '?page_size=100')
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  const data: PaginatedResponse = await res.json()
  return data.items
}

/** 分页查询（v2.1 新增） */
export async function fetchPaginated(params: {
  page?: number; page_size?: number; search?: string; sort_by?: string; order?: string
} = {}): Promise<PaginatedResponse> {
  const query = new URLSearchParams()
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  if (params.search) query.set('search', params.search)
  if (params.sort_by) query.set('sort_by', params.sort_by)
  if (params.order) query.set('order', params.order)
  const qs = query.toString()
  const res = await fetch(BASE_URL + (qs ? '?' + qs : ''))
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
