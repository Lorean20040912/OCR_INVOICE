import React, { useMemo, useRef, useState } from "react";

const API_BASE = "http://localhost:5000";

function App() {
  const fileInputRef = useRef(null);
  const [invoices, setInvoices] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const current = useMemo(() => invoices[currentIndex] || null, [invoices, currentIndex]);

  const chooseFiles = () => fileInputRef.current?.click();

  const onFilesSelected = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    setIsUploading(true);
    setMsg("");

    try {
      const form = new FormData();
      for (const f of files) form.append("files", f);

      const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Upload eșuat (${res.status})`);
      }
      const data = await res.json();
      const newInvoices = (data && data.invoices) || [];

      const normalized = newInvoices.map((inv) => {
        const filePath = inv.file_path || "";
        const serverFile = filePath.split(/[/\\\\]/).pop() || "";
        return { ...inv, server_filename: serverFile };
      });

      setInvoices((prev) => {
        const merged = [...prev, ...normalized];
        if (prev.length === 0 && merged.length > 0) setCurrentIndex(0);
        return merged;
      });
    } catch (err) {
      console.error(err);
      setMsg(err.message || "Upload eșuat");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const prev = () => {
    if (!invoices.length) return;
    setCurrentIndex((i) => (i - 1 + invoices.length) % invoices.length);
  };
  const next = () => {
    if (!invoices.length) return;
    setCurrentIndex((i) => (i + 1) % invoices.length);
  };

  const reprocessCurrent = async () => {
    if (!current) return;
    setBusy(true);
    setMsg("");
    try {
      const payload = {
        file_path: current.file_path || undefined,
        server_filename: current.server_filename || undefined,
        unique_id: current.unique_id || undefined,
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
      setInvoices((prev) => prev.map((it, idx) => (idx === currentIndex ? { ...it, ...upd } : it)));
      setMsg("OCR reprocesat.");
    } catch (e) {
      console.error(e);
      setMsg(e.message || "Eroare la reprocesare OCR");
    } finally {
      setBusy(false);
    }
  };

  const sendTo1C = async () => {
    if (!current) return;
    setBusy(true);
    setMsg("");
    try {
      const res = await fetch(`${API_BASE}/api/send-to-1c`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...current,
          use_api: true,
          export_format: "json",
        }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok || !body.success) {
        throw new Error(body.error || `Trimitere eșuată (${res.status})`);
      }
      setMsg(body.message || "Trimis cu succes");
    } catch (e) {
      console.error(e);
      setMsg(e.message || "Eroare trimitere către 1C");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Procesare Facturi OCR + 1C</h1>
          <div className="flex items-center gap-2">
            <button
              onClick={chooseFiles}
              disabled={isUploading}
              className={`px-3 py-1.5 rounded-md text-white text-sm ${
                isUploading ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isUploading ? "Se încarcă..." : "Adaugă fișiere"}
            </button>
            <input
              ref={fileInputRef}
              onChange={onFilesSelected}
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff"
              className="hidden"
            />
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {msg ? (
          <div className="mb-4 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm">{msg}</div>
        ) : null}

        {!invoices.length ? (
          <div className="bg-white border rounded-xl p-8 text-center text-gray-500">
            Încarcă una sau mai multe facturi pentru a începe.
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Factură {currentIndex + 1} din {invoices.length}
              </div>
              <div className="flex gap-2">
                <button onClick={prev} className="px-3 py-1.5 rounded-md border bg-white hover:bg-gray-50 text-sm">
                  ◀ Anterioara
                </button>
                <button onClick={next} className="px-3 py-1.5 rounded-md border bg-white hover:bg-gray-50 text-sm">
                  Următoarea ▶
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <div className="bg-white border rounded-xl p-4">
                <div className="text-sm font-medium mb-3">Previzualizare</div>
                {current?.server_filename ? (
                  <div className="rounded-lg border overflow-hidden">
                    <img
                      src={`${API_BASE}/api/image/${encodeURIComponent(current.server_filename)}`}
                      alt={current.original_filename || "Factura"}
                      className="w-full h-[520px] object-contain bg-gray-100"
                    />
                  </div>
                ) : (
                  <div className="h-[520px] rounded-lg border bg-gray-100 flex items-center justify-center text-gray-400">
                    Fără imagine disponibilă
                  </div>
                )}
              </div>

              <div className="bg-white border rounded-xl p-4">
                <div className="text-sm font-medium mb-3">Detalii factură</div>
                <div className="text-sm text-gray-700 space-y-2">
                  <div><span className="text-gray-500">Fișier:</span> {current.original_filename || "-"}</div>
                  <div><span className="text-gray-500">Număr:</span> {current.invoice_number || "-"}</div>
                  <div><span className="text-gray-500">Data:</span> {current.invoice_date || "-"}</div>
                  <div><span className="text-gray-500">Furnizor:</span> {current.contractor || "-"}</div>
                  <div><span className="text-gray-500">IDNO:</span> {current.idno || "-"}</div>
                  <div><span className="text-gray-500">Suma:</span> {current.total_amount != null ? current.total_amount : "-"}</div>
                  <div><span className="text-gray-500">TVA:</span> {current.vat_amount != null ? current.vat_amount : "-"}</div>
                  <div><span className="text-gray-500">Confidence:</span> {current.confidence != null ? current.confidence : "-"}</div>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    onClick={reprocessCurrent}
                    disabled={busy}
                    className={`px-3 py-1.5 rounded-md border text-sm ${
                      busy ? "bg-gray-100 text-gray-400 cursor-not-allowed" : "bg-white hover:bg-gray-50 text-gray-700"
                    }`}
                  >
                    Reprocesează OCR
                  </button>
                  <a
                    href={
                      current?.server_filename
                        ? `${API_BASE}/api/image/${encodeURIComponent(current.server_filename)}`
                        : undefined
                    }
                    target="_blank"
                    rel="noreferrer"
                    className={`px-3 py-1.5 rounded-md border text-sm ${
                      current?.server_filename ? "bg-white hover:bg-gray-50 text-gray-700" : "bg-gray-100 text-gray-400 pointer-events-none"
                    }`}
                  >
                    Vezi fișier
                  </a>
                  <button
                    onClick={sendTo1C}
                    disabled={busy}
                    className={`px-3 py-1.5 rounded-md text-sm text-white ${
                      busy ? "bg-emerald-400 cursor-not-allowed" : "bg-emerald-600 hover:bg-emerald-700"
                    }`}
                  >
                    Trimite la 1C
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
