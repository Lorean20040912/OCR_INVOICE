import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCw, RefreshCw } from 'lucide-react';

function InvoicePreview({ invoice, apiUrl }) {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);

  const handleZoomIn = () => {
    if (zoom < 200) setZoom(zoom + 25);
  };

  const handleZoomOut = () => {
    if (zoom > 50) setZoom(zoom - 25);
  };

  const handleRotate = () => {
    setRotation((rotation + 90) % 360);
  };

  const handleReset = () => {
    setZoom(100);
    setRotation(0);
  };

  // Construiește URL-ul imaginii
  const getImageUrl = () => {
    if (!invoice.file_path) return null;
    const filename = invoice.file_path.split(/[\\/]/).pop();
    return `${apiUrl}/api/image/${filename}`;
  };

  const imageUrl = getImageUrl();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">
          Preview Factură
        </h2>

        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 50}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Zoom Out"
          >
            <ZoomOut size={20} />
          </button>

          <span className="text-sm font-medium text-gray-600 min-w-[60px] text-center">
            {zoom}%
          </span>

          <button
            onClick={handleZoomIn}
            disabled={zoom >= 200}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Zoom In"
          >
            <ZoomIn size={20} />
          </button>

          <div className="w-px h-6 bg-gray-300 mx-2" />

          <button
            onClick={handleRotate}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            title="Rotește 90°"
          >
            <RotateCw size={20} />
          </button>

          <button
            onClick={handleReset}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            title="Reset"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {/* OCR Confidence Badge */}
      {invoice.confidence !== undefined && (
        <div className="mb-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 rounded-full">
            <span className="text-sm text-gray-600">Confidence OCR:</span>
            <span className={`text-sm font-semibold ${
              invoice.confidence > 0.7 ? 'text-green-600' :
              invoice.confidence > 0.4 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {Math.round(invoice.confidence * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* Image Preview */}
      <div className="border-2 border-gray-200 rounded-lg overflow-hidden bg-gray-50">
        <div className="h-[600px] overflow-auto">
          {imageUrl ? (
            <div className="flex items-center justify-center min-h-full p-4">
              <img
                src={imageUrl}
                alt="Invoice preview"
                style={{
                  transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                  transition: 'transform 0.3s ease',
                  maxWidth: '100%',
                  height: 'auto'
                }}
                className="shadow-lg"
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400">
                <p className="text-lg font-medium">Preview indisponibil</p>
                <p className="text-sm">Imaginea nu poate fi afișată</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* File Info */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <span className="font-medium">Fișier:</span>{' '}
          {invoice.original_filename || 'N/A'}
        </p>
      </div>
    </div>
  );
}

export default InvoicePreview;
