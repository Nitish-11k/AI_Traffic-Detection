import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { Play, Square, AlertOctagon, Car, Activity } from 'lucide-react';

// --- CONFIG (YAHAN BHI URL/KEY DALO) ---
const supabase = createClient(
  'https://pltcwxcaxfkhhwsfpcvg.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsdGN3eGNheGZraGh3c2ZwY3ZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2NzQwODUsImV4cCI6MjA4MDI1MDA4NX0.QLwf-s6WHriFK6-osXCntlzR9AruM5Hr9r3Li-WU2-M'
);

const RealTimeMonitoring: React.FC = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [violations, setViolations] = useState<any[]>([]);
  const [streamUrl, setStreamUrl] = useState("");

  useEffect(() => {
    // 1. Purana Data Lao
    const fetchHistory = async () => {
      const { data } = await supabase
        .from('violations')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(5);
      if (data) setViolations(data);
    };
    fetchHistory();

    // 2. Real-time Listener (Magic)
    const channel = supabase
      .channel('live-traffic')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'violations' }, (payload) => {
        console.log("New Violation:", payload.new);
        setViolations((prev) => [payload.new, ...prev].slice(0, 7)); // Show top 7
      })
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  const toggleMonitoring = () => {
    if (isMonitoring) {
      setIsMonitoring(false);
      setStreamUrl("");
    } else {
      setIsMonitoring(true);
      // Cache busting timestamp
      setStreamUrl(`http://localhost:8000/video_feed?t=${Date.now()}`);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Live AI Traffic Monitor</h1>
        <button
          onClick={toggleMonitoring}
          className={`px-6 py-2 rounded-lg font-bold flex items-center gap-2 text-white ${isMonitoring ? 'bg-red-600' : 'bg-blue-600'}`}
        >
          {isMonitoring ? <><Square size={20}/> Stop Feed</> : <><Play size={20}/> Start Feed</>}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* VIDEO PLAYER */}
        <div className="lg:col-span-2 bg-black rounded-xl overflow-hidden shadow-2xl h-[480px] relative flex items-center justify-center">
          {isMonitoring ? (
            <img src={streamUrl} alt="Live Stream" className="w-full h-full object-contain" />
          ) : (
            <div className="text-gray-500 flex flex-col items-center">
              <Activity size={48} className="mb-2"/>
              <p>Feed Offline</p>
            </div>
          )}
          {isMonitoring && <div className="absolute top-4 right-4 bg-red-600 text-white px-3 py-1 rounded animate-pulse font-bold text-sm">LIVE</div>}
        </div>

        {/* ALERTS PANEL */}
        <div className="bg-white rounded-xl shadow-lg border p-4 h-[480px] overflow-y-auto">
          <h2 className="font-bold text-lg mb-4 flex items-center gap-2 border-b pb-2">
            <AlertOctagon className="text-red-500"/> Recent Violations
          </h2>

          <div className="space-y-3">
            {violations.map((v) => (
              <div key={v.id} className="p-3 bg-red-50 border-l-4 border-red-500 rounded shadow-sm transition-all hover:bg-red-100">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-red-800 capitalize">{v.type.replace('_', ' ')}</h3>
                    <p className="text-xs text-gray-600 mt-1 flex items-center gap-1">
                      <Car size={12}/> ID: {v.vehicle_id || 'Unknown'}
                    </p>
                  </div>
                  <span className="text-xs font-mono bg-white px-2 py-1 rounded border">
                    {new Date(v.created_at).toLocaleTimeString()}
                  </span>
                </div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-red-500 h-1.5 rounded-full" style={{width: `${v.confidence * 100}%`}}></div>
                </div>
              </div>
            ))}

            {violations.length === 0 && (
              <p className="text-center text-gray-400 mt-10">No violations detected yet...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitoring;