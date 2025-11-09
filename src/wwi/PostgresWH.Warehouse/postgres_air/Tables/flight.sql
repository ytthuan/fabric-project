CREATE TABLE [postgres_air].[flight] (

	[flight_id] int NULL, 
	[flight_no] varchar(8000) NULL, 
	[scheduled_departure] datetime2(6) NULL, 
	[scheduled_arrival] datetime2(6) NULL, 
	[departure_airport] varchar(8000) NULL, 
	[arrival_airport] varchar(8000) NULL, 
	[status] varchar(8000) NULL, 
	[aircraft_code] varchar(8000) NULL, 
	[actual_departure] datetime2(6) NULL, 
	[actual_arrival] datetime2(6) NULL, 
	[update_ts] datetime2(6) NULL
);