import React, { useState, useEffect } from 'react';
import { Download, Search, AlertTriangle, Car, Users, MapPin, BarChart3, Eye } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { apiService, Violation, ViolationStats } from '../services/api';

// Update Interface to include image
interface ViolationWithImage extends Violation {
  violation_image?: string;
}

const ViolationReports: React.FC = () => {
  const [violations, setViolations] = useState<ViolationWithImage[]>([]);
  const [stats, setStats] = useState<ViolationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState<string | null>(null); // For Modal

  useEffect(() => {
    fetchViolations();
  }, []);

  const fetchViolations = async () => {
    try {
      setLoading(true);
      const response = await apiService.getViolations();
      // @ts-ignore
      setViolations(response.violations);
      setStats(response.statistics);
    } catch (error) {
      console.error('Error fetching violations:', error);
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

  // Mock data for charts if stats are missing
  const pieData = stats && stats.by_type ? [
    { name: 'Red Light', value: stats.by_type.red_light || 0, color: '#ef4444' },
    { name: 'Wrong Side', value: stats.by_type.wrong_side || 0, color: '#f59e0b' },
    { name: 'No Helmet', value: stats.by_type.no_helmet || 0, color: '#8b5cf6' },
  ] : [];

  if (loading) {
    return <div className="flex justify-center p-10">Loading Reports...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Violation Reports</h1>
          <p className="text-gray-600">Proof of Violations</p>
        </div>
        <button onClick={fetchViolations} className="btn-primary flex items-center gap-2">
            <BarChart3 className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-white p-4 rounded shadow border-l-4 border-blue-500">
            <p className="text-gray-500">Total Violations</p>
            <p className="text-2xl font-bold">{stats?.total_violations || 0}</p>
        </div>
        <div className="card bg-white p-4 rounded shadow border-l-4 border-red-500">
            <p className="text-gray-500">Red Light</p>
            <p className="text-2xl font-bold">{stats?.by_type?.red_light || 0}</p>
        </div>
        <div className="card bg-white p-4 rounded shadow border-l-4 border-yellow-500">
            <p className="text-gray-500">Wrong Side</p>
            <p className="text-2xl font-bold">{stats?.by_type?.wrong_side || 0}</p>
        </div>
        <div className="card bg-white p-4 rounded shadow border-l-4 border-purple-500">
            <p className="text-gray-500">No Helmet</p>
            <p className="text-2xl font-bold">{stats?.by_type?.no_helmet || 0}</p>
        </div>
      </div>

      {/* Violations Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Proof</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {violations.map((violation) => (
              <tr key={violation.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-bold capitalize" style={{ color: getViolationTypeColor(violation.type) }}>
                    {violation.type.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4">{violation.vehicle_id}</td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {new Date(violation.timestamp).toLocaleString()}
                </td>
                <td className="px-6 py-4">{(violation.confidence * 100).toFixed(1)}%</td>
                <td className="px-6 py-4">
                  {violation.violation_image ? (
                    <button
                        onClick={() => setSelectedImage(violation.violation_image || null)}
                        className="text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium"
                    >
                        <Eye size={16} /> View Proof
                    </button>
                  ) : (
                    <span className="text-gray-400">No Image</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" onClick={() => setSelectedImage(null)}>
            <div className="bg-white p-2 rounded-lg max-w-3xl w-full">
                <img src={selectedImage} alt="Proof" className="w-full h-auto rounded" />
                <p className="text-center mt-2 text-gray-500 text-sm">Click outside to close</p>
            </div>
        </div>
      )}
    </div>
  );
};

export default ViolationReports;