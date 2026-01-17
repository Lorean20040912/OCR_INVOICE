import React from 'react';
import { CheckCircle, XCircle, Download, ChevronLeft, ChevronRight } from 'lucide-react';

function InvoiceForm({
  invoice,
  onUpdate,
  onApprove,
  onReject,
  onExport,
  currentIndex,
  totalInvoices,
  onNavigate,
  exportFormat
}) {
  const isProcessed = invoice.status === 'approved' || invoice.status === 'rejected';

  const getStatusBadge = () => {
    if (invoice.status === 'approved') {
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
          <CheckCircle size={16} />
          Aprobată
        </span>
      );
    }
    if (invoice.status === 'rejected') {
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
          <XCircle size={16} />
          Respinsă
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
        În așteptare
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header with Navigation */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Date Factură
          </h2>
          {getStatusBadge()}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate(currentIndex - 1)}
            disabled={currentIndex === 0}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft size={20} />
          </button>

          <span className="text-sm font-medium text-gray-600 min-w-[80px] text-center">
            {currentIndex + 1} / {totalInvoices}
          </span>

          <button
            onClick={() => onNavigate(currentIndex + 1)}
            disabled={currentIndex === totalInvoices - 1}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Form Fields */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Număr Factură *
          </label>
          <input
            type="text"
            value={invoice.invoice_number || ''}
            onChange={(e) => onUpdate('invoice_number', e.target.value)}
            disabled={isProcessed}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Ex: INV-2024-001"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data Facturii *
            </label>
            <input
              type="date"
              value={invoice.invoice_date || ''}
              onChange={(e) => onUpdate('invoice_date', e.target.value)}
              disabled={isProcessed}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data Livrării
            </label>
            <input
              type="date"
              value={invoice.delivery_date || ''}
              onChange={(e) => onUpdate('delivery_date', e.target.value)}
              disabled={isProcessed}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contragent (Nume Companie) *
          </label>
          <input
            type="text"
            value={invoice.contractor || ''}
            onChange={(e) => onUpdate('contractor', e.target.value)}
            disabled={isProcessed}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="Ex: SRL COMPANIA EXEMPLU"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            IDNO (Cod Fiscal - 13 cifre) *
          </label>
          <input
            type="text"
            value={invoice.idno || ''}
            onChange={(e) => onUpdate('idno', e.target.value)}
            disabled={isProcessed}
            maxLength={13}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="1234567890123"
          />
          {invoice.idno && invoice.idno.length !== 13 && (
            <p className="text-sm text-red-600 mt-1">IDNO trebuie să aibă 13 cifre</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Valoare Totală (MDL) *
            </label>
            <input
              type="number"
              step="0.01"
              value={invoice.total_amount || ''}
              onChange={(e) => onUpdate('total_amount', e.target.value)}
              disabled={isProcessed}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              placeholder="0.00"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              TVA (MDL)
            </label>
            <input
              type="number"
              step="0.01"
              value={invoice.vat_amount || ''}
              onChange={(e) => onUpdate('vat_amount', e.target.value)}
              disabled={isProcessed}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              placeholder="0.00"
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        {!isProcessed && (
          <>
            <button
              onClick={onApprove}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
            >
              <CheckCircle size={20} />
              Aprobă și Trimite în 1C
            </button>

            <button
              onClick={onReject}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
            >
              <XCircle size={20} />
              Respinge Factura
            </button>
          </>
        )}

        <button
          onClick={onExport}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
        >
          <Download size={20} />
          Descarcă Export ({exportFormat.toUpperCase()})
        </button>
      </div>

      {/* Validation Info */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800 font-medium mb-2">
          ℹ️ Informații importante:
        </p>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Câmpurile marcate cu * sunt obligatorii</li>
          <li>• IDNO trebuie să conțină exact 13 cifre</li>
          <li>• Datele pot fi editate înainte de aprobare</li>
          <li>• Exportul manual este disponibil oricând</li>
        </ul>
      </div>
    </div>
  );
}

export default InvoiceForm;
