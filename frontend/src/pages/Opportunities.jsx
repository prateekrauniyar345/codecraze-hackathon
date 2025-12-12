import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { opportunitiesAPI, grantsAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiBriefcase } from 'react-icons/fi';
import GrantSearch from '../components/GrantSearch';

const Opportunities = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('FULL_TIME');
  const [researchTab, setResearchTab] = useState('suggestions'); // 'suggestions' or 'search'
  const [grantSuggestions, setGrantSuggestions] = useState([]);
  const [grantLoading, setGrantLoading] = useState(false);
  const [suggestionsPage, setSuggestionsPage] = useState(1);
  const [suggestionsPageSize, setSuggestionsPageSize] = useState(10);
  const [suggestionsTotalPages, setSuggestionsTotalPages] = useState(0);
  const [suggestionsFetched, setSuggestionsFetched] = useState(false);

  useEffect(() => {
    if (typeFilter !== 'RESEARCH') {
      fetchOpportunities();
    }
  }, [typeFilter]);

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const response = await opportunitiesAPI.list(null, typeFilter);
      setOpportunities(response.data);
    } catch (error) {
      toast.error('Failed to load opportunities');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchSuggestions = async () => {
    setGrantLoading(true);
    try {
      const response = await grantsAPI.getGrantSuggestions();
      const items = response.data?.items || [];
      setGrantSuggestions(items);
      setSuggestionsFetched(true);
      setSuggestionsPage(1);
      setSuggestionsPageSize(10);
      setSuggestionsTotalPages(items.length ? Math.ceil(items.length / 10) : 0);
    } catch (error) {
      toast.error('Failed to fetch grant suggestions');
    } finally {
      setGrantLoading(false);
    }
  };


  const opportunityTypes = [
    { value: 'FULL_TIME', label: 'Full Time Jobs' },
    { value: 'INTERNSHIP', label: 'Internships' },
    { value: 'RESEARCH', label: 'Research Opportunities' },
  ];

  if (loading && typeFilter !== 'RESEARCH') {
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

      {typeFilter === 'RESEARCH' ? (
        <div>
          <div className="mb-4 border-b border-gray-200 dark:border-gray-700">
            <ul className="flex flex-wrap -mb-px text-sm font-medium text-center" role="tablist">
              <li className="mr-2" role="presentation">
                <button
                  className={`inline-block p-4 border-b-2 rounded-t-lg ${researchTab === 'suggestions' ? 'border-primary-600 text-primary-600' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'}`}
                  onClick={() => setResearchTab('suggestions')}
                  type="button"
                  role="tab"
                  aria-selected={researchTab === 'suggestions'}
                >
                  Get Suggestions
                </button>
              </li>
              <li className="mr-2" role="presentation">
                <button
                  className={`inline-block p-4 border-b-2 rounded-t-lg ${researchTab === 'search' ? 'border-primary-600 text-primary-600' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'}`}
                  onClick={() => setResearchTab('search')}
                  type="button"
                  role="tab"
                  aria-selected={researchTab === 'search'}
                >
                  Search Opportunities
                </button>
              </li>
            </ul>
          </div>
          {grantLoading ? (
            <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>
          ) : (
            <div>
              {researchTab === 'suggestions' && (
                <div>
                  {!suggestionsFetched ? (
                    <div className="py-6">
                      <button className="btn btn-primary" onClick={handleFetchSuggestions}>Get suggestions based on profile</button>
                    </div>
                  ) : (
                    <div>
                      <div className="space-y-4">
                        {grantSuggestions.slice((suggestionsPage - 1) * suggestionsPageSize, suggestionsPage * suggestionsPageSize).map((grant) => (
                          <div key={grant.opportunity_id} className="card hover:shadow-lg transition-shadow">
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{grant.title}</h3>
                            <p className="text-gray-600 dark:text-gray-400 mb-2">{grant.agency_name}</p>
                            <p className="text-sm text-gray-500">Posted: {grant.post_date}</p>
                          </div>
                        ))}
                      </div>

                      {/* Pagination for suggestions */}
                      <div className="flex items-center justify-between mt-4">
                        <div className="flex items-center space-x-2">
                          <button className="btn" onClick={() => setSuggestionsPage(p => Math.max(1, p - 1))} disabled={suggestionsPage <= 1}>Prev</button>
                          <span>Page {suggestionsPage} of {suggestionsTotalPages || 1}</span>
                          <button className="btn" onClick={() => setSuggestionsPage(p => (suggestionsTotalPages ? Math.min(suggestionsTotalPages, p + 1) : p + 1))} disabled={suggestionsTotalPages && suggestionsPage >= suggestionsTotalPages}>Next</button>
                        </div>
                        <div className="flex items-center space-x-2">
                          <label className="text-sm">Page size</label>
                          <select value={suggestionsPageSize} onChange={(e) => { const s = Number(e.target.value); setSuggestionsPageSize(s); setSuggestionsPage(1); setSuggestionsTotalPages(grantSuggestions.length ? Math.ceil(grantSuggestions.length / s) : 0); }} className="select select-bordered">
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                            <option value={50}>50</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
              <div style={{ display: researchTab === 'search' ? 'block' : 'none' }}>
                <GrantSearch />
              </div>
            </div>
          )}
        </div>
      ) : (
      <>
        {opportunities.length === 0 ? (
          <div className="card text-center py-12">
            <FiBriefcase className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No opportunities yet
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
      </>
      )}
    </div>
  );
};

export default Opportunities;
