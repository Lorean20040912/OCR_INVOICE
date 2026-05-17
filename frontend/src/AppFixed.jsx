import React, { useRef, useState } from "react";

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

      const normalized = newInvoices.map((inv) => {
        const filePath = inv.file_path || "";
        const serverFile = filePath.split(/[/\\\\]/).pop() || "";
        return { ...inv, server_filename: serverFile, reprocessing: false };
      });

      setInvoices((prev) => [...prev, ...normalized]);
    } catch (err) {
      console.error(err);
      setError(err.message || "Upload eșuat");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const reprocess = async (inv, index) => {
    try {
      setInvoices((prev) =>
        prev.map((it, i) => (i === index ? { ...it, reprocessing: true } : it))
      );

      const payload = {
        file_path: inv.file_path || undefined,
        server_filename: inv.server_filename || undefined,
        unique_id: inv.unique_id || undefined,
      };

      const res = await fetch(`${API_BASE}/api/reprocess`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const body = await res.json().catch(() => ({}));
      if (!res.ok || !body.success) {
        throw new Error(body.error || `Reprocesare eșuată (${res.status})`);
      }

      const upd = body.invoice || {};
      setInvoices((prev) =>
        prev.map((it, i) => (i === index ? { ...it, ...upd, reprocessing: false } : it))
      );
    } catch (err) {
      console.error(err);
      setInvoices((prev) =>
        prev.map((it, i) =>
          i === index ? { ...it, reprocessing: false, ocr_error: err.message || "Eroare OCR" } : it
        )
      );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold tracking-tight">
            Procesare Facturi OCR + 1C
          </h1>
          <span className="text-xs text-gray-500">Motor OCR: Azure</span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-lg font-medium">Încarcă facturi</h2>
              <p className="text-sm text-gray-500">
                Poți adăuga fișiere oricând, fără să reîncarci pagina.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={onAddMoreClick}
                disabled={isUploading}
                className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-white transition ${
                  isUploading
                    ? "bg-blue-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {isUploading ? (
                  <>
                    <svg
                      className="animate-spin h-4 w-4 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                      />
                    </svg>
                    Se încarcă...
                  </>
                ) : (
                  <>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-4 w-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 5 17 10" />
                      <line x1="12" y1="5" x2="12" y2="15" />
                    </svg>
                    Adaugă facturi
                  </>
                )}
              </button>
              <input
                type="file"
                multiple
                accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff"
                ref={fileInputRef}
                onChange={onFilesSelected}
                className="hidden"
              />
            </div>
          </div>

          {error ? (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}
        </div>

        <div className="mt-6">
          <h3 className="text-base font-medium mb-3">Facturi procesate</h3>
          {invoices.length === 0 ? (
            <div className="text-sm text-gray-500">Încă nu ai încărcat nicio factură.</div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {invoices.map((inv, idx) => {
                const ocrFailed =
                  !inv.invoice_number &&
                  !inv.invoice_date &&
                  !inv.contractor &&
                  !inv.idno &&
                  inv.confidence === 0;

                return (
                  <div
                    key={inv.unique_id || inv.file_path || idx}
                    className="bg-white border rounded-xl shadow-sm p-4 flex flex-col"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-semibold">
                          {inv.original_filename || inv.invoice_number || "Factura"}
                        </div>
                        {ocrFailed ? (
                          <div className="mt-1 inline-flex items-center gap-1 rounded-full bg-yellow-100 text-yellow-800 px-2 py-0.5 text-xs">
                            <span>OCR neconcludent</span>
                          </div>
                        ) : null}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => reprocess(inv, idx)}
                          disabled={inv.reprocessing}
                          className={`text-xs inline-flex items-center gap-1 rounded-md border px-2.5 py-1.5 transition ${
                            inv.reprocessing
                              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                              : "bg-white hover:bg-gray-50 text-gray-700"
                          }`}
                          title="Reprocesează OCR pentru acest fișier"
                        >
                          {inv.reprocessing ? (
                            <>
                              <svg
                                className="animate-spin h-3.5 w-3.5 text-gray-400"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                              >
                                <circle
                                  className="opacity-25"
                                  cx="12"
                                  cy="12"
                                  r="10"
                                  stroke="currentColor"
                                  strokeWidth="4"
                                />
                                <path
                                  className="opacity-75"
                                  fill="currentColor"
                                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                                />
                              </svg>
                              OCR...
                            </>
                          ) : (
                            <>
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-3.5 w-3.5"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                              >
                                <polyline points="1 4 1 10 7 10" />
                                <path d="M3.51 15a9 9 0 1 0 .49-5.27L1 10" />
                              </svg>
                              Reprocesează OCR
                            </>
                          )}
                        </button>

                        {inv.server_filename ? (
                          <a
                            href={`${API_BASE}/api/image/${encodeURIComponent(inv.server_filename)}`}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs inline-flex items-center gap-1 rounded-md border px-2.5 py-1.5 bg-white hover:bg-gray-50 text-gray-700 transition"
                          >
                            Vezi fișier
                          </a>
                        ) : null}
                      </div>
                    </div>

                    <div className="mt-3 text-sm text-gray-700 space-y-1">
                      <div><span className="text-gray-500">Număr:</span> {inv.invoice_number || "-"}</div>
                      <div><span className="text-gray-500">Data:</span> {inv.invoice_date || "-"}</div>
                      <div><span className="text-gray-500">Furnizor:</span> {inv.contractor || "-"}</div>
                      <div><span className="text-gray-500">IDNO:</span> {inv.idno || "-"}</div>
                      <div><span className="text-gray-500">Suma:</span> {inv.total_amount != null ? inv.total_amount : "-"}</div>
                      <div><span className="text-gray-500">TVA:</span> {inv.vat_amount != null ? inv.vat_amount : "-"}</div>
                      <div><span className="text-gray-500">Confidence:</span> {inv.confidence != null ? inv.confidence : "-"}</div>
                    </div>

                    {inv.ocr_error ? (
                      <div className="mt-3 rounded-md border border-yellow-200 bg-yellow-50 text-yellow-800 text-xs p-2">
                        {inv.ocr_error}
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
