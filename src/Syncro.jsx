import React, { useState, useCallback } from 'react';
import { Button } from 'primereact/button';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import { Toast } from 'primereact/toast';
import { useRef } from 'react';

const WordCloudViewer = () => {
  const [imageSrc, setImageSrc] = useState(null);
  const [loading, setLoading] = useState(false);
  const [maxWordLength, setMaxWordLength] = useState(10);
  const [error, setError] = useState(null);
  const toast = useRef(null);

  const wordLengthOptions = [
    { label: '5 words', value: 5 },
    { label: '10 words', value: 10 },
    { label: '15 words', value: 15 },
    { label: '20 words', value: 20 },
    { label: '25 words', value: 25 },
    { label: '30 words', value: 30 },
    { label: '50 words', value: 50 },
    { label: 'Unlimited', value: null }
  ];

  const fetchWordCloud = useCallback(async () => {
    setLoading(true);
    setImageSrc(null);
    setError(null);
    
    try {
      const url = new URL('https://pstrlaae9381.dsglobal.org:5000/wordcloud');
      if (maxWordLength) {
        url.searchParams.append('max_words', maxWordLength.toString());
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setImageSrc(imageUrl);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Word cloud generated successfully!',
        life: 3000
      });
    } catch (err) {
      console.error('Error fetching word cloud:', err);
      setError('Failed to generate word cloud. Please try again.');
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to generate word cloud. Please try again.',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  }, [maxWordLength]);

  const downloadWordCloud = useCallback(() => {
    if (!imageSrc) return;
    
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `wordcloud_${maxWordLength || 'unlimited'}_words_${new Date().toISOString().split('T')[0]}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.current?.show({
      severity: 'success',
      summary: 'Downloaded',
      detail: 'Word cloud downloaded successfully!',
      life: 3000
    });
  }, [imageSrc, maxWordLength]);

  const handleRetry = useCallback(() => {
    setError(null);
    fetchWordCloud();
  }, [fetchWordCloud]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4">
      <Toast ref={toast} />
      
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
          <div className="mb-6 lg:mb-0">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Word Cloud Generator
            </h1>
            <p className="text-gray-600 mt-2 text-lg">
              Generate beautiful word clouds with customizable parameters
            </p>
          </div>
          
          {imageSrc && !loading && (
            <div className="flex items-center gap-3">
              <Button
                icon="pi pi-download"
                label="Download"
                severity="success"
                size="large"
                onClick={downloadWordCloud}
                className="shadow-lg hover:shadow-xl transition-shadow duration-200"
              />
            </div>
          )}
        </div>

        {/* Controls Section */}
        <Card className="mb-8 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="flex flex-col gap-2 min-w-0 flex-1">
              <label htmlFor="word-length" className="text-sm font-semibold text-gray-700">
                Maximum Words
              </label>
              <Dropdown
                id="word-length"
                value={maxWordLength}
                options={wordLengthOptions}
                onChange={(e) => setMaxWordLength(e.value)}
                placeholder="Select word limit"
                className="w-full sm:w-auto min-w-48"
                disabled={loading}
              />
            </div>
            
            <Button
              label={loading ? "Generating..." : "Generate Word Cloud"}
              icon={loading ? "pi pi-spin pi-spinner" : "pi pi-cloud"}
              size="large"
              onClick={fetchWordCloud}
              disabled={loading}
              className="shadow-md hover:shadow-lg transition-shadow duration-200 mt-4 sm:mt-6"
            />
          </div>
        </Card>

        {/* Main Content Section */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm min-h-96">
          {/* Loading State */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <ProgressSpinner 
                style={{ width: '60px', height: '60px' }} 
                strokeWidth="3" 
                animationDuration="1s"
              />
              <p className="text-gray-600 mt-4 text-lg">
                Generating your word cloud...
              </p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md text-center">
                <i className="pi pi-exclamation-triangle text-red-500 text-3xl mb-3"></i>
                <h3 className="text-lg font-semibold text-red-800 mb-2">
                  Generation Failed
                </h3>
                <p className="text-red-600 mb-4">{error}</p>
                <Button
                  label="Try Again"
                  icon="pi pi-refresh"
                  onClick={handleRetry}
                  className="p-button-outlined"
                  severity="danger"
                />
              </div>
            </div>
          )}

          {/* Success State - Word Cloud Display */}
          {imageSrc && !loading && (
            <div className="flex flex-col items-center">
              <div className="relative group">
                <img
                  src={imageSrc}
                  alt="Generated Word Cloud"
                  className="rounded-xl shadow-2xl max-w-full h-auto transition-all duration-300 ease-in-out group-hover:shadow-3xl"
                  style={{ maxWidth: '97vw' }}
                />
                <div className="absolute inset-0 bg-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl pointer-events-none"></div>
              </div>
              
              <div className="mt-6 flex flex-col sm:flex-row gap-3 items-center">
                <Button
                  icon="pi pi-download"
                  label="Download High Quality"
                  severity="success"
                  size="large"
                  onClick={downloadWordCloud}
                  className="shadow-lg hover:shadow-xl transition-shadow duration-200"
                />
                <Button
                  icon="pi pi-refresh"
                  label="Generate New"
                  severity="secondary"
                  outlined
                  onClick={fetchWordCloud}
                  className="shadow-md hover:shadow-lg transition-shadow duration-200"
                />
              </div>
            </div>
          )}

          {/* Initial State */}
          {!imageSrc && !loading && !error && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <i className="pi pi-cloud text-6xl text-blue-300 mb-4"></i>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                Ready to Generate
              </h3>
              <p className="text-gray-500 max-w-md">
                Choose your word limit and click "Generate Word Cloud" to create a beautiful visualization of your data.
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default WordCloudViewer;
