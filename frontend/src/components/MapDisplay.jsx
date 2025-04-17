import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './MapDisplay.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

const MapDisplay = ({ route, hosStops }) => {
	const mapContainer = useRef(null);
	const map = useRef(null);

	useEffect(() => {
		if (!route || !mapContainer.current) return;

		// Initialize map
		map.current = new mapboxgl.Map({
			container: mapContainer.current,
			style: 'mapbox://styles/mapbox/streets-v11',
			center: [
				route.segments[0].from.longitude,
				route.segments[0].from.latitude,
			],
			zoom: 5,
		});

		// Add navigation control
		map.current.addControl(new mapboxgl.NavigationControl());

		// Wait for map to load
		map.current.on('load', () => {
			// Combine all coordinates to find bounds
			const coordinates = [];

			// Add route segments
			route.segments.forEach((segment, index) => {
				const id = `route-${index}`;
				const routeCoordinates = segment.geometry.coordinates;

				// Add coordinates to overall array for bounds calculation
				coordinates.push(...routeCoordinates);

				// Add route line
				map.current.addSource(id, {
					type: 'geojson',
					data: {
						type: 'Feature',
						properties: {},
						geometry: segment.geometry,
					},
				});

				map.current.addLayer({
					id: id,
					type: 'line',
					source: id,
					layout: {
						'line-join': 'round',
						'line-cap': 'round',
					},
					paint: {
						'line-color': '#3182CE',
						'line-width': 5,
					},
				});
			});

			// Add markers for locations
			// Current location
			addMarker(
				map.current,
				[
					route.segments[0].from.longitude,
					route.segments[0].from.latitude,
				],
				'Current Location',
				'#3182CE'
			);

			// Pickup location
			addMarker(
				map.current,
				[
					route.stops[0].location.longitude,
					route.stops[0].location.latitude,
				],
				'Pickup',
				'#38A169'
			);

			// Dropoff location
			addMarker(
				map.current,
				[
					route.stops[1].location.longitude,
					route.stops[1].location.latitude,
				],
				'Dropoff',
				'#E53E3E'
			);

			// Add markers for rest stops
			hosStops.forEach((stop, index) => {
				// For simplicity, we'll place rest stops along the route
				// In a real app, we would calculate proper coordinates
				const segmentIndex = Math.min(
					index % route.segments.length,
					route.segments.length - 1
				);
				const segment = route.segments[segmentIndex];
				const coordinates = segment.geometry.coordinates;
				const midpointIndex = Math.floor(coordinates.length / 2);

				if (coordinates && coordinates.length > 0) {
					const stopCoordinates =
						coordinates[midpointIndex] || coordinates[0];
					addMarker(
						map.current,
						stopCoordinates,
						`${stop.reason}`,
						'#ED8936'
					);
				}
			});

			// Add fuel stops
			route.fuel_stops.forEach((stop, index) => {
				// For simplicity, we'll evenly distribute fuel stops
				const segmentIndex = index % route.segments.length;
				const segment = route.segments[segmentIndex];
				const coordinates = segment.geometry.coordinates;
				const position = Math.floor(
					(coordinates.length / route.fuel_stops.length) * (index + 1)
				);

				if (coordinates && coordinates.length > 0) {
					const stopCoordinates =
						coordinates[position] || coordinates[0];
					addMarker(
						map.current,
						stopCoordinates,
						'Fuel Stop',
						'#805AD5'
					);
				}
			});

			// Fit map to show all points
			if (coordinates.length > 0) {
				const bounds = coordinates.reduce((bounds, coord) => {
					return bounds.extend(coord);
				}, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));

				map.current.fitBounds(bounds, {
					padding: 50,
				});
			}
		});

		// Cleanup
		return () => {
			if (map.current) {
				map.current.remove();
			}
		};
	}, [route, hosStops]);

	return (
		<div className='map-container'>
			<div ref={mapContainer} className='map'></div>
			<div className='map-legend'>
				<div className='legend-item'>
					<div
						className='legend-color'
						style={{ backgroundColor: '#3182CE' }}></div>
					<div>Current Location</div>
				</div>
				<div className='legend-item'>
					<div
						className='legend-color'
						style={{ backgroundColor: '#38A169' }}></div>
					<div>Pickup</div>
				</div>
				<div className='legend-item'>
					<div
						className='legend-color'
						style={{ backgroundColor: '#E53E3E' }}></div>
					<div>Dropoff</div>
				</div>
				<div className='legend-item'>
					<div
						className='legend-color'
						style={{ backgroundColor: '#ED8936' }}></div>
					<div>Rest Stop</div>
				</div>
				<div className='legend-item'>
					<div
						className='legend-color'
						style={{ backgroundColor: '#805AD5' }}></div>
					<div>Fuel Stop</div>
				</div>
			</div>
		</div>
	);
};

// Helper function to add a marker
function addMarker(map, coordinates, title, color) {
	// Create a DOM element for the marker
	const el = document.createElement('div');
	el.className = 'marker';
	el.style.backgroundColor = color;

	// Add the marker to the map
	new mapboxgl.Marker({
		element: el,
		anchor: 'bottom',
	})
		.setLngLat(coordinates)
		.setPopup(
			new mapboxgl.Popup({ offset: 25 }).setHTML(`<h3>${title}</h3>`)
		)
		.addTo(map);
}

export default MapDisplay;
