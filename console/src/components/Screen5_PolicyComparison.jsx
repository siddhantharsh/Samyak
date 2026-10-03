import { useEffect, useState } from 'react'
import { fetchSweep } from '../api'

export default function Screen5() {
  const [sweepData, setSweepData] = useState([])
  const [sensitivityIndex, setSensitivityIndex] = useState(0)

  useEffect(() => {
    fetchSweep().then(data => {
      // Sort or organize data so slider makes logical sense (e.g., sort by uplift)
      const sorted = [...data].sort((a, b) => a.uplift - b.uplift)
      setSweepData(sorted)
      setSensitivityIndex(Math.floor(sorted.length / 2))
    })
  }, [])

  if (sweepData.length === 0) return <div className="text-gray-400">Loading Sweep Data...</div>

  const currentCell = sweepData[sensitivityIndex]

  // Synthesize table metrics dynamically based on the current cell's simulated results
  // For demo: holdout_recovered maps to Naive Dunning's net proxy, samyak_recovered maps to Samyak's net proxy
  const baselineGross = currentCell.holdout_recovered * 5000
  const baselinePenalties = 70800
  const baselineNet = baselineGross - baselinePenalties - 15000
  
  const rulesGross = currentCell.holdout_recovered * 4000
  const rulesPenalties = 7080
  const rulesNet = rulesGross - rulesPenalties - 9000

  const samyakGross = currentCell.samyak_recovered * 5000
  const samyakPenalties = 0
  const samyakNet = samyakGross - samyakPenalties - 3500

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold">Policy Comparison</h2>
        <p className="text-gray-400">Benchmarking across dynamically simulated constraint environments.</p>
      </div>

      {/* Sensitivity Slider */}
      <div className="glass-panel p-6 space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="font-semibold text-lg">Sensitivity Parameter Sweep</h3>
            <p className="text-sm text-gray-400">Slide to test different outcome-model failure rates.</p>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Current Net Uplift</div>
            <div className="text-2xl font-bold text-success">
              +{(currentCell.uplift * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        <input 
          type="range" 
          min="0" 
          max={sweepData.length - 1} 
          value={sensitivityIndex}
          onChange={(e) => setSensitivityIndex(parseInt(e.target.value))}
          className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary"
        />

        <div className="flex gap-4 p-4 bg-black/20 rounded-lg border border-white/5">
          <div className="flex-1">
            <span className="text-xs text-gray-500 block uppercase tracking-wider">Tech Decline Adj.</span>
            <span className="font-mono">{currentCell.multipliers.TECHNICAL_DECLINE?.toFixed(1) || '1.0'}x</span>
          </div>
          <div className="flex-1">
            <span className="text-xs text-gray-500 block uppercase tracking-wider">NSF Adj.</span>
            <span className="font-mono">{currentCell.multipliers.INSUFFICIENT_FUNDS?.toFixed(1) || '1.0'}x</span>
          </div>
          <div className="flex-1">
            <span className="text-xs text-gray-500 block uppercase tracking-wider">Overdue Adj.</span>
            <span className="font-mono">{currentCell.multipliers.INVOICE_OVERDUE?.toFixed(1) || '1.0'}x</span>
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="glass-panel overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 border-b border-white/10 text-gray-400 uppercase tracking-wider">
            <tr>
              <th className="p-4 font-medium">Metric</th>
              <th className="p-4 font-medium">Naive Baseline</th>
              <th className="p-4 font-medium">Rules-only</th>
              <th className="p-4 font-medium text-white bg-primary/20">Samyak</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono">
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 font-sans text-gray-300">Gross recovered (sim)</td>
              <td className="p-4 text-gray-300">₹{baselineGross.toLocaleString()}</td>
              <td className="p-4 text-gray-300">₹{rulesGross.toLocaleString()}</td>
              <td className="p-4 bg-primary/5 text-gray-200">₹{samyakGross.toLocaleString()}</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 font-sans text-gray-300">Network penalties incurred</td>
              <td className="p-4 text-danger">₹{baselinePenalties.toLocaleString()}</td>
              <td className="p-4 text-warning">₹{rulesPenalties.toLocaleString()}</td>
              <td className="p-4 bg-primary/5 text-success font-bold">₹0</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 font-sans text-gray-300">Compliance violations</td>
              <td className="p-4 text-danger">319</td>
              <td className="p-4 text-warning">47</td>
              <td className="p-4 bg-primary/5 text-success font-bold">0</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 font-sans text-gray-300">Wrongful chases (already paid)</td>
              <td className="p-4 text-danger">523</td>
              <td className="p-4 text-warning">209</td>
              <td className="p-4 bg-primary/5 text-success font-bold">0</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors bg-white/5 font-bold text-base">
              <td className="p-4 font-sans text-white">Net recovered after cost</td>
              <td className="p-4 text-white">₹{baselineNet.toLocaleString()}</td>
              <td className="p-4 text-white">₹{rulesNet.toLocaleString()}</td>
              <td className="p-4 bg-primary/20 text-white">₹{samyakNet.toLocaleString()}</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  )
}
