# streams: API URL endpoints to be called
# properties:
#   <root node>: Plural stream name for the endpoint
#   path: API endpoint relative path, when added to the base URL, creates the full path,
#       default = stream_name
#   key_properties: Primary key fields for identifying an endpoint record.
#   replication_method: INCREMENTAL or FULL_TABLE
#   replication_keys: bookmark_field(s), typically a date-time, used for filtering the results
#        and setting the state
#   params: Query, sort, and other endpoint specific parameters; default = {}
#   data_key: JSON element containing the results list for the endpoint; default = 'results'
#   bookmark_query_field: From date-time field used for filtering the query
#   alt_character_set: Alternate character set to try if UTF-8 decoding does not work

STREAMS = {
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/us_daily.csv
    # Single file w/ daily updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_daily': {
        'search_path': 'search/code?q=filename:us_daily+extension:csv+path:data+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_current.csv
    # Single file w/ daily updates (updated rows). Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_states_current': {
        'search_path': 'search/code?q=path:data+filename:states_current+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_daily_4pm_et.csv
    # Single file w/ daily updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_states_daily': {
        'search_path': 'search/code?q=path:data+filename:states_daily_4pm_et+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_info.csv
    # Single file w/ occasional updates (updated rows). Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_states_info': {
        'search_path': 'search/code?q=path:data+filename:states_info+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_counties.csv
    # Single file w/ minimal updates. Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_population_counties': {
        'search_path': 'search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_counties+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states_agegroups.csv
    # Single file w/ minimal updates. Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_population_states_age_groups': {
        'search_path': 'search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_states_agegroups+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states.csv
    # Single file w/ minimal updates. Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_population_states': {
        'search_path': 'search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_states+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=desc',
        'exclude_files': ['us_census_2018_population_estimates_states_agegroups.csv'],
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/kff_hospital_beds/kff_usa_hospital_beds_per_capita_2018.csv
    # Single file w/ minimal updates. Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_states_kff_hospital_beds': {
        'search_path': 'search/code?q=path:kff_hospital_beds+filename:kff_usa_hospital_beds_per_capita_2018+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/acs_health_insurance/acs_2018_health_insurance_coverage_estimates.csv
    # Single file w/ minimal updates. Use FULL_TABLE replication w/ activate_version
    'c19_trk_us_states_acs_health_insurance': {
        'search_path': 'search/code?q=path:acs_health_insurance+filename:acs_2018_health_insurance_coverage_estimates+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference https://github.com/covid19-eu-zh/covid19-eu-data/tree/master/dataset/daily
    # Many files w/ new files each day. Use INCREMENTAL replication only (NOT activate_version)
    # NOTE: -filename:ecdc in search_path means: exclude ecdc filenames
    'eu_daily': {
        'search_path': 'search/code?q=-filename:ecdc+path:dataset/daily+extension:csv+repo:covid19-eu-zh/covid19-eu-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference https://github.com/covid19-eu-zh/covid19-eu-data/tree/master/dataset/daily/ecdc
    # Many files w/ new file each day. Use INCREMENTAL replication only (NOT activate_version)
    'eu_ecdc_daily': {
        'search_path': 'search/code?q=filename:ecdc+path:dataset/daily/ecdc+extension:csv+repo:covid19-eu-zh/covid19-eu-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Dati COVID-19 Italia (COVID-19 data Italy)
    # Reference: https://github.com/pcm-dpc/COVID-19/tree/master/dati-andamento-nazionale
    # Many files w/ new file each day. Use INCREMENTAL replication only (NOT activate_version)
    'italy_national_daily': {
        'search_path': 'search/code?q=path:dati-andamento-nazionale+extension:csv+repo:pcm-dpc/COVID-19&sort=indexed&order=desc',
        'exclude_files': ['dpc-covid19-ita-andamento-nazionale-latest.csv', 'dpc-covid19-ita-andamento-nazionale.csv'],
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'alt_character_set': 'latin_1'
    },
    # Dati COVID-19 Italia (COVID-19 data Italy)
    # Reference: https://github.com/pcm-dpc/COVID-19/tree/master/dati-andamento-nazionale
    # Many files w/ new files each day. Use INCREMENTAL replication only (NOT activate_version)
    'italy_regional_daily': {
        'search_path': 'search/code?q=path:dati-regioni+extension:csv+repo:pcm-dpc/COVID-19&sort=indexed&order=desc',
        'exclude_files': ['dpc-covid19-ita-regioni-latest.csv', 'dpc-covid19-ita-regioni.csv'],
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'alt_character_set': 'latin_1'
    },
    # Dati COVID-19 Italia (COVID-19 data Italy)
    # Reference: https://github.com/pcm-dpc/COVID-19
    # Many files w/ new files each day. Use INCREMENTAL replication only (NOT activate_version)
    'italy_provincial_daily': {
        'search_path': 'search/code?q=path:dati-province+extension:csv+repo:pcm-dpc/COVID-19&sort=indexed&order=desc',
        'exclude_files': ['dpc-covid19-ita-province-latest.csv', 'dpc-covid19-ita-province.csv'],
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'alt_character_set': 'latin_1'
    },
    # Reference: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
    # Many files w/ new file each day. Use INCREMENTAL replication only (NOT activate_version)
    'jh_csse_daily': {
        'search_path': 'search/code?q=path:csse_covid_19_data/csse_covid_19_daily_reports+extension:csv+repo:CSSEGISandData/COVID-19&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/nytimes/covid-19-data/blob/master/us-states.csv
    # Single file w/ daily updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'nytimes_us_states': {
        'search_path': 'search/code?q=filename:us-states+extension:csv+repo:nytimes/covid-19-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv
    # Single file w/ daily updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'nytimes_us_counties': {
        'search_path': 'search/code?q=filename:us-counties+extension:csv+repo:nytimes/covid-19-data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/tree/master/case-counts
    # Many files w/ daily updates to all files, but not at same time (additional rows).  Use INCREMENTAL replication only (NOT activate_version)
    'neherlab_case_counts': {
        'search_path': 'search/code?q=path:case-counts+extension:tsv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['git_path', '__sdc_row_number'],
        'replication_method': 'INCREMENTAL',
        'activate_version': False,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'skip_header_rows': 3,
        'csv_delimiter': '\t'
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/blob/master/country_codes.csv
    # Single file w/ minimal updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'neherlab_country_codes': {
        'search_path': 'search/code?q=filename:country_codes+extension:csv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since'
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/blob/master/populationData.tsv
    # Single file w/ minimal updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'neherlab_population': {
        'search_path': 'search/code?q=filename:populationData+extension:tsv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'csv_delimiter': '\t'
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/blob/master/hospital-data/ICU_capacity.tsv
    # Single file w/ minimal updates (additional rows). Use FULL_TABLE replication w/ activate_version
    'neherlab_icu_capacity': {
        'search_path': 'search/code?q=path:hospital-data+filename:ICU_capacity+extension:tsv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=desc',
        'data_key': 'items',
        'key_properties': ['__sdc_row_number'],
        'replication_method': 'FULL_TABLE',
        'activate_version': True,
        'replication_keys': ['git_last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'csv_delimiter': '\t'
    }
    # Add new streams here
}
