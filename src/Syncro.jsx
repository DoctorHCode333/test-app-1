

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Card } from 'primereact/card';

const WordCloudViewer = () => {
  const [imageSrc, setImageSrc] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchWordCloud = async () => {
    setLoading(true);
    setImageSrc(null); // clear old image
    try {
      // const response = await fetch('http://localhost:5000/wordcloud');
      const response = await fetch('https://pstrlaae9381.dsglobal.org:5000/wordcloud');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setImageSrc(url);
    } catch (err) {
      console.error('Error fetching word cloud:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-gray-50 to-blue-100">
      <Card className="w-full p-6">
        <h2 className="text-2xl font-bold text-center mb-6 text-blue-800">Word Cloud Generator</h2>

        <div className="flex justify-center mb-6">
          <Button
            label="Generate Word Cloud"
            icon="pi pi-cloud"
            className="p-button-lg p-button-primary"
            onClick={fetchWordCloud}
          />
        </div>

        {loading && (
          <div className="flex justify-center items-center h-64">
            <ProgressSpinner style={{ width: '50px', height: '50px' }} strokeWidth="4" />
          </div>
        )}

        {imageSrc && (
          <div className="flex flex-col items-center">
            <img
              src={imageSrc}
              alt="Word Cloud"
              className="rounded-lg shadow-lg max-w-full h-auto transition duration-300 ease-in-out"
            />

            <a
              href={imageSrc}
              download="wordcloud.png"
              className="mt-4"
            >
              <Button
                icon="pi pi-download"
                label="Download Word Cloud"
                className="p-button-outlined p-button-success"
              />
            </a>
          </div>
        )}
      </Card>
    </div>
  );
};

export default WordCloudViewer;
