import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { opportunitiesAPI, materialsAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiEdit2, FiTrash2, FiExternalLink, FiFileText } from 'react-icons/fi';

const OpportunityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [oppRes, matsRes] = await Promise.all([
        opportunitiesAPI.get(id),
        materialsAPI.getForOpportunity(id),
      ]);
      setOpportunity(oppRes.data);
      setMaterials(matsRes.data);
    } catch (error) {
      toast.error('Failed to load opportunity');
      navigate('/opportunities');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    setUpdating(true);
    try {
      await opportunitiesAPI.update(id, { status: newStatus });
      setOpportunity({ ...opportunity, status: newStatus });
      toast.success('Status updated');
    } catch (error) {
      toast.error('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this opportunity?')) return;
    
    try {
      await opportunitiesAPI.delete(id);
      toast.success('Opportunity deleted');
      navigate('/opportunities');
    } catch (error) {
      toast.error('Failed to delete');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{opportunity.title}</h1>
          {opportunity.organization && (
            <p className="mt-2 text-xl text-gray-600 dark:text-gray-400">{opportunity.organization}</p>
          )}
        </div>
        <div className="flex space-x-2">
          <Link to={`/generate/${id}`} className="btn btn-primary">
            <FiFileText className="inline mr-2" />
            Generate Materials
          </Link>
          <button onClick={handleDelete} className="btn bg-red-600 text-white hover:bg-red-700">
            <FiTrash2 className="inline mr-2" />
            Delete
          </button>
        </div>
      </div>

      {/* Fit Score & Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {opportunity.fit_score !== null && (
          <div className="card bg-gradient-to-r from-primary-500 to-primary-600 text-white">
            <p className="text-lg font-medium mb-2">Fit Score</p>
            <p className="text-5xl font-bold">{opportunity.fit_score}/100</p>
          </div>
        )}
        
        <div className="card">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Status</p>
          <select
            value={opportunity.status}
            onChange={(e) => handleStatusUpdate(e.target.value)}
            disabled={updating}
            className="input"
          >
            <option value="TO_APPLY">To Apply</option>
            <option value="APPLIED">Applied</option>
            <option value="INTERVIEW">Interview</option>
            <option value="OFFER">Offer</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {/* Details */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Details</h2>
        <dl className="space-y-3">
          {opportunity.url && (
            <div>
              <dt className="text-sm font-medium text-gray-500">URL</dt>
              <dd>
                <a href={opportunity.url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline flex items-center">
                  {opportunity.url}
                  <FiExternalLink className="ml-1 h-4 w-4" />
                </a>
              </dd>
            </div>
          )}
          {opportunity.deadline && (
            <div>
              <dt className="text-sm font-medium text-gray-500">Deadline</dt>
              <dd className="text-gray-900 dark:text-white">{new Date(opportunity.deadline).toLocaleDateString()}</dd>
            </div>
          )}
          <div>
            <dt className="text-sm font-medium text-gray-500 mb-2">Description</dt>
            <dd className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{opportunity.description}</dd>
          </div>
        </dl>
      </div>

      {/* Fit Analysis */}
      {opportunity.fit_analysis && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Fit Analysis</h2>
          
          {opportunity.fit_analysis.strengths && opportunity.fit_analysis.strengths.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-green-700 dark:text-green-400 mb-2">✓ Strengths</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                {opportunity.fit_analysis.strengths.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}

          {opportunity.fit_analysis.gaps && opportunity.fit_analysis.gaps.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-yellow-700 dark:text-yellow-400 mb-2">! Gaps</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                {opportunity.fit_analysis.gaps.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            </div>
          )}

          {opportunity.fit_analysis.recommendations && opportunity.fit_analysis.recommendations.length > 0 && (
            <div>
              <h3 className="font-medium text-blue-700 dark:text-blue-400 mb-2">💡 Recommendations</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                {opportunity.fit_analysis.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Generated Materials */}
      {materials.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Generated Materials</h2>
          <div className="space-y-4">
            {materials.map((material) => (
              <div key={material.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  {material.material_type.replace('_', ' ').toUpperCase()}
                </p>
                <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{material.content}</p>
                <p className="text-xs text-gray-500 mt-2">
                  Generated {new Date(material.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OpportunityDetail;
