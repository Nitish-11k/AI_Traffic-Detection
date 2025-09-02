import React, { useState, useEffect } from 'react';
import { 
  Download, 
  Filter, 
  Search, 
  Calendar,
  MapPin,
  Clock,
  AlertTriangle,
  Car,
  Users,
  TrendingUp,
  BarChart3
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { apiService, Violation, ViolationStats } from '../services/api';

const ViolationReports: React.FC = () => {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [stats, setStats] = useState<ViolationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [dateRange, setDateRange] = useState('7d');

  useEffect(() => {
    fetchViolations();
  }, []);

  const fetchViolations = async () => {
    try {
      setLoading(true);
      const response = await apiService.getViolations();
      setViolations(response.violations);
      setStats(response.statistics);
    } catch (error) {
      console.error('Error fetching violations:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredViolations = violations.filter(violation => {
    const matchesSearch = violation.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         violation.vehicle_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || violation.type === filterType;
    return matchesSearch && matchesFilter;
  });

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

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString();
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Type', 'Timestamp', 'Confidence', 'Vehicle ID', 'Location X', 'Location Y'];
    const csvContent = [
      headers.join(','),
      ...filteredViolations.map(v => [
        v.id,
        v.type,
        v.timestamp,
        v.confidence,
        v.vehicle_id,
        v.location.x,
        v.location.y
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `violations_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Mock data for charts
  const hourlyData = [
    { hour: '00:00', violations: 2 },
    { hour: '04:00', violations: 1 },
    { hour: '08:00', violations: 8 },
    { hour: '12:00', violations: 12 },
    { hour: '16:00', violations: 15 },
    { hour: '20:00', violations: 6 },
  ];

  const dailyData = [
    { day: 'Mon', violations: 45 },
    { day: 'Tue', violations: 52 },
    { day: 'Wed', violations: 38 },
    { day: 'Thu', violations: 61 },
    { day: 'Fri', violations: 78 },
    { day: 'Sat', violations: 42 },
    { day: 'Sun', violations: 35 },
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
          <h1 className="text-3xl font-bold text-gray-900">Violation Reports</h1>
          <p className="text-gray-600 mt-1">Comprehensive analysis of traffic violations</p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button
            onClick={exportToCSV}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={fetchViolations}
            className="btn-primary flex items-center space-x-2"
          >
            <BarChart3 className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
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
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Violations */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Violations (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="violations" fill="#3b82f6" />
            </BarChart>
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

      {/* Filters and Search */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search violations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 input w-full sm:w-64"
              />
            </div>

            {/* Filter by type */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input w-full sm:w-48"
            >
              <option value="all">All Types</option>
              <option value="red_light">Red Light</option>
              <option value="wrong_side">Wrong Side</option>
              <option value="no_helmet">No Helmet</option>
            </select>

            {/* Date range */}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="input w-full sm:w-48"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>

          <div className="text-sm text-gray-500">
            Showing {filteredViolations.length} of {violations.length} violations
          </div>
        </div>
      </div>

      {/* Violations Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Violation Details</h3>
        
        {filteredViolations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vehicle ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date & Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredViolations.map((violation) => (
                  <tr key={violation.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div 
                          className="w-3 h-3 rounded-full mr-3"
                          style={{ backgroundColor: getViolationTypeColor(violation.type) }}
                        ></div>
                        <span className="text-sm font-medium text-gray-900">
                          {getViolationTypeLabel(violation.type)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {violation.vehicle_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatDate(violation.timestamp)}</div>
                      <div className="text-sm text-gray-500">{formatTime(violation.timestamp)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        violation.confidence > 0.8 
                          ? 'bg-success-100 text-success-800'
                          : violation.confidence > 0.6
                          ? 'bg-warning-100 text-warning-800'
                          : 'bg-danger-100 text-danger-800'
                      }`}>
                        {(violation.confidence * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ({violation.location.x.toFixed(0)}, {violation.location.y.toFixed(0)})
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-primary-600 hover:text-primary-900">
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No violations found matching your criteria</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ViolationReports;

