import React, { useState } from 'react';
import { X, Upload, Download, FileText } from 'lucide-react';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ImportModal: React.FC<ImportModalProps> = ({ isOpen, onClose }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleImport = async () => {
    if (!file) return;

    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simular importación (implementar endpoint real)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      alert('Productos importados exitosamente');
      onClose();
    } catch (error) {
      console.error('Error importing products:', error);
      alert('Error al importar productos');
    } finally {
      setImporting(false);
    }
  };

  const downloadTemplate = () => {
    // Crear CSV template
    const csvContent = `SKU,Nombre,Categoría,Material,Tipo Apertura,Precio Base,Precio por m²,Activo
VEN-001,Ventana Ejemplo,Ventanas,ALUMINIO,CORREDIZA,0,45000,true
PTA-001,Puerta Ejemplo,Puertas,PVC,BATIENTE,85000,0,true`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plantilla_productos.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h3 className="text-lg font-medium text-gray-900">Importar Productos</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <button
              onClick={downloadTemplate}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              Descargar Plantilla CSV
            </button>
            <p className="text-sm text-gray-500 mt-2">
              Descarga la plantilla para ver el formato requerido
            </p>
          </div>

          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex items-center justify-center">
                <FileText className="w-8 h-8 text-blue-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Arrastra tu archivo CSV aquí
                </p>
                <p className="text-gray-500 mb-4">o</p>
                <label className="cursor-pointer">
                  <span className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                    Seleccionar archivo
                  </span>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
            )}
          </div>

          {file && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                <strong>Importante:</strong> La importación creará nuevos productos o actualizará los existentes basándose en el SKU.
              </p>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 p-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            disabled={importing}
          >
            Cancelar
          </button>
          <button
            onClick={handleImport}
            disabled={!file || importing}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {importing ? 'Importando...' : 'Importar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImportModal;