import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { opportunitiesAPI, profilesAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiBriefcase, FiUpload, FiSearch, FiTrendingUp } from 'react-icons/fi';

const Dashboard = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState({ total: 0, toApply: 0, applied: 0, interview: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [oppsRes, profileRes] = await Promise.all([
        opportunitiesAPI.list(),
        profilesAPI.getLatest().catch(() => null),
      ]);

      setOpportunities(oppsRes.data);
      setProfile(profileRes?.data);

      // Calculate stats
      const total = oppsRes.data.length;
      const toApply = oppsRes.data.filter(o => o.status === 'TO_APPLY').length;
      const applied = oppsRes.data.filter(o => o.status === 'APPLIED').length;
      const interview = oppsRes.data.filter(o => o.status === 'INTERVIEW').length;
      
      setStats({ total, toApply, applied, interview });
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">Welcome back! Here's your application overview.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Opportunities</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
            </div>
            <FiBriefcase className="h-12 w-12 text-primary-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">To Apply</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.toApply}</p>
            </div>
            <FiUpload className="h-12 w-12 text-yellow-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Applied</p>
              <p className="text-3xl font-bold text-blue-600">{stats.applied}</p>
            </div>
            <FiSearch className="h-12 w-12 text-blue-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Interviews</p>
              <p className="text-3xl font-bold text-green-600">{stats.interview}</p>
            </div>
            <FiTrendingUp className="h-12 w-12 text-green-600" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/upload" className="btn btn-primary">
            <FiUpload className="inline mr-2" />
            Upload Resume
          </Link>
          <Link to="/analyze" className="btn btn-primary">
            <FiSearch className="inline mr-2" />
            Analyze Opportunity
          </Link>
          <Link to="/opportunities" className="btn btn-secondary">
            <FiBriefcase className="inline mr-2" />
            View All Opportunities
          </Link>
        </div>
      </div>

      {/* Profile Status */}
      {!profile && (
        <div className="card bg-yellow-50 dark:bg-yellow-900 border-l-4 border-yellow-400">
          <p className="text-yellow-800 dark:text-yellow-200">
            <strong>Action Required:</strong> Please upload your resume to create a profile before analyzing opportunities.
            <Link to="/upload" className="ml-2 underline">Upload now</Link>
          </p>
        </div>
      )}

      {/* Recent Opportunities */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Opportunities</h2>
          <Link to="/opportunities" className="text-primary-600 hover:text-primary-700">View all →</Link>
        </div>
        
        {opportunities.length === 0 ? (
          <p className="text-gray-600 dark:text-gray-400">No opportunities yet. Start by analyzing some!</p>
        ) : (
          <div className="space-y-4">
            {opportunities.slice(0, 5).map((opp) => (
              <Link
                key={opp.id}
                to={`/opportunities/${opp.id}`}
                className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-primary-500 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white">{opp.title}</h3>
                    {opp.organization && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">{opp.organization}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-4">
                    {opp.fit_score !== null && (
                      <div className="text-right">
                        <p className="text-2xl font-bold text-primary-600">{opp.fit_score}</p>
                        <p className="text-xs text-gray-500">fit score</p>
                      </div>
                    )}
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
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
    </div>
  );
};

export default Dashboard;
