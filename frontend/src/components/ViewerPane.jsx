import React, { useEffect, useMemo, useRef, useState } from "react";

function isPdfFile(name = "") {
  return /\.pdf$/i.test(name);
}

// Încarcă PDF.js din CDN o singură dată (fără npm install)
let pdfjsLibPromise = null;
function ensurePdfJs() {
  if (!pdfjsLibPromise) {
    const libUrl = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.mjs";
    pdfjsLibPromise = import(/* @vite-ignore */ libUrl).then((mod) => mod?.default || mod);
  }
  return pdfjsLibPromise;
}

export default function ViewerPane({ src, filename, zoom = 1 }) {
  const canvasRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const isPdf = useMemo(() => isPdfFile(filename || src || ""), [filename, src]);

  useEffect(() => {
    let cancelled = false;

    async function renderPdf() {
      setReady(false);
      setErr(null);
      setLoading(true);
      try {
        const pdfjsLib = await ensurePdfJs();
        if (!pdfjsLib || !isPdf || !src || cancelled) return;

        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("Nu s-a putut inițializa canvasContext.");

        // Dezactivez worker-ul pentru a evita probleme CORS/module worker în dev/proxy
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

        const loadingTask = pdfjsLib.getDocument({
          url: src,
          withCredentials: false,
          disableWorker: true,
          // @ts-ignore - pdfjs-dist acceptă signal în implementarea curentă
          signal: controller.signal,
        });

        const pdf = await loadingTask.promise;
        if (cancelled) return;

        const page = await pdf.getPage(1);

        // Scale după zoom și devicePixelRatio pentru claritate
        const dpr = window.devicePixelRatio || 1;
        const scale = Math.max(0.5, Math.min(zoom || 1, 2));
        const viewport = page.getViewport({ scale: scale * dpr });

        canvas.width = Math.floor(viewport.width);
        canvas.height = Math.floor(viewport.height);
        // Afișează în CSS la dimensiunea "logică" (fără dpr)
        canvas.style.width = Math.floor(viewport.width / dpr) + "px";
        canvas.style.height = Math.floor(viewport.height / dpr) + "px";

        const renderContext = { canvasContext: ctx, viewport };
        if (cancelled) return;

        await page.render(renderContext).promise;
        if (!cancelled) {
          setReady(true);
          setErr(null);
        }

        clearTimeout(timeoutId);
      } catch (e) {
        if (!cancelled) {
          setErr("PDF nu s-a putut încărca. Încearcă să descarci fișierul sau verifică accesul.");
          setReady(false);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    if (isPdf && src) {
      renderPdf();
    }

    return () => {
      cancelled = true;
    };
  }, [src, isPdf, zoom]);

  // Pentru imagini folosim <img> cu feedback de stare
  const [imgLoaded, setImgLoaded] = useState(false);
  const [imgErr, setImgErr] = useState(null);
  useEffect(() => {
    setImgLoaded(false);
    setImgErr(null);
  }, [src]);

  if (!src) {
    return (
      <div className="h-[520px] rounded-md border bg-gray-100 flex items-center justify-center text-gray-400">
        Fără previzualizare
      </div>
    );
  }

  if (isPdf) {
    // Randăm doar prima pagină pe canvas, fără UI sau butoane ale viewer-ului
    return (
      <div className="rounded-md border overflow-auto bg-gray-100" style={{ height: 520 }}>
        <canvas ref={canvasRef} className="block max-w-full h-auto" />
        {loading && (
          <div className="text-sm text-gray-600 p-3">Se încarcă previzualizarea PDF...</div>
        )}
        {err && (
          <div className="text-sm text-red-600 p-3">
            {err}
          </div>
        )}
      </div>
    );
  }

  // Imagine simplă cu zoom prin transform + feedback la încărcare/eroare
  return (
    <div className="rounded-md border overflow-auto bg-gray-100" style={{ height: 520 }}>
      {!imgLoaded && !imgErr && (
        <div className="text-sm text-gray-600 p-3">Se încarcă imaginea...</div>
      )}
      {imgErr && (
        <div className="text-sm text-red-600 p-3">
          Nu s-a putut încărca imaginea. Verifică sursa sau încearcă din nou.
        </div>
      )}
      <img
        src={src}
        alt={filename || "Factura"}
        decoding="async"
        loading="eager"
        onLoad={() => setImgLoaded(true)}
        onError={() => setImgErr(true)}
        style={{
          transform: `scale(${zoom || 1})`,
          transformOrigin: "top left",
          maxWidth: "100%",
          height: "auto",
          display: imgLoaded ? "block" : "none",
        }}
        className="block"
      />
    </div>
  );
}
