// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt
// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt




frappe.ui.form.on('Sales Man Visit', {
	onload: function (frm) {
		
	  if (frm.is_new()) {
		
		frm.set_value('date', frappe.datetime.get_today());
		frm.set_value('time', frappe.datetime.now_datetime());
  
		// Retrieve location data if necessary fields are empty
		if (!frm.doc.latitude || !frm.doc.longitude || !frm.doc.location) {
		  checkLocationPermission().then(permission => {
			if (permission) {
			  navigator.geolocation.getCurrentPosition(
				function (position) {
				  const latitude = position.coords.latitude;
				  const longitude = position.coords.longitude;
				  const geoJSONString =
					'{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[0,0]}}]}';
				  const geoJSONObject = JSON.parse(geoJSONString);
				  geoJSONObject.features[0].geometry.coordinates = [
					longitude,
					latitude,
				  ];
				  const locationData = JSON.stringify(geoJSONObject);
  
				  // Set latitude, longitude, and location fields
				  frm.set_value('latitude', latitude);
				  frm.set_value('longitude', longitude);
				  frm.set_value('location', locationData);
				  frm.set_value('is_set_location', 1);
  
				  getAddressFromCoordinates(latitude, longitude)
					.then(function (address) {
					  frm.set_value('address', address);
					  frm.set_df_property('address', 'read_only');
					  frm.refresh_field('address');
					})
					.catch(function (error) {
					  frappe.msgprint(
						__('Error getting address: {0}', [error.message]),
					  );
					});
				},
				function (error) {
				  frm.set_value('is_set_location', 0);
  
				  frappe.msgprint(__('Please enable location permission'));
				},
			  );
			} else {
			  frm.set_value('is_set_location', 0);
			  frappe.msgprint(__('Please enable location permission'));
			}
		  });
		}
	  }
	},
	before_save: function (frm) {
	  if (frm.is_new()) {
		
		frm.set_value('date', frappe.datetime.get_today());
		frm.set_value('time', frappe.datetime.now_datetime());
		// Retrieve location data if necessary fields are empty
		checkLocationPermission().then(permission => {
		  if (permission) {
			navigator.geolocation.getCurrentPosition(
			  function (position) {
				const latitude = position.coords.latitude;
				const longitude = position.coords.longitude;
				const geoJSONString =
				  '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[0,0]}}]}';
				const geoJSONObject = JSON.parse(geoJSONString);
				geoJSONObject.features[0].geometry.coordinates = [
				  longitude,
				  latitude,
				];
				const locationData = JSON.stringify(geoJSONObject);
  
				// Set latitude, longitude, and location fields
  
				getAddressFromCoordinates(latitude, longitude)
				  .then(function (address) {
					frm.set_value('latitude', latitude);
					frm.set_value('longitude', longitude);
					frm.set_value('location', locationData);
					frm.set_value('is_set_location', 1);
					frm.set_value('address', address);
					
					
				  })
				  .catch(function (error) {
					frappe.msgprint(
					  __('Error getting address: {0}', [error.message]),
					);
				  });
			  },
			  function (error) {
				frm.set_value('is_set_location', 0);
				frappe.msgprint(__('Please enable location permission'));
			  },
			);
		  } else {
			frm.set_value('is_set_location', 0);
			frappe.msgprint(__('Please enable location permission'));
		  }
		});
	  }
	},
	refresh: function (frm) {
	  const isNew = frm.is_new();
  
	  frm.set_df_property('log_type', 'read_only', !isNew);
	  frm.set_df_property('address', 'read_only', !isNew);
	  frm.set_df_property('time', 'read_only', !isNew);
	  frm.set_df_property('latitude', 'read_only', !isNew);
	  frm.set_df_property('longitude', 'read_only', !isNew);
	},
	latitude: function (frm) {
	  regenerateAddress(frm);
	},
	longitude: function (frm) {
	  regenerateAddress(frm);
	},
  });
  
  function getDateFromDateTimestring(dateTimeString) {
	const [datePart] = dateTimeString?.split(' ');
	return datePart;
  }
  
  function getAddressFromCoordinates(latitude, longitude) {
	return new Promise(function (resolve, reject) {
	  const url = `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`;
  
	  fetch(url)
		.then(response => {
		  if (!response.ok) {
			throw new Error('Network response was not ok');
		  }
		  return response.json();
		})
		.then(data => {
		  const address = data.display_name;
		  resolve(address);
		})
		.catch(error => {
		  reject(error);
		});
	});
  }
  
  function checkLocationPermission() {
	return new Promise(resolve => {
	  navigator.permissions.query({name: 'geolocation'}).then(result => {
		if (result.state === 'granted') {
		  resolve(true);
		} else if (result.state === 'prompt') {
		  navigator.geolocation.getCurrentPosition(
			function () {
			  resolve(true);
			},
			function () {
			  resolve(false);
			},
		  );
		} else {
		  resolve(false);
		}
	  });
	});
  }
  
  function regenerateAddress(frm) {
	const latitude = frm.doc.latitude;
	const longitude = frm.doc.longitude;
  
	if (latitude && longitude) {
	  getAddressFromCoordinates(latitude, longitude)
		.then(function (address) {
		  frm.set_value('address', address);
		})
		.catch(function (error) {
		  frappe.msgprint(__('Error getting address: {0}', [error.message]));
		});
	}
  }
  

