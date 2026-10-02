import { useEffect } from 'react';
import { useGameStore } from './store/gameStore';
import { useGameClock } from './hooks/useGameClock';
import { CityMap3D } from './components/CityMap3D';
import { SidePanel } from './components/SidePanel';
import { StartScreen } from './components/StartScreen';
import { SurvivorsPanel } from './components/SurvivorsPanel';
import { TopBar } from './components/TopBar';
import { GameOverOverlay, NightTint, NoticeToast, SiegeBanner } from './components/Overlays';

/**
 * Raiz da aplicacao.
 *
 * Retoma a partida salva ao abrir e escolhe entre carregamento, erro de
 * conexao, tela inicial e o jogo em si.
 */
function App() {
  const { init, loaded, game, fatalError } = useGameStore();
  useGameClock();

  useEffect(() => {
    void init();
  }, [init]);

  return (
    <div className="w-screen h-screen bg-gray-900 text-gray-100 flex flex-col font-mono relative overflow-hidden">
      {!loaded ? (
        <div className="flex-1 flex items-center justify-center text-yellow-500 animate-pulse text-xl">
          ESTABLISHING SATELLITE UPLINK...
        </div>
      ) : fatalError ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="border border-red-500/50 bg-red-900/10 p-8 rounded flex flex-col items-center gap-4">
            <h2 className="text-2xl text-red-500 font-bold tracking-widest">SIGNAL LOST</h2>
            <p className="text-red-400 text-center max-w-md">{fatalError}</p>
            <button
              onClick={() => void init()}
              className="px-6 py-2 border border-red-500 text-red-500 hover:bg-red-500 hover:text-white transition-all uppercase tracking-wider"
            >
              Retry Uplink
            </button>
          </div>
        </div>
      ) : !game ? (
        <StartScreen />
      ) : (
        <>
          <TopBar />
          <div className="flex-1 flex min-h-0">
            <SurvivorsPanel />
            <main className="flex-1 relative bg-[#1e1e1e] min-w-0">
              <CityMap3D />
              <NightTint />
              <SiegeBanner />
            </main>
            <SidePanel />
          </div>
          <GameOverOverlay />
        </>
      )}
      <NoticeToast />
    </div>
  );
}

export default App;
