import { useEffect, useState } from 'react'
import { fetchFunnel } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Screen1() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchFunnel().then(res => {
      const chartData = [
        { name: '₹ At Risk', Treatment: res.treatment.at_risk, Holdout: res.holdout.at_risk },
        { name: '₹ Suppressed', Treatment: res.treatment.suppressed, Holdout: res.holdout.suppressed },
        { name: '₹ Feasible', Treatment: res.treatment.feasible, Holdout: res.holdout.feasible },
        { name: '₹ Acted On', Treatment: res.treatment.acted, Holdout: res.holdout.acted },
        { name: '₹ Recovered', Treatment: res.treatment.recovered, Holdout: res.holdout.recovered }
      ]
      setData(chartData)
    })
  }, [])

  if (!data) return <div className="text-gray-400">Loading Funnel...</div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold">Recovery Funnel</h2>
        <p className="text-gray-400">Comparing Samyak control plane against baseline holdout.</p>
      </div>
      
      <div className="glass-panel p-6 h-[500px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
            <XAxis dataKey="name" stroke="#a1a1aa" />
            <YAxis 
              stroke="#a1a1aa" 
              tickFormatter={(val) => `₹${(val/1000).toFixed(0)}k`}
            />
            <Tooltip 
              cursor={{fill: '#ffffff05'}}
              contentStyle={{ backgroundColor: '#15151e', borderColor: '#ffffff20', color: '#fff' }}
              formatter={(value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(value)}
            />
            <Legend />
            <Bar dataKey="Holdout" fill="#3f3f46" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Treatment" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
