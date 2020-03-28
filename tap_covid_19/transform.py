import math
import string
from datetime import datetime
import pytz
from singer.utils import strftime
import re


us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

jh_country_name_map = {
    'US': 'United States of America',
    'United States': 'United States of America',
    'The Bahamas': 'Bahamas',
    'Bahamas The': 'Bahamas',
    'China': 'Mainland China',
    'Congo Brazzaville': 'Republic of the Congo',
    'Congo Kinshasa': 'Democratic Republic of Congo',
    'Czechia': 'Czech Republic',
    'Dominica': 'Dominican Republic',
    'Gambia The': 'Gambia',
    'The Gambia': 'Gambia',
    'Hong Kong SAR': 'Hong Kong',
    'Iran Islamic Republic of': 'Iran',
    'Republic of Ireland': 'Ireland',
    'Korea South': 'South Korea',
    'Republic of Korea': 'South Korea',
    'occupied Palestinian territory': 'Palestine',
    'Macao SAR': 'Macau',
    'Republic of Moldova': 'Moldova',
    'Russian Federation': 'Russia',
    'Taipei and environs': 'Taiwan',
    'TimorLeste': 'East Timor',
    'Viet Nam': 'Vietnam'
}


# Convert camelCase to snake_case
def camel_to_snake_case(name):
    regsub = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', regsub).lower()


# Convert keys in json
def transform_c19_trk(record):
    timezone = pytz.timezone('UTC')
    new_record = {}
    for key, val in list(record.items()):
        # Convert camelCase to snake_case for keys
        new_key = camel_to_snake_case(key)
        new_val = val
        # Remove ending .0 to convert to integer w/out error
        if isinstance(val, str):
            if val[-2:] == '.0':
                new_val = val[:-2]
        if key in ('state_local_government', 'non_profit', 'for_profit', 'pop_density'):
            new_val = val.replace('NA', '0')
        if key == 'date':
            new_val = strftime(timezone.localize(datetime.strptime(val, '%Y%m%d')))[:10]
        new_record[new_key] = new_val
    return new_record


def transform_eu_daily(record):
    new_record = {}

    # Git file fields
    file_name = record.get('git_file_name')
    new_record['git_path'] = record.get('git_path')
    new_record['git_sha'] = record.get('git_sha')
    new_record['git_last_modified'] = record.get('git_last_modified')
    new_record['git_file_name'] = file_name
    new_record['row_number'] = record.get('row_number')

    # Datetime
    dt_str = record.get('datetime')
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
    new_record['datetime'] = dt_str
    new_record['date'] = dt.date()

    # Report fields
    new_record['cases_100k_pop'] = record.get('cases/100k pop.')

    # ECDC files
    new_record['source'] = 'ecdc' if file_name.startswith('ecdc') else 'country'
    country = record.get('country')

    # Intensive Care sometimes ends with .0
    intensive_care = record.get('intensive_care', '0')
    if intensive_care[-2:] == '.0':
        intensive_care = intensive_care[:-2]
    new_record['intensive_care'] = intensive_care

    # Skip totals for ECDC files
    if country == 'Total':
        return None

    cases = record.get('cases')
    # e.g. "1 to 4"
    if 'to' in cases:
        lower, upper = cases.split(' to ')
        new_record['cases_lower'] = lower
        new_record['cases_upper'] = upper
        new_record['cases'] = None

    else:
        new_record['cases_lower'] = record.get('cases_lower')
        new_record['cases_upper'] = record.get('cases_upper')
        new_record['cases'] = record.get('cases')

    unchanged_fields =  [
        'country',
        'nuts_1',
        'nuts_2',
        'nuts_3',
        'lau',
        'population',
        'percent',
        'deaths',
        'recovered',
        'hospitalized',
        'tests',
        'quarantine',
    ]
    new_record.update({f: record.get(f) for f in unchanged_fields})

    return new_record


# CSV headers
# Initial: Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered
# 03-01-2020: Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered,Latitude,Longitude
# O3-23-2020: FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key
# Date formats: 1/22/2020 17:00, 2020-02-02T23:43:02
def transform_jh_csse_daily(record):
    # Header key variations for each field:
    province_state_keys = ['Province/State', 'Province_State']
    country_region_keys = ['Country/Region', 'Country_Region']
    last_update_keys = ['Last Update', 'Last_Update']
    confirmed_keys = ['Confirmed']
    deaths_keys = ['Deaths']
    recovered_keys = ['Recovered']
    latitude_keys = ['Latitude', 'Lat']
    longitude_keys = ['Longitude', 'Long_']
    active_keys = ['Active']
    combined_keys = ['Combined_Key']
    fips_keys = ['FIPS']
    admin_keys = ['Admin2']

    # Git file fields
    file_name = record.get('git_file_name')
    new_record = {}
    new_record['git_path'] = record.get('git_path')
    new_record['git_sha'] = record.get('git_sha')
    new_record['git_last_modified'] = record.get('git_last_modified')
    new_record['git_file_name'] = file_name
    new_record['row_number'] = record.get('row_number')

    # Date/Datetime from file_name
    timezone = pytz.timezone('UTC')
    file_date_str = file_name.lower().replace('.csv', '')
    file_dttm = timezone.localize(datetime.strptime(file_date_str, '%m-%d-%Y'))
    file_dttm_str = strftime(file_dttm)
    file_date_str = file_dttm_str[:10]
    new_record['date'] = file_date_str
    new_record['datetime'] = file_dttm_str

    # For US State code lookup
    abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

    # Loop thru keys/values
    is_a_cruise = False
    county = None
    for key, val in list(record.items()):
        # Trim keys
        key = str(key).strip()
        if isinstance(val, str):
            val = val.strip()
        if val == '':
            val = None

        # Replace key/values and field transformations, cleansing
        if key in province_state_keys:
            new_record['province_state'] = val
            state = None

            if val is None or val == '' or val == 'None':
                new_val = 'None'
            vals = []
            if val:
                vals = val.split(',')
            val_len = len(vals)
            if val in ('Washington, D.C.', 'District of Columbia'):
                new_val = 'Washington, D.C.'
            elif val in ('Virgin Islands, U.S.', 'United States Virgin Islands'):
                new_val = 'U.S. Virgin Islands'
            elif val in ('Recovered', 'US', 'Wuhan Evacuee'):
                new_val = 'None'
            elif val_len == 0:
                new_val = 'None'
            elif val_len == 1:
                state = abbrev_us_state.get(val)
                if state:
                    new_val = state
                else:
                    new_val = val
            else:
                for value in vals:
                    # Trim new_val
                    new_val = str(value).strip()
                    if 'county' in new_val.lower():
                        county = new_val.replace('County', '').replace('county', '').strip()

                    # Lookup State code to get State Name
                    state = abbrev_us_state.get(new_val)
                if state:
                    new_val = state

            if 'cruise' in new_val.lower() or 'princess' in new_val.lower() or 'from' \
                in new_val.lower():
                is_a_cruise = True
                new_val = 'Cruise Ship'

            if new_val is None or new_val == '' or new_val == 'None':
                new_val = 'None'

            new_record['province_state_cleansed'] = new_val

        elif key in country_region_keys:
            new_record['country_region'] = val

            # Remove punctuation
            new_val = val.translate(str.maketrans('', '', string.punctuation))

            if 'cruise' in new_val.lower() or 'princess' in new_val.lower() or 'from' \
                in new_val.lower():
                is_a_cruise = True
                new_record['province_state_cleansed'] = 'Cruise Ship'

            # Replace/standardize country names
            country_map = jh_country_name_map.get(new_val)
            if country_map:
                new_val = country_map

            new_record['country_region_cleansed'] = new_val

        elif key in last_update_keys:
            new_val = val
            # Try format 1
            try:
                new_val = strftime(timezone.localize(datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')))
            except Exception as err:
                pass
            # Try format 2
            try:
                new_val = strftime(timezone.localize(datetime.strptime(val, '%m/%d/%Y %H:%M')))
            except Exception as err:
                pass
            new_record['last_update'] = new_val

        elif key in confirmed_keys:
            try:
                new_val = int(val)
            except Exception as err:
                new_val = 0
                pass
            new_record['confirmed'] = new_val

        elif key in deaths_keys:
            new_val = 0
            try:
                new_val = int(val)
            except Exception as err:
                pass
            new_record['deaths'] = new_val

        elif key in recovered_keys:
            new_val = 0
            try:
                new_val = int(val)
            except Exception as err:
                pass
            new_record['recovered'] = new_val

        elif key in latitude_keys:
            new_val = None
            try:
                new_val = round(float(val), 10)
            except Exception as err:
                pass
            if new_val == 0.0:
                new_val = None
            new_record['latitude'] = new_val

        elif key in longitude_keys:
            new_val = None
            try:
                new_val = round(float(val), 10)
            except Exception as err:
                pass
            if new_val == 0.0:
                new_val = None
            new_record['longitude'] = new_val

        elif key in active_keys:
            try:
                new_val = int(val)
            except Exception as err:
                new_val = 0
            new_record['active'] = new_val

        elif key in combined_keys:
            new_record['combined_key'] = val

        elif key in fips_keys:
            new_record['fips'] = val

        elif key in admin_keys:
            new_record['admin_area'] = val

        # End keys loop

    new_record['is_a_cruise'] = is_a_cruise

    if new_record.get('province_state') is None:
        new_record['province_state'] = 'None'

    return new_record


# CSV headers
# us-states, 03-27-2020: date,state,fips,cases,deaths
# us-counties, 03-27-2020: date,county,state,fips,cases,deaths
# date formats: 2020-01-28
def transform_nytimes(record):
    # Git file fields
    new_record = record

    # Date/Datetime from date field
    timezone = pytz.timezone('UTC')
    date_str = record.get('date')
    dttm = timezone.localize(datetime.strptime(date_str, '%Y-%m-%d')) # YYYY-MM-DD
    dttm_str = strftime(dttm)
    new_record['date'] = date_str
    new_record['datetime'] = dttm_str

    # For US State code lookup
    abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))
    state_code = record.get('state')
    new_record['state_name'] = abbrev_us_state.get(state_code)

    return new_record


# CSV headers, 3/27/2020: [location] time	cases	deaths	hospitalized	ICU	recovered
#  location on some files; otherwise location in file name
# Date formats: 2020-01-28
def transform_neherlab_case_counts(record):
    new_record = record

    # Date/Datetime from date field
    timezone = pytz.timezone('UTC')
    date_str = record.get('time')
    dttm = None
    try:
        dttm = timezone.localize(datetime.strptime(date_str, '%Y-%m-%d')) # YYYY-MM-DD
    except Exception as err:
        pass
    # Try format 2
    try:
        dttm = timezone.localize(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')) # YYYY-MM-DDTHH:MM:SS
    except Exception as err:
        pass
    dttm_str = strftime(dttm)
    new_record['date'] = date_str[:10]
    new_record['datetime'] = dttm_str
    new_record.pop('time', None)

    if not record.get('location'):
        # Get location from Git path
        new_record['location'] = record.get('git_path').replace(
            'case-counts/', '').replace('.tsv', '')

    return new_record


# CSV headers, 3/27/2020: name,alpha-2,alpha-3,country-code,iso_3166-2,region,sub-region,intermediate-region,region-code,sub-region-code,intermediate-region-code
def transform_neherlab_country_codes(record):
    new_record = {}
    for key, val in list(record.items()):
        # Replace dashes in keys with underscores
        new_key = key.replace('-', '_')
        new_record[new_key] = val
    return new_record


# CSV headers, 3/27/2020: name	populationServed	ageDistribution	hospitalBeds	ICUBeds	suspectedCaseMarch1st	importsPerDay
def transform_neherlab_population(record):
    new_record = {}
    for key, val in list(record.items()):
        new_key = key
        if key == 'populationServed':
            new_key = 'population'
        elif key == 'ageDistribution':
            new_key = 'country'
        elif key == 'hospitalBeds':
            new_key = 'hospital_beds'
        elif key == 'ICUBeds':
            new_key = 'icu_beds'
        elif key == 'suspectedCaseMarch1st':
            new_key = 'suspected_cases_mar_1st'
        elif key == 'importsPerDay':
            new_key = 'imports_per_day'

        new_record[new_key] = val
    return new_record


def transform_record(stream_name, record):
    if stream_name == 'jh_csse_daily':
        new_record = transform_jh_csse_daily(record)
    elif stream_name == 'eu_daily':
        new_record = transform_eu_daily(record)
    elif stream_name in ('nytimes_us_states', 'nytimes_us_counties'):
        new_record = transform_nytimes(record)
    elif stream_name == 'neherlab_case_counts':
        new_record = transform_neherlab_case_counts(record)
    elif stream_name == 'neherlab_country_codes':
        new_record = transform_neherlab_country_codes(record)
    elif stream_name == 'neherlab_population':
        new_record = transform_neherlab_country_codes(record)
    elif stream_name[:7] == 'c19_trk':
        new_record = transform_c19_trk(record)

    # elif (other streams)
    else:
        new_record = record

    return new_record
