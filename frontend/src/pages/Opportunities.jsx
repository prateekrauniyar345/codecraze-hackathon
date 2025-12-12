import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { opportunitiesAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiBriefcase, FiFilter } from 'react-icons/fi';

const Opportunities = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState(null);
  const [typeFilter, setTypeFilter] = useState('FULL_TIME');

  useEffect(() => {
    fetchOpportunities();
  }, [statusFilter, typeFilter]);

  const fetchOpportunities = async () => {
    try {
      const response = await opportunitiesAPI.list(statusFilter, typeFilter);
      setOpportunities(response.data);
    } catch (error) {
      toast.error('Failed to load opportunities');
    } finally {
      setLoading(false);
    }
  };

  const opportunityTypes = [
    { value: 'FULL_TIME', label: 'Full Time Jobs' },
    { value: 'INTERNSHIP', label: 'Internships' },
    { value: 'RESEARCH', label: 'Research Opportunities' },
  ];


  const statuses = [
    { value: null, label: 'All' },
    { value: 'TO_APPLY', label: 'To Apply' },
    { value: 'APPLIED', label: 'Applied' },
    { value: 'INTERVIEW', label: 'Interview' },
    { value: 'OFFER', label: 'Offer' },
    { value: 'REJECTED', label: 'Rejected' },
  ];

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Opportunities</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Track and manage your applications</p>
        </div>
        <Link to="/analyze" className="btn btn-primary">
          + Add New Opportunity
        </Link>
      </div>

      <div className="mb-4 border-b border-gray-200 dark:border-gray-700">
        <ul className="flex flex-wrap -mb-px text-sm font-medium text-center" id="myTab" data-tabs-toggle="#myTabContent" role="tablist">
            {opportunityTypes.map((tab) => (
                <li className="mr-2" role="presentation" key={tab.value}>
                    <button
                        className={`inline-block p-4 border-b-2 rounded-t-lg ${
                            typeFilter === tab.value
                                ? 'border-primary-600 text-primary-600'
                                : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
                        }`}
                        onClick={() => setTypeFilter(tab.value)}
                        type="button"
                        role="tab"
                        aria-selected={typeFilter === tab.value}
                    >
                        {tab.label}
                    </button>
                </li>
            ))}
        </ul>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center space-x-2 flex-wrap">
          <FiFilter className="h-5 w-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter:</span>
          {statuses.map((status) => (
            <button
              key={status.value || 'all'}
              onClick={() => setStatusFilter(status.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300'
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>
      </div>

      {/* Opportunities List */}
      {opportunities.length === 0 ? (
        <div className="card text-center py-12">
          <FiBriefcase className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {statusFilter ? `No ${statusFilter.toLowerCase().replace('_', ' ')} opportunities` : 'No opportunities yet'}
          </p>
          <Link to="/analyze" className="btn btn-primary">
            Analyze Your First Opportunity
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <Link
              key={opp.id}
              to={`/opportunities/${opp.id}`}
              className="card hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1 mr-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {opp.title}
                  </h3>
                  {opp.organization && (
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{opp.organization}</p>
                  )}
                  <p className="text-sm text-gray-500 dark:text-gray-500 line-clamp-2">
                    {opp.description}
                  </p>
                  {opp.deadline && (
                    <p className="text-sm text-gray-500 mt-2">
                      Deadline: {new Date(opp.deadline).toLocaleDateString()}
                    </p>
                  )}
                </div>
                
                <div className="flex flex-col items-end space-y-2">
                  {opp.fit_score !== null && (
                    <div className="text-right">
                      <p className="text-3xl font-bold text-primary-600">{opp.fit_score}</p>
                      <p className="text-xs text-gray-500">fit score</p>
                    </div>
                  )}
                  <span className={`px-4 py-2 rounded-full text-xs font-medium whitespace-nowrap ${
                    opp.status === 'TO_APPLY' ? 'bg-yellow-100 text-yellow-800' :
                    opp.status === 'APPLIED' ? 'bg-blue-100 text-blue-800' :
                    opp.status === 'INTERVIEW' ? 'bg-green-100 text-green-800' :
                    opp.status === 'OFFER' ? 'bg-purple-100 text-purple-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {opp.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Opportunities;
