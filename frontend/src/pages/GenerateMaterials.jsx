import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { opportunitiesAPI, materialsAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiFileText, FiMail, FiList, FiCheckSquare } from 'react-icons/fi';

const GenerateMaterials = () => {
  const { opportunityId } = useParams();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState(['email', 'subject_line', 'fit_bullets']);
  const [generatedMaterials, setGeneratedMaterials] = useState([]);

  useEffect(() => {
    fetchOpportunity();
  }, [opportunityId]);

  const fetchOpportunity = async () => {
    try {
      const response = await opportunitiesAPI.get(opportunityId);
      setOpportunity(response.data);
    } catch (error) {
      toast.error('Failed to load opportunity');
      navigate('/opportunities');
    } finally {
      setLoading(false);
    }
  };

  const materialTypes = [
    { value: 'email', label: 'Cold Email', icon: FiMail, description: 'Professional email to recruiter' },
    { value: 'subject_line', label: 'Email Subject', icon: FiList, description: 'Attention-grabbing subject line' },
    { value: 'sop_paragraph', label: 'SOP Paragraph', icon: FiFileText, description: 'Statement of purpose paragraph' },
    { value: 'fit_bullets', label: 'Fit Bullets', icon: FiCheckSquare, description: 'Key qualifications bullets' },
  ];

  const toggleType = (type) => {
    if (selectedTypes.includes(type)) {
      setSelectedTypes(selectedTypes.filter(t => t !== type));
    } else {
      setSelectedTypes([...selectedTypes, type]);
    }
  };

  const handleGenerate = async () => {
    if (selectedTypes.length === 0) {
      toast.error('Please select at least one material type');
      return;
    }

    setGenerating(true);
    try {
      const response = await materialsAPI.generate({
        opportunity_id: parseInt(opportunityId),
        material_types: selectedTypes,
      });
      
      setGeneratedMaterials(response.data);
      toast.success('Materials generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleDone = () => {
    navigate(`/opportunities/${opportunityId}`);
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generate Materials</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          For: <span className="font-medium">{opportunity.title}</span>
        </p>
      </div>

      {generatedMaterials.length === 0 ? (
        <>
          {/* Material Type Selection */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Select Materials to Generate
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {materialTypes.map((type) => {
                const Icon = type.icon;
                const isSelected = selectedTypes.includes(type.value);
                
                return (
                  <button
                    key={type.value}
                    onClick={() => toggleType(type.value)}
                    className={`p-4 border-2 rounded-lg text-left transition-colors ${
                      isSelected
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <Icon className={`h-6 w-6 mt-1 ${isSelected ? 'text-primary-600' : 'text-gray-400'}`} />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">{type.label}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{type.description}</p>
                      </div>
                      {isSelected && (
                        <div className="h-6 w-6 bg-primary-600 rounded-full flex items-center justify-center text-white">
                          ✓
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Generate Button */}
          <div className="card bg-blue-50 dark:bg-blue-900">
            <p className="text-blue-900 dark:text-blue-100 mb-4">
              {selectedTypes.length === 0 
                ? 'Select at least one material type to generate.'
                : `Ready to generate ${selectedTypes.length} material${selectedTypes.length > 1 ? 's' : ''}.`
              }
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating || selectedTypes.length === 0}
              className="btn btn-primary w-full"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white inline-block mr-2"></div>
                  Generating...
                </>
              ) : (
                'Generate Materials'
              )}
            </button>
          </div>
        </>
      ) : (
        <>
          {/* Generated Materials Display */}
          <div className="space-y-6">
            {generatedMaterials.map((material) => {
              const materialType = materialTypes.find(t => t.value === material.material_type);
              const Icon = materialType?.icon || FiFileText;
              
              return (
                <div key={material.id} className="card">
                  <div className="flex items-center space-x-2 mb-4">
                    <Icon className="h-6 w-6 text-primary-600" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {materialType?.label || material.material_type}
                    </h3>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                      {material.content}
                    </p>
                  </div>
                  <div className="mt-4 flex justify-end space-x-2">
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(material.content);
                        toast.success('Copied to clipboard!');
                      }}
                      className="btn btn-secondary text-sm"
                    >
                      Copy to Clipboard
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Done Button */}
          <div className="card text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Materials generated successfully! You can copy them or view them later in the opportunity details.
            </p>
            <button onClick={handleDone} className="btn btn-primary">
              View Opportunity Details
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default GenerateMaterials;
