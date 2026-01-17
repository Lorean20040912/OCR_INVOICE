import React from 'react';
import { X, Server, FileJson, FileCode, Database } from 'lucide-react';

function ConfigPanel({ config, setConfig, onClose }) {
  const handleToggleApi = () => {
    setConfig({ ...config, useApi: !config.useApi });
  };

  const handleFormatChange = (format) => {
    setConfig({ ...config, exportFormat: format });
  };

  const handleInputChange = (field, value) => {
    setConfig({ ...config, [field]: value });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6 border-2 border-indigo-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Server className="text-indigo-600" size={24} />
          <h2 className="text-2xl font-bold text-gray-800">
            Configurări Sistem
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X size={24} />
        </button>
      </div>

      <div className="space-y-6">
        {/* API Toggle */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="font-semibold text-gray-800 mb-1">
                Integrare API 1C
              </h3>
              <p className="text-sm text-gray-600">
                Trimite facturi direct prin API. Dacă API nu funcționează, se va folosi automat exportul.
              </p>
            </div>
            <button
              onClick={handleToggleApi}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                config.useApi ? 'bg-green-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                  config.useApi ? 'translate-x-7' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          {config.useApi && (
            <p className="text-sm text-green-700 font-medium">
              ✓ API Activat
            </p>
          )}
          {!config.useApi && (
            <p className="text-sm text-gray-600">
              Se va folosi doar export în formatul selectat
            </p>
          )}
        </div>

        {/* Export Format Selection */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-3">
            Format Export (Fallback)
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Selectează formatul pentru export manual sau când API nu funcționează:
          </p>

          <div className="space-y-3">
            {/* JSON Option */}
            <label className="flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer hover:bg-white transition-colors">
              <input
                type="radio"
                name="exportFormat"
                value="json"
                checked={config.exportFormat === 'json'}
                onChange={(e) => handleFormatChange(e.target.value)}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <FileJson size={20} className="text-blue-600" />
                  <span className="font-medium text-gray-800">JSON</span>
                  <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                    Recomandat
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  Format modern, compatibil cu 1C 8.3+. Ideal pentru API-uri și import automat.
                </p>
              </div>
            </label>

            {/* XML Option */}
            <label className="flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer hover:bg-white transition-colors">
              <input
                type="radio"
                name="exportFormat"
                value="xml"
                checked={config.exportFormat === 'xml'}
                onChange={(e) => handleFormatChange(e.target.value)}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <FileCode size={20} className="text-orange-600" />
                  <span className="font-medium text-gray-800">XML</span>
                </div>
                <p className="text-sm text-gray-600">
                  Standard pentru schimb de date. Compatibil cu 1C 8.x și sisteme vechi.
                </p>
              </div>
            </label>

            {/* DBF/CSV Option */}
            <label className="flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer hover:bg-white transition-colors">
              <input
                type="radio"
                name="exportFormat"
                value="dbf"
                checked={config.exportFormat === 'dbf'}
                onChange={(e) => handleFormatChange(e.target.value)}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Database size={20} className="text-purple-600" />
                  <span className="font-medium text-gray-800">DBF / CSV</span>
                </div>
                <p className="text-sm text-gray-600">
                  Pentru 1C 7.7 și import manual. Poate fi deschis în Excel.
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* API Configuration */}
        {config.useApi && (
          <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
            <h3 className="font-semibold text-gray-800 mb-3">
              Credențiale API 1C
            </h3>

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL API
                </label>
                <input
                  type="text"
                  value={config.apiUrl}
                  onChange={(e) => handleInputChange('apiUrl', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="http://localhost:5000"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <input
                    type="text"
                    value={config.apiUsername}
                    onChange={(e) => handleInputChange('apiUsername', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="admin"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    value={config.apiPassword}
                    onChange={(e) => handleInputChange('apiPassword', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Help Info */}
        <div className="p-4 bg-yellow-50 rounded-lg border-2 border-yellow-200">
          <h4 className="font-semibold text-yellow-800 mb-2">
            💡 Sfaturi utile:
          </h4>
          <ul className="text-sm text-yellow-800 space-y-1">
            <li>• JSON: Cel mai rapid și modern, recomandat pentru 1C 8.3+</li>
            <li>• XML: Universal, funcționează cu orice versiune 1C</li>
            <li>• DBF/CSV: Pentru versiuni vechi sau import manual în Excel</li>
            <li>• Dacă API eșuează, exportul se face automat în formatul selectat</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ConfigPanel;
