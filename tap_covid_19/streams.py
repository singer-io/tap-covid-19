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

STREAMS = {
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/us_daily.csv
    'c19_trk_us_daily_files': {
        'search_path': 'search/code?q=path:data+filename:us_daily+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_daily': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_current.csv
    'c19_trk_us_states_current_files': {
        'search_path': 'search/code?q=path:data+filename:states_current+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_states_current': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_daily_4pm_et.csv
    'c19_trk_us_states_daily_files': {
        'search_path': 'search/code?q=path:data+filename:states_daily_4pm_et+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_states_daily': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_info.csv
    'c19_trk_us_states_info': {
        'search_path': 'search/code?q=path:data+filename:states_info+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_states_info': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_counties.csv
    'c19_trk_us_population_counties_files': {
        'search_path': 'search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_counties+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_population_counties': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states_agegroups.csv
    'c19_trk_us_population_states_age_groups_files': {
        'search_path': 'search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_states_agegroups+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_population_states_age_groups': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states.csv
    'c19_trk_us_population_states_files': {
        'search_path': 'search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_states+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_population_states': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/kff_hospital_beds/kff_usa_hospital_beds_per_capita_2018.csv
    'c19_trk_us_states_kff_hospital_beds_files': {
        'search_path': 'search/code?q=path:kff_hospital_beds+filename:kff_usa_hospital_beds_per_capita_2018+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_states_kff_hospital_beds': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/COVID19Tracking/associated-data/blob/master/acs_health_insurance/acs_2018_health_insurance_coverage_estimates.csv
    'c19_trk_us_states_acs_health_insurance_files': {
        'search_path': 'search/code?q=path:acs_health_insurance+filename:acs_2018_health_insurance_coverage_estimates+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'c19_trk_us_states_acs_health_insurance': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference https://github.com/covid19-eu-zh/covid19-eu-data/tree/master/dataset/daily
    'eu_daily_files': {
        'search_path': 'search/code?q=path:dataset/daily+extension:csv+repo:covid19-eu-zh/covid19-eu-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'eu_daily': {
                'key_properties': [
                    'git_file_name',
                    'row_number'
                ],
                'replication_method': 'FULL_TABLE',
            },
        },
    },
    # Reference: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
    'jh_csse_daily_files': {
        'search_path': 'search/code?q=path:csse_covid_19_data/csse_covid_19_daily_reports+extension:csv+repo:CSSEGISandData/COVID-19&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'jh_csse_daily': {
                'key_properties': ['date', 'row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/nytimes/covid-19-data/blob/master/us-states.csv
    'nytimes_us_states_files': {
        'search_path': 'search/code?q=filename:us-states+extension:csv+repo:nytimes/covid-19-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'nytimes_us_states': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv
    'nytimes_us_counties_files': {
        'search_path': 'search/code?q=filename:us-counties+extension:csv+repo:nytimes/covid-19-data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'nytimes_us_counties': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/tree/master/case-counts
    'neherlab_case_counts_files': {
        'search_path': 'search/code?q=path:case-counts+extension:tsv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'skip_header_rows': 3,
        'csv_delimiter': '\t',
        'children': {
            'neherlab_case_counts': {
                'key_properties': ['git_path', 'row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/blob/master/country_codes.csv
    'neherlab_country_codes_files': {
        'search_path': 'search/code?q=filename:country_codes+extension:csv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'children': {
            'neherlab_country_codes': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    },
    # Reference: https://github.com/neherlab/covid19_scenarios_data/blob/master/populationData.tsv
    'neherlab_population_files': {
        'search_path': 'search/code?q=filename:populationData+extension:tsv+repo:neherlab/covid19_scenarios_data&sort=indexed&order=asc',
        'data_key': 'items',
        'key_properties': ['path'],
        'replication_method': 'INCREMENTAL',
        'replication_keys': ['last_modified'],
        'bookmark_query_field': 'If-Modified-Since',
        'csv_delimiter': '\t',
        'children': {
            'neherlab_population': {
                'key_properties': ['row_number'],
                'replication_method': 'FULL_TABLE'
            }
        }
    }
    # Add new streams here
}

# De-nest children nodes for Discovery mode
def flatten_streams():
    flat_streams = {}
    # Loop through parents
    for stream_name, endpoint_config in STREAMS.items():
        flat_streams[stream_name] = {
            'key_properties': endpoint_config.get('key_properties'),
            'replication_method': endpoint_config.get('replication_method'),
            'replication_keys': endpoint_config.get('replication_keys')
        }
        # Loop through children
        children = endpoint_config.get('children')
        if children:
            for child_stream_name, child_endpoint_config in children.items():
                flat_streams[child_stream_name] = {
                    'key_properties': child_endpoint_config.get('key_properties'),
                    'replication_method': child_endpoint_config.get('replication_method'),
                    'replication_keys': child_endpoint_config.get('replication_keys')
                }
    return flat_streams
