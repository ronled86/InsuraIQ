import React, { useEffect, useState } from 'react'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnon = import.meta.env.VITE_SUPABASE_ANON_KEY as string
const apiBase = import.meta.env.VITE_API_BASE as string
const isLocalDev = import.meta.env.VITE_LOCAL_DEV === 'true'

const supabase = supabaseUrl && supabaseAnon ? createClient(supabaseUrl, supabaseAnon) : null

function useSession() {
  const [session, setSession] = useState<any>(null)
  useEffect(() => {
    if (isLocalDev) {
      // In local dev mode, create a fake session
      setSession({ 
        access_token: 'local-dev-token',
        user: { email: 'local@example.com', id: 'local-user' }
      })
      return
    }
    
    if (!supabase) {
      console.error('Supabase not configured')
      return
    }
    
    supabase.auth.getSession().then(({ data }) => setSession(data.session))
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => setSession(s))
    return () => { sub.subscription.unsubscribe() }
  }, [])
  return session
}

type Policy = {
  id: number; insurer: string; product_type: string; premium_monthly: number; deductible: number; coverage_limit: number; owner_name: string;
  policy_number: string; start_date: string; end_date: string; notes?: string; active: boolean; user_id: string;
}

export function App() {
  const session = useSession()
  
  if (isLocalDev && session) {
    return <Dashboard session={session} />
  }
  
  if (!session) return <AuthUI />
  return <Dashboard session={session} />
}

function AuthUI() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  
  if (!supabase) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h1 className="auth-title">InsuraIQ</h1>
          <div className="alert alert-warning">
            <p>Supabase not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your environment.</p>
            <p>Or set VITE_LOCAL_DEV=true for local development mode.</p>
          </div>
        </div>
      </div>
    )
  }
  
  async function signIn(e: React.FormEvent) { 
    e.preventDefault(); 
    if (!supabase) return; 
    const { error } = await supabase.auth.signInWithPassword({ email, password }); 
    setMsg(error ? error.message : 'Logged in') 
  }
  async function signUp(e: React.FormEvent) { 
    e.preventDefault(); 
    if (!supabase) return; 
    const { error } = await supabase.auth.signUp({ email, password }); 
    setMsg(error ? error.message : 'Check your email to confirm') 
  }
  async function magicLink(e: React.FormEvent) { 
    e.preventDefault(); 
    if (!supabase) return; 
    const { error } = await supabase.auth.signInWithOtp({ email }); 
    setMsg(error ? error.message : 'Magic link sent') 
  }
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">InsuraIQ</h1>
        <form onSubmit={signIn} className="auth-form">
          <div className="form-group">
            <label className="form-label">Email</label>
            <input 
              type="email"
              placeholder="Enter your email" 
              value={email} 
              onChange={e=>setEmail(e.target.value)} 
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password"
              placeholder="Enter your password" 
              value={password} 
              onChange={e=>setPassword(e.target.value)} 
            />
          </div>
          <div className="form-group">
            <button type="submit" className="btn btn-primary">Sign In</button>
          </div>
          <div className="form-group">
            <button type="button" className="btn btn-secondary" onClick={signUp}>Sign Up</button>
          </div>
          <div className="form-group">
            <button type="button" className="btn btn-secondary" onClick={magicLink}>Magic Link</button>
          </div>
        </form>
        {msg && <div className={`alert ${msg.includes('error') ? 'alert-error' : 'alert-success'}`}>{msg}</div>}
      </div>
    </div>
  )
}

function Dashboard({ session }: { session: any }) {
  const token = session?.access_token
  const [tab, setTab] = useState<'policies'|'compare'|'history'|'recs'|'quotes'>('policies')
  const [policies, setPolicies] = useState<Policy[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [result, setResult] = useState<any | null>(null)
  const [recs, setRecs] = useState<any[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [pdf, setPdf] = useState<File | null>(null)
  const [quotes, setQuotes] = useState<any[]>([])
  const [uploadStatus, setUploadStatus] = useState<string>('')

  async function api(path: string, init?: RequestInit) {
    const r = await fetch(`${apiBase}${path}`, { ...(init||{}), headers: { ...(init?.headers||{}), Authorization: `Bearer ${token}` } })
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  }
  async function refresh() { const pols = await api('/policies'); setPolicies(pols) }

  useEffect(()=>{ refresh(); loadRecs() }, [token])

  async function uploadCsv() {
    if (!file) return
    setUploadStatus('Uploading CSV...')
    try {
      const fd = new FormData(); fd.append('file', file)
      await fetch(`${apiBase}/policies/upload`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
      await refresh()
      setUploadStatus('CSV uploaded successfully!')
      setFile(null)
      setTimeout(() => setUploadStatus(''), 3000)
    } catch (error) {
      setUploadStatus(`Error: ${error}`)
      setTimeout(() => setUploadStatus(''), 5000)
    }
  }
  
  async function importPdf() {
    if (!pdf) return
    setUploadStatus('Importing PDF...')
    try {
      const fd = new FormData(); fd.append('file', pdf)
      const response = await fetch(`${apiBase}/policies/import/pdf`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
      const result = await response.json()
      if (!response.ok) {
        throw new Error(result.detail || 'Upload failed')
      }
      await refresh()
      setUploadStatus(`PDF imported successfully! Created policy ID: ${result.created_id}`)
      setPdf(null)
      setTimeout(() => setUploadStatus(''), 5000)
    } catch (error) {
      setUploadStatus(`Error: ${error}`)
      setTimeout(() => setUploadStatus(''), 5000)
    }
  }
  async function compare() {
    const data = await api('/advisor/compare', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ policy_ids: selected }) })
    setResult(data); setTab('compare')
  }
  async function loadRecs() { const data = await api('/advisor/recommendations'); setRecs(data) }
  async function loadQuotes() {
    const p = policies[0]
    if (!p) return
    const data = await api(`/advisor/quotes_demo?product_type=${encodeURIComponent(p.product_type)}&coverage_limit=${p.coverage_limit}&deductible=${p.deductible}`)
    setQuotes(data); setTab('quotes')
  }

  async function saveRow(p: Policy) {
    const body = { ...p }; delete (body as any).id; delete (body as any).user_id
    await api(`/policies/${p.id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) })
    await refresh()
  }
  async function deleteRow(id: number) {
    await api(`/policies/${id}`, { method: 'DELETE' }); await refresh()
  }

  return (
    <div className="container">
      <div className="header">
        <div>
          <h2>Dashboard</h2>
          <div className="user-email">Signed in as {session?.user?.email}</div>
        </div>
        <button className="btn btn-secondary" onClick={()=>{ 
          if (isLocalDev) {
            window.location.reload()
          } else if (supabase) {
            supabase.auth.signOut()
          }
        }}>Sign out</button>
      </div>

      <div className="tabs">
        <div className={`tab ${tab==='policies'?'active':''}`} onClick={()=>setTab('policies')}>Policies</div>
        <div className={`tab ${tab==='compare'?'active':''}`} onClick={()=>setTab('compare')}>Compare</div>
        <div className={`tab ${tab==='history'?'active':''}`} onClick={()=>setTab('history')}>History</div>
        <div className={`tab ${tab==='recs'?'active':''}`} onClick={()=>setTab('recs')}>Recommendations</div>
        <div className={`tab ${tab==='quotes'?'active':''}`} onClick={loadQuotes}>Quotes Demo</div>
      </div>

      {tab==='policies' && (
        <section>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Upload Policy Documents</h3>
              <p className="card-subtitle">Import policies from CSV files or PDF documents</p>
            </div>
            <div className="card-body">
              {uploadStatus && (
                <div className={`alert ${uploadStatus.includes('Error') ? 'alert-error' : uploadStatus.includes('successfully') ? 'alert-success' : 'alert-info'} mb-4`}>
                  {uploadStatus}
                </div>
              )}
              
              <div className="controls">
                <div className="file-upload">
                  <input type="file" accept=".csv" onChange={e=>setFile(e.target.files?.[0] || null)} />
                  <div className="file-upload-label">
                    📄 {file ? file.name : 'Choose CSV File'}
                  </div>
                </div>
                <button className="btn btn-primary" onClick={uploadCsv} disabled={!file || uploadStatus.includes('Uploading')}>
                  {uploadStatus.includes('Uploading') && uploadStatus.includes('CSV') ? 'Uploading...' : 'Upload CSV'}
                </button>
                
                <div className="file-upload">
                  <input type="file" accept=".pdf" onChange={e=>setPdf(e.target.files?.[0] || null)} />
                  <div className="file-upload-label">
                    📑 {pdf ? pdf.name : 'Choose PDF File'}
                  </div>
                </div>
                <button className="btn btn-success" onClick={importPdf} disabled={!pdf || uploadStatus.includes('Importing')}>
                  {uploadStatus.includes('Importing') ? 'Importing...' : 'Import PDF'}
                </button>
              </div>
            </div>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Insurer</th>
                  <th>Type</th>
                  <th>Premium</th>
                  <th>Deductible</th>
                  <th>Coverage Limit</th>
                  <th>Policy Owner</th>
                  <th>Policy Number</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Status</th>
                  <th>
                    <input 
                      type="checkbox" 
                      onChange={e => {
                        if (e.target.checked) {
                          setSelected(policies.map(p => p.id))
                        } else {
                          setSelected([])
                        }
                      }}
                      checked={selected.length === policies.length && policies.length > 0}
                      title="Select/Deselect All"
                    />
                  </th>
                </tr>
              </thead>
              <tbody>
                {policies.map(p => (
                  <EditableRow key={p.id} p={p} onSave={saveRow} onDelete={()=>deleteRow(p.id)} onSelect={checked=> setSelected(s => checked ? [...s, p.id] : s.filter(x=>x!==p.id)) } />
                ))}
              </tbody>
            </table>
          </div>
          
          {policies.length > 0 && (
            <div className="table-summary">
              <div className="summary-stats">
                <span className="stat">
                  <strong>Total Policies:</strong> {policies.length}
                </span>
                <span className="stat">
                  <strong>Selected:</strong> {selected.length}
                </span>
                <span className="stat">
                  <strong>Total Monthly Premium:</strong> {
                    new Intl.NumberFormat('en-US', { 
                      style: 'currency', 
                      currency: 'USD' 
                    }).format(
                      policies
                        .filter(p => selected.includes(p.id))
                        .reduce((sum, p) => sum + p.premium_monthly, 0)
                    )
                  }
                </span>
                {selected.length > 0 && (
                  <div className="bulk-actions">
                    <button 
                      className="btn btn-danger"
                      onClick={() => {
                        if (confirm(`Are you sure you want to delete ${selected.length} selected policies?`)) {
                          selected.forEach(id => deleteRow(id))
                          setSelected([])
                        }
                      }}
                    >
                      Delete Selected ({selected.length})
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      )}

      {tab==='compare' && (
        <section>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Policy Comparison</h3>
              <p className="card-subtitle">Compare selected policies to find the best value</p>
            </div>
            <div className="card-body">
              <button className="btn btn-primary" onClick={compare} disabled={selected.length < 2}>
                Compare Selected ({selected.length})
              </button>
              
              {result ? (
                <div className="mt-4">
                  <div className="alert alert-info">
                    {result.summary}
                  </div>
                  <div className="table-container">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>ID</th><th>Insurer</th><th>Type</th><th>Premium</th>
                          <th>Deductible</th><th>Coverage</th><th>Value Rating</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.table?.map((r:any)=>(
                          <tr key={r.id}>
                            <td>{r.id}</td><td>{r.insurer}</td><td>{r.product_type}</td>
                            <td>${r.premium_monthly}</td><td>${r.deductible}</td>
                            <td>${r.coverage_limit}</td><td>{r.coverage_per_shekel}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="alert alert-warning mt-4">
                  Select at least 2 policies to compare them
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {tab==='history' && <History token={token} />}

      {tab==='recs' && (
        <section>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">AI Recommendations</h3>
              <p className="card-subtitle">Personalized insurance recommendations based on your portfolio</p>
            </div>
            <div className="card-body">
              {recs.length > 0 ? (
                <div className="space-y-4">
                  {recs.map((r:any,i:number)=>(
                    <div key={i} className="card">
                      <div className="card-body">
                        <h4 className="font-semibold text-lg text-gray-800">{r.title}</h4>
                        <p className="text-gray-600 mt-2">{r.reason}</p>
                        <p className="text-sm text-gray-500 mt-1">{r.impact}</p>
                        {r.explanation && (
                          <details className="mt-2">
                            <summary className="cursor-pointer text-blue-600">View Details</summary>
                            <pre className="text-xs bg-gray-100 p-2 mt-1 rounded">{JSON.stringify(r.explanation, null, 2)}</pre>
                          </details>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="alert alert-info">
                  No recommendations available. Add some policies to get personalized advice.
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {tab==='quotes' && (
        <section>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Insurance Quotes</h3>
              <p className="card-subtitle">Compare quotes from multiple insurers</p>
            </div>
            <div className="card-body">
              <div className="alert alert-info mb-4">
                Using either stubbed data or your aggregator if configured
              </div>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Insurer</th><th>Monthly Premium</th><th>Deductible</th><th>Coverage Limit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quotes.map((q:any, i:number)=>(
                      <tr key={i}>
                        <td><strong>{q.insurer}</strong></td>
                        <td className="text-green-600 font-semibold">${q.monthly}</td>
                        <td>${q.deductible}</td>
                        <td>${q.coverage}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

function EditableRow({ p, onSave, onDelete, onSelect }: { p: Policy, onSave: (p: Policy)=>void, onDelete: ()=>void, onSelect:(checked:boolean)=>void }) {
  const [row, setRow] = useState<Policy>(p)
  const [editingField, setEditingField] = useState<string | null>(null)
  
  useEffect(()=>{
    setRow(p)
    setEditingField(null)
  }, [p.id])
  
  const handleFieldSave = (fieldName: string, value: any) => {
    const updatedRow = { ...row, [fieldName]: value }
    setRow(updatedRow)
    onSave(updatedRow)
    setEditingField(null)
  }
  
  const handleFieldCancel = () => {
    setRow(p) // Reset to original values
    setEditingField(null)
  }
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }
  
  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', { 
        year: '2-digit', 
        month: 'short', 
        day: 'numeric' 
      })
    } catch {
      return dateStr
    }
  }
  
  const EditableCell = ({ fieldName, value, type = 'text', formatter }: { 
    fieldName: string, 
    value: any, 
    type?: string,
    formatter?: (val: any) => string 
  }) => {
    const isEditing = editingField === fieldName
    
    if (isEditing) {
      return (
        <div className="editing-cell">
          <input
            type={type}
            value={value}
            onChange={e => {
              const newValue = type === 'number' ? (parseFloat(e.target.value) || 0) : e.target.value
              setRow({...row, [fieldName]: newValue})
            }}
            onKeyDown={e => {
              if (e.key === 'Enter') {
                handleFieldSave(fieldName, value)
              } else if (e.key === 'Escape') {
                handleFieldCancel()
              }
            }}
            onBlur={() => handleFieldSave(fieldName, value)}
            autoFocus
            className="inline-edit-input"
          />
        </div>
      )
    }
    
    return (
      <span 
        className="editable-field" 
        onClick={() => setEditingField(fieldName)}
        title={`Click to edit ${fieldName}. Current value: ${formatter ? formatter(value) : value}`}
      >
        {formatter ? formatter(value) : value}
      </span>
    )
  }
  
  return (
    <tr>
      <td>{row.id}</td>
      <td>
        <EditableCell fieldName="insurer" value={row.insurer} />
      </td>
      <td>
        <EditableCell fieldName="product_type" value={row.product_type} />
      </td>
      <td>
        <EditableCell 
          fieldName="premium_monthly" 
          value={row.premium_monthly} 
          type="number"
          formatter={formatCurrency}
        />
      </td>
      <td>
        <EditableCell 
          fieldName="deductible" 
          value={row.deductible} 
          type="number"
          formatter={formatCurrency}
        />
      </td>
      <td>
        <EditableCell 
          fieldName="coverage_limit" 
          value={row.coverage_limit} 
          type="number"
          formatter={formatCurrency}
        />
      </td>
      <td>
        <EditableCell fieldName="owner_name" value={row.owner_name} />
      </td>
      <td>
        <EditableCell fieldName="policy_number" value={row.policy_number} />
      </td>
      <td>
        <EditableCell 
          fieldName="start_date" 
          value={row.start_date} 
          type="date"
          formatter={formatDate}
        />
      </td>
      <td>
        <EditableCell 
          fieldName="end_date" 
          value={row.end_date} 
          type="date"
          formatter={formatDate}
        />
      </td>
      <td>
        {editingField && (
          <div className="edit-actions">
            <span className="edit-hint">Press Enter to save, Esc to cancel</span>
          </div>
        )}
      </td>
      <td>
        <input 
          type="checkbox" 
          onChange={e=>onSelect(e.target.checked)}
          className="policy-checkbox"
        />
      </td>
    </tr>
  )
}

function History({ token }:{ token: string }) {
  const apiBase = import.meta.env.VITE_API_BASE as string
  const [items, setItems] = useState<any[]>([])
  useEffect(()=>{
    fetch(`${apiBase}/advisor/compare_history`, { headers: { Authorization: `Bearer ${token}`}})
      .then(r=>r.json()).then(setItems).catch(console.error)
  }, [token])
  return (
    <section>
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Comparison History</h3>
          <p className="card-subtitle">View your previous policy comparisons</p>
        </div>
        <div className="card-body">
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th><th>Policy IDs</th><th>Created</th><th>Summary</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it:any)=>(
                  <tr key={it.id}>
                    <td>{it.id}</td>
                    <td><span className="text-blue-600">{it.policy_ids.join(', ')}</span></td>
                    <td>{new Date(it.created_at).toLocaleString()}</td>
                    <td>{it.result?.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  )
}