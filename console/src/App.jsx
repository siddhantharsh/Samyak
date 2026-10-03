import { useState } from 'react'
import Screen1 from './components/Screen1_MoneyFunnel'
import Screen3 from './components/Screen3_CaseDetail'
import Screen5 from './components/Screen5_PolicyComparison'

function App() {
  const [currentScreen, setCurrentScreen] = useState('1')

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-panel border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center font-bold">
            S
          </div>
          <h1 className="text-xl font-bold tracking-tight">Samyak Control Plane</h1>
        </div>
        <nav className="flex gap-2">
          {[
            { id: '1', label: 'Funnel' },
            { id: '3', label: 'Case Detail' },
            { id: '5', label: 'Policy Compare' }
          ].map(s => (
            <button
              key={s.id}
              onClick={() => setCurrentScreen(s.id)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                currentScreen === s.id 
                  ? 'bg-primary text-white' 
                  : 'hover:bg-white/10 text-gray-400 hover:text-white'
              }`}
            >
              {s.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          {currentScreen === '1' && <Screen1 />}
          {currentScreen === '3' && <Screen3 />}
          {currentScreen === '5' && <Screen5 />}
        </div>
      </main>
    </div>
  )
}

export default App
