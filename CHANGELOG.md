# Changelog

## 0.0.9
  * Add `character_set` parameter to `streams.py` and `sync.py` to deal with errors arising from accented characters in the Italian dataset files, which use `latin_1` and not `utf-8`. Fixes error decoding: `Forlì-Cesena`.

## 0.0.8
  * Change field `row_number` (a reserved word in Redshift) to `__sdc_row_number`. This requires dropping/re-loading tables in downstream target. Added 403 error handling for API Abuse Detection to wait for 2 minutes before resuming requests. Add endpoint: `neherlab_icu_capacity`.

## 0.0.7
  * Functional testing and validation changes to fields, streams, transforms.

## 0.0.6
  * Adjust `streams.py` and `sync.py` logic for `activate_version` based on source data replication strategy: single files vs. multiple files daily.

## 0.0.5
  * Fix issue with EU Daily providing decimal numbers for `hospitalized`. Add logic for `exclude_files`.

## 0.0.4
  * Change sorting, filtering, bookmarking strategy to reduce number of API calls and fix issue where all files are updated each sync.

## 0.0.3
  * Add Activate Version logic, improve JH CSSE cleansing. Adjust EU Daily PK. Add data sources for: NY Times, Neherlab (https://neherlab.org/), and COVID-19 Tracking Project.

## 0.0.2
  * Add EU Daily endpoint/streams.

## 0.0.1
  * Initial commit
