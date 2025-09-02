import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Car, 
  Users, 
  TrendingUp, 
  Clock,
  MapPin,
  Activity
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { apiService } from '../services/api';

interface ViolationStats {
  total_violations: number;
  by_type: {
    red_light: number;
    wrong_side: number;
    no_helmet: number;
  };
  recent_violations: number;
  violation_rate: number;
}

interface RecentViolation {
  id: string;
  type: string;
  timestamp: string;
  confidence: number;
  location: { x: number; y: number };
  vehicle_id: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<ViolationStats | null>(null);
  const [recentViolations, setRecentViolations] = useState<RecentViolation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [violationsResponse, statsResponse] = await Promise.all([
        apiService.getViolations(),
        apiService.getViolationStats()
      ]);
      
      setRecentViolations(violationsResponse.violations.slice(0, 5));
      setStats(statsResponse);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getViolationTypeColor = (type: string) => {
    switch (type) {
      case 'red_light': return '#ef4444';
      case 'wrong_side': return '#f59e0b';
      case 'no_helmet': return '#8b5cf6';
      default: return '#6b7280';
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

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Mock data for charts
  const violationTrendData = [
    { time: '00:00', violations: 2 },
    { time: '04:00', violations: 1 },
    { time: '08:00', violations: 8 },
    { time: '12:00', violations: 12 },
    { time: '16:00', violations: 15 },
    { time: '20:00', violations: 6 },
  ];

  const pieData = stats ? [
    { name: 'Red Light', value: stats.by_type.red_light, color: '#ef4444' },
    { name: 'Wrong Side', value: stats.by_type.wrong_side, color: '#f59e0b' },
    { name: 'No Helmet', value: stats.by_type.no_helmet, color: '#8b5cf6' },
  ] : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">AI Traffic Violation Detection System</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={fetchDashboardData}
            className="btn-primary flex items-center space-x-2"
          >
            <Activity className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Violations</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_violations || 0}</p>
            </div>
            <div className="p-3 bg-danger-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-danger-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-success-600 font-medium">+12%</span>
            <span className="text-gray-500 ml-1">from last hour</span>
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Red Light Violations</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.by_type.red_light || 0}</p>
            </div>
            <div className="p-3 bg-danger-100 rounded-lg">
              <Car className="w-6 h-6 text-danger-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-gray-500">Most common violation</span>
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Wrong Side Driving</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.by_type.wrong_side || 0}</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <MapPin className="w-6 h-6 text-warning-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-gray-500">Direction violations</span>
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">No Helmet</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.by_type.no_helmet || 0}</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <Users className="w-6 h-6 text-warning-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-gray-500">Safety violations</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Violation Trend */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Violation Trend (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={violationTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="violations" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Violation Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Violation Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Violations */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Recent Violations</h3>
          <Clock className="w-5 h-5 text-gray-400" />
        </div>
        
        {recentViolations.length > 0 ? (
          <div className="space-y-4">
            {recentViolations.map((violation) => (
              <div key={violation.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: getViolationTypeColor(violation.type) }}
                  ></div>
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
                    Location: ({violation.location.x.toFixed(0)}, {violation.location.y.toFixed(0)})
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No recent violations detected</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

