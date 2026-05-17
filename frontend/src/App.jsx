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

const API_BASE = "http://localhost:5000";

function App() {
  const fileInputRef = useRef(null);
  const [invoices, setInvoices] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  const onAddMoreClick = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const onFilesSelected = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    setIsUploading(true);
    setError("");

    try {
      const form = new FormData();
      for (const f of files) {
        form.append("files", f);
      }

      const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || `Upload eșuat (${res.status})`);
      }

      const data = await res.json();
      const newInvoices = (data && data.invoices) || [];

      // Normalizez filename pentru preview: extrag ultimul segment din file_path
      const normalized = newInvoices.map((inv) => {
        const filePath = inv.file_path || "";
        const serverFile = filePath.split(/[/\\\\]/).pop() || "";
        return { ...inv, server_filename: serverFile };
      });

      setInvoices((prev) => [...prev, ...normalized]);
    } catch (err) {
      console.error(err);
      setError(err.message || "Upload eșuat");
    } finally {
      setIsUploading(false);
      // permite selectarea aceluiași fișier din nou
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div style={{ fontFamily: "system-ui, Arial", maxWidth: 1000, margin: "20px auto", padding: 16 }}>
      <h1 style={{ fontSize: 24, marginBottom: 8 }}>Procesare Facturi OCR + 1C</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>
        Încarcă una sau mai multe facturi. Poți adăuga alte fișiere ulterior, fără să reîncarci pagina.
      </p>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}>
        <button
          onClick={onAddMoreClick}
          disabled={isUploading}
          style={{
            background: "#2563eb",
            color: "white",
            border: 0,
            borderRadius: 8,
            padding: "10px 14px",
            cursor: "pointer",
            opacity: isUploading ? 0.8 : 1,
          }}
        >
          {isUploading ? "Se încarcă..." : "Adaugă alte facturi"}
        </button>

        <input
          type="file"
          multiple
          accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff"
          ref={fileInputRef}
          onChange={onFilesSelected}
          style={{ display: "none" }}
        />

        <span style={{ fontSize: 12, color: "#666" }}>
          Motor OCR: Azure (setat în backend)
        </span>
      </div>

      {error ? (
        <div style={{ background: "#fee2e2", color: "#991b1b", border: "1px solid #fecaca", padding: 10, borderRadius: 8, marginBottom: 16 }}>
          {error}
        </div>
      ) : null}

      <div style={{ marginTop: 16 }}>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Facturi procesate</h2>
        {invoices.length === 0 ? (
          <div style={{ color: "#666" }}>Încă nu ai încărcat nicio factură.</div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
            {invoices.map((inv) => (
              <div key={inv.unique_id || inv.file_path} style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 12 }}>
                <div style={{ fontWeight: 600, marginBottom: 6 }}>
                  {inv.original_filename || inv.invoice_number || "Factura"}
                </div>
                <div style={{ fontSize: 13, color: "#374151" }}>
                  <div>Număr: {inv.invoice_number || "-"}</div>
                  <div>Data: {inv.invoice_date || "-"}</div>
                  <div>Furnizor: {inv.contractor || "-"}</div>
                  <div>IDNO: {inv.idno || "-"}</div>
                  <div>Suma: {inv.total_amount != null ? inv.total_amount : "-"}</div>
                  <div>TVA: {inv.vat_amount != null ? inv.vat_amount : "-"}</div>
                  <div>Confidence: {inv.confidence != null ? inv.confidence : "-"}</div>
                </div>

                {inv.server_filename ? (
                  <div style={{ marginTop: 8 }}>
                    <a
                      href={`${API_BASE}/api/image/${encodeURIComponent(inv.server_filename)}`}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: 13, color: "#2563eb", textDecoration: "none" }}
                    >
                      Vezi fișierul
                    </a>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
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
