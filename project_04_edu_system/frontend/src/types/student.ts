// TypeScript 类型定义 —— 前后端数据契约

/** 学生成绩数据（与后端 StudentResponse 对应） */
export interface Student {
  name: string
  chinese: number
  math: number
  english: number
  total: number
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
