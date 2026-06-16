import { useEffect, useState } from 'react';
import { Package, AlertTriangle, TrendingUp, DollarSign, Clock, RefreshCw } from 'lucide-react';
import { sparePartsAPI } from '../api/client';

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
      const params: any = {};
      if (filterEquipment) params.equipment_type = filterEquipment;
      if (filterStatus) params.status = filterStatus;
      if (filterCriticality) params.criticality = filterCriticality;

      const response = await sparePartsAPI.list(params);
      setParts(response.data.parts);
      setStatistics(response.data.statistics);
    } catch (error) {
      console.error('Failed to fetch spare parts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'IN_STOCK': return '#22c55e';
      case 'LOW_STOCK': return '#eab308';
      case 'OUT_OF_STOCK': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#3b82f6';
      case 'LOW': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const equipmentTypes = ['Air Compressor', 'Cooling Fan System', 'Rolling Mill', 'Conveyor Motor'];

  const urgentParts = parts.filter(
    (p) => p.status === 'OUT_OF_STOCK' || (p.status === 'LOW_STOCK' && p.criticality === 'CRITICAL')
  );

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xs font-mono tracking-widest mb-1" style={{ color: 'var(--accent-cyan)' }}>
            📦 SPARE PARTS INVENTORY
          </h2>
          <p className="text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
            Real-time parts tracking & procurement management
          </p>
        </div>
        <button
          onClick={fetchSpareparts}
          disabled={loading}
          className="p-1.5 rounded-sm transition-all"
          style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            color: 'var(--accent-cyan)'
          }}
        >
          <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-5 gap-3 mb-4">
          <div 
            className="rounded-sm p-3 border"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <Package className="w-3.5 h-3.5" style={{ color: 'var(--text-tertiary)' }} />
            </div>
            <div className="text-2xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>TOTAL</div>
            <div className="text-2xl font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
              {statistics.total_parts}
            </div>
          </div>

          <div 
            className="rounded-sm p-3 border"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-3.5 h-3.5" style={{ color: '#ef4444' }} />
            </div>
            <div className="text-2xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>OUT OF STOCK</div>
            <div className="text-2xl font-bold font-mono" style={{ color: '#ef4444' }}>
              {statistics.out_of_stock}
            </div>
          </div>

          <div 
            className="rounded-sm p-3 border"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-3.5 h-3.5" style={{ color: '#eab308' }} />
            </div>
            <div className="text-2xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>LOW STOCK</div>
            <div className="text-2xl font-bold font-mono" style={{ color: '#eab308' }}>
              {statistics.low_stock}
            </div>
          </div>

          <div 
            className="rounded-sm p-3 border"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-3.5 h-3.5" style={{ color: '#f97316' }} />
            </div>
            <div className="text-2xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>CRITICAL</div>
            <div className="text-2xl font-bold font-mono" style={{ color: '#f97316' }}>
              {statistics.critical_parts}
            </div>
          </div>

          <div 
            className="rounded-sm p-3 border"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-3.5 h-3.5" style={{ color: '#22c55e' }} />
            </div>
            <div className="text-2xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>VALUE</div>
            <div className="text-xl font-bold font-mono" style={{ color: '#22c55e' }}>
              ${Math.floor(statistics.total_inventory_value / 1000)}K
            </div>
          </div>
        </div>
      )}

      {/* Urgent Procurement Alerts */}
      {urgentParts.length > 0 && (
        <div 
          className="mb-4 rounded-sm p-3 border"
          style={{
            backgroundColor: '#7f1d1d20',
            borderColor: '#ef4444'
          }}
        >
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-4 h-4" style={{ color: '#ef4444' }} />
            <div className="text-xs font-mono uppercase" style={{ color: '#ef4444' }}>
              URGENT PROCUREMENT REQUIRED
            </div>
          </div>
          <div className="space-y-1">
            {urgentParts.slice(0, 3).map((part) => (
              <div key={part.part_id} className="text-xs font-mono flex items-center justify-between" style={{ color: 'var(--text-secondary)' }}>
                <span>
                  <span style={{ color: 'var(--text-primary)' }}>{part.part_id}</span> - {part.part_name}
                </span>
                <span className="text-2xs" style={{ color: 'var(--text-tertiary)' }}>
                  Lead: {part.lead_time_days}d
                </span>
              </div>
            ))}
            {urgentParts.length > 3 && (
              <div className="text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                +{urgentParts.length - 3} more requiring attention
              </div>
            )}
          </div>
        </div>
      )}

      {/* Filters */}
      <div 
        className="rounded-sm p-3 border mb-4"
        style={{
          backgroundColor: 'var(--bg-surface)',
          borderColor: 'var(--border-default)'
        }}
      >
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-2xs font-mono uppercase mb-1" style={{ color: 'var(--text-tertiary)' }}>
              Equipment Type
            </label>
            <select
              value={filterEquipment}
              onChange={(e) => setFilterEquipment(e.target.value)}
              className="w-full px-2 py-1.5 text-xs font-mono rounded-sm"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                color: 'var(--text-primary)'
              }}
            >
              <option value="">All Equipment</option>
              {equipmentTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-2xs font-mono uppercase mb-1" style={{ color: 'var(--text-tertiary)' }}>
              Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-2 py-1.5 text-xs font-mono rounded-sm"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                color: 'var(--text-primary)'
              }}
            >
              <option value="">All Status</option>
              <option value="IN_STOCK">In Stock</option>
              <option value="LOW_STOCK">Low Stock</option>
              <option value="OUT_OF_STOCK">Out of Stock</option>
            </select>
          </div>
          <div>
            <label className="block text-2xs font-mono uppercase mb-1" style={{ color: 'var(--text-tertiary)' }}>
              Criticality
            </label>
            <select
              value={filterCriticality}
              onChange={(e) => setFilterCriticality(e.target.value)}
              className="w-full px-2 py-1.5 text-xs font-mono rounded-sm"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                color: 'var(--text-primary)'
              }}
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
      <div className="flex-1 overflow-hidden">
        <div 
          className="rounded-sm overflow-hidden h-full"
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-default)'
          }}
        >
          {/* Table Header */}
          <div 
            className="grid grid-cols-12 gap-2 px-4 py-2 border-b text-2xs font-mono uppercase sticky top-0"
            style={{
              backgroundColor: 'var(--bg-elevated)',
              borderColor: 'var(--border-default)',
              color: 'var(--text-tertiary)'
            }}
          >
            <div className="col-span-1">PART ID</div>
            <div className="col-span-2">PART NAME</div>
            <div className="col-span-2">EQUIPMENT TYPE</div>
            <div className="col-span-1">QUANTITY</div>
            <div className="col-span-1">STATUS</div>
            <div className="col-span-1">CRITICALITY</div>
            <div className="col-span-1">LEAD TIME</div>
            <div className="col-span-1">UNIT COST</div>
            <div className="col-span-2">SUPPLIER</div>
          </div>

          {/* Table Body */}
          <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 420px)' }}>
            {loading ? (
              <div className="text-center py-12">
                <p className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>Loading spare parts...</p>
              </div>
            ) : parts.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-12 h-12 mx-auto mb-3 opacity-30" style={{ color: 'var(--text-tertiary)' }} />
                <p className="text-sm font-mono" style={{ color: 'var(--text-secondary)' }}>No spare parts found</p>
                <p className="text-xs font-sans mt-1" style={{ color: 'var(--text-tertiary)' }}>Try adjusting your filters</p>
              </div>
            ) : (
              parts.map((part, index) => (
                <div
                  key={part.part_id}
                  className="grid grid-cols-12 gap-2 px-4 py-3 border-b hover:bg-opacity-50 transition-all"
                  style={{
                    borderColor: 'var(--border-subtle)',
                    backgroundColor: index % 2 === 0 ? 'transparent' : 'var(--bg-base)'
                  }}
                >
                  <div className="col-span-1 text-xs font-mono" style={{ color: 'var(--text-primary)' }}>
                    {part.part_id}
                  </div>
                  <div className="col-span-2 text-sm font-sans" style={{ color: 'var(--text-primary)' }}>
                    {part.part_name}
                  </div>
                  <div className="col-span-2 text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
                    {part.equipment_type}
                  </div>
                  <div className="col-span-1 text-xs font-mono">
                    <span style={{ color: part.quantity_available < part.minimum_stock ? '#ef4444' : 'var(--text-primary)' }}>
                      {part.quantity_available}
                    </span>
                    <span style={{ color: 'var(--text-tertiary)' }}> / {part.minimum_stock}</span>
                  </div>
                  <div className="col-span-1">
                    <span
                      className="px-2 py-0.5 rounded-sm text-2xs font-mono inline-block"
                      style={{
                        backgroundColor: `${getStatusColor(part.status)}20`,
                        color: getStatusColor(part.status)
                      }}
                    >
                      {part.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="col-span-1">
                    <span
                      className="px-2 py-0.5 rounded-sm text-2xs font-mono inline-block"
                      style={{
                        backgroundColor: `${getCriticalityColor(part.criticality)}20`,
                        color: getCriticalityColor(part.criticality)
                      }}
                    >
                      {part.criticality}
                    </span>
                  </div>
                  <div className="col-span-1 text-xs font-mono flex items-center" style={{ color: 'var(--text-secondary)' }}>
                    <Clock className="w-3 h-3 mr-1" style={{ color: 'var(--text-tertiary)' }} />
                    {part.lead_time_days}d
                  </div>
                  <div className="col-span-1 text-xs font-mono" style={{ color: 'var(--text-primary)' }}>
                    ${part.unit_cost.toFixed(2)}
                  </div>
                  <div className="col-span-2 text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                    {part.supplier}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SparePartsInventory;
