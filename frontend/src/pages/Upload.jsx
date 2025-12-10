import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentsAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiUpload, FiFile, FiCheckCircle } from 'react-icons/fi';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState('resume');
  const [uploading, setUploading] = useState(false);
  const [documentId, setDocumentId] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast.error('File too large. Maximum size is 10MB');
        return;
      }
      if (!selectedFile.name.match(/\.(pdf|docx|doc)$/i)) {
        toast.error('Invalid file type. Please upload PDF or DOCX');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const response = await documentsAPI.upload(file, docType);
      setDocumentId(response.data.id);
      toast.success('Document uploaded successfully!');
      
      // Redirect to dashboard after a moment
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);

    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Upload Documents</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Upload your resume, research papers, or other relevant documents. We'll extract the text and help you build a comprehensive profile.
        </p>
      </div>

      <div className="card">
        <div className="space-y-6">
          <div className="form-group">
            <label htmlFor="docType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Document Type
            </label>
            <select
              id="docType"
              name="docType"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
            >
              <option value="resume">Resume / CV</option>
              <option value="research_paper">Research Paper</option>
              <option value="project_information">Project Information</option>
              <option value="cover_letter">Cover Letter</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          {!file ? (
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-12">
              <div className="text-center">
                <FiUpload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <span className="btn btn-primary">
                      Choose file
                    </span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".pdf,.docx,.doc"
                      onChange={handleFileChange}
                    />
                  </label>
                </div>
                <p className="mt-2 text-sm text-gray-500">PDF or DOCX up to 10MB</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <FiFile className="h-8 w-8 text-primary-600" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900 dark:text-white">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                {!uploading && !documentId && (
                  <button
                    onClick={() => setFile(null)}
                    className="text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                )}
              </div>

              {documentId ? (
                <div className="flex items-center space-x-2 text-green-600">
                  <FiCheckCircle className="h-5 w-5" />
                  <span>
                    Upload complete! Redirecting...
                  </span>
                </div>
              ) : (
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="btn btn-primary w-full"
                >
                  {uploading ? 'Uploading...' : 'Upload Document'}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="card bg-blue-50 dark:bg-blue-900">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
          What happens next?
        </h3>
        <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
          <li>• Your document will be uploaded securely.</li>
          <li>• We'll extract the text from your document.</li>
          <li>• If you upload a resume, a profile will be automatically created or updated.</li>
          <li>• You can then analyze opportunities and generate materials.</li>
        </ul>
      </div>
    </div>
  );
};

export default Upload;
