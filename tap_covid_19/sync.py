
import base64
import io
import csv
import time
from datetime import datetime
import pytz
import singer
from singer import metrics, metadata, Transformer, utils
from singer.utils import strptime_to_utc
from singer.messages import RecordMessage
from tap_covid_19.streams import STREAMS
from tap_covid_19.transform import transform_record

LOGGER = singer.get_logger()


def write_schema(catalog, stream_name):
    stream = catalog.get_stream(stream_name)
    schema = stream.schema.to_dict()
    try:
        singer.write_schema(stream_name, schema, stream.key_properties)
    except OSError as err:
        LOGGER.error('OS Error writing schema for: {}'.format(stream_name))
        raise err


def write_record(stream_name, record, time_extracted, version=None):
    try:
        if version:
            singer.messages.write_message(
                RecordMessage(
                    stream=stream_name,
                    record=record,
                    version=version,
                    time_extracted=time_extracted))
        else:
            singer.messages.write_record(
                stream_name=stream_name,
                record=record,
                time_extracted=time_extracted)
    except OSError as err:
        LOGGER.error('OS Error writing record for: {}'.format(stream_name))
        LOGGER.error('record: {}'.format(record))
        raise err


def get_bookmark(state, stream, default):
    if (state is None) or ('bookmarks' not in state):
        return default
    return (
        state
        .get('bookmarks', {})
        .get(stream, default)
    )


def write_bookmark(state, stream, value):
    if 'bookmarks' not in state:
        state['bookmarks'] = {}
    state['bookmarks'][stream] = value
    LOGGER.info('Write state for stream: {}, value: {}'.format(stream, value))
    singer.write_state(state)


def transform_datetime(this_dttm):
    with Transformer() as transformer:
        new_dttm = transformer._transform_datetime(this_dttm)
    return new_dttm


def process_records(catalog, #pylint: disable=too-many-branches
                    stream_name,
                    records,
                    time_extracted,
                    version=None):
    stream = catalog.get_stream(stream_name)
    schema = stream.schema.to_dict()
    stream_metadata = metadata.to_map(stream.metadata)

    with metrics.record_counter(stream_name) as counter:
        for record in records:
            # Transform record for Singer.io
            with Transformer() as transformer:
                try:
                    transformed_record = transformer.transform(
                        record, schema, stream_metadata)
                except Exception as err:
                    LOGGER.error('Transformer error: {}, Strean: {}'.format(err, stream_name))
                    LOGGER.error('record: {}'.format(record))
                    raise err

                # LOGGER.info('transformed_record: {}'.format(transformed_record)) # COMMENT OUT

                write_record(
                    stream_name,
                    transformed_record,
                    time_extracted=time_extracted,
                    version=version)
                counter.increment()

        return counter.value


# Sync a specific endpoint.
def sync_endpoint(client, #pylint: disable=too-many-branches
                  catalog,
                  state,
                  start_date,
                  stream_name,
                  search_path,
                  endpoint_config,
                  bookmark_field=None,
                  selected_streams=None):

    # Endpoint parameters
    bookmark_query_field = endpoint_config.get('bookmark_query_field', None)
    data_key = endpoint_config.get('data_key', stream_name)
    exclude_files = endpoint_config.get('exclude_files', [])
    csv_delimiter = endpoint_config.get('csv_delimiter', ',')
    skip_header_rows = endpoint_config.get('skip_header_rows', 0)
    activate_version_ind = endpoint_config.get('activate_version', False)
    alt_character_set = endpoint_config.get('alt_character_set', 'utf-8')
    # LOGGER.info('data_key = {}'.format(data_key))

    # Get the latest bookmark for the stream and set the last_datetime
    last_datetime = get_bookmark(state, stream_name, start_date)
    last_dttm = strptime_to_utc(last_datetime)
    timezone = pytz.timezone('UTC')
    bookmark_dttm = utils.now() # Initialize bookmark_dttn
    max_bookmark_value = None

    # Convert to GitHub date format, example: Sun, 13 Oct 2019 22:40:01 GMT
    last_modified = last_dttm.strftime("%a, %d %b %Y %H:%M:%S %Z'")
    LOGGER.info('HEADER If-Modified-Since: {}'.format(last_modified))

    # Write schema and log selected fields for stream
    write_schema(catalog, stream_name)
    selected_fields = get_selected_fields(catalog, stream_name)
    LOGGER.info('Stream: {}, selected_fields: {}'.format(stream_name, selected_fields))
    
    # pagination: loop thru all pages of data using next_url (if not None)
    page = 1
    offset = 0
    file_count = 0
    total_records = 0
    next_url = '{}/{}'.format(client.base_url, search_path)

    # Loop through all search items pages (while there are more pages, next_url)
    #   and until bookmark_dttm < last_dttm
    first_record = True
    while next_url is not None and bookmark_dttm >= last_dttm:
        LOGGER.info('Search URL for Stream {}: {}'.format(stream_name, next_url))

        # API request search_data
        search_data = {}
        search_data, next_url, search_last_modified = client.get(
            url=next_url,
            endpoint=stream_name)
        LOGGER.info('next_url = {}'.format(next_url))
        # LOGGER.info('search_data = {}'.format(search_data)) # COMMENT OUT

        # time_extracted: datetime when the data was extracted from the API
        time_extracted = utils.now()
        search_items = search_data.get(data_key, [])
        if not search_items:
            LOGGER.info('Stream: {}, no files found'.format(stream_name))
            break # No data results

        i = 0 # i = search item number
        item_total = len(search_items)
        # Loop through all search items until bookmark_dttm < last_dttm
        while i <= (item_total - 1) and bookmark_dttm >= last_dttm:
            item = search_items[i]
            file_name = item.get('name')
            # Skip excluded files
            if file_name in exclude_files:
                i = i + 1
                if i > (item_total - 1):
                    break
                else:
                    item = search_items[i]
            csv_records = []
            file_count = file_count + 1
            # url (content url) is preferable to git_url (blob url) b/c it provides
            #   last-modified header for bookmark
            # However, git_url allows for up to 100 MB files; url allows for up to 1 MB files
            # Therefore, we use the git_url (blob) endpoint
            # And make another call to the commits endpoint to get last-modified
            file_url = item.get('git_url')
            git_repository = item.get('repository', {}).get('name')
            git_owner = item.get('repository', {}).get('owner', {}).get('login')
            file_path = item.get('path')
            file_sha = item.get('sha')
            file_name = item.get('name')
            file_html_url = item.get('html_url')
            
            headers = {}
            if bookmark_query_field:
                headers[bookmark_query_field] = last_modified
            # API request commits_data for single-file, to get file last_modified
            commit_url = '{}/repos/{}/{}/commits?path={}'.format(
                client.base_url, git_owner, git_repository, file_path)
            LOGGER.info('Commit URL for Stream {}: {}'.format(stream_name, commit_url))
            commit_data, commits_next_url, commit_last_modified = client.get(
                url=commit_url,
                headers=headers,
                endpoint='{}_commits'.format(stream_name))
            
            # Bookmarking: search data (and commit data) sorted by last-modified desc
            # 1st item on 1st page sets max_bookmark_value = last-modified
            bookmark_dttm = strptime_to_utc(commit_last_modified)
            if first_record and bookmark_dttm > last_dttm:
                max_bookmark_value = commit_last_modified
                max_bookmark_dttm = bookmark_dttm
                max_bookmark_epoch = int((max_bookmark_dttm - timezone.localize(datetime(1970, 1, 1))).total_seconds())

                # For some streams (activate_version = True):
                # Emit a Singer ACTIVATE_VERSION message before initial sync (but not subsequent syncs)
                # everytime after each sheet sync is complete.
                # This forces hard deletes on the data downstream if fewer records are sent.
                # https://github.com/singer-io/singer-python/blob/master/singer/messages.py#L137
                if activate_version_ind:
                    if last_datetime == start_date:
                        activate_version = 0
                    else:
                        activate_version = max_bookmark_epoch
                    activate_version_message = singer.ActivateVersionMessage(
                            stream=stream_name,
                            version=activate_version)
                    if last_datetime == start_date:
                        # initial load, send activate_version before AND after data sync
                        singer.write_message(activate_version_message)
                        LOGGER.info('INITIAL SYNC, Stream: {}, Activate Version: {}'.format(stream_name, activate_version))
                else:
                    activate_version = None
                # End: if first_record and bookmark_dttm > last_dttm

            if commit_data and bookmark_dttm >= last_dttm:
                # API request file_data for item, single-file (ignore file_next_url)
                file_data = {}
                headers = {}
                LOGGER.info('File URL for Stream {}: {}'.format(stream_name, file_url))
                file_data, file_next_url, file_last_modified = client.get(
                    url=file_url,
                    headers=headers,
                    endpoint=stream_name)
                # LOGGER.info('file_data: {}'.format(file_data)) # TESTING ONLY - COMMENT OUT

                if file_data:
                    # Read, decode, and parse content blob to json
                    content = file_data.get('content')
                    content_list = []
                    if content:
                        content_b64 = base64.b64decode(content)
                        # Italian files typically use character_set: utf-8
                        #  However, some newer files use character_set: latin_1
                        # All other files use character_set: utf-8 (default)
                        try:
                            content_str = content_b64.decode('utf-8')
                        except UnicodeDecodeError as err:
                            LOGGER.warning('UTF-8 UNICODE DECODE ERROR: {}'.format(err))
                            # Try decoding with Alternate Character Set (from streams.py)
                            content_str = content_b64.decode(alt_character_set)
                        content_array = content_str.splitlines()
                        content_array_sliced = content_array[skip_header_rows:]
                        reader = csv.DictReader(content_array_sliced, delimiter=csv_delimiter)
                        content_list = [r for r in reader]

                    LOGGER.info('Retrieved file_name: {}'.format(file_name))

                    # LOGGER.info('file_data: {}'.format(file_data)) # TESTING ONLY - COMMENT OUT

                    # Loop thru and append csv records
                    row_number = 1
                    for record in content_list:
                        record['git_owner'] = git_owner
                        record['git_repository'] = git_repository
                        record['git_url'] = file_url
                        record['git_html_url'] = file_html_url
                        record['git_path'] = file_path
                        record['git_sha'] = file_sha
                        record['git_file_name'] = file_name
                        record['git_last_modified'] = commit_last_modified
                        record['__sdc_row_number'] = row_number

                        # Transform record and append
                        transformed_csv_record = {}
                        try:
                            transformed_csv_record = transform_record(stream_name, record)
                        except Exception as err:
                            LOGGER.error('Transform Record error: {}, Strean: {}'.format(err, stream_name))
                            LOGGER.error('record: {}'.format(record))
                            raise err

                        # Bad records and totals
                        if transformed_csv_record is None:
                            continue

                        csv_records.append(transformed_csv_record)
                        row_number = row_number + 1
                    # End If file_data

                record_count = process_records(
                    catalog=catalog,
                    stream_name=stream_name,
                    records=csv_records,
                    time_extracted=time_extracted,
                    version=activate_version)
                LOGGER.info('Stream {}, batch processed {} records'.format(
                    stream_name, record_count))
                total_records = total_records + record_count
                # End if commit_data
            first_record = False
            i = i + 1 # Next search item record
            # End: while i <= (item_total - 1) and bookmark_dttm >= last_dttm

        # to_rec: to record; ending record for the batch page
        to_rec = offset + file_count
        LOGGER.info('Synced Stream: {}, page: {}, records: {} to {}'.format(
            stream_name,
            page,
            offset,
            to_rec))
        # Pagination: increment the offset by the limit (batch-size) and page
        offset = offset + file_count
        page = page + 1
        # End: next_url is not None and bookmark_dttm >= last_dttm

    if file_count > 0 and max_bookmark_value:
        # End of Stream: Send Activate Version (if needed) and update State
        if activate_version_ind:
            singer.write_message(activate_version_message)
        write_bookmark(state, stream_name, max_bookmark_value)
    else:
        LOGGER.warning('NO NEW DATA FOR STREAM: {}'.format(stream_name))
        write_bookmark(state, stream_name, last_datetime)

    # Return total_records across all pages
    LOGGER.info('Synced Stream: {}, TOTAL pages: {}, file count: {}, total records: {}'.format(
        stream_name,
        page - 1,
        file_count,
        total_records))
    return total_records


# Currently syncing sets the stream currently being delivered in the state.
# If the integration is interrupted, this state property is used to identify
#  the starting point to continue from.
# Reference: https://github.com/singer-io/singer-python/blob/master/singer/bookmarks.py#L41-L46
def update_currently_syncing(state, stream_name):
    if (stream_name is None) and ('currently_syncing' in state):
        del state['currently_syncing']
    else:
        singer.set_currently_syncing(state, stream_name)
    singer.write_state(state)


# List selected fields from stream catalog
def get_selected_fields(catalog, stream_name):
    stream = catalog.get_stream(stream_name)
    mdata = metadata.to_map(stream.metadata)
    mdata_list = singer.metadata.to_list(mdata)
    selected_fields = []
    for entry in mdata_list:
        field = None
        try:
            field = entry['breadcrumb'][1]
            if entry.get('metadata', {}).get('selected', False):
                selected_fields.append(field)
        except IndexError:
            pass
    return selected_fields

def sync(client, config, catalog, state):
    start_date = config.get('start_date')

    # Get selected_streams from catalog, based on state last_stream
    #   last_stream = Previous currently synced stream, if the load was interrupted
    last_stream = singer.get_currently_syncing(state)
    LOGGER.info('last/currently syncing stream: {}'.format(last_stream))
    selected_streams = []
    for stream in catalog.get_selected_streams(state):
        selected_streams.append(stream.stream)
    LOGGER.info('selected_streams: {}'.format(selected_streams))

    if not selected_streams:
        return

    # Loop through selected_streams
    for stream_name, endpoint_config in STREAMS.items():
        if stream_name in selected_streams:
            LOGGER.info('START Syncing Stream: {}'.format(stream_name))
            update_currently_syncing(state, stream_name)
            search_path = endpoint_config.get('search_path', stream_name)
            bookmark_field = next(iter(endpoint_config.get('replication_keys', [])), None)
            total_records = sync_endpoint(
                client=client,
                catalog=catalog,
                state=state,
                start_date=start_date,
                stream_name=stream_name,
                search_path=search_path,
                endpoint_config=endpoint_config,
                bookmark_field=bookmark_field,
                selected_streams=selected_streams)

            update_currently_syncing(state, None)
            LOGGER.info('FINISHED Syncing Stream: {}, total_records: {}'.format(
                stream_name,
                total_records))
