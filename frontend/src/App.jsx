import React, { useState } from 'react';
import { Upload, CheckCircle, XCircle, Settings, RotateCw } from 'lucide-react';
import InvoicePreview from './components/InvoicePreview';
import InvoiceForm from './components/InvoiceForm';
import ConfigPanel from './components/ConfigPanel';

function App() {
  const [invoices, setInvoices] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [message, setMessage] = useState(null);

  const [config, setConfig] = useState({
    useApi: true,
    exportFormat: 'json',
    apiUrl: 'http://localhost:5000',
    apiUsername: 'admin',
    apiPassword: 'password'
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
        setInvoices(data.invoices);
        setCurrentIndex(0);
        setMessage({ type: 'success', text: `${data.invoices.length} facturi încărcate cu succes!` });
      } else {
        setMessage({ type: 'error', text: 'Eroare la încărcarea facturilor' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Eroare: ${error.message}` });
    } finally {
      setIsUploading(false);
    }
  };

  const handleApprove = async () => {
    const currentInvoice = invoices[currentIndex];

    try {
      const response = await fetch(`${config.apiUrl}/api/send-to-1c`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...currentInvoice,
          use_api: config.useApi,
          export_format: config.exportFormat
        })
      });

      const result = await response.json();

      if (result.success) {
        updateInvoiceStatus(currentIndex, 'approved');
        setMessage({
          type: 'success',
          text: `Factură aprobată! Metoda: ${result.method}`
        });

        // Merge la următoarea factură
        if (currentIndex < invoices.length - 1) {
          setTimeout(() => setCurrentIndex(currentIndex + 1), 1000);
        }
      } else {
        setMessage({ type: 'error', text: `Eroare: ${result.error}` });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Eroare: ${error.message}` });
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
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Procesare Facturi OCR + 1C
              </h1>
              <p className="text-gray-600">
                Sistem automatizat pentru Republica Moldova
              </p>
            </div>

            <button
              onClick={() => setShowConfig(!showConfig)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Settings size={20} />
              Configurări
            </button>
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

        {/* Config Panel */}
        {showConfig && (
          <ConfigPanel
            config={config}
            setConfig={setConfig}
            onClose={() => setShowConfig(false)}
          />
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
        {currentInvoice && (
          <div className="grid grid-cols-2 gap-6">
            <InvoicePreview
              invoice={currentInvoice}
              apiUrl={config.apiUrl}
            />

            <InvoiceForm
              invoice={currentInvoice}
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
