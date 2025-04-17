import React from 'react';
import './ELDLogs.css';

const ELDLogs = ({ logs }) => {
	if (!logs || logs.length === 0) {
		return <div className='no-logs'>No log data available.</div>;
	}

	return (
		<div className='eld-logs'>
			<h2>ELD Log Sheets</h2>

			{logs.map((log, index) => (
				<div key={index} className='log-sheet'>
					<div className='log-header'>
						<h3>
							Day {log.day} - {log.date}
						</h3>
					</div>

					<div className='log-grid-container'>
						<div className='log-grid'>
							<div className='grid-times'>
								{Array.from({ length: 25 }, (_, i) => (
									<div key={i} className='time-marker'>
										{i === 24
											? 'M'
											: i.toString().padStart(2, '0')}
									</div>
								))}
							</div>

							<div className='grid-statuses'>
								<div className='status-label'>Off Duty</div>
								<div className='status-label'>Sleeper</div>
								<div className='status-label'>Driving</div>
								<div className='status-label'>On Duty</div>
							</div>

							<div className='grid-chart'>
								{log.grid.map((row, rowIndex) => (
									<div key={rowIndex} className='grid-row'>
										{row.map((cell, cellIndex) => {
											// Calculate hour and quarter
											const hour = Math.floor(
												cellIndex / 4
											);
											const quarter = cellIndex % 4;

											// Determine if this cell is active
											const isActive = cell === 1;

											return (
												<div
													key={cellIndex}
													className={`grid-cell ${
														isActive ? 'active' : ''
													}`}
													style={{
														gridColumn: `${
															hour * 4 +
															quarter +
															1
														} / span 1`,
														gridRow: `${
															rowIndex + 1
														} / span 1`,
													}}></div>
											);
										})}
									</div>
								))}
							</div>
						</div>
					</div>

					<div className='log-summary'>
						<h4>Hours Summary</h4>
						<div className='hours-summary'>
							<div className='hours-item'>
								<span>Off Duty:</span>
								<span>{log.hours.off_duty.toFixed(2)} hrs</span>
							</div>
							<div className='hours-item'>
								<span>Sleeper Berth:</span>
								<span>
									{log.hours.sleeper_berth.toFixed(2)} hrs
								</span>
							</div>
							<div className='hours-item'>
								<span>Driving:</span>
								<span>{log.hours.driving.toFixed(2)} hrs</span>
							</div>
							<div className='hours-item'>
								<span>On Duty (Not Driving):</span>
								<span>
									{log.hours.on_duty_not_driving.toFixed(2)}{' '}
									hrs
								</span>
							</div>
							<div className='hours-item total'>
								<span>Total Hours:</span>
								<span>{log.total_hours.toFixed(2)} hrs</span>
							</div>
						</div>
					</div>

					<div className='log-locations'>
						<h4>Location History</h4>
						<table className='locations-table'>
							<thead>
								<tr>
									<th>Time</th>
									<th>Status</th>
									<th>Location</th>
								</tr>
							</thead>
							<tbody>
								{log.locations.map((location, i) => (
									<tr key={i}>
										<td>{location.time}</td>
										<td>{location.status}</td>
										<td className='location-address'>
											{location.location}
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>
			))}
		</div>
	);
};

export default ELDLogs;
