import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useApp } from '../context/AppContext';
import { Layers, Eye, RefreshCw, AlertTriangle, Compass } from 'lucide-react';
import type { FeatureCollection, Feature } from 'geojson';
import type { Incident, Resource, Shelter, Route, RoadSegment } from '../types';

interface GisMapProps {
  onSelectIncident?: (incident: Incident) => void;
  onSelectResource?: (resource: Resource) => void;
  onSelectShelter?: (shelter: Shelter) => void;
  height?: string;
}

export const GisMap: React.FC<GisMapProps> = ({
  onSelectIncident,
  onSelectResource,
  onSelectShelter,
  height = '500px'
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  const { incidents, resources, shelters, roadSegments, routes } = useApp();

  const [showIncidents, setShowIncidents] = useState(true);
  const [showResources, setShowResources] = useState(true);
  const [showShelters, setShowShelters] = useState(true);
  const [showRoads, setShowRoads] = useState(true);
  const [showRoutes, setShowRoutes] = useState(true);

  const markersRef = useRef<maplibregl.Marker[]>([]);

  // Initialize MapLibre
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm-tiles': {
            type: 'raster',
            tiles: [
              'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
              'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors, CartoDB'
          }
        },
        layers: [
          {
            id: 'osm-tiles-layer',
            type: 'raster',
            source: 'osm-tiles',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [80.6480, 16.5062], // Suryanagar
      zoom: 12.8,
      attributionControl: false
    });

    map.current.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Render Features & Markers
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    // 1. Incidents
    if (showIncidents) {
      incidents.forEach(inc => {
        const el = document.createElement('div');
        el.className = 'cursor-pointer transform hover:scale-125 transition-transform';
        const isCrit = inc.severity === 'CRITICAL';
        el.innerHTML = `
          <div style="background-color: ${isCrit ? '#DC2626' : '#D97706'}; color: white; padding: 4px 6px; border-radius: 4px; font-weight: 800; font-size: 11px; display: flex; align-items: center; gap: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.3); border: 1.5px solid white;">
            <span>${isCrit ? '⚠️' : '⚡'}</span>
            <span>${inc.sector}</span>
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([inc.longitude, inc.latitude])
          .addTo(map.current!);

        el.addEventListener('click', () => {
          if (onSelectIncident) onSelectIncident(inc);
          new maplibregl.Popup({ offset: 12 })
            .setLngLat([inc.longitude, inc.latitude])
            .setHTML(`
              <div style="font-family: inherit;">
                <div style="font-weight: 700; color: #0F172A; font-size: 13px;">${inc.title}</div>
                <div style="color: #64748B; font-size: 11px; margin-top: 2px;">${inc.address}</div>
                <div style="margin-top: 6px; font-size: 11px; display: flex; gap: 6px;">
                  <span style="background: #FEE2E2; color: #991B1B; padding: 2px 6px; border-radius: 3px; font-weight: 600;">${inc.severity}</span>
                  <span style="background: #EFF6FF; color: #1D4ED8; padding: 2px 6px; border-radius: 3px; font-weight: 600;">Trapped: ${inc.trapped_count}</span>
                  <span style="background: #FEF3C7; color: #92400E; padding: 2px 6px; border-radius: 3px; font-weight: 600;">Score: ${inc.priority_score}</span>
                </div>
              </div>
            `)
            .addTo(map.current!);
        });

        markersRef.current.push(marker);
      });
    }

    // 2. Resources
    if (showResources) {
      resources.forEach(res => {
        const el = document.createElement('div');
        el.className = 'cursor-pointer transform hover:scale-125 transition-transform';
        const isDispatched = res.status === 'IN_TRANSIT' || res.status === 'ASSIGNED';
        el.innerHTML = `
          <div style="background-color: ${isDispatched ? '#2563EB' : '#0F172A'}; color: white; padding: 3px 5px; border-radius: 3px; font-weight: 700; font-size: 10px; border: 1px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.25);">
            ${res.callsign}
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([res.current_longitude, res.current_latitude])
          .addTo(map.current!);

        el.addEventListener('click', () => {
          if (onSelectResource) onSelectResource(res);
          new maplibregl.Popup({ offset: 10 })
            .setLngLat([res.current_longitude, res.current_latitude])
            .setHTML(`
              <div style="font-family: inherit;">
                <div style="font-weight: 700; color: #0F172A;">${res.name} (${res.callsign})</div>
                <div style="font-size: 11px; color: #64748B;">Type: ${res.resource_type} | Base: ${res.base_station}</div>
                <div style="margin-top: 4px; font-size: 11px;">
                  Status: <b>${res.status}</b> | Speed: ${res.speed_kmh} km/h | Fuel: ${res.fuel_percent}%
                </div>
              </div>
            `)
            .addTo(map.current!);
        });

        markersRef.current.push(marker);
      });
    }

    // 3. Shelters
    if (showShelters) {
      shelters.forEach(sh => {
        const el = document.createElement('div');
        el.className = 'cursor-pointer transform hover:scale-125 transition-transform';
        el.innerHTML = `
          <div style="background-color: #4F46E5; color: white; padding: 3px 6px; border-radius: 4px; font-weight: 700; font-size: 10px; border: 1.5px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            🏠 ${sh.code}
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([sh.longitude, sh.latitude])
          .addTo(map.current!);

        el.addEventListener('click', () => {
          if (onSelectShelter) onSelectShelter(sh);
          new maplibregl.Popup({ offset: 10 })
            .setLngLat([sh.longitude, sh.latitude])
            .setHTML(`
              <div style="font-family: inherit;">
                <div style="font-weight: 700; color: #0F172A;">${sh.name}</div>
                <div style="font-size: 11px; color: #64748B;">${sh.address}</div>
                <div style="margin-top: 4px; font-size: 11px;">
                  Occupancy: <b>${sh.current_occupancy}/${sh.total_capacity}</b>
                  ${sh.has_medical_facility ? ' | 🏥 Field Clinic' : ''}
                </div>
              </div>
            `)
            .addTo(map.current!);
        });

        markersRef.current.push(marker);
      });
    }

    // 4. Update Road Segments and Routes via Map Layers
    map.current.on('load', () => {
      updateMapLayers();
    });

    if (map.current.isStyleLoaded()) {
      updateMapLayers();
    }

  }, [incidents, resources, shelters, roadSegments, routes, showIncidents, showResources, showShelters, showRoads, showRoutes]);

  const updateMapLayers = () => {
    if (!map.current) return;

    // Road Network Layer
    const roadGeoJson: FeatureCollection = {
      type: 'FeatureCollection',
      features: roadSegments.map(s => {
        const isBlocked = s.conditions && s.conditions.some(c => c.is_blocked);
        return {
          type: 'Feature',
          properties: {
            code: s.code,
            name: s.name,
            isBlocked: isBlocked ? 'yes' : 'no'
          },
          geometry: {
            type: 'LineString',
            coordinates: [
              [s.start_lng, s.start_lat],
              [s.end_lng, s.end_lat]
            ]
          }
        };
      })
    };

    if (map.current.getSource('roads-source')) {
      (map.current.getSource('roads-source') as maplibregl.GeoJSONSource).setData(roadGeoJson);
    } else {
      map.current.addSource('roads-source', {
        type: 'geojson',
        data: roadGeoJson
      });

      map.current.addLayer({
        id: 'roads-line',
        type: 'line',
        source: 'roads-source',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': [
            'case',
            ['==', ['get', 'isBlocked'], 'yes'],
            '#DC2626', // Red for blocked
            '#94A3B8'  // Gray for clear
          ],
          'line-width': [
            'case',
            ['==', ['get', 'isBlocked'], 'yes'],
            4.5,
            2.5
          ],
          'line-dasharray': [
            'case',
            ['==', ['get', 'isBlocked'], 'yes'],
            ['literal', [2, 2]],
            ['literal', [1]]
          ]
        }
      });
    }

    // Active Routes Layer
    const routeFeatures: Feature[] = [];
    routes.forEach(r => {
      if (r.waypoints && r.waypoints.length >= 2) {
        routeFeatures.push({
          type: 'Feature',
          properties: {
            id: r.id,
            status: r.status,
            distance: r.total_distance_km,
            eta: r.estimated_eta_minutes
          },
          geometry: {
            type: 'LineString',
            coordinates: r.waypoints.map(w => [w[1], w[0]]) // [lng, lat]
          }
        });
      }
    });

    const routeGeoJson: FeatureCollection = {
      type: 'FeatureCollection',
      features: routeFeatures
    };

    if (map.current.getSource('routes-source')) {
      (map.current.getSource('routes-source') as maplibregl.GeoJSONSource).setData(routeGeoJson);
    } else {
      map.current.addSource('routes-source', {
        type: 'geojson',
        data: routeGeoJson
      });

      map.current.addLayer({
        id: 'routes-line',
        type: 'line',
        source: 'routes-source',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': [
            'case',
            ['==', ['get', 'status'], 'INVALIDATED'],
            '#EF4444',
            '#2563EB' // Deep blue
          ],
          'line-width': 4.5,
          'line-opacity': 0.85
        }
      });
    }
  };

  const recenterMap = () => {
    map.current?.flyTo({
      center: [80.6480, 16.5062],
      zoom: 12.8,
      essential: true
    });
  };

  return (
    <div className="relative border border-slate-200 rounded-md overflow-hidden bg-slate-50 shadow-xs">
      <div ref={mapContainer} style={{ height, width: '100%' }} />

      {/* Map Control Bar Overlay */}
      <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-xs p-2 rounded border border-slate-200 shadow-md text-xs z-10 flex flex-col gap-1.5 font-sans">
        <div className="flex items-center justify-between pb-1 border-b border-slate-200 font-bold text-slate-800">
          <span className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-blue-600" />
            GIS LAYERS
          </span>
          <button
            onClick={recenterMap}
            className="p-1 hover:bg-slate-100 rounded text-slate-600 hover:text-slate-900 cursor-pointer"
            title="Recenter Suryanagar"
          >
            <Compass className="w-3.5 h-3.5" />
          </button>
        </div>

        <label className="flex items-center gap-1.5 cursor-pointer text-slate-700">
          <input
            type="checkbox"
            checked={showIncidents}
            onChange={e => setShowIncidents(e.target.checked)}
            className="rounded border-slate-300 text-blue-600 focus:ring-0"
          />
          <span>Incidents ({incidents.length})</span>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer text-slate-700">
          <input
            type="checkbox"
            checked={showResources}
            onChange={e => setShowResources(e.target.checked)}
            className="rounded border-slate-300 text-blue-600 focus:ring-0"
          />
          <span>Fleet Units ({resources.length})</span>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer text-slate-700">
          <input
            type="checkbox"
            checked={showShelters}
            onChange={e => setShowShelters(e.target.checked)}
            className="rounded border-slate-300 text-blue-600 focus:ring-0"
          />
          <span>Shelters ({shelters.length})</span>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer text-slate-700">
          <input
            type="checkbox"
            checked={showRoads}
            onChange={e => setShowRoads(e.target.checked)}
            className="rounded border-slate-300 text-blue-600 focus:ring-0"
          />
          <span>Road Network ({roadSegments.length})</span>
        </label>
      </div>

      {/* Legend Badge Bottom Left */}
      <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-xs px-2.5 py-1.5 rounded border border-slate-200 shadow-sm text-[11px] text-slate-700 z-10 flex items-center gap-3">
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-red-600" />
          <span>Critical Incident</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
          <span>Active Asset / Route</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-600" />
          <span>Shelter</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-4 h-1 border-t-2 border-dashed border-red-600" />
          <span>Road Closure</span>
        </div>
      </div>
    </div>
  );
};
