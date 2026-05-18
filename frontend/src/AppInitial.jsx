import React, { useState, useRef } from 'react';
import { Upload, CheckCircle, XCircle, Settings, RotateCw } from 'lucide-react';
import ViewerPane from './components/ViewerPane.jsx';
import InvoiceForm from './components/InvoiceForm';

function App() {
  const [invoices, setInvoices] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [message, setMessage] = useState(null);
  const [zoom, setZoom] = useState(1);

  const addMoreInputRef = useRef(null);

  // Păstrăm câmpurile pentru compatibilitate cu ConfigPanel, dar NU mai folosim API 1C
  const [config, setConfig] = useState({
    exportFormat: 'json',
    apiUrl: 'http://localhost:5000'
  });

  const stats = {
    total: invoices.length,
    approved: invoices.filter(inv => inv.status === 'approved').length,
    rejected: invoices.filter(inv => inv.status === 'rejected').length,
    pending: invoices.filter(inv => inv.status === 'pending').length
  };

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    setIsUploading(true);
    setMessage(null);

    const formData = new FormData();
    for (let file of files) {
      formData.append('files', file);
    }

    try {
      const response = await fetch(`${config.apiUrl}/api/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setInvoices(prev => {
          const merged = prev.length ? [...prev, ...(data.invoices || [])] : (data.invoices || []);
          // dacă era prima încărcare, rămânem pe 0; altfel păstrăm indexul curent
          if (prev.length === 0 && merged.length > 0) setCurrentIndex(0);
          return merged;
        });
        setMessage({ type: 'success', text: `${(data.invoices || []).length} facturi încărcate cu succes!` });
      } else {
        setMessage({ type: 'error', text: 'Eroare la încărcarea facturilor' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Eroare: ${error.message}` });
    } finally {
      setIsUploading(false);
      // reset input pentru a permite aceeași selecție din nou
      if (e?.target) e.target.value = '';
      if (addMoreInputRef.current) addMoreInputRef.current.value = '';
    }
  };

  // Eliminat apelul către /api/send-to-1c; marcăm doar local ca aprobat și navigăm mai departe
  const handleApprove = () => {
    updateInvoiceStatus(currentIndex, 'approved');
    setMessage({ type: 'success', text: 'Factură aprobată (local).' });

    if (currentIndex < invoices.length - 1) {
      setTimeout(() => setCurrentIndex(currentIndex + 1), 1000);
    }
  };

  const handleReject = () => {
    updateInvoiceStatus(currentIndex, 'rejected');
    setMessage({ type: 'info', text: 'Factură respinsă' });

    if (currentIndex < invoices.length - 1) {
      setTimeout(() => setCurrentIndex(currentIndex + 1), 500);
    }
  };

  const handleExport = async () => {
    const currentInvoice = invoices[currentIndex];

    try {
      const response = await fetch(`${config.apiUrl}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...currentInvoice,
          format: config.exportFormat
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `invoice_${currentInvoice.invoice_number || 'export'}.${config.exportFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        setMessage({ type: 'success', text: `Export ${config.exportFormat.toUpperCase()} descărcat!` });
      } else {
        setMessage({ type: 'error', text: 'Eroare la export' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Eroare: ${error.message}` });
    }
  };

  const updateInvoiceStatus = (index, status) => {
    setInvoices(prev => prev.map((inv, i) =>
      i === index ? { ...inv, status } : inv
    ));
  };

  const updateInvoiceData = (field, value) => {
    setInvoices(prev => prev.map((inv, i) =>
      i === currentIndex ? { ...inv, [field]: value } : inv
    ));
  };

  const currentInvoice = invoices[currentIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Hidden input pentru adăugare rapidă fără refresh */}
        <input
          ref={addMoreInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileUpload}
          className="hidden"
          disabled={isUploading}
        />

        {/* Stil pentru a ascunde câmpul 'Data livrării' indiferent unde e definit */}
        <style>{`
          #delivery_date, [name="delivery_date"], label[for="delivery_date"] {
            display: none !important;
          }
        `}</style>

        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Procesare Facturi OCR
              </h1>
              <p className="text-gray-600">
                Sistem automatizat pentru Republica Moldova
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => addMoreInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-60"
                disabled={isUploading}
              >
                <Upload size={18} />
                Adaugă facturi
              </button>

              <button
                onClick={() => setShowConfig(!showConfig)}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Settings size={20} />
                Configurări
              </button>
            </div>
          </div>

          {/* Statistics */}
          {invoices.length > 0 && (
            <div className="mt-6 grid grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
                <div className="text-sm text-gray-600">Total Facturi</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
                <div className="text-sm text-gray-600">Aprobate</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
                <div className="text-sm text-gray-600">Respinse</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
                <div className="text-sm text-gray-600">În Așteptare</div>
              </div>
            </div>
          )}

          {/* Progress Bar */}
          {invoices.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>Progres procesare</span>
                <span>{Math.round((stats.approved + stats.rejected) / stats.total * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${(stats.approved + stats.rejected) / stats.total * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Config Panel (simplificat, fără câmpuri 1C) */}
        {showConfig && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800">Configurări</h2>
              <button
                onClick={() => setShowConfig(false)}
                className="text-gray-500 hover:text-gray-700"
                aria-label="Închide"
              >
                ✕
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">API URL</label>
                <input
                  type="text"
                  className="w-full border rounded-md px-3 py-2"
                  value={config.apiUrl}
                  onChange={(e) => setConfig((c) => ({ ...c, apiUrl: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Format export</label>
                <select
                  className="w-full border rounded-md px-3 py-2"
                  value={config.exportFormat}
                  onChange={(e) => setConfig((c) => ({ ...c, exportFormat: e.target.value }))}
                >
                  <option value="json">JSON</option>
                  <option value="xml">XML</option>
                  <option value="dbf">DBF</option>
                  <option value="xlsx">XLSX</option>
                  <option value="zip">ZIP (1C pachet)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-50 border-l-4 border-green-500' :
            message.type === 'error' ? 'bg-red-50 border-l-4 border-red-500' :
            'bg-blue-50 border-l-4 border-blue-500'
          }`}>
            <p className={`font-medium ${
              message.type === 'success' ? 'text-green-800' :
              message.type === 'error' ? 'text-red-800' :
              'text-blue-800'
            }`}>
              {message.text}
            </p>
          </div>
        )}

        {/* Upload Area */}
        {invoices.length === 0 && (
          <div className="bg-white rounded-lg shadow-lg p-12">
            <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-12 cursor-pointer hover:border-indigo-500 transition-colors">
              <Upload size={64} className="text-gray-400 mb-4" />
              <span className="text-xl font-semibold text-gray-700 mb-2">
                Încarcă Facturi
              </span>
              <span className="text-gray-500 mb-4">
                PDF, PNG, JPG (multiplu)
              </span>
              <input
                type="file"
                multiple
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isUploading}
              />
              {isUploading && (
                <div className="flex items-center gap-2 text-indigo-600">
                  <RotateCw size={20} className="animate-spin" />
                  <span>Se procesează...</span>
                </div>
              )}
            </label>
          </div>
        )}

        {/* Invoice Processing */}
        {invoices.length > 0 && (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm font-medium">Previzualizare</div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setZoom((z) => Math.max(0.25, z - 0.25))}
                    className="px-2 py-1 border rounded-md hover:bg-gray-50"
                    title="Micșorează"
                  >
                    −
                  </button>
                  <button
                    onClick={() => setZoom((z) => Math.min(4, z + 0.25))}
                    className="px-2 py-1 border rounded-md hover:bg-gray-50"
                    title="Mărește"
                  >
                    +
                  </button>
                  <button
                    onClick={() => setZoom(1)}
                    className="px-2 py-1 border rounded-md hover:bg-gray-50"
                    title="Reset"
                  >
                    100%
                  </button>
                </div>
              </div>

              <ViewerPane
                src={
                  invoices[currentIndex]?.preview_url
                    ? `${config.apiUrl}${invoices[currentIndex].preview_url}`
                    : `${config.apiUrl}/api/image/${encodeURIComponent(invoices[currentIndex]?.server_filename || '')}`
                }
                filename={invoices[currentIndex]?.server_filename}
                zoom={zoom}
              />
            </div>

            <InvoiceForm
              invoice={invoices[currentIndex]}
              onUpdate={updateInvoiceData}
              onApprove={handleApprove}
              onReject={handleReject}
              onExport={handleExport}
              currentIndex={currentIndex}
              totalInvoices={invoices.length}
              onNavigate={setCurrentIndex}
              exportFormat={config.exportFormat}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
