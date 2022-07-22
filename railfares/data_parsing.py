import pandas as pd
import geopandas as gpd
import csv
import re
import string
# import contextily as cx
import folium


#POSSIBLY DEPRECATED
def get_nlc_codes():

    url_str = 'http://www.railwaycodes.org.uk/crs/crs'

    list_of_letters = list(string.ascii_lowercase)

    nlc_codes = pd.DataFrame(columns = ['Location', 'CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX'])

    for i in list_of_letters:
        
        full_url = url_str + i + '.shtm'
        
        html_tab = pd.read_html(full_url)
        df = html_tab[1]
        df.columns = html_tab[0].columns.values
        nlc_codes = pd.concat([nlc_codes, df])
        
    return nlc_codes



def get_station_clusters(project_dir):
    
    
    with open(project_dir + 'RJFAF214/RJFAF214.FSC', newline = '') as f:
        reader = csv.reader(f)
        for row in reader:
    
            if "Records" in row[0]:
                number_rows = int(re.findall(r'\d+', row[0])[0])
                break
    
    station_clusters = pd.read_csv(project_dir + 'RJFAF214/RJFAF214.FSC', skiprows = 6, nrows = number_rows, names = ['col'])
    
    return pd.DataFrame({'update-marker': station_clusters['col'].str[0],
                   'cluster_id': station_clusters['col'].str[1:5],
                   'cluster_nlc': station_clusters['col'].str[5:9],
                   'end_date': station_clusters['col'].str[9:17],
                   'start_date': station_clusters['col'].str[17:25]})

def get_cluster_from_nlc(nlc_code, project_dir, end_date = '31122999'):
    
    station_clusters = get_station_clusters(project_dir)
    
    return station_clusters[(station_clusters['cluster_nlc'] == nlc_code) & (station_clusters['end_date'] == end_date)].reset_index()

def get_nlc_from_cluster(cluster_id, project_dir, end_date = '31122999'):
    
    station_clusters = get_station_clusters(project_dir)
    
    if not isinstance(cluster_id, pd.Series):
        
        cluster_id = [cluster_id]
    
    return station_clusters[(station_clusters['cluster_id'].isin(cluster_id)) & (station_clusters['end_date'] == end_date)].reset_index()

def get_location_records(location_type, project_dir):
    
    with open(project_dir + 'RJFAF214/RJFAF214.LOC', newline = '') as f:
        reader = csv.reader(f)
        for row in reader:
    
            if "Records" in row[0]:
                number_rows = int(re.findall(r'\d+', row[0])[0])
                break
    
    location_df = pd.read_csv(project_dir + 'RJFAF214/RJFAF214.LOC', skiprows = 6, nrows = number_rows, names = ['col'])
    
    if location_type == 'location record':
        
        location_record = location_df[location_df['col'].apply(lambda x: (len(x) == 289) and (x[1] == 'L'))]
    
        return pd.DataFrame({'update_marker': location_record['col'].str[0],
                             'record_type': location_record['col'].str[1],
                             'uic_code': location_record['col'].str[2:9],
                             'end_date': location_record['col'].str[9:17],
                             'start_date': location_record['col'].str[17:25],
                             'quote_date': location_record['col'].str[25:33],
                             'admin_area_code': location_record['col'].str[33:36],
                             'nlc_code': location_record['col'].str[36:40],
                             'description': location_record['col'].str[40:56],
                             'crs_code': location_record['col'].str[56:59],
                             'resv_code': location_record['col'].str[59:64],
                             'ers_counry': location_record['col'].str[64:66],
                             'ers_code': location_record['col'].str[66:69],
                             'fare_group': location_record['col'].str[69:75],
                             'county': location_record['col'].str[75:77:],
                             'pte_code': location_record['col'].str[77:79],
                             'zone_no': location_record['col'].str[79:83],
                             'zone_ind': location_record['col'].str[83:85],
                             'region': location_record['col'].str[85],
                             'hierarchy': location_record['col'].str[86],
                             'cc_desc_out': location_record['col'].str[87:128],
                             'cc_desc_rtn': location_record['col'].str[128:144],
                             'atb_desc_out': location_record['col'].str[144:204],
                             'atb_desc_rtn': location_record['col'].str[204:234],
                             'special_facilities': location_record['col'].str[234:260],
                             'lul_direction_ind': location_record['col'].str[260],
                             'lul_uts_mode': location_record['col'].str[261],
                             'lul_zone_1': location_record['col'].str[262],
                             'lul_zone_2': location_record['col'].str[263],
                             'lul_zone_3': location_record['col'].str[264],
                             'lul_zone_4': location_record['col'].str[265],
                             'lul_zone_5': location_record['col'].str[266],
                             'lul_zone_6': location_record['col'].str[267],
                             'lul_uts_london_stn': location_record['col'].str[268],
                             'uts_code': location_record['col'].str[269:272],
                             'uts_a_code': location_record['col'].str[272:275],
                             'uts_ptr_bias': location_record['col'].str[275],
                             'uts_offset': location_record['col'].str[276],
                             'uts_north': location_record['col'].str[277:280],
                             'uts_east': location_record['col'].str[280:283],
                             'uts_south': location_record['col'].str[283:286],
                             'uts_west': location_record['col'].str[286:289]})
    
    if location_type == 'associated stations':
        
        location_record = location_df[location_df['col'].apply(lambda x: (len(x) == 27) and (x[1] == 'A'))]
        
        return pd.DataFrame({'update_marker': location_record['col'].str[0],
                             'record_type': location_record['col'].str[1],
                             'uic_code': location_record['col'].str[2:9],
                             'end_date': location_record['col'].str[9:17],
                             'assoc_uic_code': location_record['col'].str[17:24],
                             'assoc_crs_code': location_record['col'].str[24:27]})
    
    if location_type == 'railcard geography':
        
        location_record = location_df[location_df['col'].apply(lambda x: (len(x) == 20) and (x[1] == 'R'))]
        
        return pd.DataFrame({'update_marker': location_record['col'].str[0],
                             'record_type': location_record['col'].str[1],
                             'uic_code': location_record['col'].str[2:9],
                             'railcard_code': location_record['col'].str[9:12],
                             'end_date': location_record['col'].str[12:20]})
    
    if location_type == 'tt group location':
        
        location_record = location_df[location_df['col'].apply(lambda x: (len(x) == 54) and (x[1] == 'G'))]
        
        return pd.DataFrame({'update_marker': location_record['col'].str[0],
                             'record_type': location_record['col'].str[1],
                             'group_uic_code': location_record['col'].str[2:9],
                             'end_date': location_record['col'].str[9:17],
                             'start_date': location_record['col'].str[17:25],
                             'quote_date': location_record['col'].str[25:33],
                             'description': location_record['col'].str[33:49],
                             'ers_country': location_record['col'].str[49:51],
                             'ers_code': location_record['col'].str[51:54]})
    
    if location_type == 'group members':
        
        location_record = location_df[location_df['col'].apply(lambda x: (len(x) == 27) and (x[1] == 'M'))]
        
        return pd.DataFrame({'update_marker': location_record['col'].str[0],
                             'record_type': location_record['col'].str[1],
                             'group_uic_code': location_record['col'].str[2:9],
                             'end_date': location_record['col'].str[9:17],
                             'member_uic_code': location_record['col'].str[17:24],
                             'members_crs_code': location_record['col'].str[24:27]})
    
    if location_type == 'synonym record':
        
        location_record = location_df[location_df['col'].apply(lambda x: (len(x) == 41) and (x[1] == 'S'))]
        
        return pd.DataFrame({'update_marker': location_record['col'].str[0],
                             'record_type': location_record['col'].str[1],
                             'uic_code': location_record['col'].str[2:9],
                             'end_date': location_record['col'].str[9:17],
                             'start_date': location_record['col'].str[17:25],
                             'description': location_record['col'].str[25:41]})



def get_flow_records(flow_type, project_dir):
    
    with open(project_dir + 'RJFAF214/RJFAF214.FFL', newline = '') as f:
        reader = csv.reader(f)
        for row in reader:
    
            if "Records" in row[0]:
                number_rows = int(re.findall(r'\d+', row[0])[0])
                break
    
    flow_df = pd.read_csv(project_dir + 'RJFAF214/RJFAF214.FFL', skiprows = 6, nrows = number_rows, names = ['col'])
    
    if flow_type == 'flow':
        
        flow_record = flow_df[flow_df['col'].apply(lambda x: (len(x) == 49) and (x[1] == 'F'))]
        
        return pd.DataFrame({'update-marker':flow_record['col'].str[0],
                             'record_type':flow_record['col'].str[1],
                             'origin_code':flow_record['col'].str[2:6],
                             'destination_code':flow_record['col'].str[6:10],
                             'route_code':flow_record['col'].str[10:15],
                             'status_code':flow_record['col'].str[15:18],
                             'usage_code':flow_record['col'].str[18],
                             'direction':flow_record['col'].str[19],
                             'end_date':flow_record['col'].str[20:28],
                             'start_date':flow_record['col'].str[28:36],
                             'toc':flow_record['col'].str[36:39],
                             'cross_london_ind':flow_record['col'].str[39],
                             'ns_disc_ind':flow_record['col'].str[40],
                             'publication_ind':flow_record['col'].str[41],
                             'flow_id':flow_record['col'].str[42:49]})
        
    if flow_type == 'fares':
        
        fare_record = flow_df[flow_df['col'].apply(lambda x: (len(x) == 22) and (x[1] == 'T'))]
        
        return pd.DataFrame({'update-marker':fare_record['col'].str[0],
                             'record_type':fare_record['col'].str[1],
                             'flow_id':fare_record['col'].str[2:9],
                             'ticket_code':fare_record['col'].str[9:12],
                             'fare':fare_record['col'].str[12:20],
                             'restriction_code':fare_record['col'].str[20:22]})



def get_ticket_type_records(project_dir):
    
    with open(project_dir + 'RJFAF214/RJFAF214.TTY', newline = '') as f:
        reader = csv.reader(f)
        for row in reader:
    
            if "Records" in row[0]:
                number_rows = int(re.findall(r'\d+', row[0])[0])
                break
    
    ticket_df = pd.read_csv(project_dir + 'RJFAF214/RJFAF214.TTY', skiprows = 6, nrows = number_rows, names = ['col'])
    
    return pd.DataFrame({'update_marker': ticket_df['col'].str[0],
                         'ticket_code': ticket_df['col'].str[1:4],
                         'end_date': ticket_df['col'].str[4:12],
                         'start_date': ticket_df['col'].str[12:20],
                         'quote_date': ticket_df['col'].str[20:28],
                         'description': ticket_df['col'].str[28:43],
                         'tkt_class': ticket_df['col'].str[43],
                         'tkt_type': ticket_df['col'].str[44],
                         'tkt_group': ticket_df['col'].str[45],
                         'last_valid_day': ticket_df['col'].str[46:54],
                         'max_passengers': ticket_df['col'].str[54:57],
                         'min_passengers': ticket_df['col'].str[57:60],
                         'max_adults': ticket_df['col'].str[60:63],
                         'min_adults': ticket_df['col'].str[63:66],
                         'max_children': ticket_df['col'].str[66:69],
                         'min_children': ticket_df['col'].str[69:72],
                         'restricted_by_date': ticket_df['col'].str[72],
                         'restricted_by_train': ticket_df['col'].str[73],
                         'restricted_by_area': ticket_df['col'].str[74],
                         'validity_code': ticket_df['col'].str[75:77],
                         'atb_description': ticket_df['col'].str[77:97],
                         'lul_xlondon_issue': ticket_df['col'].str[97],
                         'reservation_required': ticket_df['col'].str[98],
                         'capri_code': ticket_df['col'].str[99:102],
                         'lul_93': ticket_df['col'].str[102],
                         'uts_code': ticket_df['col'].str[103:105],
                         'time_restriction': ticket_df['col'].str[105],
                         'free_pass_lul': ticket_df['col'].str[106],
                         'package_mkr': ticket_df['col'].str[107],
                         'fare_multiplier': ticket_df['col'].str[108:111],
                         'discount_category': ticket_df['col'].str[111:113]})


def get_ticket_validity(project_dir):
    
    with open(project_dir + 'RJFAF214/RJFAF214.TVL', newline = '') as f:
        reader = csv.reader(f)
        for row in reader:
    
            if "Records" in row[0]:
                number_rows = int(re.findall(r'\d+', row[0])[0])
                break
    
    validity_df = pd.read_csv(project_dir + 'RJFAF214/RJFAF214.TVL', skiprows = 6, nrows = number_rows, names = ['col'])
    
    return pd.DataFrame({'validity_code': validity_df['col'].str[0:2],
                         'end_date': validity_df['col'].str[2:10],
                         'start_date': validity_df['col'].str[10:18],
                         'description': validity_df['col'].str[18:38],
                         'out_days': validity_df['col'].str[38:40],
                         'out_months': validity_df['col'].str[40:42],
                         'ret_days': validity_df['col'].str[42:44],
                         'ret_months': validity_df['col'].str[44:46],
                         'ret_after_days': validity_df['col'].str[46:48],
                         'ret_after_months': validity_df['col'].str[48:50],
                         'ret_after_day': validity_df['col'].str[50:52],
                         'break_out': validity_df['col'].str[52],
                         'break_rtn': validity_df['col'].str[53],
                         'out_description': validity_df['col'].str[54:68],
                         'rtn_description': validity_df['col'].str[68:82]})

def get_station_location(project_dir):
    
    
    timetable = pd.read_csv(project_dir + 'ttis418/ttisf418.msn', skiprows = 1, names = ['col'])
    

    station_locations = timetable[timetable['col'].apply(lambda x: (len(x) == 82) and (x[0] == 'A'))]
    
    station_df = pd.DataFrame({'Station name':station_locations['col'].str[5:31].str.rstrip(), 
                               'CRS Code': station_locations['col'].str[49:52],
                               'Minor CRS code': station_locations['col'].str[43:46]})
    
    station_points = gpd.points_from_xy(station_locations['col'].str[53:57] + '00', station_locations['col'].str[59:63] + '00',  crs = 'OSGB36 / British National Grid')
    
    return gpd.GeoDataFrame(station_df, geometry = station_points)

def get_station_code_from_name(station_name, project_dir):
    
    station_name = station_name.lower()
    
    station_gdf = get_station_location(project_dir)
    
    station_crs = station_gdf[station_gdf['Station name'].str.lower().str.contains(station_name)][['Station name', 'CRS Code', 'Minor CRS code']]
    
    loc_records_df = get_location_records('location record', project_dir)[['nlc_code', 'crs_code']]
    
    return station_crs.merge(loc_records_df, left_on = 'CRS Code', right_on = 'crs_code', how = 'left').drop_duplicates()

def get_station_name_from_code(station_code, project_dir):
    
    if not isinstance(station_code, pd.Series):
        
        station_code = [station_code]
    
    station_gdf = get_station_location(project_dir)
    
    loc_records_df = get_location_records('location record', project_dir)[['nlc_code', 'crs_code']]
    
    station_nlc = loc_records_df[loc_records_df['nlc_code'].apply(lambda x: any([str(k) in x for k in station_code]))].drop_duplicates()
    
    return station_gdf.merge(station_nlc, left_on = 'CRS Code', right_on = 'crs_code', how = 'inner')


def plot_isocost_stations(starting_station_code, destination_stations, out_path, project_dir):
    
    station_gdf = get_station_location(project_dir)
    station_gdf = station_gdf.to_crs(epsg = 4326)
    
    starting_gdf = station_gdf[station_gdf['CRS Code'] == starting_station_code]
    
    destination_gdf = station_gdf[station_gdf['CRS Code'].isin(destination_stations['crs_code'])]
    
    # ax = starting_gdf.plot(figsize = (10,10), color = 'red')
    # destination_gdf.plot(ax = ax, color = 'yellow')
    # cx.add_basemap(ax = ax, crs = station_gdf.crs, zoom = 13, source = cx.providers.Stamen.TonerLite)
    
    
    starting_gdf['label'] = 'starting'
    starting_gdf['fare'] = 0
    destination_gdf['label'] = 'destination'
    destination_gdf = destination_gdf.merge(destination_stations[['crs_code', 'fare']], left_on = 'CRS Code', right_on = 'crs_code')
    
    stats_gdf = starting_gdf.append(destination_gdf).reset_index()
    
    geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in stats_gdf.geometry ]
    cost_map = folium.Map(location = [stats_gdf.dissolve().centroid[0].coords[0][1],stats_gdf.dissolve().centroid[0].coords[0][0]], tiles = "Stamen Terrain", zoom_start = 10)
    # Iterate through list and add a marker for each volcano, color-coded by its type.
    i = 0
    for coordinates in geo_df_list:
       
        if stats_gdf['label'][i] == 'starting':
            
            type_color = 'green'
        
        elif stats_gdf['label'][i] == 'destination':
            
            type_color = 'blue'


        # Place the markers with the popup labels and data
        cost_map.add_child(folium.Marker(location = coordinates,
                                popup =
                                "Station: " + str(stats_gdf['Station name'][i]) + '<br>' +
                                "Fare: £" + str(stats_gdf['fare'][i]).ljust(4,'0'),
                                icon = folium.Icon(color = "%s" % type_color)))
        i = i + 1
        
    cost_map.save(out_path)




