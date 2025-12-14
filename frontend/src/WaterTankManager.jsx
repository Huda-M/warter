import React, { useState, useEffect } from "react";
import {
  Droplets,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Bot,
  Hand
} from "lucide-react";

const DEFAULT_TARGET = 80;
const LEAK_THRESHOLD = 0.3;

export default function WaterTankManager() {
  const [waterLevel, setWaterLevel] = useState(60);
  const [capacity] = useState(1000);
  const [flowRate, setFlowRate] = useState(20);

  const [isFilling, setIsFilling] = useState(false);
  const [isDraining, setIsDraining] = useState(false);

  const [isAiMode, setIsAiMode] = useState(true);
  const [targetLevel, setTargetLevel] = useState(null);

  const [aiLogs, setAiLogs] = useState([]);
  const [previousLevel, setPreviousLevel] = useState(waterLevel);
  const [leakDetected, setLeakDetected] = useState(false);

  const effectiveTarget = targetLevel ?? DEFAULT_TARGET;
  const currentVolume = ((waterLevel / 100) * capacity).toFixed(0);

  const addAiLog = (text) => {
    setAiLogs((prev) => [
      {
        time: new Date().toLocaleTimeString("en-US"),
        text
      },
      ...prev.slice(0, 4)
    ]);
  };

  useEffect(() => {
    let interval;

    if (isFilling) {
      interval = setInterval(() => {
        setWaterLevel((prev) =>
          prev >= effectiveTarget && isAiMode
            ? prev
            : Math.min(prev + flowRate / 20, 100)
        );
      }, 1000);
    }

    if (isDraining) {
      interval = setInterval(() => {
        setWaterLevel((prev) =>
          prev <= effectiveTarget && isAiMode
            ? prev
            : Math.max(prev - flowRate / 20, 0)
        );
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isFilling, isDraining, flowRate, effectiveTarget, isAiMode]);

  const makeAiDecision = () => {
    if (leakDetected) return;

    if (waterLevel < effectiveTarget - 1) {
      setIsFilling(true);
      setIsDraining(false);
      addAiLog(`📈 Filling to ${effectiveTarget}%`);
    } else if (waterLevel > effectiveTarget + 1) {
      setIsDraining(true);
      setIsFilling(false);
      addAiLog(`📉 Draining to ${effectiveTarget}%`);
    } else {
      setIsFilling(false);
      setIsDraining(false);
      addAiLog(`⏸ Stable at ${effectiveTarget}%`);
    }
  };

  useEffect(() => {
    if (!isAiMode) return;

    const aiInterval = setInterval(makeAiDecision, 2000);
    return () => clearInterval(aiInterval);
  }, [isAiMode, waterLevel, effectiveTarget, leakDetected]);

  useEffect(() => {
    if (isFilling || isDraining) {
      setPreviousLevel(waterLevel);
      return;
    }

    const diff = previousLevel - waterLevel;

    if (diff > LEAK_THRESHOLD && isAiMode) {
      setLeakDetected(true);
      setIsFilling(false);
      setIsDraining(false);
      addAiLog("🚨 Water leak detected!");
    }

    setPreviousLevel(waterLevel);
  }, [waterLevel]);

  const getColor = () => {
    if (waterLevel < 30) return "bg-red-500";
    if (waterLevel < 60) return "bg-yellow-400";
    return "bg-blue-500";
  };

  return (
    <div className="min-h-screen bg-blue-50 p-6">
      <div className="max-w-5xl mx-auto space-y-6">

        <h1 className="text-4xl font-bold text-center text-blue-900 flex justify-center gap-2 items-center">
          <Droplets /> Water Tank Management System
        </h1>

        <div className="bg-white p-4 rounded-xl shadow flex justify-between items-center">
          <div className="flex gap-3 items-center font-bold">
            {isAiMode ? <Bot /> : <Hand />}
            {isAiMode ? "AI Control" : "Manual Control"}
          </div>
          <button
            onClick={() => {
              setIsAiMode(!isAiMode);
              setIsFilling(false);
              setIsDraining(false);
              setLeakDetected(false);
              addAiLog(
                isAiMode
                  ? "🖐 Manual control activated"
                  : "🤖 AI control activated"
              );
            }}
            className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          >
            Switch Mode
          </button>
        </div>

        {leakDetected && (
          <div className="bg-red-100 border border-red-500 text-red-700 p-4 rounded shadow flex gap-2 items-center">
            <AlertTriangle />
            <span className="font-bold">
              Warning: Water leak detected in the tank!
            </span>
          </div>
        )}

        <div className="bg-white p-6 rounded-xl shadow">
          <div className="relative h-72 bg-gray-200 rounded overflow-hidden border-2 border-gray-300">
            <div
              className={`absolute bottom-0 w-full transition-all duration-500 ${getColor()}`}
              style={{ height: `${waterLevel}%` }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-white p-4 rounded shadow text-center">
                <div className="text-4xl font-bold">{waterLevel.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">
                  {currentVolume} / {capacity} liters
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow">
            <label className="font-bold block mb-2">
              Target Level: {effectiveTarget}%
            </label>
            <input
              type="range"
              min="20"
              max="95"
              value={effectiveTarget}
              onChange={(e) => setTargetLevel(Number(e.target.value))}
              className="w-full"
            />

            <label className="font-bold mt-4 block mb-2">
              Flow Rate (liters/minute)
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={flowRate}
              onChange={(e) => setFlowRate(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-center font-bold text-lg mt-2">{flowRate}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow space-y-4">
            <h3 className="font-bold text-lg mb-4">Manual Controls</h3>
            <button
              disabled={isAiMode}
              onClick={() => {
                setIsFilling(true);
                setIsDraining(false);
              }}
              className="w-full p-3 bg-green-500 text-white rounded disabled:bg-gray-300 hover:bg-green-600 transition-colors flex items-center justify-center gap-2 font-semibold"
            >
              <TrendingUp /> Start Filling
            </button>

            <button
              disabled={isAiMode}
              onClick={() => {
                setIsDraining(true);
                setIsFilling(false);
              }}
              className="w-full p-3 bg-red-500 text-white rounded disabled:bg-gray-300 hover:bg-red-600 transition-colors flex items-center justify-center gap-2 font-semibold"
            >
              <TrendingDown /> Start Draining
            </button>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="font-bold text-xl mb-3">AI Decision Log</h2>
          {aiLogs.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No logs yet</p>
          ) : (
            <div className="space-y-1">
              {aiLogs.map((log, i) => (
                <div key={i} className="flex justify-between border-b py-2 hover:bg-gray-50">
                  <span>{log.text}</span>
                  <span className="text-sm text-gray-500">{log.time}</span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}