import { useState } from 'react';
import { grantsAPI } from '../api/client';
import { toast } from 'react-toastify';
import MultiSelectChipFilter from './MultiSelectChipFilter';

const GrantSearch = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pageOffset, setPageOffset] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [totalRecords, setTotalRecords] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [filters, setFilters] = useState({
        opportunity_status: { one_of: [] },
        funding_instrument: { one_of: [] },
        applicant_type: { one_of: [] },
        agency: { one_of: [] },
        funding_category: { one_of: [] },
        post_date: { start_date: null, end_date: null },
        close_date: { start_date: null, end_date: null },
        award_floor: { min: null, max: null },
        award_ceiling: { min: null, max: null },
        is_cost_sharing: { one_of: [] },
    });

    const opportunityStatusOptions = [
        { value: 'posted', label: 'Posted' },
        { value: 'forecasted', label: 'Forecasted' },
        { value: 'closed', label: 'Closed' },
        { value: 'archived', label: 'Archived' },
    ];

    const fundingInstrumentOptions = [
        { value: 'grant', label: 'Grant' },
        { value: 'cooperative_agreement', label: 'Cooperative Agreement' },
    ];

    const applicantTypeOptions = [
        { value: 'state_governments', label: 'State Governments' },
        { value: 'county_governments', label: 'County Governments' },
        { value: 'individuals', label: 'Individuals' },
        { value: 'nonprofits', label: 'Nonprofits' },
    ];

    const fundingCategoryOptions = [
        { value: 'recovery_act', label: 'Recovery Act' },
        { value: 'arts', label: 'Arts' },
        { value: 'natural_resources', label: 'Natural Resources' },
        { value: 'education', label: 'Education' },
    ];


    const handleSearch = async (e, opts = {}) => {
        if (e && e.preventDefault) e.preventDefault();
        const page = opts.page || pageOffset;
        const size = opts.pageSize || pageSize;
        setLoading(true);
        try {
            const payload = {
                query: searchQuery,
                filters,
                pagination: { page_offset: page, page_size: size },
            };
            const response = await grantsAPI.searchGrants(payload);
            const data = response.data || {};
            setSearchResults(data.items || []);
                
                
            setPageOffset(data.page_offset || page);
            setPageSize(data.page_size || size);
            setTotalPages(data.page_size ? Math.ceil((data.total_records || 0) / data.page_size) : 0);
        } catch (error) {
            toast.error('Failed to search for grants');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (filterName, value, type = 'one_of') => {
        setFilters(prevFilters => {
            if (type === 'date') {
                return {
                    ...prevFilters,
                    [filterName]: { ...prevFilters[filterName], ...value },
                };
            }
            if (type === 'range') {
                return {
                    ...prevFilters,
                    [filterName]: { ...prevFilters[filterName], ...value },
                };
            }
            return {
                ...prevFilters,
                [filterName]: { one_of: value },
            };
        });
    };

    const toggleCheckbox = (filterName, val) => {
        setFilters(prev => {
            const cur = prev[filterName]?.one_of || [];
            const exists = cur.includes(val);
            const next = exists ? cur.filter(x => x !== val) : [...cur, val];
            // reset to first page when filters change
            setPageOffset(1);
            return { ...prev, [filterName]: { one_of: next } };
        });
    };

    const setDate = (filterName, field, value) => {
        setPageOffset(1);
        setFilters(prev => ({ ...prev, [filterName]: { ...prev[filterName], [field]: value || null } }));
    };

    const setRange = (filterName, field, value) => {
        const num = value === '' || value === null ? null : Number(value);
        setPageOffset(1);
        setFilters(prev => ({ ...prev, [filterName]: { ...prev[filterName], [field]: num } }));
    };

    const goToPage = (p) => {
        if (p < 1) return;
        if (totalPages && p > totalPages) return;
        setPageOffset(p);
        handleSearch(null, { page: p, pageSize });
    };

    const handlePageSizeChange = (e) => {
        const newSize = Number(e.target.value) || 10;
        setPageSize(newSize);
        setPageOffset(1);
        handleSearch(null, { page: 1, pageSize: newSize });
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-1">
                <div className="card p-4">
                    <h3 className="text-lg font-semibold mb-4">Filters</h3>
                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Opportunity Status</h4>
                        {opportunityStatusOptions.map(opt => (
                            <label key={opt.value} className="flex items-center space-x-2 mb-1">
                                <input type="checkbox" checked={(filters.opportunity_status.one_of || []).includes(opt.value)} onChange={() => toggleCheckbox('opportunity_status', opt.value)} />
                                <span>{opt.label}</span>
                            </label>
                        ))}
                    </div>

                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Funding Instrument</h4>
                        {fundingInstrumentOptions.map(opt => (
                            <label key={opt.value} className="flex items-center space-x-2 mb-1">
                                <input type="checkbox" checked={(filters.funding_instrument.one_of || []).includes(opt.value)} onChange={() => toggleCheckbox('funding_instrument', opt.value)} />
                                <span>{opt.label}</span>
                            </label>
                        ))}
                    </div>

                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Applicant Type</h4>
                        {applicantTypeOptions.map(opt => (
                            <label key={opt.value} className="flex items-center space-x-2 mb-1">
                                <input type="checkbox" checked={(filters.applicant_type.one_of || []).includes(opt.value)} onChange={() => toggleCheckbox('applicant_type', opt.value)} />
                                <span>{opt.label}</span>
                            </label>
                        ))}
                    </div>

                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Funding Category</h4>
                        {fundingCategoryOptions.map(opt => (
                            <label key={opt.value} className="flex items-center space-x-2 mb-1">
                                <input type="checkbox" checked={(filters.funding_category.one_of || []).includes(opt.value)} onChange={() => toggleCheckbox('funding_category', opt.value)} />
                                <span>{opt.label}</span>
                            </label>
                        ))}
                    </div>
                     <div className="mb-4">
                        <h4 className="font-semibold mb-2">Agency</h4>
                        <input
                            type="text"
                            placeholder="e.g., NSF, NIH"
                            className="input input-bordered w-full"
                            onChange={(e) => handleFilterChange('agency', e.target.value.split(',').map(s => s.trim()))}
                        />
                    </div>
                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Post Date</h4>
                        <div className="mb-2">
                            <label className="block text-sm mb-1">Start Date</label>
                            <input type="date" className="input input-bordered w-full" onChange={e => setDate('post_date', 'start_date', e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm mb-1">End Date</label>
                            <input type="date" className="input input-bordered w-full" onChange={e => setDate('post_date', 'end_date', e.target.value)} />
                        </div>
                    </div>
                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Close Date</h4>
                        <div className="mb-2">
                            <label className="block text-sm mb-1">Start Date</label>
                            <input type="date" className="input input-bordered w-full" onChange={e => setDate('close_date', 'start_date', e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm mb-1">End Date</label>
                            <input type="date" className="input input-bordered w-full" onChange={e => setDate('close_date', 'end_date', e.target.value)} />
                        </div>
                    </div>
                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Award Floor</h4>
                        <input type="number" placeholder="Min" className="input input-bordered w-full" onChange={e => handleFilterChange('award_floor', { min: e.target.value }, 'range')} />
                    </div>
                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Award Ceiling</h4>
                        <input type="number" placeholder="Max" className="input input-bordered w-full" onChange={e => handleFilterChange('award_ceiling', { max: e.target.value }, 'range')} />
                    </div>
                    <div className="mb-4">
                        <h4 className="font-semibold mb-2">Is Cost Sharing</h4>
                        <select className="select select-bordered w-full" onChange={e => handleFilterChange('is_cost_sharing', e.target.value === 'any' ? [] : [e.target.value === 'yes'])}>
                            <option value="any">Any</option>
                            <option value="yes">Yes</option>
                            <option value="no">No</option>
                        </select>
                    </div>
                </div>
            </div>
            <div className="md:col-span-3">
                <form onSubmit={handleSearch} className="flex items-center space-x-2 mb-4">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search for grants..."
                        className="input input-bordered w-full"
                    />
                    <button type="submit" className="btn btn-primary">Search</button>
                </form>
                {loading ? (
                    <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>
                ) : (
                    <div className="space-y-4">
                        {searchResults.map((grant) => (
                            <div key={grant.opportunity_id} className="card hover:shadow-lg transition-shadow p-4">
                                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{grant.title}</h3>
                                <p className="text-gray-600 dark:text-gray-400 mb-2">{grant.agency_name}</p>
                                <p className="text-sm text-gray-500">Posted: {grant.post_date}</p>
                            </div>
                        ))}

                        {/* Pagination controls */}
                        <div className="flex items-center justify-between mt-4">
                            <div className="flex items-center space-x-2">
                                <button className="btn" onClick={() => goToPage(pageOffset - 1)} disabled={pageOffset <= 1}>Prev</button>
                                <span>Page {pageOffset} of {totalPages || 1}</span>
                                <button className="btn" onClick={() => goToPage(pageOffset + 1)} disabled={totalPages && pageOffset >= totalPages}>Next</button>
                            </div>
                            <div className="flex items-center space-x-2">
                                <label className="text-sm">Page size</label>
                                <select value={pageSize} onChange={handlePageSizeChange} className="select select-bordered">
                                    <option value={10}>10</option>
                                    <option value={20}>20</option>
                                    <option value={50}>50</option>
                                </select>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GrantSearch;
