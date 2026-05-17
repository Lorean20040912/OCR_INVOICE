import React, { useEffect, useMemo, useRef, useState } from "react";

function isPdfFile(name = "") {
  return /\.pdf$/i.test(name);
}

// Încarcă PDF.js din CDN o singură dată (fără npm install)
let pdfjsLibPromise = null;
function ensurePdfJs() {
  if (!pdfjsLibPromise) {
    const libUrl = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.mjs";
    const workerUrl = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.mjs";
    pdfjsLibPromise = import(/* @vite-ignore */ libUrl).then((mod) => {
      const pdfjs = mod?.default || mod;
      if (pdfjs && pdfjs.GlobalWorkerOptions) {
        pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;
      }
      return pdfjs;
    });
  }
  return pdfjsLibPromise;
}

export default function ViewerPane({ src, filename, zoom = 1 }) {
  const canvasRef = useRef(null);
  const [ready, setReady] = useState(false);

  const isPdf = useMemo(() => isPdfFile(filename || src || ""), [filename, src]);

  useEffect(() => {
    let cancelled = false;

    async function renderPdf() {
      setReady(false);
      try {
        const pdfjsLib = await ensurePdfJs();
        if (!pdfjsLib || !isPdf || !src || cancelled) return;

        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");

        const loadingTask = pdfjsLib.getDocument({ url: src, withCredentials: false });
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: zoom || 1 });

        canvas.width = Math.floor(viewport.width);
        canvas.height = Math.floor(viewport.height);

        const renderContext = { canvasContext: ctx, viewport };
        if (cancelled) return;
        await page.render(renderContext).promise;
        if (!cancelled) setReady(true);
      } catch (e) {
        // Dacă nu putem încărca PDF.js sau documentul, afișăm fallback
        setReady(false);
      }
    }

    if (isPdf) {
      renderPdf();
    }

    return () => {
      cancelled = true;
    };
  }, [src, isPdf, zoom]);

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
        <canvas
          ref={canvasRef}
          className="block"
          style={{ display: ready ? "block" : "block" }}
        />
        {!ready && (
          <div className="text-sm text-gray-500 p-3">Se încarcă previzualizarea PDF...</div>
        )}
      </div>
    );
  }

  // Imagine simplă cu zoom prin transform
  return (
    <div className="rounded-md border overflow-auto bg-gray-100" style={{ height: 520 }}>
      <img
        src={src}
        alt={filename || "Factura"}
        style={{ transform: `scale(${zoom || 1})`, transformOrigin: "top left" }}
        className="block"
      />
    </div>
  );
}
