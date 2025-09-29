import React, { useState } from 'react';
import GeographicSelectors from './GeographicSelectors';

const GeographicSelectorsExample: React.FC = () => {
  const [provinciaId, setProvinciaId] = useState<number | null>(null);
  const [municipioId, setMunicipioId] = useState<number | null>(null);
  const [localidadId, setLocalidadId] = useState<number | null>(null);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Selectores Geográficos</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Seleccionar Ubicación</h2>
        
        <GeographicSelectors
          provinciaId={provinciaId}
          municipioId={municipioId}
          localidadId={localidadId}
          onProvinciaChange={setProvinciaId}
          onMunicipioChange={setMunicipioId}
          onLocalidadChange={setLocalidadId}
        />

        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <h3 className="font-medium mb-2">Valores seleccionados:</h3>
          <ul className="space-y-1 text-sm">
            <li>Provincia ID: {provinciaId || 'No seleccionada'}</li>
            <li>Municipio ID: {municipioId || 'No seleccionado'}</li>
            <li>Localidad ID: {localidadId || 'No seleccionada'}</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GeographicSelectorsExample;