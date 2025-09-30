import React, { useState } from 'react';

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

interface GeographicInputsProps {
  provincia: string;
  municipio: string;
  localidad: string;
  onProvinciaChange: (value: string) => void;
  onMunicipioChange: (value: string) => void;
  onLocalidadChange: (value: string) => void;
  disabled?: boolean;
}

const GeographicInputs: React.FC<GeographicInputsProps> = ({
  provincia,
  municipio,
  localidad,
  onProvinciaChange,
  onMunicipioChange,
  onLocalidadChange,
  disabled = false
}) => {
  const [provincias, setProvincias] = useState<Provincia[]>([]);
  const [municipios, setMunicipios] = useState<Municipio[]>([]);
  const [localidades, setLocalidades] = useState<Localidad[]>([]);
  
  const [showProvincias, setShowProvincias] = useState(false);
  const [showMunicipios, setShowMunicipios] = useState(false);
  const [showLocalidades, setShowLocalidades] = useState(false);

  const loadProvincias = async (search = '') => {
    try {
      const url = search 
        ? `https://z5906h8z-8002.brs.devtunnels.ms/api/provincias/?search=${search}`
        : 'https://z5906h8z-8002.brs.devtunnels.ms/api/provincias/';
      const response = await fetch(url);
      const data = await response.json();
      setProvincias(data);
      setShowProvincias(true);
    } catch (error) {
      console.error('Error loading provincias:', error);
    }
  };

  const loadMunicipios = async (search = '', provinciaId?: number) => {
    try {
      let url = 'https://z5906h8z-8002.brs.devtunnels.ms/api/municipios/';
      const params = [];
      if (search) params.push(`search=${search}`);
      if (provinciaId) params.push(`provincia_id=${provinciaId}`);
      if (params.length > 0) url += `?${params.join('&')}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setMunicipios(data);
      setShowMunicipios(true);
    } catch (error) {
      console.error('Error loading municipios:', error);
    }
  };

  const loadLocalidades = async (search = '', municipioId?: number) => {
    try {
      let url = 'https://z5906h8z-8002.brs.devtunnels.ms/api/localidades/';
      const params = [];
      if (search) params.push(`search=${search}`);
      if (municipioId) params.push(`municipio_id=${municipioId}`);
      if (params.length > 0) url += `?${params.join('&')}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setLocalidades(data);
      setShowLocalidades(true);
    } catch (error) {
      console.error('Error loading localidades:', error);
    }
  };

  const handleProvinciaClick = () => {
    loadProvincias(provincia);
  };

  const handleProvinciaChange = (value: string) => {
    onProvinciaChange(value);
    if (value.length > 0) {
      setTimeout(() => loadProvincias(value), 300);
    }
  };

  const handleProvinciaSelect = (p: Provincia) => {
    console.log('Selecting provincia:', p.nombre);
    onProvinciaChange(p.nombre);
    setShowProvincias(false);
    setShowMunicipios(false);
    setShowLocalidades(false);
    onMunicipioChange('');
    onLocalidadChange('');
    setMunicipios([]);
    setLocalidades([]);
  };

  const handleMunicipioClick = () => {
    const selectedProvincia = provincias.find(p => p.nombre === provincia);
    loadMunicipios(municipio, selectedProvincia?.id);
  };

  const handleMunicipioChange = (value: string) => {
    onMunicipioChange(value);
    if (value.length > 0) {
      const selectedProvincia = provincias.find(p => p.nombre === provincia);
      setTimeout(() => loadMunicipios(value, selectedProvincia?.id), 300);
    }
  };

  const handleMunicipioSelect = (m: Municipio) => {
    onMunicipioChange(m.nombre);
    setShowMunicipios(false);
    setShowLocalidades(false);
    onLocalidadChange('');
    setLocalidades([]);
  };

  const handleLocalidadClick = () => {
    const selectedMunicipio = municipios.find(m => m.nombre === municipio);
    loadLocalidades(localidad, selectedMunicipio?.id);
  };

  const handleLocalidadChange = (value: string) => {
    onLocalidadChange(value);
    if (value.length > 0) {
      const selectedMunicipio = municipios.find(m => m.nombre === municipio);
      setTimeout(() => loadLocalidades(value, selectedMunicipio?.id), 300);
    }
  };

  const handleLocalidadSelect = (l: Localidad) => {
    onLocalidadChange(l.nombre);
    setShowLocalidades(false);
  };

  const filteredProvincias = provincias.filter(p => 
    p.nombre.toLowerCase().includes(provincia.toLowerCase())
  );

  const filteredMunicipios = municipios.filter(m => 
    m.nombre.toLowerCase().includes(municipio.toLowerCase())
  );

  const filteredLocalidades = localidades.filter(l => 
    l.nombre.toLowerCase().includes(localidad.toLowerCase())
  );

  return (
    <>
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Provincia
        </label>
        <input
          type="text"
          value={provincia}
          onChange={(e) => handleProvinciaChange(e.target.value)}
          onClick={handleProvinciaClick}
          onBlur={() => setTimeout(() => setShowProvincias(false), 200)}
          disabled={disabled}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Escribir provincia..."
        />
        {showProvincias && filteredProvincias.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
            {filteredProvincias.map((p) => (
              <div
                key={p.id}
                className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => handleProvinciaSelect(p)}
              >
                {p.nombre}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Municipio
        </label>
        <input
          type="text"
          value={municipio}
          onChange={(e) => handleMunicipioChange(e.target.value)}
          onClick={handleMunicipioClick}
          onBlur={() => setTimeout(() => setShowMunicipios(false), 200)}
          disabled={disabled}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Escribir municipio..."
        />
        {showMunicipios && filteredMunicipios.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
            {filteredMunicipios.map((m) => (
              <div
                key={m.id}
                className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => handleMunicipioSelect(m)}
              >
                {m.nombre}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Localidad
        </label>
        <input
          type="text"
          value={localidad}
          onChange={(e) => handleLocalidadChange(e.target.value)}
          onClick={handleLocalidadClick}
          onBlur={() => setTimeout(() => setShowLocalidades(false), 200)}
          disabled={disabled}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Escribir localidad..."
        />
        {showLocalidades && filteredLocalidades.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
            {filteredLocalidades.map((l) => (
              <div
                key={l.id}
                className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => handleLocalidadSelect(l)}
              >
                {l.nombre}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
};

export default GeographicInputs;