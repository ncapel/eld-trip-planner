import React, { useState } from 'react';
import './App.css';
import TripForm from './components/TripForm';
import MapDisplay from './components/MapDisplay';
import ELDLogs from './components/ELDLogs';
import TripSummary from './components/TripSummary';
import LoadingOverlay from './components/LoadingOverlay';

function App() {
	const [tripData, setTripData] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const [activeTab, setActiveTab] = useState('map');

	const handleTripSubmit = async (formData) => {
		setLoading(true);
		setError(null);

		try {
			const response = await fetch(
				'https://eld-trip-planner-backend.vercel.app/api/plan',
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(formData),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const data = await response.json();
			setTripData(data);
			setActiveTab('map');
		} catch (err) {
			console.error('Error planning trip:', err);
			setError(
				'Failed to plan trip. Please check your inputs and try again.'
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className='App'>
			<header className='App-header'>
				<h1>ELD Trip Planner</h1>
			</header>

			<main className='App-main'>
				<div className='sidebar'>
					<TripForm onSubmit={handleTripSubmit} />

					{tripData && (
						<TripSummary
							distance={tripData.route.total_distance}
							duration={tripData.route.total_duration}
							restStops={tripData.hos_plan.rest_stops.length}
							tripDays={tripData.hos_plan.total_trip_days}
						/>
					)}
				</div>

				<div className='content'>
					{error && <div className='error-message'>{error}</div>}

					{tripData && (
						<div className='tabs'>
							<div className='tab-buttons'>
								<button
									className={
										activeTab === 'map' ? 'active' : ''
									}
									onClick={() => setActiveTab('map')}>
									Route Map
								</button>
								<button
									className={
										activeTab === 'logs' ? 'active' : ''
									}
									onClick={() => setActiveTab('logs')}>
									ELD Logs
								</button>
							</div>

							<div className='tab-content'>
								{activeTab === 'map' && (
									<MapDisplay
										route={tripData.route}
										hosStops={tripData.hos_plan.rest_stops}
									/>
								)}

								{activeTab === 'logs' && (
									<ELDLogs logs={tripData.eld_logs} />
								)}
							</div>
						</div>
					)}

					{!tripData && !error && !loading && (
						<div className='welcome-message'>
							<h2>Welcome to the ELD Trip Planner</h2>
							<p>
								Enter your trip details in the form to get
								started.
							</p>
							<p>
								This tool will help you plan your trip while
								staying compliant with Hours of Service
								regulations.
							</p>
						</div>
					)}
				</div>
			</main>

			{loading && <LoadingOverlay />}
		</div>
	);
}

export default App;
