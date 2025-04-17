import React from 'react';
import './TripSummary.css';

const TripSummary = ({ distance, duration, restStops, tripDays }) => {
	return (
		<div className='trip-summary'>
			<h2>Trip Summary</h2>

			<div className='summary-stats'>
				<div className='stat-item'>
					<div className='stat-value'>{distance.toFixed(1)}</div>
					<div className='stat-label'>Miles</div>
				</div>

				<div className='stat-item'>
					<div className='stat-value'>{duration.toFixed(1)}</div>
					<div className='stat-label'>Hours</div>
				</div>

				<div className='stat-item'>
					<div className='stat-value'>{restStops}</div>
					<div className='stat-label'>Stops</div>
				</div>

				<div className='stat-item'>
					<div className='stat-value'>{tripDays}</div>
					<div className='stat-label'>Days</div>
				</div>
			</div>

			<div className='hos-compliance'>
				<div className='compliance-note'>
					<strong>Note:</strong> This plan follows the
					property-carrying hours of service regulations
					(70hrs/8days).
				</div>
			</div>
		</div>
	);
};

export default TripSummary;
