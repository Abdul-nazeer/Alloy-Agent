import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface SparePart {
  part_id: string;
  part_name: string;
  equipment_type: string;
  quantity_available: number;
  minimum_stock: number;
  unit_cost: number;
  lead_time_days: number;
  supplier: string;
  status: 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK';
  criticality: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

interface Statistics {
  total_parts: number;
  out_of_stock: number;
  low_stock: number;
  critical_parts: number;
  total_inventory_value: number;
}

const SparePartsInventory: React.FC = () => {
  const [parts, setParts] = useState<SparePart[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterEquipment, setFilterEquipment] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterCriticality, setFilterCriticality] = useState('');

  useEffect(() => {
    fetchSpareparts();
  }, [filterEquipment, filterStatus, filterCriticality]);

  const fetchSpareparts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filterEquipment) params.append('equipment_type', filterEquipment);
      if (filterStatus) params.append('status', filterStatus);
      if (filterCriticality) params.append('criticality', filterCriticality);

      const response = await axios.get(`${API_BASE}/spare-parts?${params.toString()}`);
      setParts(response.data.parts);
      setStatistics(response.data.statistics);
    } catch (error) {
      console.error('Failed to fetch spare parts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'IN_STOCK':
        return 'bg-green-100 text-green-800';
      case 'LOW_STOCK':
        return 'bg-yellow-100 text-yellow-800';
      case 'OUT_OF_STOCK':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCriticalityBadgeClass = (criticality: string) => {
    switch (criticality) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800';
      case 'MEDIUM':
        return 'bg-blue-100 text-blue-800';
      case 'LOW':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const equipmentTypes = ['Air Compressor', 'Cooling Fan System', 'Rolling Mill', 'Conveyor Motor'];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Spare Parts Inventory</h2>
        <p className="text-gray-600">Manage spare parts availability and procurement</p>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Parts</div>
            <div className="text-2xl font-bold text-gray-900">{statistics.total_parts}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Out of Stock</div>
            <div className="text-2xl font-bold text-red-600">{statistics.out_of_stock}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Low Stock</div>
            <div className="text-2xl font-bold text-yellow-600">{statistics.low_stock}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Critical Parts</div>
            <div className="text-2xl font-bold text-orange-600">{statistics.critical_parts}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Inventory Value</div>
            <div className="text-2xl font-bold text-green-600">
              ${statistics.total_inventory_value.toLocaleString()}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Equipment Type</label>
            <select
              value={filterEquipment}
              onChange={(e) => setFilterEquipment(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Equipment</option>
              {equipmentTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="IN_STOCK">In Stock</option>
              <option value="LOW_STOCK">Low Stock</option>
              <option value="OUT_OF_STOCK">Out of Stock</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Criticality</label>
            <select
              value={filterCriticality}
              onChange={(e) => setFilterCriticality(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Levels</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Parts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Part ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Part Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Equipment Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Criticality
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lead Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Unit Cost
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Supplier
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                  Loading spare parts...
                </td>
              </tr>
            ) : parts.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                  No spare parts found
                </td>
              </tr>
            ) : (
              parts.map((part) => (
                <tr key={part.part_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {part.part_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {part.part_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {part.equipment_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <span className={part.quantity_available < part.minimum_stock ? 'text-red-600 font-semibold' : ''}>
                        {part.quantity_available}
                      </span>
                      <span className="text-gray-400 ml-1">/ {part.minimum_stock} min</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(
                        part.status
                      )}`}
                    >
                      {part.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getCriticalityBadgeClass(
                        part.criticality
                      )}`}
                    >
                      {part.criticality}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {part.lead_time_days} days
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${part.unit_cost.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {part.supplier}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Procurement Alerts */}
      {parts.filter((p) => p.status === 'OUT_OF_STOCK' || (p.status === 'LOW_STOCK' && p.criticality === 'CRITICAL'))
        .length > 0 && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-red-900 mb-2">⚠️ Procurement Alerts</h3>
          <div className="space-y-2">
            {parts
              .filter(
                (p) =>
                  p.status === 'OUT_OF_STOCK' || (p.status === 'LOW_STOCK' && p.criticality === 'CRITICAL')
              )
              .map((part) => (
                <div key={part.part_id} className="text-sm text-red-800">
                  <span className="font-semibold">{part.part_id}</span>: {part.part_name} -{' '}
                  {part.status === 'OUT_OF_STOCK' ? (
                    <span className="font-semibold">OUT OF STOCK</span>
                  ) : (
                    <span>LOW STOCK ({part.quantity_available} units)</span>
                  )}{' '}
                  - Lead time: {part.lead_time_days} days
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SparePartsInventory;
