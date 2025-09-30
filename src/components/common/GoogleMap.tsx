import React from 'react';

interface GoogleMapProps {
  calle?: string;
  numero?: string;
  localidad?: string;
  municipio?: string;
  provincia?: string;
  latitud?: number;
  longitud?: number;
  height?: string;
}

const GoogleMap: React.FC<GoogleMapProps> = ({
  calle,
  numero,
  localidad,
  municipio,
  provincia,
  latitud,
  longitud,
  height = '400px'
}) => {
  const hasCoordinates = latitud && longitud;
  const hasAddress = calle && numero && localidad && municipio && provincia;

  if (!hasCoordinates && !hasAddress) {
    return (
      <div 
        className="d-flex align-items-center justify-content-center bg-light rounded"
        style={{ height }}
      >
        <div className="text-center text-muted">
          <i className="bi bi-geo-alt fs-1 mb-2"></i>
          <p className="mb-0">No hay datos de ubicación disponibles</p>
        </div>
      </div>
    );
  }

  let mapUrl = 'https://maps.google.com/maps?';
  
  if (hasCoordinates) {
    mapUrl += `q=${latitud},${longitud}&output=embed`;
  } else if (hasAddress) {
    const address = `${calle} ${numero}, ${localidad}, ${municipio}, ${provincia}`;
    mapUrl += `q=${encodeURIComponent(address)}&output=embed`;
  }

  return (
    <div style={{ height, width: '100%' }}>
      <iframe
        width="100%"
        height="100%"
        frameBorder="0"
        style={{ border: 0, borderRadius: '8px' }}
        src={mapUrl}
        allowFullScreen
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        title="Mapa de ubicación"
      />
    </div>
  );
};

export default GoogleMap;