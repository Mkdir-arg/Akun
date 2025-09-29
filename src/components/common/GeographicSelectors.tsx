import React, { useState, useEffect } from 'react';

interface Provincia {
  id: number;
  nombre: string;
}

interface Municipio {
  id: number;
  nombre: string;
  provincia_id: number;
}

interface Localidad {
  id: number;
  nombre: string;
  municipio_id: number;
}

interface GeographicSelectorsProps {
  provinciaId?: number | null;
  municipioId?: number | null;
  localidadId?: number | null;
  onProvinciaChange: (provinciaId: number | null) => void;
  onMunicipioChange: (municipioId: number | null) => void;
  onLocalidadChange: (localidadId: number | null) => void;
  disabled?: boolean;
}

const GeographicSelectors: React.FC<GeographicSelectorsProps> = ({
  provinciaId,
  municipioId,
  localidadId,
  onProvinciaChange,
  onMunicipioChange,
  onLocalidadChange,
  disabled = false
}) => {
  const [provincias, setProvincias] = useState<Provincia[]>([]);
  const [municipios, setMunicipios] = useState<Municipio[]>([]);
  const [localidades, setLocalidades] = useState<Localidad[]>([]);
  
  const [provinciaSearch, setProvinciaSearch] = useState('');
  const [municipioSearch, setMunicipioSearch] = useState('');
  const [localidadSearch, setLocalidadSearch] = useState('');
  
  const [loadingProvincias, setLoadingProvincias] = useState(false);
  const [loadingMunicipios, setLoadingMunicipios] = useState(false);
  const [loadingLocalidades, setLoadingLocalidades] = useState(false);

  // Cargar provincias
  useEffect(() => {
    const loadProvincias = async () => {
      setLoadingProvincias(true);
      try {
        const params = new URLSearchParams();
        if (provinciaSearch) params.append('search', provinciaSearch);
        
        const response = await fetch(`http://localhost:8002/api/provincias/?${params}`);
        const data = await response.json();
        setProvincias(data);
      } catch (error) {
        console.error('Error loading provincias:', error);
      } finally {
        setLoadingProvincias(false);
      }
    };

    const timeoutId = setTimeout(loadProvincias, 300);
    return () => clearTimeout(timeoutId);
  }, [provinciaSearch]);

  // Cargar municipios cuando cambia la provincia
  useEffect(() => {
    if (!provinciaId) {
      setMunicipios([]);
      return;
    }

    const loadMunicipios = async () => {
      setLoadingMunicipios(true);
      try {
        const params = new URLSearchParams();
        params.append('provincia_id', provinciaId.toString());
        if (municipioSearch) params.append('search', municipioSearch);
        
        const response = await fetch(`http://localhost:8002/api/municipios/?${params}`);
        const data = await response.json();
        setMunicipios(data);
      } catch (error) {
        console.error('Error loading municipios:', error);
      } finally {
        setLoadingMunicipios(false);
      }
    };

    const timeoutId = setTimeout(loadMunicipios, 300);
    return () => clearTimeout(timeoutId);
  }, [provinciaId, municipioSearch]);

  // Cargar localidades cuando cambia el municipio
  useEffect(() => {
    if (!municipioId) {
      setLocalidades([]);
      return;
    }

    const loadLocalidades = async () => {
      setLoadingLocalidades(true);
      try {
        const params = new URLSearchParams();
        params.append('municipio_id', municipioId.toString());
        if (localidadSearch) params.append('search', localidadSearch);
        
        const response = await fetch(`http://localhost:8002/api/localidades/?${params}`);
        const data = await response.json();
        setLocalidades(data);
      } catch (error) {
        console.error('Error loading localidades:', error);
      } finally {
        setLoadingLocalidades(false);
      }
    };

    const timeoutId = setTimeout(loadLocalidades, 300);
    return () => clearTimeout(timeoutId);
  }, [municipioId, localidadSearch]);

  const handleProvinciaChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value ? parseInt(e.target.value) : null;
    onProvinciaChange(value);
    onMunicipioChange(null);
    onLocalidadChange(null);
    setMunicipioSearch('');
    setLocalidadSearch('');
  };

  const handleMunicipioChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value ? parseInt(e.target.value) : null;
    onMunicipioChange(value);
    onLocalidadChange(null);
    setLocalidadSearch('');
  };

  const handleLocalidadChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value ? parseInt(e.target.value) : null;
    onLocalidadChange(value);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Selector de Provincia */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Provincia
        </label>
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar provincia..."
            value={provinciaSearch}
            onChange={(e) => setProvinciaSearch(e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          {loadingProvincias && (
            <div className="absolute right-3 top-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>
        <select
          value={provinciaId || ''}
          onChange={handleProvinciaChange}
          disabled={disabled}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        >
          <option value="">Seleccionar provincia</option>
          {provincias.map((provincia) => (
            <option key={provincia.id} value={provincia.id}>
              {provincia.nombre}
            </option>
          ))}
        </select>
      </div>

      {/* Selector de Municipio */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Municipio
        </label>
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar municipio..."
            value={municipioSearch}
            onChange={(e) => setMunicipioSearch(e.target.value)}
            disabled={disabled || !provinciaId}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          {loadingMunicipios && (
            <div className="absolute right-3 top-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>
        <select
          value={municipioId || ''}
          onChange={handleMunicipioChange}
          disabled={disabled || !provinciaId}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        >
          <option value="">Seleccionar municipio</option>
          {municipios.map((municipio) => (
            <option key={municipio.id} value={municipio.id}>
              {municipio.nombre}
            </option>
          ))}
        </select>
      </div>

      {/* Selector de Localidad */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Localidad
        </label>
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar localidad..."
            value={localidadSearch}
            onChange={(e) => setLocalidadSearch(e.target.value)}
            disabled={disabled || !municipioId}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          {loadingLocalidades && (
            <div className="absolute right-3 top-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>
        <select
          value={localidadId || ''}
          onChange={handleLocalidadChange}
          disabled={disabled || !municipioId}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        >
          <option value="">Seleccionar localidad</option>
          {localidades.map((localidad) => (
            <option key={localidad.id} value={localidad.id}>
              {localidad.nombre}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default GeographicSelectors;