import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  Wifi, 
  WifiOff,
  AlertTriangle,
  Car,
  Users,
  MapPin,
  Activity,
  Settings
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiService } from '../services/api';

interface RealTimeViolation {
  id: string;
  type: string;
  timestamp: string;
  confidence: number;
  location: { x: number; y: number };
  vehicle_id: string;
}

const RealTimeMonitoring: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [violations, setViolations] = useState<RealTimeViolation[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    red_light: 0,
    wrong_side: 0,
    no_helmet: 0
  });
  const [recentViolations, setRecentViolations] = useState<RealTimeViolation[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      setConnectionStatus('connecting');
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'violation') {
            const violation: RealTimeViolation = data.data;
            handleNewViolation(violation);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        console.log('WebSocket disconnected');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setConnectionStatus('disconnected');
  };

  const handleNewViolation = (violation: RealTimeViolation) => {
    setViolations(prev => [violation, ...prev.slice(0, 99)]); // Keep last 100 violations
    setRecentViolations(prev => [violation, ...prev.slice(0, 9)]); // Keep last 10 violations
    
    // Update stats
    setStats(prev => ({
      total: prev.total + 1,
      red_light: violation.type === 'red_light' ? prev.red_light + 1 : prev.red_light,
      wrong_side: violation.type === 'wrong_side' ? prev.wrong_side + 1 : prev.wrong_side,
      no_helmet: violation.type === 'no_helmet' ? prev.no_helmet + 1 : prev.no_helmet,
    }));
  };

  const startMonitoring = () => {
    setIsMonitoring(true);
    connectWebSocket();
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
    disconnectWebSocket();
    setViolations([]);
    setRecentViolations([]);
    setStats({ total: 0, red_light: 0, wrong_side: 0, no_helmet: 0 });
  };

  const getViolationTypeColor = (type: string) => {
    switch (type) {
      case 'red_light': return 'bg-danger-100 text-danger-800 border-danger-200';
      case 'wrong_side': return 'bg-warning-100 text-warning-800 border-warning-200';
      case 'no_helmet': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getViolationTypeLabel = (type: string) => {
    switch (type) {
      case 'red_light': return 'Red Light Violation';
      case 'wrong_side': return 'Wrong Side Driving';
      case 'no_helmet': return 'No Helmet';
      default: return type;
    }
  };

  const getViolationTypeIcon = (type: string) => {
    switch (type) {
      case 'red_light': return <Car className="w-4 h-4" />;
      case 'wrong_side': return <MapPin className="w-4 h-4" />;
      case 'no_helmet': return <Users className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Real-Time Monitoring</h1>
          <p className="text-gray-600 mt-1">Live traffic violation detection and monitoring</p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {connectionStatus === 'connected' ? (
              <Wifi className="w-5 h-5 text-success-600" />
            ) : connectionStatus === 'connecting' ? (
              <div className="w-5 h-5 border-2 border-warning-600 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <WifiOff className="w-5 h-5 text-danger-600" />
            )}
            <span className={`text-sm font-medium ${
              connectionStatus === 'connected' ? 'text-success-600' :
              connectionStatus === 'connecting' ? 'text-warning-600' : 'text-danger-600'
            }`}>
              {connectionStatus === 'connected' ? 'Connected' :
               connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
            </span>
          </div>

          {/* Control Buttons */}
          {!isMonitoring ? (
            <button
              onClick={startMonitoring}
              className="btn-primary flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>Start Monitoring</span>
            </button>
          ) : (
            <button
              onClick={stopMonitoring}
              className="btn-danger flex items-center space-x-2"
            >
              <Square className="w-4 h-4" />
              <span>Stop Monitoring</span>
            </button>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Violations</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 bg-danger-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-danger-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <Activity className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-success-600 font-medium">Live</span>
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Red Light</p>
              <p className="text-3xl font-bold text-gray-900">{stats.red_light}</p>
            </div>
            <div className="p-3 bg-danger-100 rounded-lg">
              <Car className="w-6 h-6 text-danger-600" />
            </div>
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Wrong Side</p>
              <p className="text-3xl font-bold text-gray-900">{stats.wrong_side}</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <MapPin className="w-6 h-6 text-warning-600" />
            </div>
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">No Helmet</p>
              <p className="text-3xl font-bold text-gray-900">{stats.no_helmet}</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <Users className="w-6 h-6 text-warning-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live Violations Feed */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Live Violations</h3>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-danger-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-500">Live</span>
            </div>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {recentViolations.map((violation, index) => (
                <motion.div
                  key={violation.id}
                  initial={{ opacity: 0, x: -20, scale: 0.95 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: 20, scale: 0.95 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-gray-50 rounded-lg border-l-4 border-danger-500"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getViolationTypeIcon(violation.type)}
                      <div>
                        <p className="font-medium text-gray-900">
                          {getViolationTypeLabel(violation.type)}
                        </p>
                        <p className="text-sm text-gray-500">
                          Vehicle ID: {violation.vehicle_id} • Confidence: {(violation.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {formatTime(violation.timestamp)}
                      </p>
                      <p className="text-xs text-gray-500">
                        Just now
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {recentViolations.length === 0 && (
              <div className="text-center py-8">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  {isMonitoring ? 'Waiting for violations...' : 'Start monitoring to see live violations'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Violation History */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent History</h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {violations.slice(0, 20).map((violation) => (
              <div key={violation.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-2 h-2 rounded-full"
                    style={{ 
                      backgroundColor: violation.type === 'red_light' ? '#ef4444' :
                                     violation.type === 'wrong_side' ? '#f59e0b' : '#8b5cf6'
                    }}
                  ></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {getViolationTypeLabel(violation.type)}
                    </p>
                    <p className="text-xs text-gray-500">
                      ID: {violation.vehicle_id}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {formatTime(violation.timestamp)}
                  </p>
                  <p className="text-xs text-gray-400">
                    {(violation.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            ))}
            
            {violations.length === 0 && (
              <div className="text-center py-8">
                <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No violations detected yet</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                isConnected ? 'bg-success-500' : 'bg-danger-500'
              }`}></div>
              <span className="font-medium text-gray-900">WebSocket Connection</span>
            </div>
            <span className={`text-sm font-medium ${
              isConnected ? 'text-success-600' : 'text-danger-600'
            }`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                isMonitoring ? 'bg-success-500' : 'bg-gray-400'
              }`}></div>
              <span className="font-medium text-gray-900">Monitoring Status</span>
            </div>
            <span className={`text-sm font-medium ${
              isMonitoring ? 'text-success-600' : 'text-gray-600'
            }`}>
              {isMonitoring ? 'Active' : 'Inactive'}
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-success-500 rounded-full"></div>
              <span className="font-medium text-gray-900">AI Detection</span>
            </div>
            <span className="text-sm font-medium text-success-600">Online</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitoring;

