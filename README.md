# tap-covid-19

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls CSV files from [GitHub v3 API ](https://developer.github.com/v3/).
- Extracts the following resources:
  - CSV Data Files: [Git API Search](https://developer.github.com/v3/search/#search-code) with [filename and extension filters](https://help.github.com/en/articles/searching-code) from the following COVID-19 Repositories; streaming in new/changed files:
    - [Johns Hopkins CSSE Data](https://github.com/CSSEGISandData/COVID-19)
      - [jh_csse_daily](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
      - [jh_csse_time_series](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)
    - [EU Data](https://github.com/covid19-eu-zh/covid19-eu-data)
      - [eu_daily](https://github.com/covid19-eu-zh/covid19-eu-data/tree/master/dataset)
    - [Italy Data](https://github.com/pcm-dpc/COVID-19)
      - [italy_national_daily](https://github.com/pcm-dpc/COVID-19/tree/master/dati-andamento-nazionale)
      - [ita_regional_daily](https://github.com/pcm-dpc/COVID-19/tree/master/dati-regioni)
      - [ita_provincial_daily](https://github.com/pcm-dpc/COVID-19/tree/master/dati-province)
    - [NY Times US Data](https://github.com/nytimes/covid-19-data)
      - [nytimes_us_states](https://github.com/nytimes/covid-19-data/blob/master/us-states.csv)
      - [nytimes_us_counties](https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv)
    - [Neherlab Scenarios Data](https://github.com/neherlab/covid19_scenarios_data) from [Neherlab Biozentrum, Center for Computaitonal Biology](https://neherlab.org/)
      - [neherlab_case_counts](https://github.com/neherlab/covid19_scenarios_data/tree/master/case-counts)
      - [neherlab_country_codes](https://github.com/neherlab/covid19_scenarios_data/blob/master/country_codes.csv)
      - [neherlab_population](https://github.com/neherlab/covid19_scenarios_data/blob/master/populationData.tsv)
    - [COVID-19 Tracking Project](https://github.com/COVID19Tracking)
      - [c19_trk_us_daily](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/us_daily.csv)
      - [c19_trk_us_states_current](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_current.csv)
      - [c19_trk_us_states_daily](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_daily_4pm_et.csv)
      - [c19_trk_us_states_info](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_info.csv)
      - [c19_trk_us_population_states](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states.csv)
      - [c19_trk_us_population_states_age_groups](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states_agegroups.csv)
      - [c19_trk_us_population_counties](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_counties.csv)
      - [c19_trk_us_states_acs_health_insurance](https://github.com/COVID19Tracking/associated-data/blob/master/acs_health_insurance/acs_2018_health_insurance_coverage_estimates.csv)
      - [c19_trk_us_states_kff_hospital_beds (per 1000 population)](https://github.com/COVID19Tracking/associated-data/blob/master/kff_hospital_beds/kff_usa_hospital_beds_per_capita_2018.csv)
        - [kff source](https://www.kff.org/other/state-indicator/beds-by-ownership/?currentTimeframe=0&sortModel=%7B%22colId%22:%22Location%22,%22sort%22:%22asc%22%7D)

- Outputs the schema for each resource
- Incrementally pulls data based on the input state (file last-modified in GitHub)


## Streams

[jh_csse_daily_files](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
- Repository: CSSEGISandData/COVID-19
- Folder: csse_covid_19_data/csse_covid_19_daily_reports
- Search Endpoint: https://api.github.com/search/code?q=path:csse_covid_19_data/csse_covid_19_daily_reports+extension:csv+repo:CSSEGISandData/COVID-19&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/CSSEGISandData/COVID-19/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[jh_csse_daily](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
- Primary key fields: date, row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse jh_daily_file content, cleanse location fields, and convert to JSON

[eu_daily_files](https://github.com/covid19-eu-zh/covid19-eu-data/tree/master/dataset/daily)
- Repository: covid19-eu-zh/covid19-eu-data
- Folder: dataset/daily/
- Search Endpoint: https://api.github.com/search/code?q=path:dataset/daily+extension:csv+repo:covid19-eu-zh/covid19-eu-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/covid19-eu-zh/covid19-eu-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fields

[eu_daily](https://github.com/covid19-eu-zh/covid19-eu-data/tree/master/dataset/daily)
- Primary key fields: git_file_name, row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse eu_daily_file content, get date from table datetime, merge differing column sets, convert to JSON
- Notes:
    - source is one of {'country', 'ecdc'}
    - datetime was chosen as a key because some countries have more than one file a single date

[italy_national_daily_files](https://github.com/pcm-dpc/COVID-19/tree/master/dati-andamento-nazionale)
- Repository: pcm-dpc/COVID-19
- Folder: dati-andamento-nazionale
- Search Endpoint: hhttps://api.github.com/search/code?q=path:dati-andamento-nazionale+extension:csv+repo:pcm-dpc/COVID-19&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/pcm-dpc/COVID-19/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[italy_national_daily](https://github.com/pcm-dpc/COVID-19/tree/master/dati-andamento-nazionale)
- Primary key fields: date, row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse italy_national_daily content, cleanse location fields, and convert to JSON

[ita_regional_daily_files](https://github.com/pcm-dpc/COVID-19/tree/master/dati-regioni)
- Repository: pcm-dpc/COVID-19
- Folder: dati-regioni
- Search Endpoint: https://api.github.com/search/code?q=path:dati-regioni+extension:csv+repo:pcm-dpc/COVID-19&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/pcm-dpc/COVID-19/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[ita_regional_daily](https://github.com/pcm-dpc/COVID-19/tree/master/dati-regioni)
- Primary key fields: date, row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse italy_regional_daily content, cleanse location fields, and convert to JSON

[ita_provincial_daily_files](https://github.com/pcm-dpc/COVID-19/tree/master/dati-province)
- Repository: pcm-dpc/COVID-19
- Folder: dati-province
- Search Endpoint: https://api.github.com/search/code?q=path:dati-province+extension:csv+repo:pcm-dpc/COVID-19&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/pcm-dpc/COVID-19/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[ita_provincial_daily](https://github.com/pcm-dpc/COVID-19/tree/master/dati-province)
- Primary key fields: date, row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse italy_provincial_daily content, cleanse location fields, and convert to JSON

[nytimes_us_states_files](https://github.com/nytimes/covid-19-data/blob/master/us-states.csv)
- Repository: nytimes/covid-19-data
- Folder: . (root folder)
- Search Endpoint: https://api.github.com/search/code?q=filename:us-states+extension:csv+repo:nytimes/covid-19-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/nytimes/covid-19-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[nytimes_us_states](https://github.com/nytimes/covid-19-data/blob/master/us-states.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us-states content and convert to JSON, lookup state_name

[nytimes_us_counties_files](https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv)
- Repository: nytimes/covid-19-data
- Folder: . (root folder)
- Search Endpoint: https://api.github.com/search/code?q=filename:us-counties+extension:csv+repo:nytimes/covid-19-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/nytimes/covid-19-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[nytimes_us_counties](https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us-counties content and convert to JSON, lookup state_name

[c19_trk_us_states_current_files](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_current.csv)
- Repository: COVID19Tracking/covid-tracking-data
- Folder: data
- Search Endpoint: https://api.github.com/search/code?q=path:data+filename:state_current+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/covid-tracking-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_states_current](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_current.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse states_current content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_states_daily_files](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_daily_4pm_et.csv)
- Repository: COVID19Tracking/covid-tracking-data
- Folder: data
- Search Endpoint: https://api.github.com/search/code?q=path:data+filename:states_daily_4pm_et+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/covid-tracking-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_states_daily](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_daily_4pm_et.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse states_daily content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_states_info_files](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_info.csv)
- Repository: COVID19Tracking/covid-tracking-data
- Folder: data
- Search Endpoint: https://api.github.com/search/code?q=path:data+filename:states_info+extension:csv+repo:COVID19Tracking/covid-tracking-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/covid-tracking-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_states_info](https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/states_info.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse states_info content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_population_states_files](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states.csv)
- Repository: COVID19Tracking/associated-data
- Folder: us_census_data
- Search Endpoint: https://api.github.com/search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_states+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/associated-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_population_states](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us_population_states content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_population_states_age_groups_files](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states_agegroups.csv)
- Repository: COVID19Tracking/associated-data
- Folder: us_census_data
- Search Endpoint: https://api.github.com/search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_states_agegroups+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/associated-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_population_states_age_groups](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_states_agegroups.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us_population_states_age_groups content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_population_counties_files](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_counties.csv)
- Repository: COVID19Tracking/associated-data
- Folder: us_census_data
- Search Endpoint: https://api.github.com/search/code?q=path:us_census_data+filename:us_census_2018_population_estimates_counties+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/associated-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_population_counties](https://github.com/COVID19Tracking/associated-data/blob/master/us_census_data/us_census_2018_population_estimates_counties.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us_population_counties content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_states_acs_health_insurance_files](https://github.com/COVID19Tracking/associated-data/blob/master/acs_health_insurance/acs_2018_health_insurance_coverage_estimates.csv)
- Repository: COVID19Tracking/associated-data
- Folder: acs_health_insurance
- Search Endpoint: https://api.github.com/search/code?q=path:acs_health_insurance+filename:acs_2018_health_insurance_coverage_estimates+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/associated-data/contents/[GIT_FILE_PATH]
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_states_acs_health_insurance](https://github.com/COVID19Tracking/associated-data/blob/master/acs_health_insurance/acs_2018_health_insurance_coverage_estimates.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us_acs_health_insurance content and convert to JSON, camelCase to snake_case field keys

[c19_trk_us_states_kff_hospital_beds_files (per 1000 population)](https://github.com/COVID19Tracking/associated-data/blob/master/kff_hospital_beds/kff_usa_hospital_beds_per_capita_2018.csv)
- Repository: COVID19Tracking/associated-data
- Folder: kff_hospital_beds
- Search Endpoint: https://api.github.com/search/code?q=path:kff_hospital_beds+filename:kff_usa_hospital_beds_per_capita_2018+extension:csv+repo:COVID19Tracking/associated-data&sort=indexed&order=asc
- File Endpoint: https://api.github.com/repos/COVID19Tracking/associated-data/contents/[GIT_FILE_PATH]
- Original Sourc: KFF (Kaiser Family Foundation)
- Primary key fields: path
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove content node, add repository fielda

[c19_trk_us_states_kff_hospital_beds (per 1000 population)](https://github.com/COVID19Tracking/associated-data/blob/master/kff_hospital_beds/kff_usa_hospital_beds_per_capita_2018.csv)
- Primary key fields: row_number
- Replication strategy: FULL_TABLE (ALL for each file)
- Transformations: Decode, parse us_kff_hospital_beds content and convert to JSON, camelCase to snake_case field keys


## Authentication
This tap requires a GitHub API Token. See Step 3 below.
Even though this tap pulls from public GitHub repositories, API request limits are much lower without a token.

## Quick Start

1. Install

    Clone this repository, and then install using setup.py. We recommend using a virtualenv:

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > python setup.py install
    OR
    > cd .../tap-covid-19
    > pip install .
    ```
2. Dependent libraries
    The following dependent libraries were installed.
    ```bash
    > pip install singer-python
    > pip install singer-tools
    > pip install target-stitch
    > pip install target-json
    
    ```
    - [singer-tools](https://github.com/singer-io/singer-tools)
    - [target-stitch](https://github.com/singer-io/target-stitch)

3. Create your tap's `config.json` file. This tap connects to GitHub with a [GitHub OAuth2 Token](https://developer.github.com/v3/#authentication). This may be a [Personal Access Token](https://github.com/settings/tokens) or [Create an authorization for an App](https://developer.github.com/v3/oauth_authorizations/#create-a-new-authorization). 

    ```json
    {
        "api_token": "YOUR_GITHUB_API_TOKEN",
        "start_date": "2019-01-01T00:00:00Z",
        "user_agent": "tap-covid-19 <api_user_email@your_company.com>"
    }
    ```

    
    Optionally, also create a `state.json` file. `currently_syncing` is an optional attribute used for identifying the last object to be synced in case the job is interrupted mid-stream. The next run would begin where the last job left off.
    The `...files` streams use a datetime bookmark based on the GitHub `last_modified` datetime of the file that is returned in the GET header response.
    The `csv-data` streams us an integer bookmark based on the UNIX epoch time when the file batch was last sent. This is used with the `row_number` as a part of the Singer.io [Activate Version](https://github.com/singer-io/singer-python/blob/master/singer/messages.py#L137) logic to insert/update and delete the delta (when the new batch has fewer records).

    ```json
    {
      "currently_syncing": "jh_csse_daily_files",
      "bookmarks": {
        "c19_trk_us_states_daily": 1585425314448,
        "nytimes_us_states": 1585425318871,
        "eu_daily_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_daily_files": "2020-01-01T00:00:00Z",
        "neherlab_country_codes_files": "2020-01-01T00:00:00Z",
        "neherlab_population": 1585425494713,
        "nytimes_us_states_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_states_current": 1585425314001,
        "c19_trk_us_population_states_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_population_states_age_groups": 1585425300888,
        "c19_trk_us_states_current_files": "2020-01-01T00:00:00Z",
        "jh_csse_daily_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_daily": 1585425316108,
        "neherlab_case_counts_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_states_daily_files": "2020-01-01T00:00:00Z",
        "neherlab_country_codes": 1585425292893,
        "c19_trk_us_states_acs_health_insurance_files": "2020-01-01T00:00:00Z",
        "nytimes_us_counties": 1585425294166,
        "c19_trk_us_population_counties_files": "2020-01-01T00:00:00Z",
        "neherlab_population_files": "2020-01-01T00:00:00Z",
        "jh_csse_daily": 1585425322477,
        "eu_daily": 1585425391712,
        "c19_trk_us_states_info": "2020-01-01T00:00:00Z",
        "c19_trk_us_states_kff_hospital_beds": 1585425391252,
        "c19_trk_us_states_kff_hospital_beds_files": "2020-01-01T00:00:00Z",
        "nytimes_us_counties_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_states_acs_health_insurance": 1585425382387,
        "c19_trk_us_population_states": 1585425497765,
        "c19_trk_us_population_states_age_groups_files": "2020-01-01T00:00:00Z",
        "c19_trk_us_population_counties": 1585425316615,
        "neherlab_case_counts": 1585425220618,
        "italy_regional_daily_files": "2020-01-01T00:00:00Z",
        "italy_provincial_daily_files": "2020-01-01T00:00:00Z",
        "italy_national_daily": 1585502945880,
        "italy_national_daily_files": "2020-01-01T00:00:00Z",
        "italy_provincial_daily": 1585502961082,
        "italy_regional_daily": 1585502952425
        }
    }
    ```

4. Run the Tap in Discovery Mode
    This creates a catalog.json for selecting objects/fields to integrate:
    ```bash
    tap-covid-19 --config config.json --discover > catalog.json
    ```
   See the Singer docs on discovery mode
   [here](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#discovery-mode).

5. Run the Tap in Sync Mode (with catalog) and [write out to state file](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-a-singer-tap-with-a-singer-target)

    For Sync mode:
    ```bash
    > tap-covid-19 --config tap_config.json --catalog catalog.json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To load to json files to verify outputs:
    ```bash
    > tap-covid-19 --config tap_config.json --catalog catalog.json | target-json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To pseudo-load to [Stitch Import API](https://github.com/singer-io/target-stitch) with dry run:
    ```bash
    > tap-covid-19 --config tap_config.json --catalog catalog.json | target-stitch --config target_config.json --dry-run > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

6. Test the Tap
    
    While developing the COVID-19 tap, the following utilities were run in accordance with Singer.io best practices:
    Pylint to improve [code quality](https://github.com/singer-io/getting-started/blob/master/docs/BEST_PRACTICES.md#code-quality):
    ```bash
    > pylint tap_covid_19 -d missing-docstring -d logging-format-interpolation -d too-many-locals -d too-many-arguments
    ```
    Pylint test resulted in the following score:
    ```bash
    Your code has been rated at 9.44/10
    ```

    To [check the tap](https://github.com/singer-io/singer-tools#singer-check-tap) and verify working:
    ```bash
    > tap-covid-19 --config tap_config.json --catalog catalog.json | singer-check-tap > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    Check tap resulted in the following:
    ```bash
    Checking stdin for valid Singer-formatted data
    The output is valid.
    It contained 90452 messages for 37 streams.

        37 schema messages
     90452 record messages
        98 state messages

    Details by stream:
    +-----------------------------------------------+---------+---------+
    | stream                                        | records | schemas |
    +-----------------------------------------------+---------+---------+
    | c19_trk_us_population_states_age_groups_files | 1       | 1       |
    | c19_trk_us_states_daily                       | 1205    | 1       |
    | neherlab_country_codes_files                  | 1       | 1       |
    | neherlab_population                           | 237     | 1       |
    | neherlab_case_counts                          | 13006   | 1       |
    | c19_trk_us_states_current_files               | 1       | 1       |
    | jh_csse_daily_files                           | 66      | 1       |
    | c19_trk_us_states_info                        | 57      | 2       |
    | c19_trk_us_states_daily_files                 | 1       | 1       |
    | c19_trk_us_states_acs_health_insurance        | 1768    | 1       |
    | nytimes_us_counties_files                     | 1       | 1       |
    | neherlab_case_counts_files                    | 270     | 1       |
    | c19_trk_us_states_current                     | 56      | 1       |
    | c19_trk_us_daily                              | 24      | 1       |
    | c19_trk_us_daily_files                        | 1       | 1       |
    | c19_trk_us_population_states_files            | 2       | 1       |
    | neherlab_country_codes                        | 250     | 1       |
    | c19_trk_us_population_counties                | 3220    | 1       |
    | eu_daily                                      | 17288   | 1       |
    | c19_trk_us_states_acs_health_insurance_files  | 1       | 1       |
    | nytimes_us_states_files                       | 1       | 1       |
    | c19_trk_us_population_counties_files          | 1       | 1       |
    | c19_trk_us_population_states                  | 988     | 1       |
    | eu_daily_files                                | 298     | 1       |
    | nytimes_us_counties                           | 15836   | 1       |
    | c19_trk_us_states_kff_hospital_beds           | 51      | 1       |
    | c19_trk_us_population_states_age_groups       | 936     | 1       |
    | nytimes_us_states                             | 1386    | 1       |
    | jh_csse_daily                                 | 28136   | 1       |
    | neherlab_population_files                     | 1       | 1       |
    | c19_trk_us_states_kff_hospital_beds_files     | 1       | 1       |
    | italy_regional_daily_files                    | 37      | 1       |
    | italy_regional_daily                          | 735     | 1       |
    | italy_national_daily_files                    | 37      | 1       |
    | italy_provincial_daily                        | 4480    | 1       |
    | italy_provincial_daily_files                  | 37      | 1       |
    | italy_national_daily                          | 35      | 1       |
    +-----------------------------------------------+---------+---------+


    ```
---

Copyright &copy; 2020 Stitch
