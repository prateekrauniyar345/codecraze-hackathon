import { useState } from 'react';
import { jobsAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiExternalLink } from 'react-icons/fi';

const JobSearch = () => {
    const [searchParams, setSearchParams] = useState({
        what: '',
        where: '',
        salary_min: '',
        salary_max: '',
        full_time: false,
        part_time: false,
        contract: false,
        permanent: false,
    });
    const [searchResults, setSearchResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [totalRecords, setTotalRecords] = useState(0);
    const [country, setCountry] = useState('us');

    const handleSearch = async (e, opts = {}) => {
        if (e && e.preventDefault) e.preventDefault();
        const currentPage = opts.page || page;
        const size = opts.pageSize || pageSize;
        setLoading(true);
        try {
            // Build payload - keep it simple, only include non-empty fields
            const payload = {
                country: country,
                page: currentPage,
                results_per_page: size,
            };

            // Only add fields that have values
            if (searchParams.what) payload.what = searchParams.what;
            if (searchParams.where) payload.where = searchParams.where;
            if (searchParams.salary_min) payload.salary_min = parseInt(searchParams.salary_min);
            if (searchParams.salary_max) payload.salary_max = parseInt(searchParams.salary_max);
            if (searchParams.full_time) payload.full_time = true;
            if (searchParams.part_time) payload.part_time = true;
            if (searchParams.contract) payload.contract = true;
            if (searchParams.permanent) payload.permanent = true;

            const response = await jobsAPI.searchJobs(payload);
            const data = response.data || {};
            setSearchResults(data.items || []);
            setTotalRecords(data.total_records || 0);
            setPage(data.page || currentPage);
            setPageSize(data.results_per_page || size);
        } catch (error) {
            toast.error('Failed to search for jobs');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (field, value) => {
        setSearchParams(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const goToPage = (p) => {
        if (p < 1) return;
        const totalPages = Math.ceil(totalRecords / pageSize);
        if (totalPages && p > totalPages) return;
        setPage(p);
        handleSearch(null, { page: p, pageSize });
    };

    const handlePageSizeChange = (e) => {
        const newSize = Number(e.target.value) || 10;
        setPageSize(newSize);
        setPage(1);
        handleSearch(null, { page: 1, pageSize: newSize });
    };

    const formatSalary = (min, max) => {
        if (!min && !max) return 'Salary not specified';
        if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
        if (min) return `$${min.toLocaleString()}+`;
        if (max) return `Up to $${max.toLocaleString()}`;
    };

    return (
        <div className="space-y-6">
            {/* Search Form */}
            <div className="card p-6">
                <h3 className="text-lg font-semibold mb-4">Search Jobs</h3>
                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Job Title / Keywords</label>
                            <input
                                type="text"
                                value={searchParams.what}
                                onChange={(e) => handleInputChange('what', e.target.value)}
                                placeholder="e.g., software engineer"
                                className="input w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Location</label>
                            <input
                                type="text"
                                value={searchParams.where}
                                onChange={(e) => handleInputChange('where', e.target.value)}
                                placeholder="e.g., San Francisco, CA"
                                className="input w-full"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Min Salary</label>
                            <input
                                type="number"
                                value={searchParams.salary_min}
                                onChange={(e) => handleInputChange('salary_min', e.target.value)}
                                placeholder="e.g., 80000"
                                className="input w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Max Salary</label>
                            <input
                                type="number"
                                value={searchParams.salary_max}
                                onChange={(e) => handleInputChange('salary_max', e.target.value)}
                                placeholder="e.g., 150000"
                                className="input w-full"
                            />
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                checked={searchParams.full_time}
                                onChange={(e) => handleInputChange('full_time', e.target.checked)}
                                className="checkbox"
                            />
                            <span>Full Time</span>
                        </label>
                        <label className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                checked={searchParams.part_time}
                                onChange={(e) => handleInputChange('part_time', e.target.checked)}
                                className="checkbox"
                            />
                            <span>Part Time</span>
                        </label>
                        <label className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                checked={searchParams.contract}
                                onChange={(e) => handleInputChange('contract', e.target.checked)}
                                className="checkbox"
                            />
                            <span>Contract</span>
                        </label>
                        <label className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                checked={searchParams.permanent}
                                onChange={(e) => handleInputChange('permanent', e.target.checked)}
                                className="checkbox"
                            />
                            <span>Permanent</span>
                        </label>
                    </div>

                    <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2">
                            <span className="text-sm font-medium">Country:</span>
                            <select
                                value={country}
                                onChange={(e) => setCountry(e.target.value)}
                                className="select select-bordered"
                            >
                                <option value="us">United States</option>
                                <option value="gb">United Kingdom</option>
                                <option value="au">Australia</option>
                                <option value="ca">Canada</option>
                            </select>
                        </label>
                        <button type="submit" className="btn btn-primary">Search</button>
                    </div>
                </form>
            </div>

            {/* Results */}
            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
            ) : (
                <div className="space-y-4">
                    {searchResults.length > 0 && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Found {totalRecords} jobs
                        </p>
                    )}
                    {searchResults.map((job) => (
                        <div key={job.id} className="card hover:shadow-lg transition-shadow p-6">
                            <div className="flex justify-between items-start mb-3">
                                <div className="flex-1">
                                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                                        {job.title}
                                    </h3>
                                    {job.company && (
                                        <p className="text-lg text-gray-700 dark:text-gray-300 mb-1">
                                            {job.company}
                                        </p>
                                    )}
                                    <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                                        {job.location && <span>📍 {job.location}</span>}
                                        {job.category && <span>🏷️ {job.category}</span>}
                                    </div>
                                </div>
                                {job.redirect_url && (
                                    <a
                                        href={job.redirect_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn-sm btn-primary"
                                    >
                                        <FiExternalLink className="mr-1" />
                                        View Job
                                    </a>
                                )}
                            </div>
                            
                            {job.description && (
                                <p className="text-gray-700 dark:text-gray-300 mb-3 line-clamp-3">
                                    {job.description}
                                </p>
                            )}

                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4 text-sm">
                                    {(job.salary_min || job.salary_max) && (
                                        <span className="font-medium text-primary-600">
                                            💰 {formatSalary(job.salary_min, job.salary_max)}
                                        </span>
                                    )}
                                    {job.contract_time && (
                                        <span className="text-gray-600 dark:text-gray-400">
                                            {job.contract_time.replace('_', ' ')}
                                        </span>
                                    )}
                                    {job.contract_type && (
                                        <span className="text-gray-600 dark:text-gray-400">
                                            {job.contract_type}
                                        </span>
                                    )}
                                    {job.created && (
                                        <span className="text-gray-500">
                                            Posted: {new Date(job.created).toLocaleDateString()}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {searchResults.length === 0 && !loading && (
                        <div className="card text-center py-12">
                            <p className="text-gray-600 dark:text-gray-400">
                                No jobs found. Try adjusting your search criteria.
                            </p>
                        </div>
                    )}

                    {/* Pagination */}
                    {searchResults.length > 0 && (
                        <div className="flex items-center justify-between mt-6">
                            <div className="flex items-center space-x-2">
                                <button
                                    className="btn"
                                    onClick={() => goToPage(page - 1)}
                                    disabled={page <= 1}
                                >
                                    Prev
                                </button>
                                <span>
                                    Page {page} of {Math.ceil(totalRecords / pageSize) || 1}
                                </span>
                                <button
                                    className="btn"
                                    onClick={() => goToPage(page + 1)}
                                    disabled={page >= Math.ceil(totalRecords / pageSize)}
                                >
                                    Next
                                </button>
                            </div>
                            <div className="flex items-center space-x-2">
                                <label className="text-sm">Page size</label>
                                <select
                                    value={pageSize}
                                    onChange={handlePageSizeChange}
                                    className="select select-bordered"
                                >
                                    <option value={10}>10</option>
                                    <option value={20}>20</option>
                                    <option value={50}>50</option>
                                </select>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default JobSearch;



