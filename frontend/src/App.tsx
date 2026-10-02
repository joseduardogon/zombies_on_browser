import { useEffect } from 'react';
import { useGameStore } from './store/gameStore';
import { BuildingView } from './components/BuildingView';
import { CityMap3D } from './components/CityMap3D';

/**
 * Raiz da aplicacao.
 *
 * Gera o mundo ao montar e alterna entre carregamento, erro e o mapa da cidade.
 */
function App() {
  const { generateWorld, isLoading, error } = useGameStore();

  useEffect(() => {
    generateWorld();
  }, [generateWorld]);

  return (
    <div className="w-screen h-screen bg-gray-900 text-gray-100 flex flex-col font-mono relative overflow-hidden">
      <BuildingView />

      <header className="absolute top-0 left-0 p-4 z-20 pointer-events-none">
        <h1 className="text-xl font-bold tracking-wider text-green-500 drop-shadow-md">
          COMMANDER INTERFACE // Z-CITY
        </h1>
      </header>

      <main className="flex-1 w-full h-full relative bg-[#1e1e1e]">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-30">
            <div className="text-yellow-500 animate-pulse text-xl">ESTABLISHING SATELLITE UPLINK...</div>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-30">
            <div className="border border-red-500/50 bg-red-900/10 p-8 rounded flex flex-col items-center gap-4">
              <h2 className="text-2xl text-red-500 font-bold tracking-widest">SIGNAL LOST</h2>
              <p className="text-red-400 font-mono text-center max-w-md">{error || 'CONNECTION FAILED'}</p>
              <button
                onClick={() => generateWorld()}
                className="px-6 py-2 border border-red-500 text-red-500 hover:bg-red-500 hover:text-white transition-all uppercase tracking-wider"
              >
                Retry Uplink
              </button>
            </div>
          </div>
        ) : (
          <CityMap3D />
        )}
      </main>

      <footer className="absolute bottom-0 w-full p-2 border-t border-gray-700 text-xs text-gray-500 flex justify-between bg-gray-800 z-20">
        <span>STATUS: ONLINE</span>
        <span>VERSION: 0.1.0 3D</span>
      </footer>
    </div>
  );
}

export default App;
