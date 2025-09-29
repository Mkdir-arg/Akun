import React from 'react';
import { FileDown } from 'lucide-react';

interface Quote {
  id: number;
  number: string;
  customer_name: string;
  customer_phone?: string;
  status: string;
  priority: string;
  valid_until: string;
  subtotal: string;
  tax_amount: string;
  total: string;
  notes: string;
}

interface QuoteItem {
  id: number;
  product: number;
  product_name: string;
  product_sku: string;
  description: string;
  quantity: string;
  unit_price: string;
  discount_pct: string;
  tax_rate: string;
  total: string;
  line_number: number;
}

interface SimplePDFGeneratorProps {
  quote: Quote;
  items: QuoteItem[];
}

const SimplePDFGenerator: React.FC<SimplePDFGeneratorProps> = ({ quote, items }) => {
  const generatePDF = () => {
    const currentDate = new Date().toLocaleDateString('es-AR');
    const validUntil = quote.valid_until ? new Date(quote.valid_until).toLocaleDateString('es-AR') : '';
    
    const content = `
PRESUPUESTO - ${quote.number}
================================

AKUN ABERTURAS
Teléfono: 11 44482992
www.akunaberturas.com.ar
akunaberturas@gmail.com

Para: ${quote.customer_name}
Teléfono móvil: ${quote.customer_phone || 'N/A'}
Presupuesto nro.: ${quote.number}
Fecha: ${currentDate}
Obra: ${quote.notes || 'N/A'}

CONDICIONES DE PAGO: 50% seña, 50% contra entrega
VENCIMIENTO: ${validUntil}
OBSERVACIONES: El presente presupuesto incluye flete y colocación
PLAZO ENTREGA: 45 días

PRODUCTOS:
----------
${items.map(item => `
${item.quantity} x ${item.product_name}
${item.description || ''}
Precio unitario: USD ${parseFloat(item.unit_price).toLocaleString('es-AR', { minimumFractionDigits: 2 })}
Total: USD ${parseFloat(item.total).toLocaleString('es-AR', { minimumFractionDigits: 2 })}
`).join('\n')}

TOTALES:
--------
Sub-Total: USD ${parseFloat(quote.subtotal).toLocaleString('es-AR', { minimumFractionDigits: 2 })}
IVA 21.00%: USD ${parseFloat(quote.tax_amount).toLocaleString('es-AR', { minimumFractionDigits: 2 })}
Total: USD ${parseFloat(quote.total).toLocaleString('es-AR', { minimumFractionDigits: 2 })}
    `;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Presupuesto_${quote.number}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={generatePDF}
      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
    >
      <FileDown className="w-4 h-4 mr-2" />
      Descargar TXT
    </button>
  );
};

export default SimplePDFGenerator;