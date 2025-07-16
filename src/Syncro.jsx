import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Filter, Play, Pause, Download, X, Loader2, Check, Search, RefreshCw } from 'lucide-react';

const RedactionSoftware = () => {
  const [selectedDateTime, setSelectedDateTime] = useState('');
  const [selectedTimeInterval, setSelectedTimeInterval] = useState({ start: '', end: '' });
  const [filters, setFilters] = useState({
    conversationId: [],
    agentName: [],
    ssn: [],
    ani: [],
    dnis: [],
    customerName: ''
  });
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [showRedactionDialog, setShowRedactionDialog] = useState(false);
  const [redactionStatus, setRedactionStatus] = useState('loading');
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoadingTable, setIsLoadingTable] = useState(false);
  const [globalFilter, setGlobalFilter] = useState('');
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [columnFilters, setColumnFilters] = useState({
    conversationId: { value: '', matchMode: 'contains' },
    agentName: { value: '', matchMode: 'contains' },
    customerName: { value: '', matchMode: 'contains' },
    ssn: { value: '', matchMode: 'contains' },
    ani: { value: '', matchMode: 'contains' },
    dnis: { value: '', matchMode: 'contains' },
    startDate: { value: '', matchMode: 'contains' }
  });

  // Mock data for dropdowns
  const mockFilterOptions = {
    conversationId: ['CONV-001', 'CONV-002', 'CONV-003', 'CONV-004', 'CONV-005'],
    agentName: ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Emily Chen', 'Robert Wilson'],
    ssn: ['***-**-1234', '***-**-5678', '***-**-9012', '***-**-3456'],
    ani: ['555-0123', '555-0456', '555-0789', '555-0234'],
    dnis: ['800-555-0100', '800-555-0200', '800-555-0300', '800-555-0400']
  };

  // Mock conversation data
  const mockConversations = [
    {
      id: 1,
      conversationId: 'CONV-001',
      agentName: 'John Smith',
      customerName: 'Alice Johnson',
      startDate: '2024-01-15 10:00:23',
      ssn: '***-**-1234',
      ani: '555-0123',
      dnis: '800-555-0100'
    },
    {
      id: 2,
      conversationId: 'CONV-002',
      agentName: 'Sarah Johnson',
      customerName: 'Bob Wilson',
      startDate: '2024-01-15 10:15:45',
      ssn: '***-**-5678',
      ani: '555-0456',
      dnis: '800-555-0200'
    },
    {
      id: 3,
      conversationId: 'CONV-003',
      agentName: 'Mike Davis',
      customerName: 'Carol Brown',
      startDate: '2024-01-15 10:30:12',
      ssn: '***-**-9012',
      ani: '555-0789',
      dnis: '800-555-0300'
    },
    {
      id: 4,
      conversationId: 'CONV-004',
      agentName: 'Emily Chen',
      customerName: 'David Lee',
      startDate: '2024-01-15 10:45:33',
      ssn: '***-**-3456',
      ani: '555-0234',
      dnis: '800-555-0400'
    },
    {
      id: 5,
      conversationId: 'CONV-005',
      agentName: 'Robert Wilson',
      customerName: 'Eva Martinez',
      startDate: '2024-01-15 11:00:18',
      ssn: '***-**-7890',
      ani: '555-0567',
      dnis: '800-555-0500'
    }
  ];

  const matchModes = [
    { label: 'Contains', value: 'contains' },
    { label: 'Does not contain', value: 'notContains' },
    { label: 'Starts with', value: 'startsWith' },
    { label: 'Ends with', value: 'endsWith' },
    { label: 'Equals', value: 'equals' },
    { label: 'Not equals', value: 'notEquals' }
  ];

  useEffect(() => {
    if (selectedDateTime && selectedTimeInterval.start && selectedTimeInterval.end) {
      setIsLoadingConversations(true);
      setTimeout(() => {
        setConversations(mockConversations);
        setFilteredConversations(mockConversations);
        setIsLoadingConversations(false);
      }, 7000);
    }
  }, [selectedDateTime, selectedTimeInterval]);

  useEffect(() => {
    applyFilters();
  }, [globalFilter, columnFilters, conversations]);

  const applyFilters = () => {
    let filtered = [...conversations];

    // Apply global filter
    if (globalFilter) {
      filtered = filtered.filter(conv => 
        Object.values(conv).some(value => 
          value.toString().toLowerCase().includes(globalFilter.toLowerCase())
        )
      );
    }

    // Apply column filters
    Object.entries(columnFilters).forEach(([column, filter]) => {
      if (filter.value) {
        filtered = filtered.filter(conv => {
          const cellValue = conv[column]?.toString().toLowerCase() || '';
          const filterValue = filter.value.toLowerCase();
          
          switch (filter.matchMode) {
            case 'contains':
              return cellValue.includes(filterValue);
            case 'notContains':
              return !cellValue.includes(filterValue);
            case 'startsWith':
              return cellValue.startsWith(filterValue);
            case 'endsWith':
              return cellValue.endsWith(filterValue);
            case 'equals':
              return cellValue === filterValue;
            case 'notEquals':
              return cellValue !== filterValue;
            default:
              return true;
          }
        });
      }
    });

    setFilteredConversations(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: Array.isArray(prev[filterType]) 
        ? (prev[filterType].includes(value)
          ? prev[filterType].filter(item => item !== value)
          : [...prev[filterType], value])
        : value
    }));
  };

  const handleApplyFilters = () => {
    setIsLoadingTable(true);
    setTimeout(() => {
      // Apply your filter logic here
      setIsLoadingTable(false);
    }, 5000);
  };

  const handleClearFilters = () => {
    setIsLoadingTable(true);
    setFilters({
      conversationId: [],
      agentName: [],
      ssn: [],
      ani: [],
      dnis: [],
      customerName: ''
    });
    setTimeout(() => {
      setIsLoadingTable(false);
    }, 5000);
  };

  const handleConversationSelect = (conversationId) => {
    setSelectedConversation(conversationId === selectedConversation ? null : conversationId);
  };

  const handleRedact = () => {
    if (!selectedConversation) return;
    
    setShowRedactionDialog(true);
    setRedactionStatus('loading');
    
    setTimeout(() => {
      setRedactionStatus('completed');
      setAudioUrl('https://www.soundjay.com/misc/sounds/bell-ringing-05.wav');
    }, 3000);
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = 'redacted-audio.wav';
    link.click();
  };

  const handleColumnFilter = (column, value, matchMode) => {
    setColumnFilters(prev => ({
      ...prev,
      [column]: { value, matchMode }
    }));
  };

  const MultiSelectDropdown = ({ label, options, selected, onChange, placeholder }) => {
    const [isOpen, setIsOpen] = useState(false);
    
    return (
      <div className="relative">
        <label className="block text-sm font-semibold text-gray-700 mb-2">{label}</label>
        <div
          className="min-h-11 px-4 py-2 border border-gray-300 rounded-lg bg-white cursor-pointer flex items-center justify-between shadow-sm hover:border-blue-400 transition-colors"
          onClick={() => setIsOpen(!isOpen)}
        >
          <div className="flex flex-wrap gap-1">
            {selected.length > 0 ? (
              selected.map(item => (
                <span key={item} className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                  {item}
                </span>
              ))
            ) : (
              <span className="text-gray-500">{placeholder}</span>
            )}
          </div>
          <svg className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        {isOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
            {options.map(option => (
              <div
                key={option}
                className="px-4 py-2 hover:bg-blue-50 cursor-pointer flex items-center transition-colors"
                onClick={() => {
                  onChange(option);
                  setIsOpen(false);
                }}
              >
                <input
                  type="checkbox"
                  checked={selected.includes(option)}
                  onChange={() => {}}
                  className="mr-3 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm">{option}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const ColumnFilter = ({ column, placeholder }) => {
    const [isOpen, setIsOpen] = useState(false);
    
    return (
      <div className="relative">
        <div className="flex items-center space-x-1">
          <input
            type="text"
            placeholder={placeholder}
            value={columnFilters[column].value}
            onChange={(e) => handleColumnFilter(column, e.target.value, columnFilters[column].matchMode)}
            className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            <Filter className="w-3 h-3" />
          </button>
        </div>
        
        {isOpen && (
          <div className="absolute z-20 mt-1 w-full bg-white border border-gray-300 rounded shadow-lg">
            {matchModes.map(mode => (
              <div
                key={mode.value}
                className="px-2 py-1 hover:bg-gray-50 cursor-pointer text-xs"
                onClick={() => {
                  handleColumnFilter(column, columnFilters[column].value, mode.value);
                  setIsOpen(false);
                }}
              >
                {mode.label}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
      <div className="bg-white rounded-xl shadow-xl p-8 border border-gray-200">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Audio Redaction Software</h1>
          <p className="text-gray-600">Select date, time interval, and apply filters to find and redact conversations</p>
        </div>
        
        {/* Date and Time Interval Selection */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-8 border border-blue-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-blue-600" />
            Date & Time Selection
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Select Date</label>
              <input
                type="date"
                value={selectedDateTime}
                onChange={(e) => setSelectedDateTime(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
              />
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Start Time</label>
              <input
                type="time"
                value={selectedTimeInterval.start}
                onChange={(e) => setSelectedTimeInterval(prev => ({ ...prev, start: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                disabled={!selectedDateTime}
              />
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">End Time</label>
              <input
                type="time"
                value={selectedTimeInterval.end}
                onChange={(e) => setSelectedTimeInterval(prev => ({ ...prev, end: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                disabled={!selectedDateTime}
              />
            </div>
          </div>
        </div>

        {/* Loading Spinner for Conversations */}
        {isLoadingConversations && (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">Loading conversations...</p>
            </div>
          </div>
        )}

        {/* Filters Section */}
        {selectedDateTime && selectedTimeInterval.start && selectedTimeInterval.end && !isLoadingConversations && (
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 mb-8 border border-purple-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <Filter className="w-5 h-5 mr-2 text-purple-600" />
              Filters
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <MultiSelectDropdown
                label="Conversation ID"
                options={mockFilterOptions.conversationId}
                selected={filters.conversationId}
                onChange={(value) => handleFilterChange('conversationId', value)}
                placeholder="Select conversation IDs"
              />
              
              <MultiSelectDropdown
                label="Agent Name"
                options={mockFilterOptions.agentName}
                selected={filters.agentName}
                onChange={(value) => handleFilterChange('agentName', value)}
                placeholder="Select agent names"
              />
              
              <MultiSelectDropdown
                label="SSN"
                options={mockFilterOptions.ssn}
                selected={filters.ssn}
                onChange={(value) => handleFilterChange('ssn', value)}
                placeholder="Select SSN"
              />
              
              <MultiSelectDropdown
                label="ANI"
                options={mockFilterOptions.ani}
                selected={filters.ani}
                onChange={(value) => handleFilterChange('ani', value)}
                placeholder="Select ANI"
              />
              
              <MultiSelectDropdown
                label="DNIS"
                options={mockFilterOptions.dnis}
                selected={filters.dnis}
                onChange={(value) => handleFilterChange('dnis', value)}
                placeholder="Select DNIS"
              />
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Customer Name</label>
                <input
                  type="text"
                  value={filters.customerName}
                  onChange={(e) => handleFilterChange('customerName', e.target.value)}
                  placeholder="Enter customer name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 shadow-sm"
                />
              </div>
            </div>
            
            <div className="flex space-x-4 mt-6">
              <button
                onClick={handleApplyFilters}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md font-medium"
              >
                Apply Filters
              </button>
              <button
                onClick={handleClearFilters}
                className="px-6 py-2 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg hover:from-gray-600 hover:to-gray-700 transition-all shadow-md font-medium flex items-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Clear Filters
              </button>
            </div>
          </div>
        )}

        {/* Loading Spinner for Table */}
        {isLoadingTable && (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">Processing filters...</p>
            </div>
          </div>
        )}

        {/* Conversations Table */}
        {conversations.length > 0 && !isLoadingConversations && !isLoadingTable && (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">Conversations</h2>
                <button
                  onClick={handleRedact}
                  disabled={!selectedConversation}
                  className="px-6 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all shadow-md font-medium"
                >
                  Redact Selected Conversation
                </button>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search/Filter interactions using Conversation ID/ Agent Name/ Customer Name/ SSN/ ANI/ DNIS
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={globalFilter}
                    onChange={(e) => setGlobalFilter(e.target.value)}
                    placeholder="Global search..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                  />
                </div>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Select</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                      <div className="space-y-2">
                        <div>Conversation ID</div>
                        <ColumnFilter column="conversationId" placeholder="Filter..." />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                      <div className="space-y-2">
                        <div>Agent Name</div>
                        <ColumnFilter column="agentName" placeholder="Filter..." />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                      <div className="space-y-2">
                        <div>Customer Name</div>
                        <ColumnFilter column="customerName" placeholder="Filter..." />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-100">
                      <div className="space-y-2">
                        <div className="flex items-center">
                          Start Date
                          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                          </svg>
                        </div>
                        <ColumnFilter column="startDate" placeholder="Filter..." />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                      <div className="space-y-2">
                        <div>SSN</div>
                        <ColumnFilter column="ssn" placeholder="Filter..." />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                      <div className="space-y-2">
                        <div>ANI</div>
                        <ColumnFilter column="ani" placeholder="Filter..." />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                      <div className="space-y-2">
                        <div>DNIS</div>
                        <ColumnFilter column="dnis" placeholder="Filter..." />
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredConversations.map(conversation => (
                    <tr key={conversation.id} className={`hover:bg-gray-50 transition-colors ${selectedConversation === conversation.id ? 'bg-blue-50' : ''}`}>
                      <td className="px-4 py-3">
                        <input
                          type="radio"
                          name="selectedConversation"
                          checked={selectedConversation === conversation.id}
                          onChange={() => handleConversationSelect(conversation.id)}
                          className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{conversation.conversationId}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{conversation.agentName}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{conversation.customerName}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{conversation.startDate}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{conversation.ssn}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{conversation.ani}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{conversation.dnis}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Redaction Dialog */}
        {showRedactionDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-8 w-full max-w-lg shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-800">
                  {redactionStatus === 'loading' ? 'Processing Redaction...' : 'Redaction Complete'}
                </h3>
                <button
                  onClick={() => setShowRedactionDialog(false)}
                  className="text-gray-500 hover:text-gray-700 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              {redactionStatus === 'loading' ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-gray-600 text-lg">Processing audio redaction...</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="flex items-center text-green-600 bg-green-50 p-4 rounded-lg">
                    <Check className="w-6 h-6 mr-3" />
                    <span className="font-medium">Redaction completed successfully!</span>
                  </div>
                  
                  <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-lg font-semibold text-gray-800">Redacted Audio</span>
                      <button
                        onClick={handleDownload}
                        className="flex items-center text-blue-600 hover:text-blue-700 font-medium transition-colors"
                      >
                        <Download className="w-5 h-5 mr-2" />
                        Download
                      </button>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={handlePlayPause}
                        className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
                      >
                        {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                      </button>
                      
                      <div className="flex-1 bg-gray-300 rounded-full h-3 overflow-hidden">
                        <div className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full w-1/3 transition-all"></div>
                      </div>
                      
                      <span className="text-sm text-gray-600 font-medium">02:15 / 05:23</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RedactionSoftware;
