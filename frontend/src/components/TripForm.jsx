import React, { useState } from 'react';
import './TripForm.css';

const TripForm = ({ onSubmit }) => {
	const [formData, setFormData] = useState({
		current_location: '',
		pickup_location: '',
		dropoff_location: '',
		current_hours: 0,
	});

	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData((prevData) => ({
			...prevData,
			[name]: value,
		}));
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		onSubmit(formData);
	};

	return (
		<div className='trip-form'>
			<h2>Trip Details</h2>
			<form onSubmit={handleSubmit}>
				<div className='form-group'>
					<label htmlFor='current_location'>Current Location</label>
					<input
						type='text'
						id='current_location'
						name='current_location'
						value={formData.current_location}
						onChange={handleChange}
						required
						placeholder='e.g. Chicago, IL'
					/>
				</div>

				<div className='form-group'>
					<label htmlFor='pickup_location'>Pickup Location</label>
					<input
						type='text'
						id='pickup_location'
						name='pickup_location'
						value={formData.pickup_location}
						onChange={handleChange}
						required
						placeholder='e.g. St. Louis, MO'
					/>
				</div>

				<div className='form-group'>
					<label htmlFor='dropoff_location'>Dropoff Location</label>
					<input
						type='text'
						id='dropoff_location'
						name='dropoff_location'
						value={formData.dropoff_location}
						onChange={handleChange}
						required
						placeholder='e.g. Dallas, TX'
					/>
				</div>

				<div className='form-group'>
					<label htmlFor='current_hours'>
						Current Cycle Used (Hours)
					</label>
					<input
						type='number'
						id='current_hours'
						name='current_hours'
						value={formData.current_hours}
						onChange={handleChange}
						required
						min='0'
						max='70'
						step='0.5'
					/>
					<span className='help-text'>
						Hours already used in your 70-hour/8-day cycle
					</span>
				</div>

				<button type='submit' className='submit-button'>
					Plan Trip
				</button>
			</form>
		</div>
	);
};

export default TripForm;
