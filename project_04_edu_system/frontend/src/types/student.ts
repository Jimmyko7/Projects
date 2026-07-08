// TypeScript 类型定义 — 前后端数据契约（v2.1：分页类型新增）

/** 学生成绩数据（与后端 StudentResponse 对应） */
export interface Student {
  name: string
  chinese: number
  math: number
  english: number
  total: number
}

/** 分页响应体（v2.1 新增） */
export interface PaginatedResponse {
  items: Student[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/** 添加学生时的请求体 */
export interface StudentCreateRequest {
  name: string
  chinese: number
  math: number
  english: number
}

/** 修改成绩时的请求体（所有字段可选） */
export interface StudentUpdateRequest {
  chinese?: number
  math?: number
  english?: number
}
