import railfares.data_parsing as data_parsing
import pandas as pd


project_dir = '/Users/fb394/Documents/GitHub/railfares/'


# start = time.process_time()
# # test = data_parsing.get_isocost_stations(starting_station, b, project_dir)
# destination_stations = data_parsing.get_isocost_from_list(station_flows_df, station_singles, project_dir)
# # flow_record['col'].str.extract('(?P<test>.)(.)(.{4})(.{4})(.{5})(.{3})(.)(.)(.{8})(.{8})(.{3})(.)(.)(.)(.{7})')
# print(time.process_time()-start)







station_gdf = data_parsing.get_station_location(project_dir)
loc_records_df = data_parsing.get_location_records('location record', project_dir)[['nlc_code', 'crs_code']]
station_gdf = station_gdf.merge(loc_records_df, left_on = 'CRS Code', right_on = 'crs_code', how = 'left').drop('crs_code',1).drop_duplicates().reset_index(drop = True)


stations_nlc_dict = {}

for idx, row in station_gdf.iterrows():
    
    stations_codes = data_parsing.get_cluster_from_nlc(row['nlc_code'], project_dir)['cluster_id'].to_list()
    stations_codes.append(row['nlc_code'])
    stations_nlc_dict[row['Station name']] = stations_codes
    print(idx)






tickets = data_parsing.get_ticket_type_records(project_dir)
validity = data_parsing.get_ticket_validity(project_dir)
# val_code = validity[validity['out_days'] == '01']['validity_code'].to_list()
val_code = validity['validity_code'].to_list()
single_tickets = pd.DataFrame([x for idx, x in tickets.iterrows() if x['end_date'] == '31122999' and x['tkt_class'] == '2' and x['tkt_type'] == 'S' and x['validity_code'] in val_code and 'anytime' in x['description'].lower()])


flow_df, fares_df = data_parsing.get_flow_records('both', project_dir)

station_gdf = data_parsing.get_station_location(project_dir)

loc_records_df = data_parsing.get_location_records('location record', project_dir)[['nlc_code', 'crs_code']]

clusters_dict = data_parsing.get_cluster_nlc_dict(project_dir)

od_list = pd.DataFrame()
progr = 0
for key, value in stations_nlc_dict.items():
    
    # get the flows starting from the station and within valid date
    station_flows_df = flow_df[(flow_df['origin_code'].isin(value)) & (flow_df['end_date'] == '31122999')]

    # get list of flows from starting station
    station_list = station_flows_df['flow_id'].to_list()
    # get fares corresponding to the flows
    station_fares_df = fares_df[fares_df['flow_id'].isin(station_list)]
    # select fares corresponding to given ticket type
    station_singles = station_fares_df[station_fares_df['ticket_code'].isin(single_tickets['ticket_code'].to_list())]
    #  convert fare to pounds
    station_singles['fare'] = station_singles['fare'].astype(int)/100
    # subset flows to only those corresponding to given ticket type
    temp_isocost_route = station_flows_df[(station_flows_df['flow_id'].isin(station_singles['flow_id'].to_list())) & (station_flows_df['end_date'] == '31122999')]
    # create boolean column to check if destination station is in cluster or not
    temp_isocost_route['bool'] = [x in clusters_dict for x in temp_isocost_route['destination_code']]
    # separate stations from clusters
    stations_route = temp_isocost_route[temp_isocost_route['bool'] == False]
    clusters_route = temp_isocost_route[temp_isocost_route['bool'] == True]
    # get unique clusters
    unique_clusters = pd.Series(clusters_route['destination_code'].unique())
    # create data frame linking cluster ids to cluster nlc codes
    clust_nlc_df = pd.DataFrame([[k, clusters_dict.get(k)] for k in unique_clusters], columns = ['cluster_id', 'cluster_nlc']).explode('cluster_nlc')
    # split clusters into the various stations part of it
    disagr_clusters = clusters_route.merge(clust_nlc_df, left_on = 'destination_code', right_on = 'cluster_id')
    # put together routes to stations and routes to disaggregated cluster
    isocost_route = pd.concat([stations_route, disagr_clusters])
    # fill nas that are due to the merge above (stations not from a cluster do not have a cluster nlc, so need filling)
    isocost_route['cluster_nlc'].fillna(isocost_route['destination_code'], inplace = True)

    # get nlc codes of destination stations
    station_code = isocost_route['cluster_nlc']
    
    if not isinstance(station_code, pd.Series):
        
        station_code = [station_code]
    
    # find destination stations in location records
    station_nlc = loc_records_df[loc_records_df['nlc_code'].isin(station_code)].drop_duplicates()
    # and merge with station geodataframe to find their name
    isocost_destinations = station_gdf.merge(station_nlc, left_on = 'CRS Code', right_on = 'crs_code', how = 'inner')
    # merge back with fares data to get destination stations names and fares
    isocost_fare = isocost_route.merge(station_singles[['flow_id','fare']], left_on = 'flow_id', right_on = 'flow_id', how = 'left')
    destination_stations = isocost_destinations.merge(isocost_fare, left_on = 'nlc_code', right_on = 'cluster_nlc')
    
    
    # repeat the same as above, but looking at existing reverse flows
    inverse_station_flows_df = flow_df[(flow_df['destination_code'].isin(value)) & (flow_df['end_date'] == '31122999') & (flow_df['direction'] == 'R')]
    inverse_station_list = inverse_station_flows_df['flow_id'].to_list()
    inverse_station_fares_df = fares_df[fares_df['flow_id'].isin(inverse_station_list)]
    inverse_station_singles = inverse_station_fares_df[inverse_station_fares_df['ticket_code'].isin(single_tickets['ticket_code'].to_list())]
    inverse_station_singles['fare'] = inverse_station_singles['fare'].astype(int)/100
    
    
    
    temp_isocost_route = inverse_station_flows_df[(inverse_station_flows_df['flow_id'].isin(inverse_station_singles['flow_id'].to_list())) & (inverse_station_flows_df['end_date'] == '31122999')]
    
    temp_isocost_route['bool'] = [x in clusters_dict  for x in temp_isocost_route['origin_code']]
    stations_route = temp_isocost_route[temp_isocost_route['bool'] == False]
    clusters_route = temp_isocost_route[temp_isocost_route['bool'] == True]
    unique_clusters = pd.Series(clusters_route['origin_code'].unique())
    
    clust_nlc_df = pd.DataFrame([[k, clusters_dict.get(k)] for k in unique_clusters], columns = ['cluster_id', 'cluster_nlc']).explode('cluster_nlc')

    disagr_clusters = clusters_route.merge(clust_nlc_df, left_on = 'origin_code', right_on = 'cluster_id')
    
    isocost_route = pd.concat([stations_route, disagr_clusters])
    isocost_route['cluster_nlc'].fillna(isocost_route['origin_code'], inplace = True)
    
    station_code = isocost_route['cluster_nlc']
    
    if not isinstance(station_code, pd.Series):
        
        station_code = [station_code]
    
    station_nlc = loc_records_df[loc_records_df['nlc_code'].apply(lambda x: any([str(k) in x for k in station_code]))].drop_duplicates()
    
    isocost_destinations = station_gdf.merge(station_nlc, left_on = 'CRS Code', right_on = 'crs_code', how = 'inner')
    
    isocost_fare = isocost_route.merge(inverse_station_singles[['flow_id','fare']], left_on = 'flow_id', right_on = 'flow_id', how = 'left')
    inverse_destination_stations = isocost_destinations.merge(isocost_fare, left_on = 'nlc_code', right_on = 'cluster_nlc')
    # inverse_destination_stations.rename(column = {'Station name': 'Temp station name', 'nlc_code': 'temp nlc_code',
    #                                               'origin_code': 'temp origin_code', 'destination_code': 'temp destination_code',
    #                                               'cluster_id': 'temp cluster_id', 'cluster_nlc': 'temp cluster_nlc'}, inplace = True)
    
    # inverse_destination_stations.rename(column = {'Temp station name': })
    
    od_df = pd.concat([destination_stations, inverse_destination_stations])[['Station name', 'geometry', 'nlc_code', 'origin_code','destination_code', 
                                                                                                     'route_code', 'end_date', 'start_date', 'toc',
                                                                                                     'flow_id', 'cluster_id', 'fare']]
    od_df.rename(columns = {'Station name': 'Destination station name'}, inplace = True)
    od_df ['Origin station name'] = key
    
    od_df_min = od_df.loc[od_df.groupby('Destination station name')['fare'].idxmin()]
    
    if any(x in value for x in od_df_min['destination_code']):
        
        raise Warning('Starting station is also in destination station')
        break
    
    od_list = pd.concat([od_list, od_df_min])
    
    print(progr)
    progr = progr + 1



