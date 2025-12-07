import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { opportunitiesAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiSearch, FiAlertCircle } from 'react-icons/fi';

const AnalyzeOpportunity = () => {
  const [opportunityText, setOpportunityText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!opportunityText.trim()) {
      toast.error('Please paste opportunity text');
      return;
    }

    setAnalyzing(true);
    try {
      const response = await opportunitiesAPI.analyze({ opportunity_text: opportunityText });
      setResult(response.data);
      toast.success('Analysis complete!');
    } catch (error) {
      if (error.response?.status === 404 && error.response?.data?.detail?.includes('profile')) {
        toast.error('Please upload your resume first');
        setTimeout(() => navigate('/upload'), 2000);
      } else {
        toast.error(error.response?.data?.detail || 'Analysis failed');
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSaveOpportunity = async () => {
    const title = prompt('Enter opportunity title:');
    if (!title) return;

    try {
      const createResponse = await opportunitiesAPI.create({
        title,
        description: opportunityText,
        organization: prompt('Organization (optional):') || null,
        url: prompt('URL (optional):') || null,
      });

      const oppId = createResponse.data.id;
      
      // Analyze the saved opportunity
      await opportunitiesAPI.analyzeExisting(oppId);
      
      toast.success('Opportunity saved and analyzed!');
      navigate(`/opportunities/${oppId}`);
    } catch (error) {
      toast.error('Failed to save opportunity');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analyze Opportunity</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Paste a job posting, internship, or scholarship description to see how well you fit.
        </p>
      </div>

      <div className="card">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Opportunity Description
            </label>
            <textarea
              value={opportunityText}
              onChange={(e) => setOpportunityText(e.target.value)}
              placeholder="Paste the full job posting or opportunity description here..."
              rows={12}
              className="input"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={analyzing || !opportunityText.trim()}
            className="btn btn-primary w-full"
          >
            {analyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white inline-block mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <FiSearch className="inline mr-2" />
                Analyze Fit
              </>
            )}
          </button>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Fit Score */}
          <div className="card bg-gradient-to-r from-primary-500 to-primary-600 text-white">
            <div className="text-center">
              <p className="text-lg font-medium mb-2">Your Fit Score</p>
              <p className="text-6xl font-bold">{result.fit_score}</p>
              <p className="text-sm mt-2 opacity-90">out of 100</p>
            </div>
          </div>

          {/* Analysis Details */}
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Analysis</h3>
            
            {result.fit_analysis.strengths && result.fit_analysis.strengths.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-green-700 dark:text-green-400 mb-2">✓ Strengths</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  {result.fit_analysis.strengths.map((strength, idx) => (
                    <li key={idx}>{strength}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.fit_analysis.gaps && result.fit_analysis.gaps.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-yellow-700 dark:text-yellow-400 mb-2">! Gaps</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  {result.fit_analysis.gaps.map((gap, idx) => (
                    <li key={idx}>{gap}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.fit_analysis.recommendations && result.fit_analysis.recommendations.length > 0 && (
              <div>
                <h4 className="font-medium text-blue-700 dark:text-blue-400 mb-2">💡 Recommendations</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  {result.fit_analysis.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Requirements */}
          {result.extracted_requirements && result.extracted_requirements.length > 0 && (
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Requirements</h3>
              <div className="space-y-2">
                {result.extracted_requirements.map((req, idx) => (
                  <div key={idx} className="flex items-start space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                    {req.is_mandatory && <FiAlertCircle className="h-5 w-5 text-red-500 mt-0.5" />}
                    <div className="flex-1">
                      <p className="text-gray-900 dark:text-white">{req.requirement_text}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {req.requirement_type} {req.is_mandatory && '• Required'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="card bg-blue-50 dark:bg-blue-900">
            <p className="text-blue-900 dark:text-blue-100 mb-4">
              Want to track this opportunity and generate application materials?
            </p>
            <button onClick={handleSaveOpportunity} className="btn btn-primary">
              Save Opportunity
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyzeOpportunity;
