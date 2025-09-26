import React, { useState, useEffect } from 'react';
import { X, DollarSign } from 'lucide-react';

interface PriceList {
  id: number;
  name: string;
  currency: string;
  is_default: boolean;
}

interface PriceListModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PriceListModal: React.FC<PriceListModalProps> = ({ isOpen, onClose }) => {
  const [priceLists, setPriceLists] = useState<PriceList[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchPriceLists();
    }
  }, [isOpen]);

  const fetchPriceLists = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/price-lists/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setPriceLists(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching price lists:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h3 className="text-lg font-medium text-gray-900">Listas de Precios</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {priceLists.map((priceList) => (
                <div key={priceList.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center">
                    <DollarSign className="w-5 h-5 text-green-600 mr-3" />
                    <div>
                      <h4 className="font-medium text-gray-900">{priceList.name}</h4>
                      <p className="text-sm text-gray-500">Moneda: {priceList.currency}</p>
                    </div>
                    {priceList.is_default && (
                      <span className="ml-3 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                        Por defecto
                      </span>
                    )}
                  </div>
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Ver Precios
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 p-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cerrar
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Nueva Lista
          </button>
        </div>
      </div>
    </div>
  );
};

export default PriceListModal;