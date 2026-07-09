import { useState } from 'react'

interface Props { studentName: string; onClose: () => void }

const AiAnalysisModal = ({ studentName, onClose }: Props) => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [question, setQuestion] = useState('')
  const [model, setModel] = useState('')

  const handleAnalyze = async () => {
    setLoading(true); setError(''); setResult(null)
    try {
      const body = question.trim() ? JSON.stringify({ question: question.trim() }) : '{}'
      const res = await fetch(`/api/v1/ai/analyze/${encodeURIComponent(studentName)}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '请求失败')
      setResult(data.analysis); setModel(data.model)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '分析失败')
    } finally { setLoading(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>🤖 AI 成绩分析 — {studentName}</h3>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <div className="ai-input-row">
            <input type="text" placeholder="自定义问题（可选，如：他的数学还有救吗？）"
              value={question} onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAnalyze()} />
            <button className="btn-primary" onClick={handleAnalyze} disabled={loading}>
              {loading ? '分析中...' : '开始分析'}
            </button>
          </div>
          {error && <p className="error-msg">❌ {error}</p>}
          {loading && <p className="loading-text">⏳ AI 正在分析...</p>}
          {result && (
            <div className="ai-result">
              <div className="ai-result-header">
                <span>📊 分析结果</span>
                {model && <span className="model-badge">{model}</span>}
              </div>
              <pre>{result}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AiAnalysisModal
