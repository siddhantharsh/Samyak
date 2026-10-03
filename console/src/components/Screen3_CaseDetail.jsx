import { useEffect, useState } from 'react'
import { fetchCase } from '../api'
import { CheckCircle, XCircle, AlertTriangle, ShieldCheck } from 'lucide-react'

export default function Screen3() {
  const [caseData, setCaseData] = useState(null)

  useEffect(() => {
    // Hardcoding specific case to demonstrate the layout
    fetchCase('CASE-7012').then(setCaseData)
  }, [])

  if (!caseData) return <div className="text-gray-400">Loading Case...</div>

  const isBlocked = caseData.dispatch.scrub_verdict === "BLOCKED"

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            Case {caseData.id}
            {isBlocked && (
              <span className="px-2 py-1 text-xs font-bold bg-danger/20 text-danger border border-danger/30 rounded-md">
                ACTION BLOCKED
              </span>
            )}
          </h2>
          <p className="text-gray-400">Deep dive into decision ledger state.</p>
        </div>
        
        {/* Diagnosis Badge */}
        <div className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${
          caseData.diagnosis.level === 'L1' 
            ? 'bg-success/10 border-success/30 text-success' 
            : 'bg-warning/10 border-warning/30 text-warning'
        }`}>
          {caseData.diagnosis.level === 'L1' ? <ShieldCheck className="w-5 h-5"/> : <AlertTriangle className="w-5 h-5"/>}
          <div>
            <div className="font-bold">{caseData.diagnosis.level} Diagnosis: {caseData.diagnosis.root_cause}</div>
            <div className="text-xs opacity-80">{caseData.diagnosis.description}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Raw Event */}
        <div className="glass-panel p-6 space-y-4">
          <h3 className="text-lg font-semibold border-b border-white/10 pb-2">Raw Event Payload</h3>
          <pre className="text-sm bg-black/50 p-4 rounded-lg overflow-x-auto text-gray-300 font-mono">
            {JSON.stringify(caseData.raw_event, null, 2)}
          </pre>
        </div>

        {/* Constraint Inspector */}
        <div className="glass-panel p-6 space-y-4">
          <h3 className="text-lg font-semibold border-b border-white/10 pb-2">Constraint Inspector</h3>
          <div className="space-y-3">
            {caseData.constraints.map(c => (
              <div key={c.id} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                {c.pass ? <CheckCircle className="text-success shrink-0" /> : <XCircle className="text-danger shrink-0" />}
                <div>
                  <div className="font-mono text-sm font-bold text-gray-200">{c.id}</div>
                  <div className="text-sm text-gray-400">{c.desc}</div>
                  {!c.pass && c.citation && (
                    <div className="mt-1 text-xs text-danger flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> Blocked by: {c.citation}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Plans and Timeline */}
        <div className="glass-panel p-6 space-y-4 lg:col-span-2">
          <h3 className="text-lg font-semibold border-b border-white/10 pb-2">Solver Plans & Execution</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
            <div className="md:col-span-1 space-y-3">
              <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Considered Plans</h4>
              {caseData.plans_considered.map(p => (
                <div key={p.id} className={`p-3 border rounded-lg flex justify-between items-center ${
                  p.id === caseData.chosen_plan.id ? 'bg-primary/20 border-primary/50' : 'bg-white/5 border-white/10 opacity-60'
                }`}>
                  <div>
                    <div className="font-bold">{p.action}</div>
                    <div className="text-xs">EV: ₹{p.ev.toFixed(2)}</div>
                  </div>
                  {p.feasible ? <span className="text-xs text-success bg-success/10 px-2 py-1 rounded">FEASIBLE</span> 
                              : <span className="text-xs text-danger bg-danger/10 px-2 py-1 rounded">INFEASIBLE</span>}
                </div>
              ))}
            </div>
            
            <div className="md:col-span-2 space-y-3">
              <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Execution Timeline</h4>
              <div className="relative border-l border-white/20 ml-3 space-y-6">
                {caseData.chosen_plan.timeline.map((step, idx) => (
                  <div key={idx} className="relative pl-6">
                    <div className="absolute w-3 h-3 bg-primary rounded-full -left-[6.5px] top-1.5 ring-4 ring-background"></div>
                    <div className="text-sm text-gray-300">{step}</div>
                  </div>
                ))}
              </div>

              {/* DLT Scrub Verdict highlighted */}
              {isBlocked && (
                <div className="mt-6 bg-danger/20 border border-danger/50 p-4 rounded-lg flex items-start gap-4 animate-pulse">
                  <ShieldCheck className="w-8 h-8 text-danger shrink-0 mt-1" />
                  <div>
                    <h4 className="font-bold text-danger">DLT Scrub Blocked Execution</h4>
                    <p className="text-sm text-danger/80">
                      The scheduled outbound message failed template variable validation. 
                      Execution was safely aborted and marked terminal in the ledger.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
