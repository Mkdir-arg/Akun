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

interface PDFGeneratorProps {
  quote: Quote;
  items: QuoteItem[];
}

const PDFGenerator: React.FC<PDFGeneratorProps> = ({ quote, items }) => {
  const generatePDF = () => {
    console.log('Botón clickeado');
    alert('Función de PDF ejecutada');
    
    const currentDate = new Date().toLocaleDateString('es-AR');
    const validUntil = quote.valid_until ? new Date(quote.valid_until).toLocaleDateString('es-AR') : '';
    
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Presupuesto ${quote.number}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .header { background: #e8eaf6; padding: 20px; margin-bottom: 20px; }
    .logo { font-size: 24px; font-weight: bold; color: #1565c0; }
    .info { margin: 10px 0; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #90caf9; }
    .totals { text-align: right; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">AKUN ABERTURAS</div>
    <div>Teléfono: 11 44482992</div>
    <div>www.akunaberturas.com.ar</div>
  </div>
  
  <div class="info">
    <strong>Para:</strong> ${quote.customer_name}<br>
    <strong>Presupuesto nro.:</strong> ${quote.number}<br>
    <strong>Fecha:</strong> ${currentDate}<br>
    <strong>Vencimiento:</strong> ${validUntil}
  </div>
  
  <table>
    <thead>
      <tr>
        <th>Cantidad</th>
        <th>Producto</th>
        <th>Precio Unitario</th>
        <th>Total</th>
      </tr>
    </thead>
    <tbody>
      ${items.map(item => `
        <tr>
          <td>${item.quantity}</td>
          <td>${item.product_name || item.description}</td>
          <td>USD ${parseFloat(item.unit_price).toFixed(2)}</td>
          <td>USD ${parseFloat(item.total).toFixed(2)}</td>
        </tr>
      `).join('')}
    </tbody>
  </table>
  
  <div class="totals">
    <div>Subtotal: USD ${parseFloat(quote.subtotal).toFixed(2)}</div>
    <div>IVA: USD ${parseFloat(quote.tax_amount).toFixed(2)}</div>
    <div><strong>Total: USD ${parseFloat(quote.total).toFixed(2)}</strong></div>
  </div>
  
  <script>
    window.print();
  </script>
</body>
</html>`;

    const newWindow = window.open();
    if (newWindow) {
      newWindow.document.write(htmlContent);
      newWindow.document.close();
    }
  };

  return (
    <button
      onClick={generatePDF}
      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
    >
      <FileDown className="w-4 h-4 mr-2" />
      Generar PDF
    </button>
  );
};

export default PDFGenerator;